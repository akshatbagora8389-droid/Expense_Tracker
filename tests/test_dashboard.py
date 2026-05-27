import pytest

def test_dashboard_summary_unauthorized(client):
    response = client.get('/api/dashboard/summary')
    assert response.status_code == 401

def test_dashboard_summary_success(client, mock_db):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'

    # Mock responses for different queries that run in dashboard_summary
    # 1. Total income
    mock_db.responses['select coalesce(sum(amount), 0) from income'] = {
        'rows': [(75000.0,)],
        'description': [('total',)]
    }
    # 2. Total expenses
    mock_db.responses['select coalesce(sum(amount), 0) from expenses'] = {
        'rows': [(25000.0,)],
        'description': [('total',)]
    }
    # 3. Income by source
    mock_db.responses['group by source'] = {
        'rows': [('Salary', 60000.0), ('Freelance', 15000.0)],
        'description': [('source',), ('total',)]
    }
    # 4. Expenses over time
    mock_db.responses['group by month'] = {
        'rows': [('2026-04', 10000.0), ('2026-05', 15000.0)],
        'description': [('month',), ('total',)]
    }
    # 5. Recent transactions (UNION query)
    mock_db.responses['union all'] = {
        'rows': [
            ('income', 'Freelance', 15000.0, '2026-05-15'),
            ('expense', 'Food', 200.0, '2026-05-14')
        ],
        'description': [('type',), ('label',), ('amount',), ('date',)]
    }

    response = client.get('/api/dashboard/summary')
    assert response.status_code == 200
    data = response.get_json()

    assert data['total_income'] == 75000.0
    assert data['total_expenses'] == 25000.0
    assert data['balance'] == 50000.0
    
    assert len(data['income_by_source']) == 2
    assert data['income_by_source'][0]['source'] == 'Salary'
    assert data['income_by_source'][0]['total'] == 60000.0

    assert len(data['expenses_over_time']) == 2
    assert data['expenses_over_time'][0]['month'] == '2026-04'
    assert data['expenses_over_time'][0]['total'] == 10000.0

    assert len(data['recent_transactions']) == 2
    assert data['recent_transactions'][0]['type'] == 'income'
    assert data['recent_transactions'][0]['label'] == 'Freelance'
    assert data['recent_transactions'][1]['type'] == 'expense'
    assert data['recent_transactions'][1]['label'] == 'Food'
