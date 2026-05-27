import pytest
from unittest.mock import patch
import sys
import os

# Ensure the app folder is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app

class MockCursor:
    def __init__(self, db_mock):
        self.db_mock = db_mock
        self.description = None
        self._lastrowid = 1
        self._rowcount = 1

    @property
    def lastrowid(self):
        return self._lastrowid

    @lastrowid.setter
    def lastrowid(self, value):
        self._lastrowid = value

    @property
    def rowcount(self):
        return self._rowcount

    @rowcount.setter
    def rowcount(self, value):
        self._rowcount = value

    def execute(self, query, params=None):
        self.db_mock.queries.append((query, params))
        query_key = query.strip().lower()
        self.db_mock.current_query = query_key
        
        # Check if we have registered mock response for this query substring
        matched = False
        for key, val in self.db_mock.responses.items():
            if key in query_key:
                self._rows = list(val.get('rows', []))
                self.description = val.get('description', [])
                if 'rowcount' in val:
                    self.rowcount = val['rowcount']
                else:
                    self.rowcount = len(self._rows) if "select" in query_key else 1
                if 'lastrowid' in val:
                    self.lastrowid = val['lastrowid']
                matched = True
                break
                
        if not matched:
            self._rows = []
            self.description = []
            self.rowcount = 0 if "select" in query_key else 1

    def fetchone(self):
        if hasattr(self, '_rows') and self._rows:
            return self._rows.pop(0)
        return None

    def fetchall(self):
        if hasattr(self, '_rows'):
            rows = self._rows
            self._rows = []
            return rows
        return []

    def close(self):
        pass

class MockDB:
    def __init__(self):
        self.queries = []
        self.responses = {}
        self.current_query = None

    def cursor(self):
        return MockCursor(self)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret'
    flask_app.config['SESSION_COOKIE_SECURE'] = False
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db():
    db = MockDB()
    with patch('app.get_db', return_value=db):
        # Also mock initial pool to avoid connection pool instantiation errors
        with patch('app.init_pool', return_value=None):
            yield db
