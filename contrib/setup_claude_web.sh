#!/usr/bin/env bash
# Setup script for Claude Code web sessions.
# Starts PostgreSQL, Redis, backend server, and frontend dev server.
# Also installs dependencies and sets up the database schema.
set -euo pipefail

echo "=== Heroes of Talisman - Claude Web Setup ==="

# 1. Start PostgreSQL
echo "[1/6] Starting PostgreSQL..."
if pg_isready -q 2>/dev/null; then
    echo "  PostgreSQL already running."
else
    pg_ctlcluster 16 main start 2>/dev/null || true
    # Enable TCP connections on localhost
    PG_CONF="/etc/postgresql/16/main/postgresql.conf"
    PG_HBA="/etc/postgresql/16/main/pg_hba.conf"
    if grep -q "^#listen_addresses" "$PG_CONF" 2>/dev/null; then
        sed -i "s/^#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" "$PG_CONF"
    fi
    # Set trust auth for local development
    sed -i 's/scram-sha-256/trust/g' "$PG_HBA" 2>/dev/null || true
    sed -i 's/peer/trust/g' "$PG_HBA" 2>/dev/null || true
    pg_ctlcluster 16 main restart 2>/dev/null || true
    # Wait for PostgreSQL to be ready
    for i in {1..10}; do
        pg_isready -q 2>/dev/null && break
        sleep 1
    done
    echo "  PostgreSQL started."
fi

# Set postgres password
psql -U postgres -c "ALTER USER postgres PASSWORD 'postgres';" 2>/dev/null || true

# 2. Create database tables
echo "[2/6] Setting up database schema..."
psql -U postgres -c "
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    data JSONB,
    chat JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);" 2>/dev/null
echo "  Database schema ready."

# 3. Start Redis
echo "[3/6] Starting Redis..."
if redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "  Redis already running."
else
    redis-server --daemonize yes 2>/dev/null
    echo "  Redis started."
fi

# 4. Install dependencies
echo "[4/6] Installing dependencies..."
npm install --silent 2>/dev/null || npm install 2>&1 | tail -3
echo "  npm dependencies installed."

# 5. Start backend server
echo "[5/6] Starting backend server on port 8000..."
# Kill existing server if running
pkill -f "uvicorn server.main:app" 2>/dev/null || true
sleep 1
PYTHONPATH=. uv run uvicorn server.main:app --host 0.0.0.0 --port 8000 &>/tmp/server.log &
SERVER_PID=$!
echo "  Backend server started (PID: $SERVER_PID, log: /tmp/server.log)"

# 6. Start frontend dev server
echo "[6/6] Starting frontend dev server on port 5173..."
# Kill existing vite if running
pkill -f "vite.*5173" 2>/dev/null || true
sleep 1
npx vite --host 0.0.0.0 --port 5173 &>/tmp/vite.log &
VITE_PID=$!
echo "  Frontend dev server started (PID: $VITE_PID, log: /tmp/vite.log)"

# Wait for services to be ready
echo ""
echo "Waiting for services..."
for i in {1..10}; do
    if curl -sf http://localhost:8000/api/games/ >/dev/null 2>&1; then
        echo "  Backend ready."
        break
    fi
    sleep 1
done
for i in {1..10}; do
    if curl -sf http://localhost:5173 >/dev/null 2>&1; then
        echo "  Frontend ready."
        break
    fi
    sleep 1
done

echo ""
echo "=== Setup Complete ==="
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  Logs:     /tmp/server.log, /tmp/vite.log"
