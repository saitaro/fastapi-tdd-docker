import orjson as json
import pytest
from starlette.testclient import TestClient

"""
docker-compose exec web python -m pytest tests/summaries_test.py -vv
"""


def get_missing_payload(body_field: str) -> dict:
    return dict(
        type='value_error.missing',
        loc=['body', body_field],
        msg='field required',
    )


def test_create_summary(test_app_with_db: TestClient):
    response = test_app_with_db.post(
        '/summaries/', data=json.dumps({'url': 'https://foo.bar'})
    )
    assert response.status_code == 201
    assert response.json()['url'] == 'https://foo.bar'


def test_create_summary_invalid_json(test_app_with_db: TestClient):
    response = test_app_with_db.post('/summaries/', data=json.dumps({}))

    assert response.status_code == 422
    assert response.json() == {'detail': [get_missing_payload('url')]}

    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'sdfsd'}))

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'invalid or missing URL scheme'


def test_read_summary(test_app_with_db: TestClient):
    response = test_app_with_db.post(
        '/summaries/', data=json.dumps({'url': 'https://foo.bar'})
    )
    summary_id = response.json()['id']
    response = test_app_with_db.get(f'/summaries/{summary_id}')
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['id'] == summary_id
    assert response_body['url'] == 'https://foo.bar'
    assert response_body['summary']
    assert response_body['created_at']


def test_read_summary_wrong_id(test_app_with_db: TestClient):
    response = test_app_with_db.get('/summaries/666')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Summary not found'

    response = test_app_with_db.get('/summaries/0')

    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'ctx': {'limit_value': 0},
                'loc': ['path', 'summary_id'],
                'msg': 'ensure this value is greater than 0',
                'type': 'value_error.number.not_gt',
            }
        ]
    }


def test_read_all_summaries(test_app_with_db: TestClient):
    response = test_app_with_db.post(
        '/summaries/', data=json.dumps({'url': 'https://foo.bar'})
    )
    summary_id = response.json()['id']
    response = test_app_with_db.get('/summaries/')

    assert response.status_code == 200

    response_list = response.json()

    assert len(tuple(filter(lambda text: text['id'] == summary_id, response_list))) == 1


def test_remove_summary(test_app_with_db: TestClient):
    response = test_app_with_db.post(
        '/summaries/', data=json.dumps({'url': 'https://foo.bar'})
    )
    summary_id = response.json()['id']
    response = test_app_with_db.delete(f'/summaries/{summary_id}')

    assert response.status_code == 200
    assert response.json() == {'id': summary_id, 'url': 'https://foo.bar'}


def test_remove_summary_incorrect_id(test_app_with_db: TestClient):
    response = test_app_with_db.delete('/summaries/666')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Summary not found'


def test_update_summary(test_app_with_db: TestClient):
    response = test_app_with_db.post(
        '/summaries/', data=json.dumps({'url': 'https://foo.bar'})
    )
    summary_id = response.json()['id']

    response = test_app_with_db.put(
        f'/summaries/{summary_id}',
        data=json.dumps({'url': 'https://foo.bar', 'summary': 'updated!'}),
    )
    assert response.status_code == 200
    assert response.json()['id'] == summary_id
    assert response.json()['url'] == 'https://foo.bar'
    assert response.json()['summary'] == 'updated!'
    assert response.json()['created_at']


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
                    'type': 'value_error.number.not_gt',
                    'loc': ['path', 'summary_id'],
                    'msg': 'ensure this value is greater than 0',
                    'ctx': {'limit_value': 0},
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
                get_missing_payload('summary'),
            ],
        ],
    ],
)
def test_update_summary_invalid(
    test_app_with_db, summary_id, payload, status_code, detail
):
    response = test_app_with_db.put(
        f'/summaries/{summary_id}',
        data=json.dumps(payload),
    )
    assert response.status_code == status_code
    assert response.json()['detail'] == detail
