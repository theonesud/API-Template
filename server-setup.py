import os
import time

import boto3
import paramiko

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_REGION = "ap-south-1"
SSH_KEY_PATH = "./meera-key.pem"


def get_ec2_instances():
    """Get all running EC2 instances"""
    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    response = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            # Get instance name from tags
            instance_name = "Unknown"
            if "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag["Key"] == "Name":
                        instance_name = tag["Value"]
                        break

            instances.append({"name": instance_name, "ip": instance["PublicIpAddress"]})

    return instances


def setup_server(
    instance_ip: str, ssh_key_path: str, frontend_domain: str, backend_domain: str
):
    """Setup Docker and other requirements on the EC2 instance"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname=instance_ip, username="ubuntu", key_filename=ssh_key_path)

        # Setup commands from the AWS.md file
        commands = [
            "sudo apt update && sudo apt upgrade -y",
            "echo 'y' | sudo ufw enable && sudo ufw allow https && sudo ufw allow http && sudo ufw allow 22",
            'ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa',
            "for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done",
            "sudo apt install -y git htop curl wget ca-certificates nginx certbot python3-certbot-nginx",
            "sudo install -m 0755 -d /etc/apt/keyrings",
            "sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
            "sudo chmod a+r /etc/apt/keyrings/docker.asc",
            'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
            "sudo apt-get update",
            "sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y",
            "sudo usermod -aG docker $USER",
        ]

        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            stderr_output = stderr.read().decode()
            if stderr_output.strip():
                print(f"> {command}")
                print(f"??? {stderr_output}")

        # Upload nginx configuration
        nginx_config = f"""
    server {{
        server_name {frontend_domain};
        client_header_buffer_size 64k;
        large_client_header_buffers 4 64k;
        location / {{
            proxy_pass http://0.0.0.0:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_buffer_size 128k;
            proxy_buffers 4 256k;
            proxy_busy_buffers_size 256k;
            proxy_max_temp_file_size 0;
        }}
    }}
    server {{
        server_name {backend_domain};
        location / {{
            proxy_pass http://0.0.0.0:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }}
    }}
        """
        sftp = ssh.open_sftp()
        with sftp.file("/tmp/meera.conf", "w") as f:
            f.write(nginx_config)

        commands = [
            "sudo mv /tmp/meera.conf /etc/nginx/conf.d/meera.conf",
            "sudo systemctl restart nginx",
            f"sudo certbot --nginx --non-interactive --agree-tos -m sudhanshupassi@gmail.com -d {frontend_domain} -d {backend_domain}",
            '(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -',
            "cat ~/.ssh/id_rsa.pub",
        ]

        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            if command == "cat ~/.ssh/id_rsa.pub":
                print(stdout.read().decode())
            stderr_output = stderr.read().decode()
            if stderr_output.strip():
                print(f"> {command}")
                print(f"??? {stderr_output}")

    except Exception as e:
        print(f"Error setting up server: {e}")
        raise
    finally:
        ssh.close()


def main():
    instances = get_ec2_instances()
    print(f"Found {len(instances)} running instances: {instances}")

    for instance in instances:
        print(f"\nSetting up server at {instance['name']} ({instance['ip']})")
        if instance["name"] == "meera-dev":
            setup_server(
                instance_ip=instance["ip"],
                ssh_key_path=SSH_KEY_PATH,
                frontend_domain="devapp.callmeeraos.com",
                backend_domain="devapi.callmeeraos.com",
            )
        elif instance["name"] == "meera-prod":
            setup_server(
                instance_ip=instance["ip"],
                ssh_key_path=SSH_KEY_PATH,
                frontend_domain="app.callmeeraos.com",
                backend_domain="api.callmeeraos.com",
            )


if __name__ == "__main__":
    main()
