import os
import requests
import json

from django.conf import settings

from fabric.api import env, sudo as _sudo, run as _run
from fabric.operations import *
from fabric.contrib import files as f
from fabric.colors import red, green, blue


"""
What the fab script does:
The script is meant to deploy a bookshop application to a digital ocean vsp (works with any vps). Server configurations are found in
a deploy folder within the project root. Virtualenv is inside the project root as well.
1. Prepare fresh environment - Install sudo apt-packages (nginx, php, python, python-pip)
2. Create directory
3. Clone repository
4. Create virtualenvironment
5. Install Requirements
6. Run using gunicorn, supervisor, and nginx

Upon deployment, hit fab prod deploy

Enjoy!

"""

deployer = input("Please write your name: ")
repo_url = "{{REPO_URL}}"


def staging():
    env.hosts = [
        "{{STAGING_HOST}}",
    ]
    env.user = "{{STAGING_HOST_USER}}"
    env.password = "{{STAGING_HOST_PASS}}"
    env.folder = "staging"

    env.use_ssh_config = False
    env.port = 22
    env.timeout = 20

    env.project_root = "{{PROJECT_ROOT}}"
    env.project_group = "{{PROJECT_GROUP}}"
    env.project_name = "{{PROJECT_NAME}}"
    env.local_settings = os.path.join(os.getcwd(), "staging/local_settings.py")
    env.branch_name = "{{STAGING_BRANCH_NAME}}"

    env.deploy_work_dir = f"{env.project_root}{env.project_name}"
    env.project_env = f"{env.deploy_work_dir}/venv/"
    env.app_root = env.deploy_work_dir + env.env.project_group
    env.systemd = "{}/deploy/{}/{}.service".format(
        env.app_root, env.folder, env.project_name
    )


def turn_off_all():
    print(red("[Turning Supervisor OFF]"))
    _sudo("systemctl stop {}.service".format(env.project_name))


def turn_on_all():
    print(green("[Turning Supervisor ON]"))
    _sudo("systemctl start {}.service".format(env.project_name))


def restart_service():
    print(green("[Restarting Supervisor]"))
    _sudo("systemctl restart {}.service".format(env.project_name))


def preparing_dir():
    if not f.exists(env.project_root):
        print(green("Creating project directory..."))
        _sudo(f"mkdir -p {env.project_root}")

    # create deploy_work_dir
    if not f.exists(env.deploy_work_dir):
        _sudo(f"mkdir -p {env.deploy_work_dir}")

    # change owner workdir with user deployer
    change_owner_cmd = f"chown -R {env.user}:{env.user} {env.project_root}"
    _sudo(change_owner_cmd)


def checking_virtualenv():
    # cleanup current env
    print(green("[CHECKING VIRTUAL ENVIRONMENT]"))
    if not f.exists(env.project_env):
        print(green("[CREATE FRESH ENVIRONMENT]"))
        _run("cd {} && virtualenv -p python3 venv".format(env.deploy_work_dir))


def preparing_virtualenv():
    # cleanup current env
    print(green("[PREPARING VIRTUAL ENVIRONMENT]"))
    if f.exists(env.project_env):
        print(red("[REMOVE VIRTUAL ENVIRONMENT]"))
        _run("cd {} && rm -rf venv".format(env.deploy_work_dir))

    # create fresh env
    print(green("[CREATE FRESH ENVIRONMENT]"))
    _run("cd {} && virtualenv -p python3 venv".format(env.deploy_work_dir))


def install_requirements():
    print(blue("[Upgrading pip and setuptools Requirements...]"))
    _run(
        "cd {} && source ../venv/bin/activate && pip install pip --upgrade \
          && pip install setuptools --upgrade".format(
            env.app_root
        )
    )
    print(blue("[Installing Requirements...]"))
    _run(
        "cd {} && source ../venv/bin/activate \
          && export CPLUS_INCLUDE_PATH=/usr/include/gdal \
          && export C_INCLUDE_PATH=/usr/include/gdal \
          && pip install -r requirements.txt".format(
            env.app_root
        )
    )


def pull_code():
    print(green("[PULLING CODE]"))
    _run(
        "source {}bin/activate && cd {} \
          && git pull origin {}".format(
            env.project_env, env.app_root, env.branch_name
        )
    )


def clone_repo():
    print(red("[Cloning repository ...]"))
    _run(
        "source {}bin/activate && cd {} \
          && git clone -b {} {} {}".format(
            env.project_env, env.app_root, env.branch_name, repo_url, env.project_group
        )
    )


def support_directory():
    # create support directories
    print(blue("[Creating support directories]"))
    if not f.exists("{}run".format(env.deploy_work_dir)):
        _run("cd {} && mkdir run".format(env.deploy_work_dir))
    if not f.exists("{}logs".format(env.deploy_work_dir)):
        _run("cd {} &&  mkdir logs".format(env.deploy_work_dir))


def copy_local_settings():
    print(red("Copying local settings..."))
    if f.exists(env.app_root + "project/local_settings.py"):
        _run("rm {}project/local_settings.py ".format(env.app_root))

    put(env.local_settings, "{}project/local_settings.py".format(env.app_root))


def create_systemd_file():
    print(red("Creating systemd file..."))
    _sudo("cp {} /etc/systemd/system/".format(env.systemd))


def reload_systemd():
    _sudo("systemctl daemon-reload")


def deploy():
    if f.exists(env.project_root):
        pull_code()
    else:
        fresh_deploy()

    create_systemd_file()
    install_requirements()
    copy_local_settings()
    reload_systemd()
    turn_off_all()
    turn_on_all()


def fresh_deploy():
    preparing_dir()
    checking_virtualenv()
    clone_repo()
    support_directory()


def restart():
    turn_off_all()
    turn_on_all()
