#!/bin/bash
IFS=$'\n'
FILES=`diff -qr /home/$USER/.steam/steam/SteamApps/common/Europa\ Universalis\ IV /home/calum/dev/MEIOUandTaxes | grep 'Only in /home/calum/.steam' | cut -c 73- | sed 's/: /\//g' | sed -e 's/^[ \t]*//'`
for file in $FILES
do
    ln -sf "/home/$USER/.steam/steam/SteamApps/common/Europa Universalis IV/$file" "/home/calum/dev/MEIOUandTaxes/$file"
    echo $file
done

#to undo:
#find /home/$USER/dev/MEIOUandTaxes -type l -exec rm {} \;
