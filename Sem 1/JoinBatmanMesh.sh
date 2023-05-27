#!/bin/bash
# Script to automatically join the mesh network

# Runs update
echo "Updating apt-get"
sudo apt-get update && sudo apt-get upgrade -y

# Installs a configuration utility for BATMAN-adv
echo -e "\nInstaling BATMAN-adv..."
sudo apt-get install -y batctl

# Sets up the mesh-metwork
echo -e "\nConnecting to the mesh network..."
cat << 'EOF' >~/start-batman-adv.sh
    #!/bin/bash
    # adds wlan0 to the batman-adv virtual interface
    sudo batctl if add wlan0
    sudo ifconfig bat0 mtu 1468

    # Tell batman-adv this is a gateway client
    sudo batctl gw_mode client

    # Activates batman-adv interfaces
    sudo ifconfig wlan0 up
    sudo ifconfig bat0 up
EOF

# Makes the start-batman-adv.sh file executable
chmod +x ~/start-batman-adv.sh

# Creates the network interface definition for the wlan0
FILE="/etc/network/interfaces.d/wlan0"                  # Creating a file under Privilege Mode
sudo bash -c "cat > $FILE" <<- EOF                        
    auto wlan0
    iface wlan0 inet manual
        wireless-channel 1
        wireless-essid call-code-mesh
        wireless-mode ad-hoc
EOF

# Ensures the batman-adv kernel module is loaded at boot time
echo -e "\nSetting BATMAN-adv to be loaded at reboot time..."
echo 'batman-adv' | sudo tee --append /etc/modules

# Stops the DHCP process from trying to manage the wlan interface
echo -e "\nStopping DHCP process to manage the wlan interface..."
echo 'denyinterfaces wlan0' | sudo tee --append /etc/dhcpcd.conf

# Makes sure the startup script gets called by inserting the path to the script before the last line of rc.local
echo -e "\nAdding startup script into rc.local..."
FILE="/etc/rc.local"
sudo bash -c "sed -i '$ d' $FILE"                         # Delete the last line (exit 0) under Privilege Mode
                                                          # Insert the path of startup script to the file under Privilege Mode
sudo bash -c "cat >> $FILE" <<- EOF                       
    /home/pi/start-batman-adv.sh &
    exit 0
EOF

# Ask for reboot
echo -e "\nMesh network setup succeed.\nReboot to complete the install? [y/n] \c"
read -r option
if [ $option = y -o $option = Y ];then
    sudo reboot
fi
