#!/bin/bash

# Use as source

vew=$(which virtualenvwrapper.sh)
source $vew
export PYTHONPATH=$PYTHONPATH:$vew
envs=$(workon)
if [[ "messaging" =~ $envs ]]
then
    mkvirtualenv messaging -r requirements.txt
else
    source $WORKON_HOME/messaging/bin/activate
    pip install -r requirements.txt
fi

messenger=$(find ~ -type d -name messenger)
export PYTHONPATH=$PYTHONPATH:$messenger
