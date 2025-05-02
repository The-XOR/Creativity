#/bin/bash
echo "Installing some modules..."
pushd /home/pi/Creativity
python -m venv /home/pi/Creativity/creaenv
activate() {
. /home/pi/Creativity/creaenv/bin/activate
}
activate
echo "Current python environment:"
which python

echo "Installing required modules"
pip install pyinstaller

popd