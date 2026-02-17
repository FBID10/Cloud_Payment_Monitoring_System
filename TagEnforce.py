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

  