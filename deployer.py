#!/usr/bin/python3

import os
import sys

from utils import bcolors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_deployer():
    print(bcolors.HEADER, "WELCOME to Deploy Generator")
    deploy_stage = input(" Deploy mode: (staging/production): ")

    if deploy_stage not in ["staging", "production"]:
        print(bcolors.FAIL, "Invalid deploy mode input")
        exit()

    deploy_stage = "staging"

    print(bcolors.OKGREEN, "======== Server Configuration ========")
    host = input("IP HOST: ")
    ssh_user = input("HOST Username: ")
    ssh_password = input("HOST Password: ")
    print("==============================")

    print(bcolors.OKGREEN, "======== Work DIR Configuration ========")
    repo_url = input("REPO URL (https): ")
    branch_name = input("Work Branch (development): ") or "development"
    project_root = input("Project Root DIR (/opt/app/): ") or "/opt/app/"
    project_group = input("Project Group (exampleproject.id): ") or "exampleproject.id"
    project_name = (
        input("Project Name (api.exampleproject.id): ") or "api.exampleproject.id"
    )
    print("========================================")

    FABFILE_REPLACE_DATA = [
        ("REPO_URL", repo_url),
        (f"{deploy_stage.upper()}_BRANCH_NAME", branch_name),
        (f"{deploy_stage.upper()}_HOST", host),
        (f"{deploy_stage.upper()}_HOST_USER", ssh_user),
        (f"{deploy_stage.upper()}_HOST_PASS", ssh_password),
        ("PROJECT_ROOT", project_root),
        ("PROJECT_GROUP", project_group),
        ("PROJECT_NAME", project_name),
        ("SYSTEMD_NAME", project_name),
    ]
    generate_fabfile(FABFILE_REPLACE_DATA)

    SUPERVISORD_REPLACE_DATA = [
        ("DEPLOY_WORK_DIR", project_root + project_name),
        ("APP_ROOT", project_root + project_name + "/" + project_group),
        ("APP_NAME", project_name),
    ]
    generate_supervisord(deploy_stage, SUPERVISORD_REPLACE_DATA)

    SYSTEMD_REPLACE_DATA = [
        ("DEPLOY_WORK_DIR", project_root + project_name),
        ("APP_ROOT", project_root + project_name + "/" + project_group),
        ("APP_NAME", project_name),
        ("PROJECT_GROUP", project_group),
    ]
    generate_systemd(deploy_stage, project_name, SYSTEMD_REPLACE_DATA)


def generate_fabfile(REPLACE_DATA):
    copy_cmd = "cp template/fabfile.py deploy/fabfile.py"
    os.system(copy_cmd)

    # Read in the file
    fabfile_path = BASE_DIR + "/deploy/fabfile.py"
    with open(fabfile_path, "r") as file:
        filedata = file.read()

    # Replace the target string
    for w_replace in REPLACE_DATA:
        filedata = filedata.replace("{{" + w_replace[0] + "}}", w_replace[1])

    # Write the file out again
    with open(fabfile_path, "w") as file:
        file.write(filedata)


def generate_supervisord(deploy_stage, REPLACE_DATA):
    copy_cmd = f"cp template/supervisord.conf deploy/{deploy_stage}/supervisord.conf"
    os.system(copy_cmd)

    # Read in the file
    fabfile_path = BASE_DIR + "/deploy/" + deploy_stage + "/supervisord.conf"
    with open(fabfile_path, "r") as file:
        filedata = file.read()

    # Replace the target string
    for w_replace in REPLACE_DATA:
        filedata = filedata.replace("{{" + w_replace[0] + "}}", w_replace[1])

    # Write the file out again
    with open(fabfile_path, "w") as file:
        file.write(filedata)


def generate_systemd(deploy_stage, project_name, REPLACE_DATA):
    copy_cmd = (
        f"cp template/systemd.service deploy/{deploy_stage}/{project_name}.service"
    )
    os.system(copy_cmd)

    # Read in the file
    fabfile_path = BASE_DIR + "/deploy/" + deploy_stage + f"/{project_name}.service"
    with open(fabfile_path, "r") as file:
        filedata = file.read()

    # Replace the target string
    for w_replace in REPLACE_DATA:
        filedata = filedata.replace("{{" + w_replace[0] + "}}", w_replace[1])

    # Write the file out again
    with open(fabfile_path, "w") as file:
        file.write(filedata)


def generate_from_env(deploy_stage):
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())

    ENV_KEYS = [
        "REPO_URL",
        f"{deploy_stage.upper()}_BRANCH_NAME",
        f"{deploy_stage.upper()}_HOST",
        f"{deploy_stage.upper()}_HOST_USER",
        f"{deploy_stage.upper()}_HOST_PASS",
        "PROJECT_ROOT",
        "PROJECT_NAME",
        "PROJECT_GROUP",
    ]
    FABFILE_REPLACE_DATA = [(key, os.environ.get(key)) for key in ENV_KEYS]
    FABFILE_REPLACE_DATA.append(("SYSTEMD_NAME", FABFILE_REPLACE_DATA[6][1]))
    generate_fabfile(FABFILE_REPLACE_DATA)

    SUPERVISORD_REPLACE_DATA = [
        ("DEPLOY_WORK_DIR", FABFILE_REPLACE_DATA[5][1] + FABFILE_REPLACE_DATA[6][1]),
        (
            "APP_ROOT",
            FABFILE_REPLACE_DATA[5][1]
            + FABFILE_REPLACE_DATA[6][1]
            + "/"
            + FABFILE_REPLACE_DATA[7][1],
        ),
        ("APP_NAME", FABFILE_REPLACE_DATA[6][1]),
    ]
    generate_supervisord(deploy_stage, SUPERVISORD_REPLACE_DATA)

    SYSTEMD_REPLACE_DATA = [
        ("DEPLOY_WORK_DIR", FABFILE_REPLACE_DATA[5][1] + FABFILE_REPLACE_DATA[6][1]),
        (
            "APP_ROOT",
            FABFILE_REPLACE_DATA[5][1]
            + FABFILE_REPLACE_DATA[6][1]
            + "/"
            + FABFILE_REPLACE_DATA[7][1],
        ),
        ("APP_NAME", FABFILE_REPLACE_DATA[6][1]),
        ("PROJECT_GROUP", FABFILE_REPLACE_DATA[7][1]),
    ]
    generate_systemd(deploy_stage, FABFILE_REPLACE_DATA[6][1], SYSTEMD_REPLACE_DATA)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        generate_deployer()
    elif sys.argv[1] in ["staging", "production"]:
        generate_from_env(sys.argv[1])
    else:
        print("Invalid operation")
