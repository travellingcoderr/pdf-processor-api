#!/bin/sh
set -e
# Railway injects PORT; default to 80 for local Docker
PORT="${PORT:-80}"
sed "s/LISTEN_PORT/${PORT}/" /etc/nginx/conf.d/default.conf.template > /tmp/default.conf
exec nginx -c /tmp/nginx.conf -g "daemon off;"
