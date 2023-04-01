#!/bin/sh

echo "Waiting for PostgreSQL..."

while ! nc -z web-db 5432; do
    echo "PostgreSQL is starting up..."
    sleep 0.1
done

echo "PostreSQL started"

exec "$@"