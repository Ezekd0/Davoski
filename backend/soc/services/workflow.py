from django.db import transaction
from ..models import Threat, Incident, Alert, AuditEvent, AnalystSettings
from .classifier import classify
SEVERITY_ORDER = {'Low': 0, 'Medium': 1, 'High': 2, 'Critical': 3}
def audit(owner, actor, action, threat=None, incident=None, simulated=False):
    return AuditEvent.objects.create(owner=owner, actor=actor, action=action, threat=threat, incident=incident, simulated=simulated)
@transaction.atomic
def create_incident(user, title, threats):
    severity = max((t.severity for t in threats), key=SEVERITY_ORDER.get)
    incident = Incident.objects.create(owner=user, title=title, severity=severity, assigned_to=user)
    incident.threats.set(threats)
    Alert.objects.create(owner=user, message=f'Incident INC-{incident.id:04d} created: {title}', severity=severity, incident=incident)
    audit(user, user, 'Incident created', incident=incident)
    return incident
@transaction.atomic
def analyze(user, data):
    result = classify(data)
    threat = Threat.objects.create(owner=user, source_ip=data['source_ip'], destination_ip=data['destination_ip'], features=data, status='Safe' if result['threat_type']=='Benign' else 'Detected', **result)
    audit(user, user, f'Demo analysis: {threat.threat_type}', threat=threat, simulated=True)
    if threat.threat_type != 'Benign':
        Alert.objects.create(owner=user, message=f'{threat.severity} {threat.threat_type} detected from {threat.source_ip}', severity=threat.severity, threat=threat)
        prefs, _ = AnalystSettings.objects.get_or_create(owner=user)
        if prefs.auto_incident and threat.severity in ['High', 'Critical']:
            create_incident(user, f'{threat.threat_type} · {threat.source_ip}', [threat])
    return threat
@transaction.atomic
def respond(user, threat, action):
    status = {'Investigate':'Investigating', 'Acknowledge':'Acknowledged', 'Contain':'Contained', 'Block source':'Contained', 'Isolate':'Contained', 'Resolve':'Resolved'}[action]
    threat.status = status
    threat.response_status = f'Simulated / Demo Response: {action}'
    threat.save(update_fields=['status','response_status'])
    audit(threat.owner, user, f'{action} — simulated response', threat=threat, simulated=True)
    Alert.objects.create(owner=threat.owner, message=f'{action} completed for THR-{threat.id:04d} (simulated)', severity='Low', threat=threat)
    return threat
