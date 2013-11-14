#!/bin/bash
GAMEPATH="/home/$USER/.steam/steam/SteamApps/common/Europa Universalis IV" 
MODPATH="/home/$USER/dev/MEIOUandTaxes" 
IFS=$'\n'
FILES=`diff -qr "$GAMEPATH" "$MODPATH" | grep "Only in $GAMEPATH" | sed -e "s%Only in $GAMEPATH%%g" -e 's/: /\//g' -e 's/^[ \t]*//'`
for file in $FILES
do
  ln -sf "$GAMEPATH/$file" "$MODPATH/$file"
  echo "$file"
done

#to undo:
#find "$MODPATH" -type l -exec rm {} \;
