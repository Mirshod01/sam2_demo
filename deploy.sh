#!/bin/bash

# SAM2 Demo Deployment Script for Vast.ai
# This script should be run on the Vast.ai server

set -e  # Exit on error

echo "Starting deployment..."

# Configuration
PROJECT_DIR="${PROJECT_DIR:-/workspace/sam2_demo}"
REPO_URL="git@github.com:Mirshod01/sam2_demo.git"
BRANCH="${BRANCH:-main}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo_warning "Project directory not found. Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
else
    echo_success "Project directory found"
    cd "$PROJECT_DIR"

    # Pull latest changes
    echo "Pulling latest changes from $BRANCH..."
    git fetch origin
    git reset --hard "origin/$BRANCH"
    echo_success "Code updated"
fi

# Install/Update Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade \
    flask \
    flask-cors \
    strawberry-graphql[flask] \
    opencv-python \
    numpy \
    pycocotools \
    dataclasses-json || echo_warning "Some dependencies failed to install"

echo_success "Python dependencies updated"

# Install/Update Node dependencies and rebuild frontend
if [ -d "demo/frontend" ]; then
    echo "Building frontend..."
    cd demo/frontend
    npm install
    npm run build
    echo_success "Frontend built successfully"
    cd "$PROJECT_DIR"
fi

# Restart services
echo "Restarting services..."

# Option 1: Using systemd (if configured)
if systemctl list-units --full -all | grep -Fq 'sam2-backend.service'; then
    sudo systemctl restart sam2-backend
    echo_success "Backend service restarted (systemd)"
fi

# Option 2: Using PM2 (if configured)
if command -v pm2 &> /dev/null; then
    pm2 restart sam2-backend 2>/dev/null || pm2 start demo/backend/server/app.py --name sam2-backend --interpreter python3
    echo_success "Backend service restarted (pm2)"
fi

# Option 3: Using Docker Compose
if [ -f "docker-compose.yml" ]; then
    docker-compose down
    docker-compose up -d --build
    echo_success "Docker containers restarted"
fi

echo_success "Deployment completed successfully!"
echo ""
echo "Access your application at:"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
