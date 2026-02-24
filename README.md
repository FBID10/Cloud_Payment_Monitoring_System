# Cloud Payment Monitoring System

A Python-based AWS monitoring solution that automatically scans EC2 instances for missing required tags and tracks compliance violations.

## Overview

The Cloud Payment Monitoring System ensures that all EC2 instances in your AWS environment comply with your organization's tagging policies. It identifies instances missing required tags, tracks repeat violations over time, and exports findings to CSV for reporting and analysis.

## Features

- **EC2 Instance Collection**: Automatically discovers all EC2 instances in a specified AWS region
- **Tag Compliance Checking**: Validates instances against a configurable list of required tags
- **Violation Tracking**: Maintains a SQLite database to track which instances have been flagged before
- **CSV Export**: Generates reports of all violations for easy analysis and sharing
- **Repeat Violation Detection**: Distinguishes between new violations and previously flagged instances

## Project Structure

```
Cloud_Payment_Monitoring_System/
├── main.py                 # Main orchestration script
├── Collector.py            # EC2 instance collection module
├── TagEnforce.py           # Tag validation and violation detection
├── StateManager.py         # SQLite database management for tracking
├── test_collector.py       # Unit tests for Collector
├── test_state_manager.py   # Unit tests for StateManager
├── instance_state.db       # SQLite database (auto-created)
└── violators.csv          # CSV report of violations (auto-generated)
```

## Installation

### Prerequisites

- Python 3.7+
- AWS CLI configured with appropriate credentials
- AWS IAM permissions for EC2 read operations

### Setup

1. Clone the repository:
```bash
git clone https://github.com/FBID10/Cloud_Payment_Monitoring_System.git
cd Cloud_Payment_Monitoring_System
```

2. Install dependencies:
```bash
pip install boto3
```

3. Configure AWS credentials:
```bash
aws configure
```

## Usage

### Basic Example

Run the main monitoring script:

```bash
python main.py
```

This will:
1. Collect all EC2 instances from the `us-east-1` region
2. Check for required tags: Owner, CostCenter, and Project
3. Generate a `violators.csv` file with findings
4. Store state in `instance_state.db` for tracking

### Customization

Modify the required tags in `main.py`:

```python
my_rules = ["Owner", "CostCenter", "Project"]
```

Change the AWS region:

```python
collector = ResourceCollector(region_name="us-west-2")
```

Use a specific AWS profile:

```python
collector = ResourceCollector(region_name="us-east-1", profile_name="my-profile")
```

## Modules

### Collector (Collector.py)

Handles AWS EC2 API interactions and instance discovery.

**Key Classes:**
- `ResourceCollector`: Collects EC2 instances from AWS

**Key Methods:**
- `get_all_instances()`: Returns all EC2 instances in the specified region

### TagEnforce (TagEnforce.py)

Validates instances against required tags and identifies violators.

**Key Classes:**
- `TagEnforcer`: Enforces tagging policies

**Key Methods:**
- `find_violators(instances)`: Returns instances missing required tags

### StateManager (StateManager.py)

Maintains a SQLite database to track flagged instances over time.

**Key Classes:**
- `StateManager`: Manages instance state and violation history

**Key Methods:**
- `record_flagged_instance()`: Records a violation in the database
- `is_instance_seen_before()`: Checks if an instance was previously flagged
- `get_instance_by_id()`: Retrieves instance details from the database

## Output

### CSV Report (violators.csv)

| InstanceId | MissingTags | LaunchTime |
|---|---|---|
| i-0123456789abcdef0 | Owner,CostCenter | 2026-02-24 10:30:45 |
| i-abcdef0123456789 | Project | 2026-02-24 11:15:22 |

### Database (instance_state.db)

Tracks instance violation history with timestamps for audit trails.

## Testing

Run unit tests to verify functionality:

```bash
python -m pytest test_collector.py
python -m pytest test_state_manager.py
```

## Advanced Configuration

### Filtering by Instance State

The system automatically discovers all instances regardless of state (running, stopped, terminated). To filter specific states, modify the `Collector.py`:

```python
# Add state filtering in get_all_instances()
if instance['State']['Name'] == 'running':
    instances.append(instance)
```

### Custom Tag Rules

Define your own tagging standards in `main.py`:

```python
# Compliance rules for your organization
my_rules = [
    "Owner",        # Who owns this resource
    "CostCenter",   # Billing cost center
    "Project",      # Project identifier
    "Environment",  # Dev/Test/Prod
    "CreatedBy",    # Who created it
    "CreatedDate"   # When it was created
]
```

### Multi-Region Scanning

Extend the system to scan multiple regions:

```python
regions = ["us-east-1", "us-west-2", "eu-west-1"]

for region in regions:
    collector = ResourceCollector(region_name=region)
    all_instances = collector.get_all_instances()
    # Process instances...
```

### Database Maintenance

Clean up old violation records:

```python
# In StateManager
def cleanup_old_records(self, days=30):
    """Remove inactive records older than specified days"""
    pass
```

## Troubleshooting

### AWS Credential Issues

If you encounter `BotoCoreError: Unable to locate credentials`:

1. Configure AWS credentials:
```bash
aws configure
```

2. Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Permission Denied Errors

Ensure your AWS IAM user has these permissions:
- `ec2:DescribeInstances`
- `ec2:DescribeTags`

### Database Lock Issues

If you encounter "database is locked" errors:
1. Ensure no other processes are accessing `instance_state.db`
2. Restart the application or clear the database:
```bash
rm instance_state.db
```

## Performance Considerations

- **Large deployments**: For 1000+ instances, expect 2-5 minutes runtime
- **Pagination**: The system automatically handles paginated API responses
- **Database**: SQLite is suitable for up to ~10k instance records

## Future Enhancements

- [ ] Automatic tag remediation
- [ ] Email/Slack notifications for new violations
- [ ] Dashboard for violation trends
- [ ] CloudTrail integration for audit trails
- [ ] Automatic tag suggestions based on usage patterns
- [ ] Multi-account AWS Organization support

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues or questions, please open an issue on the GitHub repository.
