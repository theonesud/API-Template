# How to set up the infrastructure, code and autodeployments

## 1. Create security credentials

-   Go to IAM in AWS Console
-   Click on "Account name" (top right)
-   Click on "Security credentials"
-   Click on "Create access key"
-   Download the credentials and save them securely

## 2. Setup AWS

-   Run `python aws-setup.py` - Create EC2 instances, security group, RDS instance
-   Add the following A records to cloudflare:
    -   @ -> 'prod instance ip' for callmeeraos.com to point to prod instance
    -   api -> 'prod instance ip' for api.callmeeraos.com to point to prod instance
    -   dev -> 'dev instance ip' for dev.callmeeraos.com to point to dev instance
    -   devapi -> 'dev instance ip' for devapi.callmeeraos.com to point to dev instance

## 3. Setup servers

-   Run `python server-setup.py` - Setup docker, nginx, certbot
-   It will print 2 ssh keys. Add both the ssh keys to the github settings > ssh keys
-   Login to dev:
    -   `ssh -i ~/.ssh/id_rsa ubuntu@devapi.callmeeraos.com`
    -   `git clone git@github.com:theonesud/meera-webapp.git`
    -   `git clone git@github.com:theonesud/meera-api.git`
    -   `cd meera-webapp && git checkout dev && cd ../meera-api && git checkout dev && cd ..`
    -   Add env files to both
    -   Run `./deploy.sh`
    -   Run `curl localhost:8000/reset_db` to initialize the database
-   Login to prod:
    -   `ssh -i ~/.ssh/id_rsa ubuntu@api.callmeeraos.com`
    -   `git clone git@github.com:theonesud/meera-webapp.git`
    -   `git clone git@github.com:theonesud/meera-api.git`
    -   Add env files to both
    -   Run `./deploy.sh`
    -   Run `curl localhost:8000/reset_db` to initialize the database

## 4. Setup Github Actions

-   Create Secrets in Github for backend and frontend repos:
    -   AWS_ID=
    -   AWS_SECRET=
    -   AWS_REGION=
    -   DEV_HOST=devapi.callmeeraos.com
    -   PROD_HOST=api.callmeeraos.com
    -   DEV_KEY=ssh key from pem file to login to dev instance
    -   PROD_KEY=ssh key from pem file to login to prod instance

## 5. If not already done, setup the following:

### Google Cloud for Authentication

-   Go to APIs and Services and enable Google+ API
-   Go to OAuth consent screen section and create new consent screen
    -   Create an external app
    -   Add links for terms and privacy policy pages
    -   Publish app to production
-   Go to Credentials section and create new OAuth2 client id and secret
    -   Add `localhost:3000` or any other frontend url to Authorised JavaScript origins
    -   Add `localhost:3000/api/auth/callback/google` to Authorised redirect URIs
    -   Similarly add for `https://app.callmeeraos.com` and `https://devapp.callmeeraos.com`
-   Download keys and save them securely
