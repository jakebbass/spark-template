#!/bin/bash

# Database migration script
set -e

echo "🔧 Running database migrations..."

# Check if we're running in Docker or local environment
if [ -n "$DOCKER_DB_HOST" ]; then
    DB_HOST="$DOCKER_DB_HOST"
else
    DB_HOST="localhost"
fi

POSTGRES_URL="postgresql://postgres:postgres@${DB_HOST}:5432/fantasy"

echo "📊 Connecting to database at ${DB_HOST}..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h "$DB_HOST" -p 5432 -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# Run migrations
echo "🚀 Applying schema migrations..."

# Apply all migration files in order
for migration in ../backend/app/db/schema_migrations/*.sql; do
    if [ -f "$migration" ]; then
        echo "📄 Applying $(basename "$migration")..."
        PGPASSWORD=postgres psql -h "$DB_HOST" -p 5432 -U postgres -d fantasy -f "$migration"
    fi
done

echo "✅ All migrations applied successfully!"