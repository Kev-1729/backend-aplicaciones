#!/bin/bash

# Script de utilidades Docker para RAG Backend

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# ========================================
# Comandos disponibles
# ========================================

build() {
    print_info "Building Docker image..."
    docker-compose build
    print_success "Image built successfully"
}

build_dev() {
    print_info "Building Docker image (dev mode)..."
    docker-compose -f docker-compose.dev.yml build
    print_success "Dev image built successfully"
}

up() {
    print_info "Starting containers..."
    docker-compose up -d
    print_success "Containers started"
    print_info "API available at: http://localhost:8000"
    print_info "Docs available at: http://localhost:8000/docs"
}

up_dev() {
    print_info "Starting containers (dev mode with hot-reload)..."
    docker-compose -f docker-compose.dev.yml up
}

down() {
    print_info "Stopping containers..."
    docker-compose down
    print_success "Containers stopped"
}

restart() {
    print_info "Restarting containers..."
    docker-compose restart
    print_success "Containers restarted"
}

logs() {
    print_info "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f backend
}

logs_dev() {
    print_info "Showing dev logs (Ctrl+C to exit)..."
    docker-compose -f docker-compose.dev.yml logs -f backend-dev
}

shell() {
    print_info "Opening shell in container..."
    docker-compose exec backend /bin/bash
}

shell_dev() {
    print_info "Opening shell in dev container..."
    docker-compose -f docker-compose.dev.yml exec backend-dev /bin/bash
}

ps() {
    print_info "Container status:"
    docker-compose ps
}

clean() {
    print_info "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup complete"
}

rebuild() {
    print_info "Rebuilding from scratch..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    print_success "Rebuild complete"
}

health() {
    print_info "Checking health status..."
    curl -f http://localhost:8000/health && print_success "Service is healthy" || print_error "Service is unhealthy"
}

test() {
    print_info "Running tests in container..."
    docker-compose exec backend pytest
}

# ========================================
# Menú de ayuda
# ========================================

show_help() {
    cat << EOF
🐳 Docker Utility Script for RAG Backend

Usage: ./docker.sh [command]

Production Commands:
  build         Build Docker image
  up            Start containers in background
  down          Stop containers
  restart       Restart containers
  logs          View container logs
  ps            Show container status
  shell         Open bash shell in container
  health        Check service health

Development Commands:
  build-dev     Build Docker image (dev mode)
  up-dev        Start containers with hot-reload
  logs-dev      View dev container logs
  shell-dev     Open bash shell in dev container

Maintenance Commands:
  clean         Remove containers and clean up
  rebuild       Rebuild from scratch (no cache)
  test          Run tests in container

Examples:
  ./docker.sh build         # Build production image
  ./docker.sh up            # Start in production mode
  ./docker.sh up-dev        # Start in dev mode with hot-reload
  ./docker.sh logs          # View logs
  ./docker.sh shell         # Open shell in container

EOF
}

# ========================================
# Main script
# ========================================

case "$1" in
    build)
        build
        ;;
    build-dev)
        build_dev
        ;;
    up)
        up
        ;;
    up-dev)
        up_dev
        ;;
    down)
        down
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    logs-dev)
        logs_dev
        ;;
    shell)
        shell
        ;;
    shell-dev)
        shell_dev
        ;;
    ps)
        ps
        ;;
    clean)
        clean
        ;;
    rebuild)
        rebuild
        ;;
    health)
        health
        ;;
    test)
        test
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
