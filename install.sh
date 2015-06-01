#!/bin/bash

DOWNLOADED=false
if [ "$(id -u)" != "0" ]; then
	echo "Sorry, you are not root."
	exit 1
fi

echo "This script will guide you to install the PythonMiniProbe"

echo "installing python-dev and build-essentials"
apt-get -y install python-dev build-essential 2>&1 >> /tmp/probe_install.log

case "$(python --version 2>&1)" in
    *" 2.7.9"*)
        echo "Correct python version!"
        ;;
    *" 3."*)
        echo "Correct python version!"
        ;;
    *)
        echo "Installing PIP!"
        apt-get -y install python-pip 2>&1 >> /tmp/probe_install.log
        ;;
esac

if [ ! -f ./README.md ]
    read -p "Use git to install the miniprobe (y|n)? " -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        git clone https://github.com/PaesslerAG/PythonMiniProbe.git /PythonMiniProbe
        cd /PythonMiniProbe
        DOWNLOADED=true
    else
        read -p "Use wget to install the miniprobe (y|n)? " -n 1 -r
        echo    # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            wget -O /tmp/probe.zip https://github.com/PaesslerAG/PythonMiniProbe/archive/master.zip
            unzip /tmp/probe.zip -d /tmp
            mv /tmp/PythonMiniProbe-master /PythonMiniProbe
            cd /PythonMiniProbe
            DOWNLOADED=true
        fi
    fi
else
    DOWNLOADED=true
fi

if [ "$DOWNLOADED" = true ]
then
    echo "Starting to install the miniprobe and requirements"
    python setup.py install
    python setup.py configure
fi
