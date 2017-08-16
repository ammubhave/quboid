#!/bin/sh

# Install Devilspie2
sudo dnf install devilspie2
mkdir -p "$HOME/.config/devilspie2"
cp "`dirname $0`/devilspie2/quboid.lua" "$HOME/.config/devilspie2"
mkdir -p "$HOME/.config/systemd/user"
cp "`dirname $0`/devilspie2/devilspie2.service" "$HOME/.config/systemd/user"


