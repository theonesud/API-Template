## Deploy with Docker & Route Backend/Frontend through Nginx and add SSL to the domain on AWS Server

### Prerequisites

-   Git clone repo
-   Add .env files
-   Add these two A Records:
    -   api -> server ip
    -   app -> server ip
-   An AMI with docker installed

### Install Requirements

-   sudo apt update && sudo apt upgrade
-   sudo apt install nginx certbot python3-certbot-nginx
-   sudo ufw enable && sudo ufw allow https && sudo ufw allow 'Nginx HTTP' && sudo ufw allow 22

### Start Server

-   docker-compose up --build -d

### Configure Nginx and add https

-   sudo nano /etc/nginx/conf.d/sheeghram.conf

```
server {
    server_name dev.sheeghram.com;
    client_header_buffer_size 64k;
    large_client_header_buffers 4 64k;
    location / {
        proxy_pass http://0.0.0.0:4000;
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
    }
}

server {
    server_name devapp.sheeghram.com;
    client_header_buffer_size 64k;
    large_client_header_buffers 4 64k;
    location / {
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
    }
}
server {
    server_name devapi.sheeghram.com;
    location / {
        proxy_pass http://0.0.0.0:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

-   sudo systemctl restart nginx
-   sudo certbot --nginx
-   crontab -e

```
0 12 * * * /usr/bin/certbot renew --quiet
```
