#!/bin/bash -e

mkdir /tmp/gear
cp -r ../ /tmp/gear

cd /tmp/gear
mkdir -p /tmp/gear/flywheel/v0

docker build -t flywheel/bids-pre-curate:$1 .

mv {manifest.json,run.py,putils} flywheel/v0

cd flywheel/v0

fw gear local

