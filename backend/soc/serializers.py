from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Threat, Incident, Alert, AuditEvent, AnalystSettings
User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    def get_role(self, obj): return 'ADMIN' if obj.is_staff else 'SECURITY ANALYST'
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'role']
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=128)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name']
    def validate(self, attrs):
        try: validate_password(attrs['password'], User(username=attrs['username'], email=attrs.get('email', '')))
        except ValidationError as e: raise serializers.ValidationError({'password': e.messages})
        return attrs
    def create(self, data): return User.objects.create_user(**data)
class FlowSerializer(serializers.Serializer):
    source_ip = serializers.IPAddressField()
    destination_ip = serializers.IPAddressField()
    destination_port = serializers.IntegerField(min_value=0, max_value=65535)
    protocol = serializers.ChoiceField(choices=['TCP', 'UDP', 'ICMP'])
    flow_duration = serializers.FloatField(min_value=0, max_value=86400000)
    packets_per_second = serializers.FloatField(min_value=0, max_value=1000000000)
    packet_length_mean = serializers.FloatField(min_value=0, max_value=65535)
    failed_logins = serializers.IntegerField(min_value=0, max_value=1000000)
    unique_ports = serializers.IntegerField(min_value=1, max_value=65536)
    outbound_bytes = serializers.IntegerField(min_value=0, max_value=10**15)
    periodic_connections = serializers.IntegerField(min_value=0, max_value=1000000)
    payload_anomaly = serializers.BooleanField()
class ThreatSerializer(serializers.ModelSerializer):
    incident_ids = serializers.PrimaryKeyRelatedField(source='incidents', many=True, read_only=True)
    class Meta:
        model = Threat
        exclude = ['owner']
class IncidentSerializer(serializers.ModelSerializer):
    assigned_analyst = serializers.CharField(source='assigned_to.username', read_only=True, default='Unassigned')
    threat_ids = serializers.PrimaryKeyRelatedField(source='threats', many=True, read_only=True)
    class Meta:
        model = Incident
        exclude = ['owner', 'threats']
        read_only_fields = ['severity', 'assigned_to']
class IncidentCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=160)
    threat_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False, max_length=100)
class IncidentUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['Open', 'Investigating', 'Contained', 'Resolved'], required=False)
    resolution = serializers.CharField(max_length=5000, required=False, allow_blank=True)
    assigned_to = serializers.IntegerField(min_value=1, required=False)
class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        exclude = ['owner']
class AuditSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    class Meta:
        model = AuditEvent
        exclude = ['owner', 'actor']
class SettingsSerializer(serializers.ModelSerializer):
    polling_seconds = serializers.IntegerField(min_value=10, max_value=300)
    class Meta:
        model = AnalystSettings
        fields = ['polling_seconds', 'auto_incident']
class ResponseSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['Investigate', 'Acknowledge', 'Contain', 'Block source', 'Isolate', 'Resolve'])
