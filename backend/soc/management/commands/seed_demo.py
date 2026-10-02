import os
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from soc.models import Threat, Alert, Incident, AuditEvent
from soc.services.workflow import analyze
class Command(BaseCommand):
    help = 'Create explicitly labeled demo users and deterministic fixture traffic (idempotent).'
    def handle(self, *args, **options):
        from django.conf import settings
        if not settings.DEBUG: raise CommandError('Demo seeding is only permitted with DEBUG=true')
        password = os.getenv('DEMO_PASSWORD', 'DemoSecure!2026')
        admin, created = get_user_model().objects.get_or_create(username='admin', defaults={'email':'admin@example.test','first_name':'Alex Morgan','is_staff':True})
        if created: admin.set_password(password); admin.save()
        analyst, created = get_user_model().objects.get_or_create(username='analyst', defaults={'email':'analyst@example.test','first_name':'Jordan Lee'})
        if created: analyst.set_password(password); analyst.save()
        if not Threat.objects.filter(owner=admin).exists():
            for i in range(36):
                data = dict(source_ip=f'192.0.2.{10+i}', destination_ip=f'10.0.0.{i%5+10}', destination_port=443, protocol='TCP', flow_duration=1250, packets_per_second=120, packet_length_mean=512, failed_logins=0, unique_ports=1, outbound_bytes=15000, periodic_connections=3, payload_anomaly=False)
                kind = i%7
                field = ['packets_per_second','unique_ports','failed_logins','periodic_connections','payload_anomaly','outbound_bytes',None][kind]
                value = [18500,45,24,80,True,150000000,0][kind]
                if field: data[field]=value
                threat = analyze(admin,data)
                stamp=timezone.now()-timedelta(days=(35-i)//6,hours=i%4,minutes=i*3)
                Threat.objects.filter(pk=threat.pk).update(created_at=stamp)
                Alert.objects.filter(threat=threat).update(created_at=stamp)
                AuditEvent.objects.filter(threat=threat).update(created_at=stamp)
                for inc in threat.incidents.all():
                    Incident.objects.filter(pk=inc.pk).update(created_at=stamp,updated_at=stamp)
                    Alert.objects.filter(incident=inc).update(created_at=stamp)
                    AuditEvent.objects.filter(incident=inc).update(created_at=stamp)
                if i%3==0 and kind!=6:
                    Threat.objects.filter(pk=threat.pk).update(status='Contained',response_status='Simulated / Demo Response: Contain')
                    for inc in threat.incidents.all(): Incident.objects.filter(pk=inc.pk).update(status='Contained')
                    AuditEvent.objects.create(owner=admin,actor=admin,threat=threat,action='Seeded containment — simulated response',simulated=True)
        self.stdout.write(self.style.SUCCESS('Demo accounts ready: admin / analyst. Password is DEMO_PASSWORD or the documented local default.'))
