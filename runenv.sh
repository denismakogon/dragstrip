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

dragstrip=$(find ~ -type d -name dragstrip)
export PYTHONPATH=$PYTHONPATH:$dragstrip
