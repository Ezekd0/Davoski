from django.db import models
from django.conf import settings
class Threat(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    source_ip = models.GenericIPAddressField()
    destination_ip = models.GenericIPAddressField()
    threat_type = models.CharField(max_length=40)
    severity = models.CharField(max_length=12)
    confidence = models.FloatField()
    status = models.CharField(max_length=20, default='Detected')
    features = models.JSONField(default=dict)
    explanation = models.JSONField(default=dict)
    recommended_action = models.CharField(max_length=200)
    response_status = models.CharField(max_length=100, default='No response')
    engine = models.CharField(max_length=60, default='Deterministic demo classifier')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
class Incident(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_incidents')
    title = models.CharField(max_length=160)
    severity = models.CharField(max_length=12)
    status = models.CharField(max_length=20, default='Open')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_incidents')
    threats = models.ManyToManyField(Threat, related_name='incidents')
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
class Alert(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=250)
    severity = models.CharField(max_length=12)
    status = models.CharField(max_length=20, default='Unread')
    threat = models.ForeignKey(Threat, null=True, blank=True, on_delete=models.CASCADE)
    incident = models.ForeignKey(Incident, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
class AuditEvent(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='audit_actions')
    action = models.CharField(max_length=200)
    threat = models.ForeignKey(Threat, null=True, on_delete=models.SET_NULL)
    incident = models.ForeignKey(Incident, null=True, on_delete=models.SET_NULL)
    simulated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
class AnalystSettings(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    polling_seconds = models.PositiveIntegerField(default=30)
    auto_incident = models.BooleanField(default=True)
