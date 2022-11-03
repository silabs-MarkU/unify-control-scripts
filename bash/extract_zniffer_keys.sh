#!/bin/bash
#set -x

echo -e "\nThis script extracts the network keys for use with the zniffer.\n"

# Have not yet been able to figure out how to input the zwave_log_security_keys command into ZPC. Then have to rearrange the data into zniffer format.


if [ "$EUID" -ne 0 ]; then
        echo -e "Please run as root!\n"
        exit 1
fi

echo -e "Checking for unify installation.."

if [ -d /var/lib/uic ]; then

        systemctl stop uic-zpc.service
        

#        zpc (then enter the command zwave_log_security_keys)

        # then reformat the data and save to a file <HomeID>.txt

        systemctl start uic-zpc.service
        echo -e "Done.\n"
else
        echo "Unify SDK does not appear to be installed, exiting.."
        exit 1
fi

exit 0
