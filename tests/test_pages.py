import pytest
from unittest.mock import patch
import os

def test_static_pages(client):
    # Test index page
    with patch('app.send_from_directory') as mock_send:
        mock_send.return_value = "index"
        response = client.get('/')
        assert response.status_code == 200
        mock_send.assert_called_with('public', 'index.html')

    # Test dashboard page
    with patch('app.send_from_directory') as mock_send:
        mock_send.return_value = "dashboard"
        response = client.get('/dashboard')
        assert response.status_code == 200
        mock_send.assert_called_with('public', 'dashboard.html')

    # Test income page
    with patch('app.send_from_directory') as mock_send:
        mock_send.return_value = "income"
        response = client.get('/income-page')
        assert response.status_code == 200
        mock_send.assert_called_with('public', 'income.html')

    # Test expenses page
    with patch('app.send_from_directory') as mock_send:
        mock_send.return_value = "expenses"
        response = client.get('/expenses-page')
        assert response.status_code == 200
        mock_send.assert_called_with('public', 'expenses.html')

    # Test advisor page
    with patch('app.send_from_directory') as mock_send:
        mock_send.return_value = "advisor"
        response = client.get('/advisor-page')
        assert response.status_code == 200
        mock_send.assert_called_with('public', 'advisor.html')

def test_diagnose_route_forbidden_in_production(client, app):
    # Set debug to False (simulating production mode)
    old_debug = app.debug
    app.debug = False
    try:
        response = client.get('/api/diagnose', headers={'X-Forwarded-Proto': 'https'})
        assert response.status_code == 403
        assert 'disabled in production' in response.get_json()['message']
    finally:
        app.debug = old_debug

def test_diagnose_route_allowed_in_debug(client, app):
    # Set debug to True (simulating debug mode)
    old_debug = app.debug
    app.debug = True
    try:
        response = client.get('/api/diagnose')
        assert response.status_code == 200
        data = response.get_json()
        assert 'resolved_host' in data
        assert 'password_present' in data
    finally:
        app.debug = old_debug

def test_https_redirection_in_production(client, app):
    # Enable production mode (debug = False)
    old_debug = app.debug
    app.debug = False
    try:
        response = client.get('/', headers={'X-Forwarded-Proto': 'http'})
        assert response.status_code == 301
        assert response.headers['Location'].startswith('https://')
    finally:
        app.debug = old_debug

def test_security_headers_in_debug_and_production(client, app):
    # Verify headers in debug mode
    old_debug = app.debug
    app.debug = True
    try:
        response = client.get('/')
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
        assert 'Strict-Transport-Security' not in response.headers
    finally:
        app.debug = old_debug

    # Verify headers in production mode
    app.debug = False
    try:
        response = client.get('/', headers={'X-Forwarded-Proto': 'https'})
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
        assert 'Strict-Transport-Security' in response.headers
    finally:
        app.debug = old_debug
