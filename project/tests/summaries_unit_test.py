import orjson as json
import pytest
from starlette.testclient import TestClient

from app.api import crud

"""
docker-compose exec web pytest -k "unit" -n auto
"""


def get_missing_payload(body_field: str, detail_input: dict | None = None) -> dict:
    return dict(
        input=detail_input or {},
        type='missing',
        loc=['body', body_field],
        msg='Field required',
        url='https://errors.pydantic.dev/2.6/v/missing',
    )


def test_create_summary(test_app_with_db: TestClient, monkeypatch: pytest.MonkeyPatch):
    async def create_mock(payload):
        return 1

    monkeypatch.setattr(crud, 'create', create_mock)

    response = test_app_with_db.post(
        '/summaries/', data=json.dumps({'url': 'https://foo.bar.com'})
    )
    assert response.status_code == 201
    assert response.json() == {'id': 1, 'url': 'https://foo.bar.com/'}


def test_create_summary_invalid_json(test_app_with_db: TestClient):
    response = test_app_with_db.post('/summaries/', data=json.dumps({}))

    assert response.status_code == 422
    assert response.json() == {'detail': [get_missing_payload('url')]}

    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'sdfsd'}))

    assert response.status_code == 422
    assert (
        response.json()['detail'][0]['msg']
        == 'Input should be a valid URL, relative URL without a base'
    )


def test_get_summary(test_app_with_db: TestClient, monkeypatch: pytest.MonkeyPatch):
    test_data = {
        'id': 1,
        'url': 'https://foo.bar/',
        'summary': 'summary',
        'created_at': '2022-01-01T00:00:00',
    }

    async def read_mock(summary_id):
        return test_data

    monkeypatch.setattr(crud, 'read', read_mock)

    response = test_app_with_db.get('/summaries/1')

    assert response.status_code == 200
    assert response.json() == test_data


def test_get_summary_wrong_id(
    test_app_with_db: TestClient, monkeypatch: pytest.MonkeyPatch
):
    async def read_mock(summary_id):
        return None

    monkeypatch.setattr(crud, 'read', read_mock)

    response = test_app_with_db.get('/summaries/666')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Summary not found'

    response = test_app_with_db.get('/summaries/0')

    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'input': '0',
                'ctx': {'gt': 0},
                'loc': ['path', 'summary_id'],
                'msg': 'Input should be greater than 0',
                'type': 'greater_than',
                'url': 'https://errors.pydantic.dev/2.6/v/greater_than',
            }
        ]
    }


def test_get_all_summaries(
    test_app_with_db: TestClient, monkeypatch: pytest.MonkeyPatch
):
    test_data = [
        {
            'id': 1,
            'url': 'https://foo.bar/',
            'summary': 'summary',
            'created_at': '2022-01-01T00:00:00',
        },
        {
            'id': 2,
            'url': 'https://testdriven.io/',
            'summary': 'summary',
            'created_at': '2025-02-17T00:00:00',
        },
    ]

    async def read_all_mock():
        return test_data

    monkeypatch.setattr(crud, 'read_all', read_all_mock)

    response = test_app_with_db.get('/summaries/')

    assert response.status_code == 200
    assert response.json() == test_data


def test_remove_summary(test_app_with_db: TestClient, monkeypatch: pytest.MonkeyPatch):
    async def read_mock(summary_id):
        return {
            'id': 7,
            'url': 'https://foo.bar/',
            'summary': 'summary',
            'created_at': '2022-01-01',
        }

    monkeypatch.setattr(crud, 'read', read_mock)

    delete_test_data = {
        'id': 7,
        'url': 'https://foo.bar/',
    }

    async def delete_mock(summary_id):
        return summary_id

    monkeypatch.setattr(crud, 'delete', delete_mock)

    response = test_app_with_db.delete('/summaries/7')

    assert response.status_code == 200
    assert response.json() == delete_test_data


def test_remove_summary_incorrect_id(
    test_app_with_db: TestClient, monkeypatch: pytest.MonkeyPatch
):
    async def delete_mock(summary_id):
        return None

    monkeypatch.setattr(crud, 'delete', delete_mock)

    response = test_app_with_db.delete('/summaries/666')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Summary not found'


def test_update_summary(test_app_with_db: TestClient, monkeypatch: pytest.MonkeyPatch):
    update_test_data = {
        'id': 7,
        'url': 'https://foo.bar/',
        'summary': 'summary',
        'created_at': '2022-01-01T00:00:00',
    }

    async def update_mock(summary_id, payload):
        return update_test_data

    monkeypatch.setattr(crud, 'update', update_mock)

    response = test_app_with_db.put(
        '/summaries/7',
        data=json.dumps({'url': 'https://test.com', 'summary': 'updated!'}),
    )
    assert response.status_code == 200
    assert response.json() == update_test_data


@pytest.mark.parametrize(
    'summary_id, payload, status_code, detail',
    [
        [
            666,
            {'url': 'https://foo.bar', 'summary': 'updated!'},
            404,
            'Summary not found',
        ],
        [
            0,
            {'url': 'https://foo.bar', 'summary': 'updated!'},
            422,
            [
                {
                    'input': '0',
                    'ctx': {'gt': 0},
                    'type': 'greater_than',
                    'loc': ['path', 'summary_id'],
                    'msg': 'Input should be greater than 0',
                    'url': 'https://errors.pydantic.dev/2.6/v/greater_than',
                }
            ],
        ],
        [
            1,
            {},
            422,
            [
                get_missing_payload('url'),
                get_missing_payload('summary'),
            ],
        ],
        [
            1,
            {'url': 'https://foo.bar'},
            422,
            [
                get_missing_payload('summary', detail_input={'url': 'https://foo.bar'}),
            ],
        ],
    ],
)
def test_update_summary_invalid(
    test_app_with_db: TestClient,
    summary_id: int,
    payload: dict,
    status_code: int,
    detail: str | list | dict,
    monkeypatch: pytest.MonkeyPatch,
):
    async def update_mock(summary_id, payload):
        return None

    monkeypatch.setattr(crud, 'update', update_mock)

    response = test_app_with_db.put(
        f'/summaries/{summary_id}',
        data=json.dumps(payload),
    )
    assert response.status_code == status_code
    assert response.json()['detail'] == detail
