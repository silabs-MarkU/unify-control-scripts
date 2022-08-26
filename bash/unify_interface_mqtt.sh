#!/bin/bash
#set -x

UNIFY_IP_ADDR="192.168.1.148"
ON_OFF_DEVICE="zw-CAA5CFB2-0003"
SLEEP_TIME=0.5

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c()
{
        echo -e "\nExiting loop, and turning off devices."
        mosquitto_pub -h $UNIFY_IP_ADDR -t "ucl/by-unid/$ON_OFF_DEVICE/ep0/OnOff/Commands/Off" -m {}
        exit 0
}

echo -e "\nStarting on/off loop for device: $ON_OFF_DEVICE"

while true; do
        mosquitto_pub -h $UNIFY_IP_ADDR -t "ucl/by-unid/$ON_OFF_DEVICE/ep0/OnOff/Commands/Off" -m {}

        sleep $SLEEP_TIME

        mosquitto_pub -h $UNIFY_IP_ADDR -t "ucl/by-unid/$ON_OFF_DEVICE/ep0/OnOff/Commands/On" -m {}

        sleep $SLEEP_TIME
done

exit 0