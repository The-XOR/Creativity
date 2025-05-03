#/bin/bash
cd /home/pi/Creativity
if [ -e /home/pi/Creativity/dist ]; then
    rm -rf /home/pi/Creativity/dist
fi

python -m venv /home/pi/Creativity/creaenv
activate() {
. /home/pi/Creativity/creaenv/bin/activate
}
activate
echo "Compiling the program..."
pyinstaller --collect-all creativity.py --onedir creativity.py
cd /home/pi/Creativity/dist
ls
