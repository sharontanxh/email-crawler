#!/bin/bash

brew install postgresql
initdb /usr/local/var/postgres
brew services start postgresql

# you can use psql cli to see what databases exist on your local server
# psql postgres 
# \l
