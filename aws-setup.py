# pip install boto3 paramiko

import os
import time
from typing import Any, Dict

import boto3
import paramiko

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_REGION = "ap-south-1"
KEY_PAIR_NAME = "meera-key"
SSH_KEY_PATH = "./meera-key.pem"
DB_INSTANCE_NAME = "meera"
DB_NAME = "meera-dev"
DB_USERNAME = "postgres"
DB_PASSWORD = ""


def create_security_group(ec2_client) -> str:
    """Create security group with required ports if it doesn't exist"""
    try:
        # Check if security group already exists
        existing_groups = ec2_client.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": ["MeeraSecurityGroup"]}]
        )

        if existing_groups["SecurityGroups"]:
            print("Security group 'MeeraSecurityGroup' already exists")
            return existing_groups["SecurityGroups"][0]["GroupId"]

        # Create new security group if it doesn't exist
        response = ec2_client.create_security_group(
            GroupName="MeeraSecurityGroup",
            Description="Security group for Meera application",
        )
        security_group_id = response["GroupId"]

        # Define inbound rules
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                # SSH
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
                # HTTP
                {
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
                # HTTPS
                {
                    "IpProtocol": "tcp",
                    "FromPort": 443,
                    "ToPort": 443,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
                # PostgreSQL
                {
                    "IpProtocol": "tcp",
                    "FromPort": 5432,
                    "ToPort": 5432,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
                # LiveKit ports
                {
                    "IpProtocol": "tcp",
                    "FromPort": 7880,
                    "ToPort": 7881,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
                {
                    "IpProtocol": "udp",
                    "FromPort": 7882,
                    "ToPort": 7882,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
            ],
        )
        print("Created new security group 'MeeraSecurityGroup'")
        return security_group_id
    except Exception as e:
        print(f"Error creating security group: {e}")
        raise


def create_rds_instance(rds_client, security_group_id: str) -> Dict[str, Any]:
    """Create RDS PostgreSQL instance"""
    try:
        # Check if the RDS instance already exists
        try:
            response = rds_client.describe_db_instances(
                DBInstanceIdentifier=DB_INSTANCE_NAME
            )
            print(
                f"RDS instance {DB_INSTANCE_NAME} already exists. Using existing instance."
            )
            return response["DBInstances"][0]
        except rds_client.exceptions.DBInstanceNotFoundFault:
            # Create new RDS instance if it doesn't exist
            response = rds_client.create_db_instance(
                DBName=DB_NAME,
                DBInstanceIdentifier=DB_INSTANCE_NAME,
                AllocatedStorage=20,
                DBInstanceClass="db.t4g.small",
                Engine="postgres",
                MasterUsername=DB_USERNAME,
                MasterUserPassword=DB_PASSWORD,
                VpcSecurityGroupIds=[security_group_id],
                PubliclyAccessible=True,
                Port=5432,
            )
            print(f"Created new RDS instance {DB_INSTANCE_NAME}")
            return response
    except Exception as e:
        print(f"Error creating RDS instance: {e}")
        raise


def create_ec2_instance(
    ec2_client, security_group_id: str, instance_name: str
) -> Dict[str, Any]:
    """Create EC2 instance"""
    try:
        response = ec2_client.run_instances(
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": instance_name}],
                }
            ],
            ImageId="ami-0287a05f0ef0e9d9a",  # Ubuntu Server 22.04 LTS (adjust AMI ID as needed)
            InstanceType="t3.medium",
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[security_group_id],
            KeyName=KEY_PAIR_NAME,
            BlockDeviceMappings=[
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": {"VolumeSize": 30, "VolumeType": "gp2"},
                }
            ],
        )
        return response["Instances"][0]
    except Exception as e:
        print(f"Error creating EC2 instance: {e}")
        raise


def create_key_pair(ec2_client, key_name: str, key_path: str) -> bool:
    """Create a new key pair if it doesn't exist and save it locally"""
    try:
        # Check if key pair already exists
        try:
            ec2_client.describe_key_pairs(KeyNames=[key_name])
            print(f"Key pair {key_name} already exists. Using existing key.")
            if not os.path.exists(key_path):
                print(
                    f"WARNING: Key file not found at {key_path}. You may need to use a different key."
                )
            return False
        except ec2_client.exceptions.ClientError as e:
            if "InvalidKeyPair.NotFound" in str(e):
                # Create new key pair
                response = ec2_client.create_key_pair(KeyName=key_name)

                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(key_path)), exist_ok=True)

                # Save private key to file
                with open(key_path, "w") as key_file:
                    key_file.write(response["KeyMaterial"])

                # Set correct permissions for key file
                os.chmod(key_path, 0o400)  # Read-only by owner

                print(f"Created new key pair {key_name} and saved to {key_path}")
                return True
            else:
                raise
    except Exception as e:
        print(f"Error creating key pair: {e}")
        raise


def main():
    # Initialize AWS clients
    ec2_client = boto3.client(
        "ec2",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    rds_client = boto3.client(
        "rds",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    # Create key pair if needed
    create_key_pair(ec2_client, KEY_PAIR_NAME, SSH_KEY_PATH)

    # Create security group
    security_group_id = create_security_group(ec2_client)

    # # Create RDS instance
    create_rds_instance(rds_client, security_group_id)

    # Create Dev EC2 instance
    create_ec2_instance(ec2_client, security_group_id, "meera-dev")
    print("Created Dev EC2 instance")

    # Create Prod EC2 instance
    create_ec2_instance(ec2_client, security_group_id, "meera-prod")
    print("Created Prod EC2 instance")


if __name__ == "__main__":
    main()
