import unittest

from flask import Flask

from utils.auth import get_client_ip


class GetClientIpTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_direct_request_uses_remote_addr(self):
        self.app.config['TRUSTED_PROXY_COUNT'] = 0
        with self.app.test_request_context('/', environ_overrides={'REMOTE_ADDR': '203.0.113.10'}):
            self.assertEqual(get_client_ip(), '203.0.113.10')

    def test_x_forwarded_for_uses_client_before_trusted_proxy(self):
        self.app.config['TRUSTED_PROXY_COUNT'] = 1
        headers = {'X-Forwarded-For': '198.51.100.20, 10.0.0.5'}
        with self.app.test_request_context(
            '/',
            headers=headers,
            environ_overrides={'REMOTE_ADDR': '10.0.0.5'},
        ):
            self.assertEqual(get_client_ip(), '198.51.100.20')

    def test_x_real_ip_is_used_when_remote_addr_is_local_proxy(self):
        self.app.config['TRUSTED_PROXY_COUNT'] = 0
        headers = {'X-Real-IP': '198.51.100.30'}
        with self.app.test_request_context(
            '/',
            headers=headers,
            environ_overrides={'REMOTE_ADDR': '127.0.0.1'},
        ):
            self.assertEqual(get_client_ip(), '198.51.100.30')

    def test_invalid_forwarded_ip_falls_back_to_remote_addr(self):
        self.app.config['TRUSTED_PROXY_COUNT'] = 1
        headers = {'X-Forwarded-For': 'not-an-ip'}
        with self.app.test_request_context(
            '/',
            headers=headers,
            environ_overrides={'REMOTE_ADDR': '203.0.113.40'},
        ):
            self.assertEqual(get_client_ip(), '203.0.113.40')


if __name__ == '__main__':
    unittest.main()
