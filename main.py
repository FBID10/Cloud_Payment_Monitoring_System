import csv

from Collector import ResourceCollector
from TagEnforce import TagEnforcer
from StateManager import StateManager


def write_violators_to_csv(violators, file_path="violators.csv"):
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["InstanceId", "MissingTags", "LaunchTime"])
        writer.writeheader()
        for violator in violators:
            writer.writerow(
                {
                    "InstanceId": violator.get("InstanceId", ""),
                    "MissingTags": ",".join(violator.get("MissingTags", [])),
                    "LaunchTime": violator.get("LaunchTime", ""),
                }
            )


if __name__ == "__main__":
    # 1. Collect the data
    collector = ResourceCollector(region_name="us-east-1")
    all_instances = collector.get_all_instances()

    # 2. Define our rules
    my_rules = ["Owner", "CostCenter", "Project"]
    enforcer = TagEnforcer(required_tags=my_rules)

    # 3. Find the violators
    flagged_resources = enforcer.find_violators(all_instances)
    write_violators_to_csv(flagged_resources)

    # 4. Initialize State Manager to track flagged instances
    state_manager = StateManager()

    # 5. Report the findings and track in database
    print(f"Total Instances Scanned: {len(all_instances)}")
    print(f"Total Violators Found: {len(flagged_resources)}")
    
    new_violations = 0
    repeat_violations = 0
    
    for v in flagged_resources:
        instance_id = v['InstanceId']
        is_seen_before = state_manager.is_instance_seen_before(instance_id)
        
        # Record the flagged instance in the database
        state_manager.record_flagged_instance(instance_id, v['MissingTags'])
        
        if is_seen_before:
            repeat_violations += 1
            status = "[REPEAT]"
        else:
            new_violations += 1
            status = "[NEW]"
        
        print(f" {status} Instance {instance_id} is missing: {v['MissingTags']}")
    
    print(f"\nSummary:")
    print(f"  New Violations: {new_violations}")
    print(f"  Repeat Violations: {repeat_violations}")
    