#!/bin/sh

echo "============================="
echo "MESSAGEBOX INSTALL SCRIPT 1.0"
echo "============================="

read -p "New Hostname (leave blank for no changes): " hostname
if [ ! -z "${hostname}" ];
then
    echo "Your new hostname: ${hostname}"
    sudo raspi-config nonint do_hostname $hostname
else
    echo "Hostname not changed."
fi

echo "\n============================="
echo "Setup raspi-config"
echo "============================="

echo "\nEnable SPI"
sudo raspi-config nonint do_spi 1
echo "Done!"

echo "\nExpand Root Fs"
sudo raspi-config nonint do_expand_rootfs
echo "Done!"

echo "\n============================="
echo "Enable OS Tweaks"
echo "============================="

echo "\nDisable HDMI"
RC_LOCAL_FILE=/etc/rc.local
DISABLED_HDMI_CMD="/usr/bin/tvservice -o"
if grep -q $DISABLED_HDMI_CMD $RC_LOCAL_FILE; then
    echo "HDMI already disabled."
else
    echo $DISABLED_HDMI_CMD | sudo tee -a  $RC_LOCAL_FILE
    echo "Done!"
fi
/usr/bin/tvservice -o


echo "\n============================="
echo "Installing required packages"
echo "============================="

echo "\nInstall pip3, dejavu-font, git, libopenjp2-7, libtiff5"
sudo apt install python3-pip ttf-dejavu git libopenjp2-7 libtiff5 -y
echo "Done!"

echo "\nInstall virtualenv"
sudo pip3 install virtualenv
echo "Done!"

echo "\n============================="
echo "Create Messagebox SYSTEMD Service"
echo "============================="

SERVICE_FILE=/lib/systemd/system/messagebox.service

if [ -f "$SERVICE_FILE" ]; then
    echo "\nMessagebox Service already exists. Nothing to do."
else 
    echo "\nCreating a new service file: ${SERVICE_FILE}"
    sudo tee -a $SERVICE_FILE > /dev/null <<EOT
[Unit]
Description=Messagebox Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python /home/pi/sample.py
User=$USER
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOT
    cat $SERVICE_FILE
    echo "Done!"

    echo "\nChange Service Permission to 644"
    sudo chmod 644 $SERVICE_FILE

    sudo systemctl daemon-reload

    echo "\nEnable Messagebox Service"
    sudo systemctl enable messagebox.service
fi

# packages
# pip3 install adafruit-circuitpython-rgb-display
# pip3 install pillow
# pip3 install gpiozero