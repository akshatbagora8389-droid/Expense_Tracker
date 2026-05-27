import pytest

def test_get_expenses_unauthorized(client):
    response = client.get('/api/expenses')
    assert response.status_code == 401

def test_get_expenses_success(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
        
    # Mock return rows
    mock_db.responses['select id, category, amount, date'] = {
        'rows': [
            (201, 'Food', 120.50, '2026-05-20', 'Lunch with colleagues', '2026-05-20 13:00:00'),
            (202, 'Transport', 450.0, '2026-05-21', 'Uber ride', '2026-05-21 09:00:00')
        ],
        'description': [('id',), ('category',), ('amount',), ('date',), ('description',), ('created_at',)]
    }
    
    response = client.get('/api/expenses')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['category'] == 'Food'
    assert data[0]['amount'] == 120.50
    assert data[1]['category'] == 'Transport'

def test_add_expense_success(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
        
    mock_db.responses['insert into expenses'] = {
        'lastrowid': 203
    }
    
    payload = {
        'category': 'Rent',
        'amount': 15000.0,
        'date': '2026-05-01',
        'description': 'May rent payment'
    }
    response = client.post('/api/expenses', json=payload)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == 'Expense added'
    assert json_data['id'] == 203

def test_add_expense_missing_fields(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Missing category
    payload = {
        'amount': 500,
        'date': '2026-05-25'
    }
    response = client.post('/api/expenses', json=payload)
    assert response.status_code == 400
    assert 'required' in response.get_json()['error']

def test_add_expense_invalid_amount(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        
    # Zero amount
    payload = {
        'category': 'Shopping',
        'amount': 0,
        'date': '2026-05-25'
    }
    response = client.post('/api/expenses', json=payload)
    assert response.status_code == 400
    assert 'positive number' in response.get_json()['error']
    
    # Negative amount
    payload['amount'] = -20.50
    response = client.post('/api/expenses', json=payload)
    assert response.status_code == 400
    assert 'positive number' in response.get_json()['error']

    # Non-numeric amount
    payload['amount'] = 'invalid'
    response = client.post('/api/expenses', json=payload)
    assert response.status_code == 400
    assert 'valid number' in response.get_json()['error']

def test_delete_expense_success(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        
    mock_db.responses['delete from expenses'] = {
        'rowcount': 1
    }
    
    response = client.delete('/api/expenses/201')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Deleted'

def test_delete_expense_not_found(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        
    mock_db.responses['delete from expenses'] = {
        'rowcount': 0
    }
    
    response = client.delete('/api/expenses/999')
    assert response.status_code == 404
    assert 'Not found' in response.get_json()['error']
