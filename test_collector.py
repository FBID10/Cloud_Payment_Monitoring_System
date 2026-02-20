import unittest
from unittest.mock import Mock, patch

import Collector


class TestResourceCollector(unittest.TestCase):
    def test_init_uses_profile_name_when_provided(self):
        session = Mock()

        with patch.object(Collector.boto3, "Session", return_value=session) as mocked_session:
            collector = Collector.ResourceCollector(region_name="us-west-2", profile_name="dev-profile")

        mocked_session.assert_called_once_with(profile_name="dev-profile")
        self.assertEqual(collector._region_name, "us-west-2")

    def test_get_all_instances_collects_and_adds_empty_tags(self):
        paginator = Mock()
        paginator.paginate.return_value = [
            {
                "Reservations": [
                    {
                        "Instances": [
                            {"InstanceId": "i-1"},
                            {"InstanceId": "i-2", "Tags": [{"Key": "Name", "Value": "web"}]},
                        ]
                    }
                ]
            }
        ]
        ec2_client = Mock()
        ec2_client.get_paginator.return_value = paginator
        session = Mock()
        session.client.return_value = ec2_client

        with patch.object(Collector.boto3, "Session", return_value=session):
            collector = Collector.ResourceCollector(region_name="us-east-1")
            instances = collector.get_all_instances()

        self.assertEqual(len(instances), 2)
        self.assertEqual(instances[0]["InstanceId"], "i-1")
        self.assertEqual(instances[0]["Tags"], [])
        self.assertEqual(instances[1]["Tags"], [{"Key": "Name", "Value": "web"}])
        session.client.assert_called_once_with("ec2", region_name="us-east-1")
        ec2_client.get_paginator.assert_called_once_with("describe_instances")
        paginator.paginate.assert_called_once_with()

    def test_get_all_instances_returns_empty_list_when_no_instances(self):
        paginator = Mock()
        paginator.paginate.return_value = [{}, {"Reservations": []}]
        ec2_client = Mock()
        ec2_client.get_paginator.return_value = paginator
        session = Mock()
        session.client.return_value = ec2_client

        with patch.object(Collector.boto3, "Session", return_value=session):
            collector = Collector.ResourceCollector(region_name="us-east-2")
            instances = collector.get_all_instances()

        self.assertEqual(instances, [])
        ec2_client.get_paginator.assert_called_once_with("describe_instances")

    def test_get_all_instances_raises_runtime_error_on_client_error(self):
        paginator = Mock()
        paginator.paginate.side_effect = Collector.ClientError(
            {"Error": {"Code": "UnauthorizedOperation", "Message": "Denied"}},
            "DescribeInstances",
        )
        ec2_client = Mock()
        ec2_client.get_paginator.return_value = paginator
        session = Mock()
        session.client.return_value = ec2_client

        with patch.object(Collector.boto3, "Session", return_value=session):
            collector = Collector.ResourceCollector()
            with self.assertRaises(RuntimeError) as ctx:
                collector.get_all_instances()

        self.assertIn("Failed to collect EC2 instances", str(ctx.exception))

    def test_get_all_instances_raises_runtime_error_on_boto_failure(self):
        paginator = Mock()
        paginator.paginate.side_effect = Collector.BotoCoreError()
        ec2_client = Mock()
        ec2_client.get_paginator.return_value = paginator
        session = Mock()
        session.client.return_value = ec2_client

        with patch.object(Collector.boto3, "Session", return_value=session):
            collector = Collector.ResourceCollector()
            with self.assertRaises(RuntimeError) as ctx:
                collector.get_all_instances()

        self.assertIn("Failed to collect EC2 instances", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
