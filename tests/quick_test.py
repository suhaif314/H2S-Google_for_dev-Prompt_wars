"""Quick API test script for TriageAI."""
import requests
import json

# Test text input
response = requests.post('http://localhost:8000/api/triage', data={
    'text': 'Building collapse at Whitefield, Bangalore. Multiple floors pancaked. Survivors calling for help from rubble. Gas leak detected. Approximately 30 people were inside the building.',
    'location': 'Whitefield, Bangalore'
})

data = response.json()
if data.get('success'):
    report = data['report']
    sev = report['severity']
    print(f"SUCCESS!")
    print(f"Severity: {sev['score']}/5")
    print(f"Justification: {sev['justification'][:100]}")
    print(f"Type: {report['incident_type']}")
    print(f"Summary: {report['summary'][:120]}")
    print(f"Actions: {len(report['immediate_actions'])} immediate actions")
    res = report['resources_needed']
    print(f"Resources: {res['ambulances']} ambulances, {res['fire_trucks']} fire trucks, {res['police_units']} police")
    print(f"Time: {data['processing_time_ms']:.0f}ms")
else:
    print(f"FAILED: {data.get('error')}")
