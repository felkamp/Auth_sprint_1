import unittest
import requests

from tests.functional.test_cases.base import BaseUnitTest
from tests.functional.test_data import data
from tests.functional.utils.utils import api_url_wth_path as _u
from flask_jwt_extended import create_access_token
from http import HTTPStatus


class TestAuth(BaseUnitTest, unittest.TestCase):
    def setUp(self):
        super(TestAuth, self).setUp()

    def test_register_success(self):
        res = requests.post(url=_u('/register'), data={'email': 'jo@ya.ru', 'password': '123'})
        self.assertTrue(HTTPStatus.OK == res.status_code)

    def test_register_failed(self):
        res = requests.post(url=_u('/register'), data=data.users[0])
        self.assertTrue(HTTPStatus.BAD_REQUEST == res.status_code)

    def test_login_success(self):
        res = requests.post(url=_u('/login'), data=data.users[0])
        resp_data = res.json()

        self.assertIn('access', resp_data)
        self.assertIn('refresh', resp_data)
        self.assertTrue(HTTPStatus.OK == res.status_code)

    def test_login_failed(self):
        res = requests.post(url=_u('/login'), data={'email': 'sub@ya.ru', 'password': '2'})
        self.assertTrue(HTTPStatus.FORBIDDEN == res.status_code)

    def test_logout_success(self):
        access_token = create_access_token(identity=data.users[0]['id'])
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.post(url=_u('/logout'), headers=headers)

        self.assertTrue(HTTPStatus.OK == res.status_code)

    def test_logout_failed(self):
        res = requests.post(url=_u('/logout'))
        self.assertTrue(HTTPStatus.UNAUTHORIZED == res.status_code)
