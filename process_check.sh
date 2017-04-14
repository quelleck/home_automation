#!/bin/bash
pgrep -f hue.py
if [ $? -eq 0 ]; then
    echo "hue is running."
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

pgrep -f hdmi_control.py
if [ $? -eq 0 ]; then
    echo "hdmi_control is running."
else
    echo "hdmi_control is not running...starting."
    sudo systemctl start hdmi_control.service
fi