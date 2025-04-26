#/bin/bash
echo "Removing systemd service"
sudo systemctl stop creativity.service
sudo systemctl disable creativity.service
sudo rm /etc/systemd/system/creativity.service
sudo systemctl  daemon-reload
