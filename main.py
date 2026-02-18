from Collector import ResourceCollector
from TagEnforce import TagEnforcer


if __name__ == "__main__":
    # 1. Collect the data
    collector = ResourceCollector(region_name="us-east-1")
    all_instances = collector.get_all_instances()

    # 2. Define our rules
    my_rules = ["Owner", "CostCenter", "Project"]
    enforcer = TagEnforcer(required_tags=my_rules)

    # 3. Find the violators
    flagged_resources = enforcer.find_violators(all_instances)

    # 4. Report the findings
    print(f"Total Instances Scanned: {len(all_instances)}")
    print(f"Total Violators Found: {len(flagged_resources)}")
    
    for v in flagged_resources:
        print(f" Instance {v['InstanceId']} is missing: {v['MissingTags']}")
    