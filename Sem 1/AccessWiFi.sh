#!/bin/bash
# Script to automatically access the WiFi by editing the wpa_supplicant configuration file

interface="wlan0"
ethdev="eth0"
WPA_path="/etc/wpa_supplicant/wpa_supplicant.conf"
backup_path="/home/pi/script/BackUpwpa_supplicant.conf"

# First function to search for a specific SSID
FindSSID()
{
  option="y"
  while [ $option = y -o $option = Y ]
  do
    #Check whether the provided SSID is in range
    echo -e "Enter a WiFi SSID: \c"
    read -r SSID
    echo "Start searching for the SSID..."
    result=$(iwlist $interface scan | grep -w "$SSID" | wc -l)  # Uses "iwlist" command to search for the available WiFi interfaces
    if [ "$result" = 0 ];
    then
      echo "No SSID:'${SSID}' found"
      echo -e "\nContinue to search for WiFi? [y/n] \c"
      read -r option
      if [ $option = y -o $option = Y ]; then
        continue
      else
        echo "Existing..."
        exit
      fi
     else
      echo "SSID:'${SSID}' Found"
      option="n"
     fi
   done
}

# Second function to backup the current wpa_supplicant file in case the new wifi fails
BackUpWiFI()
{
  sudo cp "$WPA_path" "$backup_path"
  echo "Captured current wifi setting"
}

# Third function to ask for the WiFi password and configure the wpa_supplicant file
AccessWiFi()
{
  pw1="0"
  pw2="1"
  until [ $pw1 == $pw2 ]; do
    echo -e "Type a password to access $SSID, then press [ENTER]: \c"
    read -s -r pw1
 
    echo -e "\nVerify the password to acccess $SSID, then press [ENTER]: \c"
    read -s -r pw2
  done
    
  network=`wpa_passphrase $SSID $pw1`                      # Setup the network using "wpa_passpharse" command 
                                                           # Adding network into wpa_supplicant file under Privilege Mode
  sudo bash -c "cat > $WPApath" <<- EOF
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=HK
 
    $network
  EOF
  
  echo -e "\nModified wpa_dupplicant.conf"
  sudo wpa_cli -i $interface reconfigure
  echo -e "\nReconfigured $interface"
}

# Fourth function to check the WiFi connectivity
CheckWiFiUp()
{
  echo "Checking WiFi connection..."
  sleep 20
  if ! wpa_cli -i "$interface" status | grep 'ip_address' >/dev/null 2>&1 # If no IP address
  then
    echo 'WiFi failed to connect, falling back to original WiFi setting'
    sudo bash -c "sudo cp $backup_path $WPA_path"           # Switchs back to the original setting under Privilege Mode
    sudo wpa_cli -i $interface reconfigure                                
  fi
  echo "New WiFi Configured!"
 }
 

# Main program to call all the functions
FindSSID
BackUpWiFI
AccessWiFi
CheckWiFiUp
