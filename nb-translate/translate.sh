#!/bin/bash
# This script will prepare NetBox to run after the code has been upgraded to
# its most recent release.

cd "$(dirname "$0")"

if [ -n "$1" ]
then
  echo
  echo "Hello, It\`s translater 8\)"
  echo "Your argumet is - $1."
  echo "Now, i don\`t need any arguments, please try again without arguments and from the Netbox root folder"
  echo
else
  COMMAND="rm -R netbox_old"
  echo "REMOVE netbox_old is exist..."
  eval $COMMAND || {
    echo "--------------------------------------------------------------------"
    echo "netbox_old is not exist!"
    echo "--------------------------------------------------------------------"
    }
#  read -p "Ok! Press any key to continue ..."
  COMMAND="cp -R netbox netbox_old"
  echo "Copy to netbox_old..."
  eval $COMMAND || {
    echo "--------------------------------------------------------------------"
    echo "ERROR BACKUP"
    echo "--------------------------------------------------------------------"
    exit 1
    }
#  read -p "DONE! Press any key to continue ..."
  COMMAND="/usr/bin/python3 ./translate.py"
  echo "Start translating..."
    eval $COMMAND || {
    echo "--------------------------------------------------------------------"
    echo "ERROR: Something went wrong"
    echo "--------------------------------------------------------------------"
    exit 1
    }
#  read -p "DONE! Press any key to continue ..."
  COMMAND="mv netbox-translated/netbox-translated netbox-translated/netbox"
  echo "Renaming netbox translate..."
    eval $COMMAND || {
    echo "--------------------------------------------------------------------"
    echo "ERROR: Something went wrong"
    echo "--------------------------------------------------------------------"
    exit 1
    }
#  read -p "DONE! Press any key to continue ..."
  COMMAND="cp -r ./netbox-translated/* netbox"
  echo "Copy to netbox netbox-translate..."
  eval $COMMAND || {
    echo "--------------------------------------------------------------------"
    echo "ERROR COPY"
    echo "--------------------------------------------------------------------"
    exit 1
    }
#  read -p "DONE! Press any key to continue ..."
  COMMAND="rm -R netbox-translated"
	echo "Remove netbox-translate..."
  eval $COMMAND || {
    echo "--------------------------------------------------------------------"
    echo "ERROR COPY"
    echo "--------------------------------------------------------------------"
    exit 1
    }
  echo 
  echo "Перевод успешно выполнен!"
fi
