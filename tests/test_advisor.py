import pytest
from unittest.mock import patch, MagicMock
import os

def test_chat_unauthorized(client):
    response = client.post('/api/chat', json={'message': 'hello'})
    assert response.status_code == 401

def test_chat_missing_message(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    assert 'required' in response.get_json()['error']

@patch('requests.post')
def test_chat_grok_success(mock_post, client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'

    # Mock environment variables
    with patch.dict(os.environ, {'GROK_API_KEY': 'fake-grok-key', 'GEMINI_API_KEY': ''}):
        # Mock database calls for context
        mock_db.responses['select coalesce(sum(amount), 0) from income'] = {'rows': [(50000.0,)], 'description': [('total',)]}
        mock_db.responses['select coalesce(sum(amount), 0) from expenses'] = {'rows': [(20000.0,)], 'description': [('total',)]}
        mock_db.responses['group by source'] = {'rows': [], 'description': []}
        mock_db.responses['group by category'] = {'rows': [], 'description': []}
        mock_db.responses['union all'] = {'rows': [], 'description': []}

        # Mock requests.post response for Grok API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'This is advice from Grok AI.'
                }
            }]
        }
        mock_post.return_value = mock_response

        response = client.post('/api/chat', json={'message': 'How is my budget?'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'Grok' in data['reply']
        assert data['reply'] == 'This is advice from Grok AI.'

@patch('google.generativeai.GenerativeModel')
def test_chat_gemini_success(mock_gen_model, client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'

    # Mock environment variables
    with patch.dict(os.environ, {'GROK_API_KEY': '', 'GEMINI_API_KEY': 'fake-gemini-key'}):
        # Mock database calls
        mock_db.responses['select coalesce(sum(amount), 0) from income'] = {'rows': [(50000.0,)], 'description': [('total',)]}
        mock_db.responses['select coalesce(sum(amount), 0) from expenses'] = {'rows': [(20000.0,)], 'description': [('total',)]}
        mock_db.responses['group by source'] = {'rows': [], 'description': []}
        mock_db.responses['group by category'] = {'rows': [], 'description': []}
        mock_db.responses['union all'] = {'rows': [], 'description': []}

        # Mock GenerativeModel instance
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'This is advice from Gemini AI.'
        mock_model_instance.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_model_instance

        response = client.post('/api/chat', json={'message': 'Can I afford a trip?'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'Gemini' in data['reply']
        assert data['reply'] == 'This is advice from Gemini AI.'

def test_chat_missing_keys(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'

    with patch.dict(os.environ, {'GROK_API_KEY': '', 'GEMINI_API_KEY': ''}):
        mock_db.responses['select coalesce(sum(amount), 0) from income'] = {'rows': [(0.0,)], 'description': [('total',)]}
        mock_db.responses['select coalesce(sum(amount), 0) from expenses'] = {'rows': [(0.0,)], 'description': [('total',)]}
        mock_db.responses['group by source'] = {'rows': [], 'description': []}
        mock_db.responses['group by category'] = {'rows': [], 'description': []}
        mock_db.responses['union all'] = {'rows': [], 'description': []}

        response = client.post('/api/chat', json={'message': 'Hello'})
        assert response.status_code == 200
        assert 'missing' in response.get_json()['reply'].lower()

@patch('google.generativeai.GenerativeModel')
@patch('requests.post')
def test_chat_fallback_grok_to_gemini(mock_post, mock_gen_model, client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'

    with patch.dict(os.environ, {'GROK_API_KEY': 'fake-grok-key', 'GEMINI_API_KEY': 'fake-gemini-key'}):
        mock_db.responses['select coalesce(sum(amount), 0) from income'] = {'rows': [(0.0,)], 'description': [('total',)]}
        mock_db.responses['select coalesce(sum(amount), 0) from expenses'] = {'rows': [(0.0,)], 'description': [('total',)]}
        mock_db.responses['group by source'] = {'rows': [], 'description': []}
        mock_db.responses['group by category'] = {'rows': [], 'description': []}
        mock_db.responses['union all'] = {'rows': [], 'description': []}

        # Grok fails with error
        mock_post.side_effect = Exception("Grok quota exceeded")

        # Gemini succeeds
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'This is fallback advice from Gemini AI.'
        mock_model_instance.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_model_instance

        response = client.post('/api/chat', json={'message': 'Hello'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'Gemini' in data['reply']
        assert data['reply'] == 'This is fallback advice from Gemini AI.'


@patch('google.generativeai.GenerativeModel')
@patch('requests.post')
def test_chat_circuit_breaker_cooldown(mock_post, mock_gen_model, client, mock_db):
    from app import health_tracker
    
    # Reset health_tracker state
    with health_tracker.lock:
        health_tracker.last_failure = {}
        health_tracker.consecutive_failures = {}

    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'

    with patch.dict(os.environ, {'GROK_API_KEY': 'fake-grok-key', 'GEMINI_API_KEY': 'fake-gemini-key'}):
        mock_db.responses['select coalesce(sum(amount), 0) from income'] = {'rows': [(0.0,)], 'description': [('total',)]}
        mock_db.responses['select coalesce(sum(amount), 0) from expenses'] = {'rows': [(0.0,)], 'description': [('total',)]}
        mock_db.responses['group by source'] = {'rows': [], 'description': []}
        mock_db.responses['group by category'] = {'rows': [], 'description': []}
        mock_db.responses['union all'] = {'rows': [], 'description': []}

        # First request: Grok fails, Gemini succeeds
        mock_post.side_effect = Exception("Grok offline/error")
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'Gemini response after Grok failed'
        mock_model_instance.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_model_instance

        # Make first request
        response1 = client.post('/api/chat', json={'message': 'Hello'})
        assert response1.status_code == 200
        assert response1.get_json()['reply'] == 'Gemini response after Grok failed'
        
        # Verify Grok is marked unhealthy
        assert not health_tracker.is_healthy('grok')

        # Reset mock_post calls to verify it is NOT called again on second request
        mock_post.reset_mock()
        
        # Make second request
        response2 = client.post('/api/chat', json={'message': 'Hello again'})
        assert response2.status_code == 200
        
        # Grok should not have been called at all because it is on cooldown/unhealthy
        mock_post.assert_not_called()
