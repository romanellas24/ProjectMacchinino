#!/bin/bash

# Comandi per bluetoothctl
bluetoothctl << EOF
power on
agent on
default-agent
pairable on
discoverable on
EOF

echo "Bluetooth abilitato - Pronto al PAIR." && bluetoothctl