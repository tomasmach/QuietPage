#!/usr/bin/env bash
#
# QuietPage Setup Script
# Initial server setup with environment validation
#
# Usage:
#   ./setup.sh [OPTIONS]
#
# Options:
#   --skip-superuser    Skip interactive superuser creation
#   --dry-run           Show what would be done without doing it
#   -h, --help          Show this help message
#

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source utility functions
# shellcheck source=utils.sh
source "$SCRIPT_DIR/utils.sh"

# Configuration
LOG_FILE="$PROJECT_ROOT/logs/deployment.log"
COMPOSE_FILE="docker-compose.prod.yml"

# Flags
SKIP_SUPERUSER=false
DRY_RUN=false

# Helper to get health endpoint URL based on running services
get_health_url() {
    if docker ps --format '{{.Names}}' | grep -q "nginx"; then
        echo "http://localhost/api/health/"
    else
        echo "http://localhost:8000/api/health/"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-superuser)
            SKIP_SUPERUSER=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            head -n 15 "$0" | grep "^#" | sed 's/^# //' | sed 's/^#//'
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Change to project root
cd "$PROJECT_ROOT"

# Ensure logs directory exists
mkdir -p logs

# Check if running as root (warn but allow)
check_not_root

# Function to validate .env variables
validate_production_env() {
    log_info "Validating production environment variables..."

    # Required variables
    local required_vars=(
        "SECRET_KEY"
        "FERNET_KEY_PRIMARY"
        "DB_NAME"
        "DB_USER"
        "DB_PASSWORD"
        "ALLOWED_HOSTS"
    )

    if ! validate_env_vars "${required_vars[@]}"; then
        return 2
    fi

    # Check DEBUG setting
    if [ "${DEBUG:-true}" = "true" ] || [ "${DEBUG:-True}" = "True" ]; then
        log_warning "DEBUG is set to True - this should be False in production!"
    fi

    # Warn about optional but recommended variables
    local optional_vars=(
        "EMAIL_HOST"
        "EMAIL_PORT"
        "EMAIL_HOST_USER"
        "EMAIL_HOST_PASSWORD"
        "SENTRY_DSN"
        "CSRF_TRUSTED_ORIGINS"
    )

    local missing_optional=()
    for var in "${optional_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_optional+=("$var")
        fi
    done

    if [ ${#missing_optional[@]} -gt 0 ]; then
        log_warning "Optional environment variables not set:"
        for var in "${missing_optional[@]}"; do
            log_warning "  - $var"
        done
        echo ""
    fi

    # Check ALLOWED_HOSTS format
    if [[ "${ALLOWED_HOSTS:-}" == *"localhost"* ]] || [[ "${ALLOWED_HOSTS:-}" == *"127.0.0.1"* ]]; then
        log_warning "ALLOWED_HOSTS contains localhost/127.0.0.1 - make sure to set production domains"
    fi

    log_success "Environment validation passed"
    return 0
}

# Function to check .env.example for new variables
check_env_example() {
    log_info "Checking for new environment variables..."

    if [ ! -f .env.example ]; then
        log_warning ".env.example not found, skipping check"
        return 0
    fi

    # Extract variable names from .env.example
    local example_vars
    example_vars=$(grep -E "^[A-Z_]+=.*$" .env.example | cut -d= -f1 | sort)

    # Extract variable names from .env
    local env_vars
    env_vars=$(grep -E "^[A-Z_]+=.*$" .env | cut -d= -f1 | sort)

    # Find variables in .env.example but not in .env
    local missing_vars=()
    while IFS= read -r var; do
        if ! echo "$env_vars" | grep -q "^${var}$"; then
            missing_vars+=("$var")
        fi
    done <<< "$example_vars"

    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_warning "New variables in .env.example not found in .env:"
        for var in "${missing_vars[@]}"; do
            log_warning "  - $var"
        done
        echo ""
        read -rp "Continue setup anyway? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "Setup aborted by user"
            exit 0
        fi
    else
        log_success "All variables from .env.example are present in .env"
    fi

    return 0
}

# Function to build Docker images
build_images() {
    log_info "Building Docker images..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would run: $dc_cmd -f $COMPOSE_FILE build --no-cache"
        return 0
    fi

    if ! $dc_cmd -f "$COMPOSE_FILE" build --no-cache; then
        log_error "Docker build failed"
        return 3
    fi

    log_success "Docker images built successfully"
    return 0
}

# Function to start database and Redis
start_core_services() {
    log_info "Starting core services (database and Redis)..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would start: db, redis"
        return 0
    fi

    if ! $dc_cmd -f "$COMPOSE_FILE" up -d db redis; then
        log_error "Failed to start core services"
        return 3
    fi

    # Wait for services to be healthy
    log_info "Waiting for database to be ready..."
    if ! wait_for_service "$(docker ps --filter name=db --format '{{.Names}}' | head -1)" 30 2; then
        log_error "Database did not become healthy"
        return 3
    fi

    log_info "Waiting for Redis to be ready..."
    if ! wait_for_service "$(docker ps --filter name=redis --format '{{.Names}}' | head -1)" 30 2; then
        log_error "Redis did not become healthy"
        return 3
    fi

    log_success "Core services are running and healthy"
    return 0
}

# Function to run migrations
run_migrations() {
    log_info "Running database migrations..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would run migrations"
        return 0
    fi

    if ! $dc_cmd -f "$COMPOSE_FILE" run --rm web python manage.py migrate; then
        log_error "Database migrations failed"
        return 4
    fi

    log_success "Database migrations completed"
    return 0
}

# Function to collect static files
collect_static() {
    log_info "Collecting static files..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would collect static files"
        return 0
    fi

    if ! $dc_cmd -f "$COMPOSE_FILE" run --rm web python manage.py collectstatic --noinput; then
        log_error "Static file collection failed"
        return 3
    fi

    log_success "Static files collected"
    return 0
}

# Function to create superuser
create_superuser() {
    if [ "$SKIP_SUPERUSER" = true ]; then
        log_info "Skipping superuser creation (--skip-superuser flag)"
        return 0
    fi

    log_info "Creating superuser..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would create superuser interactively"
        return 0
    fi

    # Check if superuser already exists
    local superuser_count
    superuser_count=$($dc_cmd -f "$COMPOSE_FILE" run --rm web python manage.py shell -c "from apps.accounts.models import User; print(User.objects.filter(is_superuser=True).count())" 2>/dev/null | tail -1)

    if [ "${superuser_count:-0}" -gt 0 ]; then
        log_info "Superuser already exists, skipping creation"
        return 0
    fi

    echo ""
    log_info "No superuser found. Creating superuser interactively..."
    if ! $dc_cmd -f "$COMPOSE_FILE" run --rm web python manage.py createsuperuser; then
        log_warning "Superuser creation cancelled or failed"
        return 0
    fi

    log_success "Superuser created"
    return 0
}

# Function to start all services
start_all_services() {
    log_info "Starting all services..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would start all services"
        return 0
    fi

    if ! $dc_cmd -f "$COMPOSE_FILE" up -d; then
        log_error "Failed to start all services"
        return 3
    fi

    log_success "All services started"
    return 0
}

# Function to verify Celery setup
verify_celery() {
    log_info "Verifying Celery setup..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would verify Celery"
        return 0
    fi

    # Check if Celery worker is running
    if ! docker ps --format '{{.Names}}' | grep -q "celery_worker"; then
        log_error "Celery worker is not running"
        return 5
    fi

    # Check if Celery beat is running
    if ! docker ps --format '{{.Names}}' | grep -q "celery_beat"; then
        log_error "Celery beat is not running"
        return 5
    fi

    log_success "Celery worker and beat are running"

    # Note: Using file-based scheduler (CELERY_BEAT_SCHEDULE in settings)
    log_info "Scheduled tasks are configured in config/settings/base.py (CELERY_BEAT_SCHEDULE)"

    return 0
}

# Function to check all containers
check_containers() {
    log_info "Checking Docker containers..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would check containers"
        return 0
    fi

    echo ""
    $dc_cmd -f "$COMPOSE_FILE" ps

    # Check if any container is not running
    local not_running
    not_running=$($dc_cmd -f "$COMPOSE_FILE" ps --filter "status=exited" --format "{{.Service}}" 2>/dev/null)

    if [ -n "$not_running" ]; then
        log_error "Some containers are not running: $not_running"
        return 5
    fi

    log_success "All containers are running"
    return 0
}

# Function to verify health endpoint
verify_health() {
    log_info "Verifying health endpoint..."

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would check health endpoint"
        return 0
    fi

    if ! wait_for_health "$(get_health_url)" 10 3; then
        log_error "Health check failed"
        return 5
    fi
    return 0
}

# Function to print final summary
print_summary() {
    print_separator
    log_success "QuietPage Setup Complete!"
    print_separator

    local dc_cmd base_url
    dc_cmd=$(get_docker_compose_cmd)

    # Determine base URL based on nginx availability
    if docker ps --format '{{.Names}}' | grep -q "nginx"; then
        base_url="http://localhost"
    else
        base_url="http://localhost:8000"
    fi

    echo ""
    echo "Services Status:"
    echo "---------------"
    $dc_cmd -f "$COMPOSE_FILE" ps 2>/dev/null || true

    cat <<EOF

Next Steps:
----------
1. Access the application:
   - Frontend: $base_url
   - Admin: $base_url/admin/
   - API: $base_url/api/

2. View logs:
   $dc_cmd -f $COMPOSE_FILE logs -f [service]

3. Run tests:
   $dc_cmd -f $COMPOSE_FILE run --rm web pytest

4. Create backups:
   ./scripts/backup.sh

5. Deploy updates:
   ./scripts/deploy.sh

EOF
    print_separator
}

# Main function
main() {
    print_separator
    log_info "QuietPage Setup Script"
    log_info "Git: $(get_git_branch) @ $(get_git_hash)"
    print_separator

    echo ""

    # Step 1: Check Docker
    log_info "Step 1/10: Checking Docker installation"
    if ! check_docker; then
        exit 1
    fi
    if ! check_docker_compose; then
        exit 1
    fi
    echo ""

    # Step 2: Check disk space
    log_info "Step 2/10: Checking disk space"
    if ! check_disk_space 10; then
        log_warning "Less than 10GB available, but continuing anyway"
    fi
    echo ""

    # Step 3: Validate .env file
    log_info "Step 3/10: Validating environment configuration"
    if ! check_env_file; then
        exit 1
    fi
    if ! validate_production_env; then
        exit 2
    fi
    check_env_example
    echo ""

    # Step 4: Build images
    log_info "Step 4/10: Building Docker images"
    if ! build_images; then
        exit 3
    fi
    echo ""

    # Step 5: Start core services
    log_info "Step 5/10: Starting core services"
    if ! start_core_services; then
        exit 3
    fi
    echo ""

    # Step 6: Run migrations
    log_info "Step 6/10: Running database migrations"
    if ! run_migrations; then
        exit 4
    fi
    echo ""

    # Step 7: Collect static files
    log_info "Step 7/10: Collecting static files"
    if ! collect_static; then
        exit 3
    fi
    echo ""

    # Step 8: Create superuser
    log_info "Step 8/10: Setting up superuser"
    create_superuser
    echo ""

    # Step 9: Start all services
    log_info "Step 9/10: Starting all services"
    if ! start_all_services; then
        exit 3
    fi
    echo ""

    # Step 10: Verify setup
    log_info "Step 10/10: Verifying setup"
    if ! check_containers; then
        exit 5
    fi
    if ! verify_celery; then
        log_warning "Celery verification had issues, but continuing"
    fi
    if ! verify_health; then
        exit 5
    fi
    echo ""

    # Print summary
    print_summary

    exit 0
}

# Run main function
main "$@"
