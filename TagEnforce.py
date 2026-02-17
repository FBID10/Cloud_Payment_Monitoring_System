class TagEnforcer:
    def __init__(self, required_tags):
        # We store the list of tags we want to enforce, e.g., ["Owner", "CostCenter"]
        self.required_tags = required_tags

    def _get_readable_tags(self, raw_tags):
        """Converts [{'Key': 'K', 'Value': 'V'}] to {'K': 'V'}"""
        tag_dict = {}
        for tag in raw_tags:
            tag_dict[tag['Key']] = tag['Value']
        return tag_dict

    def find_violators(self, instances):
        """Identifies which instances are missing required tags."""
        violators = []

        for instance in instances:
            instance_id = instance['InstanceId']
            # Convert the AWS tag list into a searchable dictionary
            readable_tags = self._get_readable_tags(instance.get('Tags', []))
            
            missing = []
            for tag in self.required_tags:
                if tag not in readable_tags:
                    missing.append(tag)
            
            # If we found missing tags, record this instance as a violator
            if missing:
                violators.append({
                    "InstanceId": instance_id,
                    "MissingTags": missing,
                    "LaunchTime": instance['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return violators