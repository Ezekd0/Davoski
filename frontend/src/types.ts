export interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    role: 'ADMIN' | 'SECURITY ANALYST';
}
export interface Flow {
    source_ip: string;
    destination_ip: string;
    destination_port: number;
    protocol: 'TCP' | 'UDP' | 'ICMP';
    flow_duration: number;
    packets_per_second: number;
    packet_length_mean: number;
    failed_logins: number;
    unique_ports: number;
    outbound_bytes: number;
    periodic_connections: number;
    payload_anomaly: boolean;
}
export type Severity = 'Critical' | 'High' | 'Medium' | 'Low';
export interface Threat {
    id: number;
    source_ip: string;
    destination_ip: string;
    threat_type: string;
    severity: Severity;
    confidence: number;
    status: string;
    features: Flow;
    explanation: {
        method: string;
        summary: string;
        features: {
            name: string;
            value: number | boolean;
            contribution: number;
        }[];
        confidence_note: string;
    };
    recommended_action: string;
    response_status: string;
    engine: string;
    created_at: string;
    incident_ids: number[];
}
export interface Incident {
    id: number;
    title: string;
    severity: Severity;
    status: string;
    assigned_to: number | null;
    assigned_analyst: string;
    threat_ids: number[];
    resolution: string;
    created_at: string;
    updated_at: string;
}
export interface Alert {
    id: number;
    message: string;
    severity: Severity;
    status: string;
    threat: number | null;
    incident: number | null;
    created_at: string;
}
export interface AuditEvent {
    id: number;
    action: string;
    actor_name: string;
    threat: number | null;
    incident: number | null;
    simulated: boolean;
    created_at: string;
}
export interface Settings {
    polling_seconds: number;
    auto_incident: boolean;
}
export interface DashboardData {
    total_threats: number;
    total_analyses: number;
    critical_threats: number;
    active_incidents: number;
    unresolved_alerts: number;
    average_confidence: number;
    detection_accuracy: null;
    mode: string;
    categories: {
        threat_type: string;
        count: number;
    }[];
    severities: {
        severity: string;
        count: number;
    }[];
    statuses: {
        status: string;
        count: number;
    }[];
    timeline: {
        date: string;
        count: number;
    }[];
    recent_threats: Threat[];
    recent_alerts: Alert[];
}
