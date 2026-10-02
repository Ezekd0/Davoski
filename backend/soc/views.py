from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Threat, Incident, Alert, AuditEvent, AnalystSettings
from .serializers import (UserSerializer, RegisterSerializer, FlowSerializer, ThreatSerializer, IncidentSerializer, IncidentCreateSerializer, IncidentUpdateSerializer, AlertSerializer, AuditSerializer, SettingsSerializer, ResponseSerializer)
from .services.workflow import analyze, respond, create_incident, audit
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except DatabaseError:
        return Response({'status': 'unhealthy', 'database': 'unavailable', 'analysis_mode': 'demo'}, status=503)
    return Response({'status':'healthy','database':'connected','analysis_mode':'demo','version':'1.0.0'})
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
@api_view(['GET'])
def profile(request): return Response(UserSerializer(request.user).data)
@api_view(['POST'])
def logout(request):
    try: RefreshToken(request.data.get('refresh', '')).blacklist()
    except Exception: raise ValidationError({'refresh':'Invalid refresh token'})
    return Response(status=204)
class OwnedViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        queryset = self.queryset.all()
        return queryset if self.request.user.is_staff else queryset.filter(owner=self.request.user)
class ThreatViewSet(OwnedViewSet):
    queryset = Threat.objects.prefetch_related('incidents')
    serializer_class = ThreatSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        for field in ['severity','status','threat_type']:
            if self.request.query_params.get(field): qs = qs.filter(**{field:self.request.query_params[field]})
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(source_ip__icontains=search)|Q(destination_ip__icontains=search)|Q(threat_type__icontains=search))
        return qs
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        serializer = FlowSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        return Response(ThreatSerializer(analyze(request.user, serializer.validated_data)).data, status=201)
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        serializer = ResponseSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            threat = Threat.objects.select_for_update().get(pk=self.get_object().pk)
            return Response(ThreatSerializer(respond(request.user, threat, serializer.validated_data['action'])).data)
class IncidentViewSet(OwnedViewSet):
    queryset = Incident.objects.prefetch_related('threats').select_related('assigned_to')
    serializer_class = IncidentSerializer
    def create(self, request):
        serializer = IncidentCreateSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        ids = set(serializer.validated_data['threat_ids'])
        threats = list(Threat.objects.filter(id__in=ids, owner=request.user))
        if len(threats) != len(ids): raise ValidationError({'threat_ids':'Select existing threats belonging to your account'})
        incident = create_incident(request.user, serializer.validated_data['title'], threats)
        return Response(IncidentSerializer(incident).data, status=201)
    def partial_update(self, request, pk=None):
        serializer = IncidentUpdateSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            incident = Incident.objects.select_for_update().get(pk=self.get_object().pk)
            data = serializer.validated_data
            resolution = data.get('resolution', incident.resolution)
            if data.get('status') == 'Resolved' and not resolution.strip(): raise ValidationError({'resolution':'A resolution note is required'})
            if 'assigned_to' in data:
                if not request.user.is_staff and data['assigned_to'] != request.user.id: raise ValidationError({'assigned_to':'Analysts may assign to themselves only'})
                if not get_user_model().objects.filter(id=data['assigned_to'], is_active=True).exists(): raise ValidationError({'assigned_to':'Analyst not found'})
            for key,value in data.items(): setattr(incident, 'assigned_to_id' if key=='assigned_to' else key, value)
            incident.save()
            audit(incident.owner, request.user, f'Incident updated: {incident.status}', incident=incident)
            Alert.objects.create(owner=incident.owner, message=f'INC-{incident.id:04d} is now {incident.status}', severity=incident.severity, incident=incident)
            return Response(IncidentSerializer(incident).data)
class AlertViewSet(OwnedViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object(); alert.status='Acknowledged'; alert.save(update_fields=['status'])
        audit(alert.owner, request.user, f'Alert ALT-{alert.id:04d} acknowledged', threat=alert.threat, incident=alert.incident)
        return Response(self.get_serializer(alert).data)
class AuditViewSet(OwnedViewSet):
    queryset = AuditEvent.objects.select_related('actor')
    serializer_class = AuditSerializer
@api_view(['GET'])
def dashboard(request):
    threats = Threat.objects.all() if request.user.is_staff else Threat.objects.filter(owner=request.user)
    incidents = Incident.objects.all() if request.user.is_staff else Incident.objects.filter(owner=request.user)
    alerts = Alert.objects.all() if request.user.is_staff else Alert.objects.filter(owner=request.user)
    since = timezone.now().date()-timedelta(days=6)
    daily = {str(r['date']):r['count'] for r in threats.filter(created_at__date__gte=since).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id'))}
    timeline = [{'date':str(since+timedelta(days=i)), 'count':daily.get(str(since+timedelta(days=i)),0)} for i in range(7)]
    return Response({'total_threats':threats.exclude(threat_type='Benign').count(), 'total_analyses':threats.count(), 'critical_threats':threats.filter(severity='Critical').count(), 'active_incidents':incidents.exclude(status='Resolved').count(), 'unresolved_alerts':alerts.filter(status='Unread').count(), 'average_confidence':round(threats.aggregate(v=Avg('confidence'))['v'] or 0,1), 'detection_accuracy':None, 'mode':'demo', 'categories':list(threats.values('threat_type').annotate(count=Count('id')).order_by('threat_type')), 'severities':list(threats.values('severity').annotate(count=Count('id')).order_by('severity')), 'statuses':list(threats.values('status').annotate(count=Count('id')).order_by('status')), 'timeline':timeline, 'recent_threats':ThreatSerializer(threats[:6],many=True).data, 'recent_alerts':AlertSerializer(alerts[:5],many=True).data})
@api_view(['GET','PATCH'])
def settings_view(request):
    settings, _ = AnalystSettings.objects.get_or_create(owner=request.user)
    if request.method=='PATCH':
        serializer = SettingsSerializer(settings,data=request.data,partial=True); serializer.is_valid(raise_exception=True); serializer.save()
        audit(request.user,request.user,'Analyst settings updated')
    return Response(SettingsSerializer(settings).data)
class UsersView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = get_user_model().objects.filter(is_active=True)
    serializer_class = UserSerializer
