#!/bin/bash

set -e
set +h

TARGET="/usr/lib/aryalinux-software-center"
REPO="/var/cache/aryalinux-software-center"
ICONLOCATION="/usr/share/pixmaps/"

if [ ! -x /usr/bin/flatpak ]; then echo "Flatpak not installed. Please install flatpak and continue." && exit; fi

sudo mkdir -pv $TARGET
sudo cp -v aryalinux-software-center $TARGET
sudo cp -vf *.py $TARGET
sudo cp -vf *.json $TARGET

sudo chmod a+x $TARGET/aryalinux-software-center
sudo mkdir -pv $REPO
sudo cp -rv repository/* $REPO
sudo mkdir -pv $ICONLOCATION
sudo cp -v asc.png $ICONLOCATION

sudo tee /usr/share/applications/asc.desktop<<EOF
[Desktop Entry]
Encoding=UTF-8
Name=AryaLinux Software Center
Comment=A front end for Flapak
GenericName=Software Center
Exec=sudo $TARGET/aryalinux-software-center
Terminal=false
Type=Application
Icon=$ICONLOCATION/asc.png
Categories=GNOME;System;
StartupNotify=true
EOF

sudo update-desktop-database
