"""
Unit tests for IAM Manager
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from iam_manager import IAMManager

class TestIAMManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('boto3.Session'):
            self.iam_manager = IAMManager(dry_run=True)
    
    @patch('boto3.Session')
    def test_create_user_dry_run(self, mock_session):
        """Test user creation in dry run mode"""
        iam_manager = IAMManager(dry_run=True)
        result = iam_manager.create_user('test-user')
        
        self.assertEqual(result['status'], 'dry_run')
        self.assertEqual(result['username'], 'test-user')
    
    @patch('boto3.Session')
    def test_create_role_dry_run(self, mock_session):
        """Test role creation in dry run mode"""
        iam_manager = IAMManager(dry_run=True)
        
        # Mock file reading
        with patch('builtins.open', unittest.mock.mock_open(read_data='{"Version": "2012-10-17"}')):
            result = iam_manager.create_role('test-role', 'trust_policy.json')
        
        self.assertEqual(result['status'], 'dry_run')
        self.assertEqual(result['role_name'], 'test-role')
    
    def test_initialization(self):
        """Test IAM Manager initialization"""
        self.assertEqual(self.iam_manager.region, 'us-east-1')
        self.assertEqual(self.iam_manager.profile, 'default')
        self.assertTrue(self.iam_manager.dry_run)

if __name__ == '__main__':
    unittest.main()