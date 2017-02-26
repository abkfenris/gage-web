#!/bin/bash
set -e

if [ "${1:0:1}" = '-' ]; then
	set -- postgres "$@"
fi

if [ "$1" = 'postgres' ]; then
#  echo "Configuring database to accept pghoard backups."
#
#cat >> /var/lib/postgresql/data/postgresql.conf <<EOT
#  wal_level = archive
#  max_wal_senders = 4
#EOT

  #echo "host    REPLICATION     $PGHOARD_USER   $PGHOARD_HOSTNAME       md5" >> /var/lib/postgresql/data/pg_hba.conf

  #file='/var/lib/postgresql/data/pg_hba.conf'

  # works to insert, but doesn't replace env variables
  #sed -i 's/host.*0\/0.*trust/host replication $PGHOARD_USER $PGHOARD_HOSTNAME md5\n&/' $file

  #sed -i 's@host.*0/0.*md5@host replication '$PGHOARD_USER' '$PGHOARD_HOSTNAME' md5\n&@' $file

  #"${psql[@]}" --username postgres -v ON_ERROR_STOP=1 <<-EOSQL
  #  CREATE USER "$PGHOARD_USER" WITH PASSWORD '$PGHOARD_PASS' REPLICATION;
  #  SELECT pg_reload_conf();
  #EOSQL

  echo "Configuring pghoard.json"
cat <<-EOCONF > /pghoard.json
{
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

  RESTORE_DIR=/restore
  echo "Starting basebackup restore"
  pghoard_restore get-basebackup --target-dir "$RESTORE_DIR" --config /pghoard.json --overwrite --restore-to-master

  echo "Recreating pghoard.json for pghoard process"
cat <<-EOCONF > /pghoard.json
{
  "backup_location": "/metadata",
  "pg_xlog_directory": "$PGDATA/pg_xlog",
  "backup_sites": {
    "default": {
      "active": "false",
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
  mkdir /metadata
  chmod 700 /metadata
  chown -R postgres /metadata

  mkdir /home/postgres
  chown -R postgres /home/postgres

  echo "Starting pghoard in the background"
  gosu postgres pghoard --config /pghoard.json &

  echo "Copying data from restore directory to PGDATA"
  cp -R $RESTORE_DIR/* $PGDATA
	chmod 700 "$PGDATA"
	chown -R postgres "$PGDATA"

	chmod g+s /run/postgresql
	chown -R postgres /run/postgresql

	# look specifically for PG_VERSION, as it is expected in the DB dir
	if [ ! -s "$PGDATA/PG_VERSION" ]; then
		eval "gosu postgres initdb $POSTGRES_INITDB_ARGS"

		# check password first so we can output the warning before postgres
		# messes it up
		if [ "$POSTGRES_PASSWORD" ]; then
			pass="PASSWORD '$POSTGRES_PASSWORD'"
			authMethod=md5
		else
			# The - option suppresses leading tabs but *not* spaces. :)
			cat >&2 <<-'EOWARN'
				****************************************************
				WARNING: No password has been set for the database.
				         This will allow anyone with access to the
				         Postgres port to access your database. In
				         Docker's default configuration, this is
				         effectively any other container on the same
				         system.
				         Use "-e POSTGRES_PASSWORD=password" to set
				         it in "docker run".
				****************************************************
			EOWARN

			pass=
			authMethod=trust
		fi

		{ echo; echo "host all all 0.0.0.0/0 $authMethod"; } >> "$PGDATA/pg_hba.conf"

		# internal start of server in order to allow set-up using psql-client
		# does not listen on external TCP/IP and waits until start finishes
		gosu postgres pg_ctl -D "$PGDATA" \
			-o "-c listen_addresses='localhost'" \
			-w start

		: ${POSTGRES_USER:=postgres}
		: ${POSTGRES_DB:=$POSTGRES_USER}
		export POSTGRES_USER POSTGRES_DB

		psql=( psql -v ON_ERROR_STOP=1 )

		if [ "$POSTGRES_DB" != 'postgres' ]; then
			"${psql[@]}" --username postgres <<-EOSQL
				CREATE DATABASE "$POSTGRES_DB" ;
			EOSQL
			echo
		fi

		if [ "$POSTGRES_USER" = 'postgres' ]; then
			op='ALTER'
		else
			op='CREATE'
		fi
		"${psql[@]}" --username postgres <<-EOSQL
			$op USER "$POSTGRES_USER" WITH SUPERUSER $pass ;
		EOSQL
		echo

		psql+=( --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" )

		echo
		for f in /docker-entrypoint-initdb.d/*; do
			case "$f" in
				*.sh)     echo "$0: running $f"; . "$f" ;;
				*.sql)    echo "$0: running $f"; "${psql[@]}" < "$f"; echo ;;
				*.sql.gz) echo "$0: running $f"; gunzip -c "$f" | "${psql[@]}"; echo ;;
				*)        echo "$0: ignoring $f" ;;
			esac
			echo
		done

		gosu postgres pg_ctl -D "$PGDATA" -m fast -w stop

		echo
		echo 'PostgreSQL init process complete; ready for start up.'
		echo
	fi

	exec gosu postgres "$@"
fi

exec "$@"
