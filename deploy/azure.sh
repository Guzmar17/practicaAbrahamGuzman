#!/usr/bin/env bash
# The free machine: a Standard_B1s with the free 64 GiB P6 disk, ports 80 and 443 open.
#
#   deploy/azure.sh ecb-<el-teu-nom>        # the DNS label: https://ecb-<nom>.francecentral.cloudapp.azure.com
#
# Free only on an Azure for Students (or free) subscription, one machine at a time; the public
# IP is billed from the first hour (cloud/azure/virtual-machine). Delete it all when marked:
#   az group delete -n rg-ecb --yes
set -euo pipefail

LABEL=${1:?"usage: deploy/azure.sh <dns-label>, e.g. ecb-laia-puig"}
GROUP=${GROUP:-rg-ecb}
LOCATION=${LOCATION:-francecentral}
HERE=$(cd "$(dirname "$0")" && pwd)

az account show --query "{name:name, offer:offer}" -o table
az group create -n "$GROUP" -l "$LOCATION" -o none
az vm create -g "$GROUP" -n vm-ecb \
  --image Ubuntu2404 --size Standard_B1s \
  --admin-username azureuser --generate-ssh-keys \
  --public-ip-sku Standard --public-ip-address-dns-name "$LABEL" \
  --os-disk-size-gb 64 --storage-sku Premium_LRS \
  --custom-data "$HERE/cloud-init.yaml" -o table
az vm open-port -g "$GROUP" -n vm-ecb --port 80 --priority 900 -o none
az vm open-port -g "$GROUP" -n vm-ecb --port 443 --priority 901 -o none

HOST="$LABEL.$LOCATION.cloudapp.azure.com"
echo "machine: $HOST"
echo "wait for cloud-init (2-4 min):  ssh azureuser@$HOST cloud-init status --wait"
echo "then:                            deploy/push.sh $HOST"
