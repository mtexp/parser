#!/bin/bash
GAMEPATH="/home/$USER/.steam/steam/SteamApps/common/Europa Universalis IV" 
MODPATH="/home/$USER/dev/MEIOUandTaxes" 
IFS=$'\n'
FILES=`diff -qr "$GAMEPATH" "$MODPATH" | grep "Only in $GAMEPATH" | cut -c 73- | sed 's/: /\//g' | sed -e 's/^[ \t]*//'`
for file in $FILES
do
    ln -sf "$GAMEPATH/$file" "$MODPATH/$file"
    echo "$file"
done

#to undo:
#find "$MODPATH" -type l -exec rm {} \;
