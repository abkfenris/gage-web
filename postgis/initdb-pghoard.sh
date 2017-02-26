#!/bin/sh
set -e

echo "Configuring database to accept pghoard backups."

cat <<EOT >> /var/lib/postgresql/data/postgresql.conf
wal_level = archive
max_wal_senders = 4
archive_timeout = 300
EOT

#echo "host    REPLICATION     $PGHOARD_USER   $PGHOARD_HOSTNAME       md5" >> /var/lib/postgresql/data/pg_hba.conf

file='/var/lib/postgresql/data/pg_hba.conf'

# works to insert, but doesn't replace env variables
#sed -i 's/host.*0\/0.*trust/host replication $PGHOARD_USER $PGHOARD_HOSTNAME md5\n&/' $file

sed -i 's@host.*0/0.*md5@host replication '$PGHOARD_USER' '$PGHOARD_HOSTNAME' md5\n&@' $file

"${psql[@]}" --username postgres -v ON_ERROR_STOP=1 <<-EOSQL
  CREATE USER "$PGHOARD_USER" WITH PASSWORD '$PGHOARD_PASS' REPLICATION;
  SELECT pg_reload_conf();
EOSQL
