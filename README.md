# Creativity

Un concetto warholiano di progetto, che e' un modo alternativo e socialmente accettabile di:
"Hai rubacchiato pezzi qu e la' per assemblare una cosa non tua".
La cosa finirebbe qui, se non fossi consapevole che tra una quindicina di giorni non mi ricordero'
piu' come assemblare il tutto, e allora eccomi qui a scrivere.

Capitolo 1 - Premessa
Ben oltre il mezzo del cammin di nostra via, mi ritrovai a pensare ad un tool per sbloccare -laddove necessario-
quella creativita' che ormai latita. E allora e' nato sto coso, che appunto -all'apice della creativita'-
e' stato chiamato "Creativity".

Capitolo 2 - Lista componenti
   n.1 Raspberrypi Zero W (quello avevo, quello ho utilizzato....)
   n.1 led RGB
   n.1 pulsante
   n.1 display RGB 160x128 1.77" ST7735. Io ho utilizzato "AZDelivery 1.77 pollici SPI TFT Display 128x160
       Pixel ST7735 2.7V - 3.3V compatibile con Arduino e Raspberry Pi" https://www.amazon.it/dp/B078JBBPXK
   n.1 MAX7219 Modulo a matrice di punti 32x8 Moduli display a LED 4 in 1 con cavi a 5 pin per Arduino 
       Raspberry Pi https://it.aliexpress.com/item/1005008005112441.html
   n.3 resistenze da 500 ohm 

Capitolo 3 - Installazione
Preparare una scheda SD con Raspberrypi OS Lite, all'inizio servira' anche una buona dose di connettivita'
con l'internet, quindi vedete un po voi.
## OCIO !
Tutto l'ambaradan necessita che L'UTENTE ATTUALE SI CHIAMI 'pi'
Se si usa un altro nome utente, e' necessario aggiornare gli script utilizzando la cartella
/home/<nome utente> corretta
## ----

Una volta cucinata atque correttamente montata la SD, cominciare la lunga preparazione con
```
git clone https://github.com/The-XOR/Creativity.git
cd Creativity/Installation
./install.sh
```
Una volta terminato lo script e nel beneaugurato caso che non siano avvenuti errori, riavviando il raspberry
dovrebbe gia' partire il programma. 

# HIC SUNT LEONES
Capitolo 4 - Ottimizzazione

Se siete anche voi dei barboni come me, avrete utilizzato un device a bassissimo impatto economico, tipo raspberrypi zero. Nel mio caso, un'attesa di piu' di un minuto per aspettare un qualsiasi output era decisamente eccessiva, quindi ho colto l'occasione per entrare nell'insidioso mondo del bare (metal)!
La creazione di un kernel ad-hoc per questo progetto prevede piu' fasi.

```
cd Creativity/Compiling
./install-dependencies.sh
./compile.sh
```
Questo produrra' nella cartella Creativity/dist una versione (meta)compilata del programma e di tutte le librerie necessarie. 

2) Copiare tutto il contenuto di Creativity/dist su un PC perche' il contenuto ci servira' dopo per la SD "ottimizzata".

3) Segno della croce, segni apotropaici a piecere, alcol a fiumi e vai di Buildroot!

Capitolo 5 - L'inferno in terra: buildroot.

1) OBBLIGATORIAMENTE all'interno (se non volete diventar passi) di una distro Debian (io vi ho avvertito, poi fate voi...) scaricare buildroot:
```
git clone https://gitlab.com/buildroot.org/buildroot.git
cd buildroot
```

2) Elenco configurazioni disponibili:
```
make list-defconfigs | grep raspberrypi 
```
Bisogna utilizzare quella del proprio apparato. Nel caso di un raspberrypi Zero:
```
make raspberrypi0w_defconfig
make menuconfig
```

###Recipe:
In the Buildroot menuconfig, navigate to:
"Kernel" → "Kernel configuration"
Select "Using an in-tree defconfig file"
"Defconfig name", enter "bcm2835" (this is the default for Raspberry Pi)
Make sure "Kernel binary format" is set to "zImage"
"Target packages" → "Libraries" → "Compression and decompression"
"Target packages" → "Text editors and vievers" → "nano"
Find "zlib" and enable it (mark with [*])

SAVE + EXIT

```
make linux-menuconfig
```
In the kernel configuration menu, navigate to:
"Device Drivers" → "SPI support"
Enable "BCM2835 SPI controller" (marked with [*])
Enable "BCM2835 SPI auxiliary controller" (marked with [*])
"Device Drivers" → "GPIO Support"
Enable "BCM2835 GPIO support" (marked with [*])

SAVE + EXIT

```
make
```
Questo e' il momento delle preghiere, con una buona bottiglia di Padre Peppe.
Se le preghiere hanno avuto effetto, cucinare una nuova SD card col contenuto che locasi in
buildroot/output/images/sdcard.img

Capitolo 5 - Ci siamo quasi
La SD card e' *quasi* pronta. Va inserita in un PC per le ultime preparazioni; tutti i file da copiare sono dentro la cartella Buildroot della repository.
1) Nella piccola partizione di boot (circa 32 MB), aggiungere al contenuto del file config.txt la voce:
```
dtparam=spi=on
```

2) Nella partizione principale:
```
cd etc
mkdir modules-load.d
cd modules-load.d
```
copiare dentro questa cartella il file spi.conf

```
cd etc
cd init.d
```
copiare dentro questa cartella i file S45spi e S99creativity

```
chmod +x S45spi
chmod +x S99creativity
rm S01syslogd S02klogd S40network
```

3) Nella cartella /root della partizione principale, e' ora di copiare il programma & affini:
- copiare il file logo.jpg
- copiare le cartelle Oblique e Tarot
- copire il contenuto salvato del programma compilato alcuni (parecchi) step piu' sopra

4) Aprire una bottiglia di ottimo rum e festeggiare, svuotandola. Abbiamo finito.

# Funzionamento
Ad ogni pressione del tasto ci si alterna tra la visualizzazione del logo e di una splendida animazione
(per non essere influenzati da fattori esterni, per seguire la propria via interiore...)

 - e -

tra la visualizzazione di una frase su cui meditare e di un Arcano Taroccato, che male non fa.

Tenendo premuto il pulsante almeno di 2 secondi ci si alterna tra queste due modalita' e a gradire si cambia
anche mazzo di Tarocchi.

Infine, resistento col pulsante premuto per 5 secondi si spegne tutto l'ambaradan.
Enough said, come cantavano i Devo...
