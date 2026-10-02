"""Replace this service with a validated trained model adapter when artifacts exist.
Scores and feature weights are deterministic demo heuristics, NOT ML probabilities or SHAP/LIME.
"""
def classify(data):
    rate, failed, ports = data['packets_per_second'], data['failed_logins'], data['unique_ports']
    if rate >= 10000:
        kind, severity, score, feature, reason = 'DDoS', 'Critical', 97.4, 'packets_per_second', 'Packet rate exceeds the demo flood threshold of 10,000 packets/s.'
    elif failed >= 10:
        kind, severity, score, feature, reason = 'Brute Force', 'High', 94.2, 'failed_logins', 'Repeated authentication failures exceed the demo threshold of 10.'
    elif ports >= 20:
        kind, severity, score, feature, reason = 'PortScan', 'High', 91.8, 'unique_ports', 'Connections touch at least 20 different destination ports.'
    elif data['payload_anomaly']:
        kind, severity, score, feature, reason = 'Web Attack', 'High', 89.6, 'payload_anomaly', 'The submitted payload anomaly flag is enabled.'
    elif data['outbound_bytes'] >= 100000000:
        kind, severity, score, feature, reason = 'Infiltration', 'High', 88.3, 'outbound_bytes', 'Outbound volume exceeds the demo 100 MB threshold.'
    elif data['periodic_connections'] >= 50:
        kind, severity, score, feature, reason = 'Botnet', 'Medium', 86.5, 'periodic_connections', 'Repeated periodic connections exceed the demo beaconing threshold.'
    else:
        kind, severity, score, feature, reason = 'Benign', 'Low', 95.1, 'packets_per_second', 'No configured demo rule was triggered. This does not establish that traffic is safe.'
    recommendation = 'Continue monitoring' if kind == 'Benign' else 'Investigate traffic, then simulate containment if appropriate'
    return {'threat_type': kind, 'severity': severity, 'confidence': score, 'recommended_action': recommendation,
            'explanation': {'method': 'Demo rule explanation (not SHAP/LIME)', 'summary': reason, 'features': [{'name': feature, 'value': data[feature], 'contribution': 1.0}], 'confidence_note': 'Illustrative demo score; not a calibrated model probability.'}}
