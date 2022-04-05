#!/bin/bash
VENV=$1
if [ -z $VENV ]; then
    echo "usage: virtualenv-activate [virtualenv_path] CMDS"
    exit 1
fi
. ${VENV}/venv/bin/activate
shift 1
echo "Executing $@ in ${VENV}"
exec "$@"
deactivate