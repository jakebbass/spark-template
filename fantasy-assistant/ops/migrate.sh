#!/bin/sh
set -e
psql $POSTGRES_URL -f backend/app/db/schema_migrations/001_init.sql
