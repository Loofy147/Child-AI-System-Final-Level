import json

def test_status(client):
    response = client.get('/api/ai/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'active'

def test_get_facts(client):
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
