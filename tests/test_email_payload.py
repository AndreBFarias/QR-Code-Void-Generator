import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.payloads import SocialPayload

class TestEmailPayload(unittest.TestCase):

    def test_email_payload_format(self):
        email = 'test@example.com'
        expected = 'MATMSG:TO:test@example.com;;'
        result = SocialPayload.email(email)
        self.assertEqual(result, expected)

    def test_email_payload_with_mailto_prefix(self):
        email = 'mailto:test@example.com'
        expected = 'MATMSG:TO:test@example.com;;'
        result = SocialPayload.email(email)
        self.assertEqual(result, expected)

    def test_email_payload_with_spaces(self):
        email = '  test@example.com  '
        expected = 'MATMSG:TO:test@example.com;;'
        result = SocialPayload.email(email)
        self.assertEqual(result, expected)
if __name__ == '__main__':
    unittest.main()