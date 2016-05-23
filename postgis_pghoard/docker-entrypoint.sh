#!/bin/bash
set -e

if [ "${1:0:1}" = '-' ]; then
  set -- pghoard "$@"
fi
sh /pghoard.json.sh

exec "$@"
