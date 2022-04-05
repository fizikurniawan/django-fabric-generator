# Deploy Django App use Fabfile


## Fabfile
What the fab script does:

The script is meant to deploy a bookshop application to a digital ocean vsp (works with any vps). Server configurations are found in a deploy folder within the project root. Virtualenv is inside the project root as well.

1. Prepare fresh environment - Install sudo apt-packages (nginx, php, python, python-pip)
2. Create directory
3. Clone repository
4. Create virtualenvironment
5. Install Requirements
6. Run using gunicorn, supervisor, and nginx

Upon deployment, hit fab prod deploy
Enjoy!



## Usage

### Run with environtment file
 1. Install [python-dotenv](https://pypi.org/project/python-dotenv/)
 2. copy *.env-example* to *.env*
 3. Adjust value *.env*
 4. Run `$ python3 deployer.py staging	` 
 5. Files will be generated on stage folder. 

### Run with console mode

 1. Run `$ python3 deployer.py`
 2. Fill every input

## ENV Value
| key |value  | Desc |
|--|--|--|
| REPO_URL |https://gitlab.com/repo_url | repo of django application |
|STAGING_BRANCH_NAME | development | branch want to deploy on staging stage |
|STAGING_HOST | 192.168.0.100 | server IP to deploy on staging stage |
|STAGING_HOST_USER | root | user server to deploy on staging stage |
|STAGING_HOST_PASS | root | pass server to deploy on staging stage |
|PROJECT_ROOT | /opt/app/ | application will be located |
|PROJECT_GROUP | example.com | You can put main domain of project. |
|PROJECT_NAME | api.example.com | You can put main subdomain of project. |


## Example .env
```text
REPO_URL=https://gitlab.com/repo_url
STAGING_BRANCH_NAME=development
STAGING_HOST=192.168.0.100
STAGING_HOST_USER=ssh_user
STAGING_HOST_PASS=ssh_password
PROJECT_ROOT=/opt/app/
PROJECT_GROUP=example.id
PROJECT_NAME=api.example.id
```