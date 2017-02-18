#!/bin/bash
pgrep -f hue.py
if [ $? -eq 0 ]; then
    echo "Hue is running."
else
    echo "hue is not running...starting."
    sudo systemctl start hue.service
fi

pgrep -f users.py
if [ $? -eq 0 ]; then
    echo "users is running."
else
    echo "users is not running...starting."
    sudo systemctl start users.service
fi