#!/usr/bin/env bash
# This commit to the VM: the files git knows (git archive, so nothing uncommitted or ignored goes),
# then install.sh there builds the page, syncs the environment and restarts the service.
#
#   deploy/push.sh ecb-<nom>.francecentral.cloudapp.azure.com
set -euo pipefail

HOST=${1:?"usage: deploy/push.sh <host>"}
git diff --quiet HEAD || echo "warning: uncommitted changes are not sent, only $(git rev-parse --short HEAD)"
git archive --format=tar HEAD | ssh "azureuser@$HOST" \
  'sudo rm -rf /srv/ecb-microbiology/next && sudo mkdir -p /srv/ecb-microbiology/next && sudo tar -x -C /srv/ecb-microbiology/next'
ssh "azureuser@$HOST" "sudo bash /srv/ecb-microbiology/next/deploy/install.sh $HOST $(git rev-parse --short HEAD)"
curl -fsS "https://$HOST/api/statistic" >/dev/null && echo "https://$HOST is up"
