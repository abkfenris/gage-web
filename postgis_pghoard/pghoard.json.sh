#!/bin/sh
set -e

echo "Configuring pghoard.json"

cat <<EOCONF > /pghoard.json
{
  "backup_location": "./metadata",
  "backup_sites": {
    "default": {
      "active_backup_mode": "pg_receivexlog",
      "nodes": [
        {
          "host": "$PG_HOSTNAME",
          "password": "$PGHOARD_PASS",
          "port": "5432",
          "user": "$PGHOARD_USER"
        }
      ],
      "object_storage": $PGHOARD_OBJECT_STORAGE
    }
  }
}
EOCONF
