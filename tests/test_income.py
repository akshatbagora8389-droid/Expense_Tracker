import pytest

def test_get_income_unauthorized(client):
    response = client.get('/api/income')
    assert response.status_code == 401

def test_get_income_success(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
        
    # Mock return rows
    mock_db.responses['select id, source, amount, date'] = {
        'rows': [
            (101, 'Salary', 50000.0, '2026-05-01', 'Monthly Salary', '2026-05-01 10:00:00'),
            (102, 'Freelance', 15000.0, '2026-05-15', 'Web Design', '2026-05-15 12:00:00')
        ],
        'description': [('id',), ('source',), ('amount',), ('date',), ('description',), ('created_at',)]
    }
    
    response = client.get('/api/income')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['source'] == 'Salary'
    assert data[0]['amount'] == 50000.0
    assert data[1]['source'] == 'Freelance'

def test_add_income_success(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
        
    mock_db.responses['insert into income'] = {
        'lastrowid': 103
    }
    
    payload = {
        'source': 'Dividends',
        'amount': 2500.50,
        'date': '2026-05-25',
        'description': 'Quarterly stock payout'
    }
    response = client.post('/api/income', json=payload)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == 'Income added'
    assert json_data['id'] == 103

def test_add_income_missing_fields(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Missing source
    payload = {
        'amount': 100,
        'date': '2026-05-25'
    }
    response = client.post('/api/income', json=payload)
    assert response.status_code == 400
    assert 'required' in response.get_json()['error']

def test_add_income_invalid_amount(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        
    # Zero amount
    payload = {
        'source': 'Gift',
        'amount': 0,
        'date': '2026-05-25'
    }
    response = client.post('/api/income', json=payload)
    assert response.status_code == 400
    assert 'positive number' in response.get_json()['error']
    
    # Negative amount
    payload['amount'] = -50
    response = client.post('/api/income', json=payload)
    assert response.status_code == 400
    assert 'positive number' in response.get_json()['error']

    # Non-numeric amount
    payload['amount'] = 'abc'
    response = client.post('/api/income', json=payload)
    assert response.status_code == 400
    assert 'valid number' in response.get_json()['error']

def test_delete_income_success(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        
    # Setup rowcount indicating 1 row deleted
    mock_db.responses['delete from income'] = {
        'rowcount': 1
    }
    
    response = client.delete('/api/income/101')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Deleted'

def test_delete_income_not_found(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        
    # Setup rowcount indicating 0 rows deleted
    mock_db.responses['delete from income'] = {
        'rowcount': 0
    }
    
    response = client.delete('/api/income/999')
    assert response.status_code == 404
    assert 'Not found' in response.get_json()['error']
