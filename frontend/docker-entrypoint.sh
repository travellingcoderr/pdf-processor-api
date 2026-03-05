#!/bin/sh
set -e
# Railway injects PORT; default to 80 for local Docker
PORT="${PORT:-80}"
sed "s/LISTEN_PORT/${PORT}/" /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g "daemon off;"
