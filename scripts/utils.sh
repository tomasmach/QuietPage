#!/usr/bin/env bash
#
# QuietPage Deployment Utilities
# Shared functions for deployment scripts
#

set -euo pipefail

# Color codes for output
if [ -t 1 ]; then
    # Terminal supports colors
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    # Non-TTY environment (e.g., logs)
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "${LOG_FILE:-/dev/null}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1" >> "${LOG_FILE:-/dev/null}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $1" >> "${LOG_FILE:-/dev/null}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "${LOG_FILE:-/dev/null}"
}

# Check if Docker is installed and running
check_docker() {
    log_info "Checking Docker installation..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        return 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker."
        return 1
    fi

    # Check Docker version (min 20.10)
    local docker_version
    docker_version=$(docker version --format '{{.Server.Version}}' | cut -d. -f1,2)
    local min_version="20.10"

    if [ "$(printf '%s\n' "$min_version" "$docker_version" | sort -V | head -n1)" != "$min_version" ]; then
        log_error "Docker version $docker_version is too old. Minimum required: $min_version"
        return 1
    fi

    log_success "Docker $docker_version is installed and running"
    return 0
}

# Check if Docker Compose is installed
check_docker_compose() {
    log_info "Checking Docker Compose installation..."

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        return 1
    fi

    # Check Docker Compose version (min 2.0)
    local compose_version
    if command -v docker-compose &> /dev/null; then
        compose_version=$(docker-compose version --short | cut -d. -f1)
    else
        compose_version=$(docker compose version --short | cut -d. -f1)
    fi

    if [ "$compose_version" -lt 2 ]; then
        log_error "Docker Compose version $compose_version is too old. Minimum required: 2.0"
        return 1
    fi

    log_success "Docker Compose v$compose_version is installed"
    return 0
}

# Get the correct docker-compose command
get_docker_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    else
        echo "docker compose"
    fi
}

# Check if .env file exists and is valid
check_env_file() {
    log_info "Checking .env file..."

    if [ ! -f .env ]; then
        log_error ".env file not found. Please create one from .env.example"
        return 1
    fi

    # Source .env file
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a

    log_success ".env file found"
    return 0
}

# Validate required environment variables
validate_env_vars() {
    local required_vars=("$@")
    local missing_vars=()

    log_info "Validating environment variables..."

    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            log_error "  - $var"
        done
        return 1
    fi

    log_success "All required environment variables are set"
    return 0
}

# Wait for health endpoint to respond
wait_for_health() {
    local url="${1:-http://localhost:8000/api/health/}"
    local max_attempts="${2:-30}"
    local wait_seconds="${3:-5}"
    local attempt=1

    log_info "Waiting for health check at $url (max ${max_attempts} attempts)..."

    while [ $attempt -le "$max_attempts" ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            log_success "Health check passed!"
            return 0
        fi

        log_info "Attempt $attempt/$max_attempts failed, waiting ${wait_seconds}s..."
        sleep "$wait_seconds"
        ((attempt++))
    done

    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Wait for Docker service to be healthy
wait_for_service() {
    local service="$1"
    local max_attempts="${2:-30}"
    local wait_seconds="${3:-2}"
    local attempt=1

    log_info "Waiting for service '$service' to be healthy..."

    while [ $attempt -le "$max_attempts" ]; do
        local health_status
        health_status=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "unknown")

        if [ "$health_status" = "healthy" ]; then
            log_success "Service '$service' is healthy"
            return 0
        fi

        log_info "Service status: $health_status (attempt $attempt/$max_attempts)"
        sleep "$wait_seconds"
        ((attempt++))
    done

    log_error "Service '$service' did not become healthy after $max_attempts attempts"
    return 1
}

# Check disk space
check_disk_space() {
    local min_gb="${1:-10}"
    local path="${2:-.}"

    log_info "Checking available disk space..."

    local available_kb
    available_kb=$(df -k "$path" | tail -1 | awk '{print $4}')
    local available_gb=$((available_kb / 1024 / 1024))

    if [ "$available_gb" -lt "$min_gb" ]; then
        log_error "Insufficient disk space: ${available_gb}GB available, ${min_gb}GB required"
        return 1
    fi

    log_success "Disk space OK: ${available_gb}GB available"
    return 0
}

# Cleanup Docker resources
cleanup_docker() {
    log_info "Cleaning up Docker resources..."

    # Remove unused images
    docker image prune -f > /dev/null 2>&1 || true

    # Remove unused containers
    docker container prune -f > /dev/null 2>&1 || true

    log_success "Docker cleanup completed"
}

# Get current git commit hash
get_git_hash() {
    git rev-parse --short HEAD 2>/dev/null || echo "unknown"
}

# Get current git branch
get_git_branch() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"
}

# Calculate SHA256 checksum of a file
get_checksum() {
    local file="$1"

    if [ ! -f "$file" ]; then
        echo "error: file not found"
        return 1
    fi

    if command -v sha256sum &> /dev/null; then
        sha256sum "$file" | awk '{print $1}'
    elif command -v shasum &> /dev/null; then
        shasum -a 256 "$file" | awk '{print $1}'
    else
        echo "error: no checksum tool available"
        return 1
    fi
}

# Format bytes to human-readable size
format_size() {
    local bytes="$1"

    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes}B"
    elif [ "$bytes" -lt $((1024 * 1024)) ]; then
        echo "$((bytes / 1024))KB"
    elif [ "$bytes" -lt $((1024 * 1024 * 1024)) ]; then
        echo "$((bytes / 1024 / 1024))MB"
    else
        echo "$((bytes / 1024 / 1024 / 1024))GB"
    fi
}

# Create timestamped backup filename
get_backup_timestamp() {
    date '+%Y-%m-%d_%H-%M-%S'
}

# Check if running as root
check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root is not recommended for deployment scripts"
        read -rp "Continue anyway? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "Aborted by user"
            exit 0
        fi
    fi
}

# Print separator line
print_separator() {
    echo "========================================================================"
}

# Export functions for use in other scripts
export -f log_info log_success log_warning log_error
export -f check_docker check_docker_compose get_docker_compose_cmd
export -f check_env_file validate_env_vars
export -f wait_for_health wait_for_service
export -f check_disk_space cleanup_docker
export -f get_git_hash get_git_branch get_checksum
export -f format_size get_backup_timestamp
export -f check_not_root print_separator
