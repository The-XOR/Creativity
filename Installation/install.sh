#/bin/bash
echo "Installing some modules..."
sudo apt update
sudo apt-get install python3-dev  libjpeg-dev zlib1g-dev
echo "Python environment construction time..."
pushd /home/pi/Creativity
python -m venv /home/pi/Creativity/creaenv
activate() {
. /home/pi/Creativity/creaenv/bin/activate
}
activate
echo "Current python environment:"
which python

echo "Installing required modules"
pip install pillow
pip install image
pip install RPi.GPIO
pip install luma.core
pip install luma.lcd
pip install luma.led_matrix

popd
echo "Installing systemd service"
sudo cp creativity.service /etc/systemd/system
sudo systemctl enable creativity.service
sudo systemctl start creativity.service
sudo systemctl daemon-reload
sudo systemctl status creativity.service
