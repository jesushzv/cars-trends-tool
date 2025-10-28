#!/bin/bash
# PostgreSQL Setup Script
# Phase 17: PostgreSQL Migration
#
# This script creates the PostgreSQL database and user for the Cars Trends Tool

set -e  # Exit on error

echo "=========================================="
echo "PostgreSQL Setup for Cars Trends Tool"
echo "=========================================="
echo ""

# Configuration
DB_NAME="carstrends"
DB_USER="carstrends"
DB_PASSWORD="carstrends"  # Change this in production!

echo "📋 Configuration:"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed!"
    echo ""
    echo "Install PostgreSQL:"
    echo "  macOS: brew install postgresql@16"
    echo "  Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo ""
    exit 1
fi

echo "✅ PostgreSQL is installed"
echo ""

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "⚠️  PostgreSQL is not running. Starting it..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql@16 || brew services start postgresql
    else
        sudo systemctl start postgresql
    fi
    sleep 2
fi

echo "✅ PostgreSQL is running"
echo ""

# Create database and user
echo "🔧 Creating database and user..."
echo ""

# Use psql to create database and user
psql postgres << EOF
-- Drop existing database and user if they exist (for clean setup)
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create database
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connect to the database and grant schema privileges
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

-- Show results
\l $DB_NAME
EOF

echo ""
echo "=========================================="
echo "✅ PostgreSQL Setup Complete!"
echo "=========================================="
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "Connection string:"
echo "  postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "Next steps:"
echo "  1. Run: python migrate_to_postgres.py"
echo "  2. Run: python main.py"
echo "  3. Test: python -m pytest tests/"
echo ""

