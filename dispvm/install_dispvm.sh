#!/bin/sh

mkdir -p ~/.mozilla/native-messaging-hosts
cp "`dirname $0`/native-messaging-host/quboid_native_messaging_host.json" ~/.mozilla/native-messaging-hosts/
