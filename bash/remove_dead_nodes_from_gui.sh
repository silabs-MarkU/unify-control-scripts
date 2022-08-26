#!/bin/bash
#set -x

echo -e "\nThis script removes dead nodes from the Unify SDK sample GUI.\n"
echo -e "** This script should be run on the system running Unify SDK **\n"

if [ "$EUID" -ne 0 ]; then
        echo -e "Please run as root!\n"
        exit 1
fi

echo -e "Checking for unify installation.."

if [ -d /var/lib/uic ]; then
        echo -e ".. Unify SDK installation found, removing nodes.\n"

        systemctl stop mosquitto.service
        systemctl stop uic-nal.service
        rm /var/lib/mosquitto/mosquitto.db
        rm /var/lib/uic/nal.db
        systemctl start mosquitto.service
        systemctl start uic-nal.service
        systemctl restart uic-zpc.service

        echo -e "Done.\n"
else
        echo "Unify SDK does not appear to be installed, exiting.."
        exit 1
fi

exit 0