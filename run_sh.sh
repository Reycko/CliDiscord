#!/bin/bash

while true
do
    clear
    echo "Bot token?"
    read -r token
    echo "Channel ID?"
    read -r chid
    echo

    python CliDiscord.py "$token" "$chid"

    echo
    echo
    echo "Press any key to restart the program."
    read -n 1 -s
done
