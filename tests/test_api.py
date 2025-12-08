import json
from child_ai.logic_engine import Predicate, Constant

def test_status(client):
    response = client.get('/api/ai/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'active'

def test_get_facts(client):
    # First, add a fact to ensure the DB is not empty
    client.post('/api/ai/facts', data=json.dumps({'fact': 'Human(Socrates)'}), content_type='application/json')

    response = client.get('/api/ai/facts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Human(Const(Socrates))' in data['facts']

def test_add_fact(client):
    response = client.post('/api/ai/facts', data=json.dumps({'fact': 'Cat(Tom)'}), content_type='application/json')
    assert response.status_code == 201

    response = client.get('/api/ai/facts')
    data = json.loads(response.data)
    assert 'Cat(Const(Tom))' in data['facts']

def test_add_default_rule(client):
    response = client.post('/api/ai/rules/default', data=json.dumps({
        'premise': 'Bird(x)',
        'conclusion': 'Flies(x)'
    }), content_type='application/json')
    assert response.status_code == 201

    # Add a fact to trigger the default rule
    client.post('/api/ai/facts', data=json.dumps({'fact': 'Bird(Tweety)'}), content_type='application/json')

    # Query the conclusion
    response = client.post('/api/ai/query', data=json.dumps({'query': 'Flies(Tweety)'}), content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['result'] == True

def test_temporal_query(client):
    # Add temporal facts
    client.post('/api/ai/facts', data=json.dumps({'fact': 'HappensAt(Login(UserA), 100)'}), content_type='application/json')
    client.post('/api/ai/facts', data=json.dumps({'fact': 'HappensAt(Logout(UserA), 200)'}), content_type='application/json')

    # Query the temporal relationship
    response = client.post('/api/ai/query/temporal', data=json.dumps({
        'operator': 'Before',
        'event1': 'Login(UserA)',
        'event2': 'Logout(UserA)'
    }), content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['result'] == True
