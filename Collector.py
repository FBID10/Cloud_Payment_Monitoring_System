import boto3
from botocore.exceptions import BotoCoreError, ClientError


class ResourceCollector:
    def __init__(self, region_name=None, profile_name=None):
        session_args = {}
        if profile_name:
            session_args["profile_name"] = profile_name
        self._session = boto3.Session(**session_args)
        self._region_name = region_name

    def _ec2_client(self):
        return self._session.client("ec2", region_name=self._region_name)

    def get_all_instances(self):
        """Return all EC2 instances, whether tagged or not."""
        instances = []
        try:
            paginator = self._ec2_client().get_paginator("describe_instances")
            for page in paginator.paginate():
                for reservation in page.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        if "Tags" not in instance:
                            instance["Tags"] = []
                        instances.append(instance)
        except (ClientError, BotoCoreError) as exc:
            raise RuntimeError("Failed to collect EC2 instances") from exc

        return instances
