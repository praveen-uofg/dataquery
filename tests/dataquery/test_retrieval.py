from tests.conftest import User
from dataquery.core.retrieval import retrieve_data


def test_retrieve_by_id(session, populate_user_table):
    test_user_id = 1
    test_user = session.query(User).filter_by(id=test_user_id).one()

    # test retrieve by id
    retrieved_data = retrieve_data(session, 'users', {'id': test_user_id})
    assert test_user.id == retrieved_data.iloc[0]['id']


def test_retrieve_by_filter_criteria(session, populate_user_table):
    test_users = session.query(User).filter_by(first_name='Rox').all()
    retrieved_data = retrieve_data(session, 'users', {'first_name': 'Rox'})
    assert len(test_users) == len(retrieved_data)

    # test retrieve many by filter criteria
    test_users = session.query(User).filter_by(gender='Male').all()
    retrieved_data = retrieve_data(session, 'users', {'gender': 'Male'})
    assert len(test_users) == len(retrieved_data)


def test_retrieve_by_nonexistent_filter_criteria(session, populate_user_table):
    # test retrieve by nonexistent id
    test_user_id = 999999
    records = retrieve_data(session, 'users', {'id': test_user_id})
    assert len(records) == 0

    # test retrieve by other filter nonexistent criteria
    records = retrieve_data(session, 'users', {'foo': 'bar'})
    assert len(records) == 0
