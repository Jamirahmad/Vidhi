from fastapi.testclient import TestClient

from src.api.main import app


def test_api_launch_and_core_routes():
    client = TestClient(app)

    assert client.get('/health/live').status_code == 200
    assert client.get('/health/ready').status_code == 200

    research_payload = {
        'request_id': 'REQ-SMOKE-1',
        'jurisdiction': 'India',
        'case_type': 'civil',
        'case_context': 'Breach of contract dispute',
        'constraints': {},
    }
    assert client.post('/research/run', json=research_payload).status_code == 200

    doc_payload = {
        'request_id': 'REQ-SMOKE-2',
        'jurisdiction': 'India',
        'case_type': 'civil',
        'document_type': 'Legal Notice',
        'facts': 'Payment default by opposite party.',
        'constraints': {},
    }
    assert client.post('/documents/generate', json=doc_payload).status_code == 200

    compliance_payload = {
        'request_id': 'REQ-SMOKE-3',
        'jurisdiction': 'India',
        'case_type': 'civil',
        'document_text': 'Draft document text',
        'constraints': {},
    }
    assert client.post('/compliance/check', json=compliance_payload).status_code == 200

    feedback_payload = {
        'request_id': 'REQ-SMOKE-4',
        'rating': 4,
        'comments': 'Looks good',
        'requires_followup': False,
    }
    assert client.post('/feedback/submit', json=feedback_payload).status_code == 201
