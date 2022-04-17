#!/bin/bash

# Checks if we have python3 installed, if not error message is shown
if ! command -v python3 &> /dev/null; then
    printf "'python3' is not installed on local machine, or is not attached to the user's PATH\n"
    exit 1
fi

# Forward off command line arguments to the python file
python3 ./parse.py $@