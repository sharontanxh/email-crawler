#!/bin/bash

brew install postgresql
initdb /usr/local/var/postgres@14
brew services start postgresql
while ! pg_isready; do
    echo "Waiting for PostgreSQL to start..."
    sleep 1
done
psql -U $(whoami) -f /src/Sql/SwiftlyDBSetup.pgsql
# you can use psql cli to see what databases exist on your local server
# psql postgres 
# \l
