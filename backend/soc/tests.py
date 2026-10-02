from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken
from .models import Threat, Incident, Alert, AuditEvent
from .services.classifier import classify

FLOW = dict(source_ip='192.0.2.42',destination_ip='10.0.0.12',destination_port=443,protocol='UDP',flow_duration=1250,packets_per_second=18500,packet_length_mean=64,failed_logins=0,unique_ports=1,outbound_bytes=15000,periodic_connections=3,payload_anomaly=False)

class HealthRenderingTests(APITestCase):
    def test_health_supports_json_and_browser_requests(self):
        for accept, content_type in [('application/json', 'application/json'), ('text/html', 'text/html')]:
            with self.subTest(accept=accept):
                response = self.client.get('/api/health/', HTTP_ACCEPT=accept)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response['Content-Type'].startswith(content_type))
                self.assertEqual(response.data['status'], 'healthy')
                self.assertEqual(response.data['database'], 'connected')

@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework_simplejwt.authentication.JWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticated'],
    'EXCEPTION_HANDLER':'soc.exceptions.api_exception_handler'})
class WorkflowTests(APITestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('tester',password='DemoSecure!2026')
        self.other=get_user_model().objects.create_user('other',password='DemoSecure!2026')
        self.admin=get_user_model().objects.create_user('root',password='DemoSecure!2026',is_staff=True)
        self.client.force_authenticate(self.user)
    def analyze(self, flow=None):
        response=self.client.post('/api/threats/analyze/',flow or FLOW,format='json')
        self.assertEqual(response.status_code,201,response.data)
        return response.data
    def test_complete_demo_workflow(self):
        result=self.analyze()
        self.assertEqual(result['threat_type'],'DDoS')
        self.assertEqual(result['severity'],'Critical')
        self.assertIn('not SHAP/LIME',result['explanation']['method'])
        self.assertEqual(Incident.objects.count(),1)
        self.assertEqual(Alert.objects.count(),2)
        response=self.client.post(f"/api/threats/{result['id']}/respond/",{'action':'Block source'},format='json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['status'],'Contained')
        self.assertIn('Simulated',response.data['response_status'])
        self.assertTrue(AuditEvent.objects.filter(threat_id=result['id'],simulated=True,action__contains='Block source').exists())
        incident=Incident.objects.first()
        response=self.client.patch(f'/api/incidents/{incident.id}/',{'status':'Resolved','resolution':'Demo source contained and reviewed.'},format='json')
        self.assertEqual(response.status_code,200)
        response=self.client.get('/api/analytics/dashboard/')
        self.assertEqual(response.data['active_incidents'],0)
        self.assertEqual(response.data['detection_accuracy'],None)
        self.assertEqual(response.data['total_threats'],1)
    def test_invalid_and_empty_input(self):
        for data in [{},{**FLOW,'source_ip':'not-an-ip'},{**FLOW,'packets_per_second':-1},{**FLOW,'destination_port':65536},{**FLOW,'unique_ports':0},{**FLOW,'protocol':'invalid'}]:
            response=self.client.post('/api/threats/analyze/',data,format='json')
            self.assertEqual(response.status_code,400)
            self.assertIn('error',response.data)
        self.assertEqual(Threat.objects.count(),0)
    def test_all_categories_deterministic(self):
        baseline={**FLOW,'packets_per_second':120}
        scenarios={'Benign':{},'DDoS':{'packets_per_second':18500},'PortScan':{'unique_ports':45},'Brute Force':{'failed_logins':24},'Botnet':{'periodic_connections':80},'Web Attack':{'payload_anomaly':True},'Infiltration':{'outbound_bytes':150000000}}
        for kind, change in scenarios.items():
            data={**baseline,**change}
            self.assertEqual(classify(data),classify(data))
            self.assertEqual(classify(data)['threat_type'],kind)
    def test_benign_does_not_create_alert_or_incident(self):
        result=self.analyze({**FLOW,'packets_per_second':120})
        self.assertEqual(result['status'],'Safe')
        self.assertEqual(Alert.objects.count(),0)
        self.assertEqual(Incident.objects.count(),0)
    def test_analyst_record_isolation(self):
        result=self.analyze()
        inc=Incident.objects.first();alert=Alert.objects.first()
        self.client.force_authenticate(self.other)
        for path in ['/api/threats/','/api/incidents/','/api/alerts/','/api/audit/']:
            self.assertEqual(self.client.get(path).data,[])
        for path in [f"/api/threats/{result['id']}/",f'/api/incidents/{inc.id}/',f'/api/alerts/{alert.id}/']:
            self.assertEqual(self.client.get(path).status_code,404)
        self.assertEqual(self.client.post(f"/api/threats/{result['id']}/respond/",{'action':'Contain'},format='json').status_code,404)
        self.assertEqual(self.client.post('/api/incidents/',{'title':'Unauthorized','threat_ids':[result['id']]},format='json').status_code,400)
        self.assertEqual(self.client.get('/api/analytics/dashboard/').data['total_analyses'],0)
    def test_admin_access_and_authorization(self):
        self.analyze()
        self.assertEqual(self.client.get('/api/users/').status_code,403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(len(self.client.get('/api/threats/').data),1)
        self.assertEqual(self.client.get('/api/users/').status_code,200)
    def test_settings_and_manual_incident_grouping(self):
        response=self.client.patch('/api/settings/',{'auto_incident':False,'polling_seconds':15},format='json')
        self.assertEqual(response.status_code,200)
        a=self.analyze();b=self.analyze({**FLOW,'packets_per_second':120,'unique_ports':45})
        self.assertEqual(Incident.objects.count(),0)
        response=self.client.post('/api/incidents/',{'title':'Related traffic','threat_ids':[a['id'],b['id']]},format='json')
        self.assertEqual(response.status_code,201,response.data)
        self.assertEqual(set(response.data['threat_ids']),{a['id'],b['id']})
        self.assertEqual(response.data['severity'],'Critical')
        self.assertEqual(self.client.patch('/api/settings/',{'polling_seconds':1},format='json').status_code,400)
    def test_resolution_requires_notes_and_assignment_authorization(self):
        self.analyze();inc=Incident.objects.first()
        self.assertEqual(self.client.patch(f'/api/incidents/{inc.id}/',{'status':'Resolved'},format='json').status_code,400)
        self.assertEqual(self.client.patch(f'/api/incidents/{inc.id}/',{'assigned_to':self.other.id},format='json').status_code,400)
        self.assertEqual(self.client.patch(f'/api/incidents/{inc.id}/',{'assigned_to':self.user.id},format='json').status_code,200)
    def test_acknowledgement_persisted_and_audited(self):
        self.analyze();alert=Alert.objects.first()
        response=self.client.post(f'/api/alerts/{alert.id}/acknowledge/',{},format='json')
        self.assertEqual(response.status_code,200)
        alert.refresh_from_db();self.assertEqual(alert.status,'Acknowledged')
        self.assertTrue(AuditEvent.objects.filter(action__contains='acknowledged').exists())
    def test_bad_response_action(self):
        result=self.analyze()
        self.assertEqual(self.client.post(f"/api/threats/{result['id']}/respond/",{'action':'execute-shell'},format='json').status_code,400)
    def test_filters(self):
        self.analyze();self.analyze({**FLOW,'packets_per_second':120})
        self.assertEqual(len(self.client.get('/api/threats/?severity=Critical&status=Detected&threat_type=DDoS&search=192.0.2').data),1)
    def test_health_and_protected_endpoints(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/health/').data['status'],'healthy')
        for path in ['/api/threats/','/api/incidents/','/api/alerts/','/api/analytics/dashboard/','/api/settings/','/api/audit/']:
            self.assertEqual(self.client.get(path).status_code,401)
    def test_authentication_refresh_rotation_logout_and_expiry(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post('/api/auth/login/',{'username':'tester','password':'incorrect'},format='json').status_code,401)
        login=self.client.post('/api/auth/login/',{'username':'tester','password':'DemoSecure!2026'},format='json')
        self.assertEqual(login.status_code,200)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+login.data['access'])
        self.assertEqual(self.client.get('/api/auth/profile/').data['username'],'tester')
        expired=AccessToken.for_user(self.user);expired.set_exp(lifetime=timedelta(seconds=-1))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+str(expired))
        self.assertEqual(self.client.get('/api/auth/profile/').status_code,401)
        self.client.credentials()
        refresh=self.client.post('/api/auth/refresh/',{'refresh':login.data['refresh']},format='json')
        self.assertEqual(refresh.status_code,200)
        self.assertNotEqual(login.data['refresh'],refresh.data['refresh'])
        self.assertEqual(self.client.post('/api/auth/refresh/',{'refresh':login.data['refresh']},format='json').status_code,401)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+refresh.data['access'])
        self.assertEqual(self.client.post('/api/auth/logout/',{'refresh':refresh.data['refresh']},format='json').status_code,204)
        self.client.credentials()
        self.assertEqual(self.client.post('/api/auth/refresh/',{'refresh':refresh.data['refresh']},format='json').status_code,401)
    def test_registration_password_hashing_and_no_privilege_escalation(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post('/api/auth/register/',{'username':'new','password':'123'},format='json').status_code,400)
        response=self.client.post('/api/auth/register/',{'username':'new','password':'DistinctSecret!482','email':'new@example.test','is_staff':True},format='json')
        self.assertEqual(response.status_code,201)
        user=get_user_model().objects.get(username='new')
        self.assertFalse(user.is_staff)
        self.assertNotEqual(user.password,'DistinctSecret!482')
        self.assertTrue(user.check_password('DistinctSecret!482'))
        self.assertNotIn('password',response.data)
    def test_cors_permitted_and_unknown_origin(self):
        allowed=self.client.get('/api/health/',HTTP_ORIGIN='http://localhost:5173')
        self.assertEqual(allowed.headers.get('Access-Control-Allow-Origin'),'http://localhost:5173')
        blocked=self.client.get('/api/health/',HTTP_ORIGIN='https://untrusted.example')
        self.assertNotIn('Access-Control-Allow-Origin',blocked.headers)
    def test_malformed_json(self):
        self.assertEqual(self.client.post('/api/threats/analyze/',data='{broken',content_type='application/json').status_code,400)

    def test_health_reports_database_outage_without_error_leakage(self):
        from unittest.mock import patch
        from django.db import OperationalError
        self.client.force_authenticate(None)
        with patch('django.db.connection.cursor', side_effect=OperationalError('private connection detail')):
            response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data['database'], 'unavailable')
        self.assertNotIn('private', str(response.data))
