"""Tests for email-related functions in app.py."""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

import app


class TestAppEmail(unittest.TestCase):
    """Tests for the email-related functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample findings for testing
        self.sample_findings = [
            {
                "SchemaVersion": "2018-10-08",
                "Id": "arn:aws:securityhub:us-east-1:123456789012:subscription/aws-foundational-security-best-practices/v/1.0.0/IAM.1/finding/12345678-1234-1234-1234-123456789012",
                "Severity": {"Label": "MEDIUM", "Normalized": 40},
                "Title": "IAM root user access key should not exist",
                "Description": "This AWS control checks whether the root user access key is available.",
                "Resources": [
                    {
                        "Type": "AwsAccount",
                        "Id": "AWS::::Account:123456789012",
                        "Partition": "aws",
                        "Region": "us-east-1",
                    }
                ],
            }
        ]

        # Sample stats for testing
        self.sample_stats = {
            "total": 1,
            "critical": 0,
            "high": 0,
            "medium": 1,
            "low": 0,
        }

    @patch("app.boto3.client")
    def test_send_email_missing_email(self, mock_boto3_client):
        """Test sending email with missing email addresses."""
        # Create a mock SES client
        mock_ses = MagicMock()
        mock_boto3_client.return_value = mock_ses

        # Clear environment variables
        if "SENDER_EMAIL" in os.environ:
            del os.environ["SENDER_EMAIL"]

        # Call the function with missing sender
        result = app.send_email(
            "test@example.com",
            self.sample_findings,
            "Sample analysis",
            self.sample_stats,
            MagicMock(),
        )

        # Verify the function returned False
        self.assertFalse(result)

        # Set sender email
        os.environ["SENDER_EMAIL"] = "sender@example.com"

        # Call the function with missing recipient
        result = app.send_email(
            None,
            self.sample_findings,
            "Sample analysis",
            self.sample_stats,
            MagicMock(),
        )

        # Verify the function returned False
        self.assertFalse(result)

    @patch("app.boto3.client")
    @patch("app.load_frameworks")
    def test_send_email_exception(self, mock_load_frameworks, mock_boto3_client):
        """Test sending email with exception."""
        # Create a mock SES client
        mock_ses = MagicMock()
        mock_boto3_client.return_value = mock_ses

        # Configure the mock to raise an exception
        mock_ses.send_raw_email.side_effect = Exception("Test exception")

        # Mock the frameworks configuration
        mock_load_frameworks.return_value = [
            {
                "id": "SOC2",
                "name": "SOC 2",
                "arn": "arn:aws:securityhub:::standards/aws-soc2",
                "description": "SOC 2 Framework",
            }
        ]

        # Create a mock mapper dictionary
        mock_mappers = {"SOC2": MagicMock()}
        mock_mappers["SOC2"].get_control_id_attribute.return_value = "SOC2Controls"

        # Create findings dict for multi-framework format
        findings_dict = {"SOC2": self.sample_findings}

        # Create analyses dict for multi-framework format
        analyses_dict = {
            "SOC2": "Sample analysis for SOC2",
            "combined": "Combined analysis",
        }

        # Stats dict for multi-framework format
        stats_dict = {"SOC2": self.sample_stats}

        # Set environment variables for testing
        os.environ["SENDER_EMAIL"] = "sender@example.com"

        # Call the function
        result = app.send_email(
            "test@example.com",
            findings_dict,
            analyses_dict,
            stats_dict,
            mock_mappers,
        )

        # Verify the function returned False
        self.assertFalse(result)

    @patch("app.boto3.client")
    def test_send_test_email_missing_email(self, mock_boto3_client):
        """Test sending test email with missing email addresses."""
        # Create a mock SES client
        mock_ses = MagicMock()
        mock_boto3_client.return_value = mock_ses

        # Clear environment variables
        if "SENDER_EMAIL" in os.environ:
            del os.environ["SENDER_EMAIL"]

        # Call the function with missing sender
        result = app.send_test_email("test@example.com")

        # Verify the function returned False
        self.assertFalse(result)

        # Set sender email
        os.environ["SENDER_EMAIL"] = "sender@example.com"

        # Call the function with missing recipient
        result = app.send_test_email(None)

        # Verify the function returned False
        self.assertFalse(result)

    @patch("app.boto3.client")
    def test_send_test_email_exception(self, mock_boto3_client):
        """Test sending test email with exception."""
        # Create a mock SES client
        mock_ses = MagicMock()
        mock_boto3_client.return_value = mock_ses

        # Configure the mock to raise an exception
        mock_ses.send_raw_email.side_effect = Exception("Test exception")

        # Set environment variables for testing
        os.environ["SENDER_EMAIL"] = "sender@example.com"

        # Call the function
        result = app.send_test_email("test@example.com")

        # Verify the function returned False
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
