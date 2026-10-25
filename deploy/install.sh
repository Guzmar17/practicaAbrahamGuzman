#!/usr/bin/env bash
# On the VM, as root (push.sh runs it): next/ becomes app/, built and restarted.
set -euo pipefail

HOST=${1:?host}
COMMIT=${2:-unknown}
ROOT=/srv/ecb-microbiology
export UV_PYTHON_INSTALL_DIR=/opt/uv/python UV_CACHE_DIR=/var/cache/uv

rm -rf "$ROOT/app" && mv "$ROOT/next" "$ROOT/app"
cd "$ROOT/app"
uv sync --frozen --no-dev
uv run --frozen --no-dev oxid build app --out www
echo "$COMMIT" > www/commit.txt
chown -R ecb:ecb "$ROOT/app"
chmod -R a+rX /opt/uv

install -m 644 deploy/ecb-microbiology.service /etc/systemd/system/ecb-microbiology.service
printf '%s {\n\treverse_proxy 127.0.0.1:8000\n}\n' "$HOST" > /etc/caddy/Caddyfile
systemctl daemon-reload
systemctl enable ecb-microbiology >/dev/null 2>&1
systemctl restart ecb-microbiology
systemctl reload caddy || systemctl restart caddy

for _ in $(seq 30); do
  curl -fsS http://127.0.0.1:8000/api/hospitals >/dev/null 2>&1 && { echo "ecb-microbiology $COMMIT is serving"; exit 0; }
  sleep 1
done
journalctl -u ecb-microbiology -n 40 --no-pager
exit 1
