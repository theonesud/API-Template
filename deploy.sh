#!/bin/bash

# Define the container name as a variable
APP_NAME="api-template"

# Pull the latest changes from the git repository
git pull

# Stop the existing Docker container if it's running
docker stop $APP_NAME || true
docker rm $APP_NAME || true

# Build the Docker image
docker build -t ${APP_NAME}-image .

# Run the Docker container
docker run -d --name $APP_NAME -p 8000:8000 ${APP_NAME}-image

echo "Deployment completed. The backend is now running on port 8000."