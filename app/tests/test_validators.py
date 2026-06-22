import unittest
from unittest.mock import patch

from validators.checks import validate_domain, validate_email


class TestEmailValidator(unittest.TestCase):

    def test_invalid_email_format(self):
        result = validate_email('not-an-email')
        self.assertFalse(result['is_likely_legit'])
        self.assertEqual(result['score'], 0)
        self.assertFalse(result['checks']['format_valid'])

    def test_disposable_email_is_flagged(self):
        result = validate_email('someone@mailinator.com')
        self.assertFalse(result['is_likely_legit'])
        self.assertTrue(result['checks']['disposable_domain'])
        self.assertIn('throwaway', result['recommendation'].lower())

    def test_free_provider_is_noted(self):
        result = validate_email('recruiter@gmail.com')
        self.assertTrue(result['checks']['free_email_provider'])


class TestDomainValidator(unittest.TestCase):

    def test_invalid_domain_format(self):
        result = validate_domain('notadomain')
        self.assertFalse(result['is_likely_legit'])
        self.assertEqual(result['score'], 0)

    @patch('validators.checks._query_records')
    def test_legitimate_domain_scoring(self, mock_query):
        def side_effect(domain, record_type):
            if record_type == 'MX':
                return ['mx.example.com']
            if record_type == 'A':
                return ['93.184.216.34']
            if record_type == 'TXT' and domain.startswith('_dmarc.'):
                return ['v=DMARC1; p=reject']
            if record_type == 'TXT':
                return ['v=spf1 include:_spf.example.com ~all']
            return []

        mock_query.side_effect = side_effect
        result = validate_domain('example.com')

        self.assertTrue(result['is_likely_legit'])
        self.assertGreaterEqual(result['score'], 80)
        self.assertTrue(result['checks']['mx_records'])
        self.assertTrue(result['checks']['has_spf'])
        self.assertTrue(result['checks']['has_dmarc'])


if __name__ == '__main__':
    unittest.main()
