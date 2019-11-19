#!/bin/bash

set -eux -o pipefail

tigervncserver -localhost no -xstartup /usr/bin/fluxbox
export DISPLAY=:1
dconf write /org/gnome/rhythmbox/plugins/active-plugins "['tray_icon']"
rhythmbox &> /root/.local/share/rhythmbox/plugins/rhythmbox-tray-icon/docker.log &
sleep 10