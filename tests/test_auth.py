import pytest
import bcrypt
import mysql.connector

def test_register_success(client, mock_db):
    # Setup database response
    # For SELECT check (email/username unique check doesn't run in get_db unless there's a custom query in register,
    # register only does INSERT. If database integrity error is raised, it throws IntegrityError)
    
    # We do a mock register request
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    }
    
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['username'] == 'newuser'
    assert json_data['message'] == 'Registered successfully'

def test_register_missing_fields(client):
    data = {
        'username': 'newuser',
        'email': ''
    }
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 400
    assert 'All fields are required' in response.get_json()['error']

def test_register_invalid_email(client):
    data = {
        'username': 'newuser',
        'email': 'invalid-email',
        'password': 'password123'
    }
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 400
    assert 'Invalid email address format' in response.get_json()['error']

def test_register_short_password(client):
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': '123'
    }
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 400
    assert 'Password must be at least 6 characters long' in response.get_json()['error']

def test_register_duplicate(client, mock_db):
    # Mock mysql.connector.IntegrityError when executing insert
    def mock_execute_raise(*args, **kwargs):
        raise mysql.connector.IntegrityError("Duplicate entry")
        
    # We can temporarily patch execute on mock_db cursor
    original_cursor = mock_db.cursor
    def cursor_with_error():
        cur = original_cursor()
        cur.execute = mock_execute_raise
        return cur
        
    mock_db.cursor = cursor_with_error
    
    data = {
        'username': 'existing',
        'email': 'existing@example.com',
        'password': 'password123'
    }
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 409
    assert 'Username or email already exists' in response.get_json()['error']

def test_login_success(client, mock_db):
    # Setup mock user in db
    pwd_hash = bcrypt.hashpw(b'secretpwd', bcrypt.gensalt()).decode()
    mock_db.responses['select id, username, password_hash'] = {
        'rows': [(10, 'myuser', pwd_hash)],
        'description': [('id',), ('username',), ('password_hash',)]
    }
    
    data = {
        'email': 'myuser@example.com',
        'password': 'secretpwd'
    }
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['username'] == 'myuser'
    assert json_data['message'] == 'Login successful'

def test_login_missing_fields(client):
    data = {'email': 'test@example.com'}
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 400

def test_login_user_not_found(client, mock_db):
    # DB returns no row
    mock_db.responses['select id, username, password_hash'] = {
        'rows': [],
        'description': [('id',), ('username',), ('password_hash',)]
    }
    data = {
        'email': 'notfound@example.com',
        'password': 'somepassword'
    }
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 401
    assert 'Invalid credentials' in response.get_json()['error']

def test_login_incorrect_password(client, mock_db):
    # DB returns correct user but wrong hash
    pwd_hash = bcrypt.hashpw(b'correctpassword', bcrypt.gensalt()).decode()
    mock_db.responses['select id, username, password_hash'] = {
        'rows': [(10, 'myuser', pwd_hash)],
        'description': [('id',), ('username',), ('password_hash',)]
    }
    data = {
        'email': 'myuser@example.com',
        'password': 'wrongpassword'
    }
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 401
    assert 'Invalid credentials' in response.get_json()['error']

def test_logout(client):
    response = client.post('/api/auth/logout')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Logged out'

def test_me_authorized(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 42
        sess['username'] = 'sessionuser'
        
    response = client.get('/api/auth/me')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['logged_in'] is True
    assert json_data['username'] == 'sessionuser'
    assert json_data['user_id'] == 42

def test_me_unauthorized(client):
    response = client.get('/api/auth/me')
    assert response.status_code == 401
    assert response.get_json()['logged_in'] is False
