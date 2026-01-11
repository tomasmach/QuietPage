#!/usr/bin/env bash
#
# QuietPage Deployment Script
# Zero-downtime deployment with automatic rollback
#
# Usage:
#   ./deploy.sh [OPTIONS]
#
# Options:
#   --branch <name>     Deploy from specific branch (default: main)
#   --skip-backup       Skip pre-deployment backup
#   --no-rollback       Don't rollback automatically on failure
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
DEPLOY_START_TIME=$(date +%s)

# Flags
TARGET_BRANCH="main"
SKIP_BACKUP=false
NO_ROLLBACK=false
DRY_RUN=false

# State variables
PREVIOUS_COMMIT=""
BACKUP_CREATED=false
DEPLOYMENT_FAILED=false

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
        --branch)
            TARGET_BRANCH="$2"
            shift 2
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --no-rollback)
            NO_ROLLBACK=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            head -n 18 "$0" | grep "^#" | sed 's/^# //' | sed 's/^#//'
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

# Cleanup function for rollback
cleanup_on_failure() {
    if [ "$DEPLOYMENT_FAILED" = true ] && [ "$NO_ROLLBACK" = false ]; then
        log_error "Deployment failed, initiating rollback..."
        rollback
        exit 10
    fi
}

# Set trap for cleanup
trap cleanup_on_failure EXIT

# Function to validate Git branch
validate_branch() {
    local branch="$1"

    # Sanitize branch name (allow only alphanumeric, dash, underscore, slash)
    if [[ ! "$branch" =~ ^[a-zA-Z0-9/_-]+$ ]]; then
        log_error "Invalid branch name: $branch"
        return 1
    fi

    return 0
}

# Function to perform pre-deployment backup
pre_deploy_backup() {
    if [ "$SKIP_BACKUP" = true ]; then
        log_info "Skipping pre-deployment backup (--skip-backup flag)"
        return 0
    fi

    log_info "Creating pre-deployment backup..."

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would create backup"
        return 0
    fi

    if "$SCRIPT_DIR/backup.sh" --pre-deploy; then
        BACKUP_CREATED=true
        log_success "Pre-deployment backup created"
        return 0
    else
        log_error "Backup failed"
        return 1
    fi
}

# Function to pull latest code
pull_code() {
    log_info "Pulling latest code from branch: $TARGET_BRANCH"

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would pull from $TARGET_BRANCH"
        return 0
    fi

    # Save current commit for potential rollback
    PREVIOUS_COMMIT=$(get_git_hash)
    log_info "Current commit: $PREVIOUS_COMMIT"

    # Fetch latest changes
    if ! git fetch origin; then
        log_error "Git fetch failed"
        return 1
    fi

    # Check if branch exists
    if ! git show-ref --verify --quiet "refs/remotes/origin/$TARGET_BRANCH"; then
        log_error "Branch $TARGET_BRANCH does not exist on remote"
        return 1
    fi

    # Pull changes
    if ! git pull origin "$TARGET_BRANCH"; then
        log_error "Git pull failed"
        return 1
    fi

    local new_commit
    new_commit=$(get_git_hash)
    log_success "Updated to commit: $new_commit"

    # Check if anything changed
    if [ "$PREVIOUS_COMMIT" = "$new_commit" ]; then
        log_info "No changes detected, but continuing deployment..."
    fi

    return 0
}

# Function to check for new env variables
check_env_changes() {
    log_info "Checking for new environment variables..."

    if [ ! -f .env.example ]; then
        log_info "No .env.example file, skipping check"
        return 0
    fi

    # Compare .env.example with .env
    local example_vars
    example_vars=$(grep -E "^[A-Z_]+=.*$" .env.example | cut -d= -f1 | sort)

    local env_vars
    env_vars=$(grep -E "^[A-Z_]+=.*$" .env | cut -d= -f1 | sort)

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
        log_warning "Please update your .env file and restart deployment"
    fi

    return 0
}

# Function to build new images
build_images() {
    log_info "Building new Docker images..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would build images"
        return 0
    fi

    # Tag images with git commit hash
    local git_hash
    git_hash=$(get_git_hash)

    if ! $dc_cmd -f "$COMPOSE_FILE" build; then
        log_error "Docker build failed"
        return 2
    fi

    # Tag the web image with git hash
    local web_image
    web_image=$($dc_cmd -f "$COMPOSE_FILE" images web -q 2>/dev/null | head -1)
    if [ -n "$web_image" ]; then
        docker tag "$web_image" "quietpage:$git_hash" 2>/dev/null || true
    fi

    log_success "Docker images built successfully"
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

    # First, check migrations with --check flag
    log_info "Checking for pending migrations..."
    if $dc_cmd -f "$COMPOSE_FILE" run --rm web python manage.py migrate --check 2>&1 | grep -q "missing migrations"; then
        log_info "Pending migrations detected"
    fi

    # Run migrations
    if ! $dc_cmd -f "$COMPOSE_FILE" run --rm web python manage.py migrate; then
        log_error "Database migrations failed"
        return 3
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

    if ! $dc_cmd -f "$COMPOSE_FILE" run --rm web python manage.py collectstatic --noinput --clear; then
        log_error "Static file collection failed"
        return 3
    fi

    log_success "Static files collected"
    return 0
}

# Function to restart services with zero downtime
restart_services() {
    log_info "Restarting services with zero downtime..."

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would restart services"
        return 0
    fi

    # Step 1: Restart Celery services first (they can have brief downtime)
    log_info "Restarting Celery beat..."
    $dc_cmd -f "$COMPOSE_FILE" restart celery_beat

    log_info "Restarting Celery worker (graceful shutdown)..."
    # Send SIGTERM for graceful shutdown
    docker kill --signal=SIGTERM "$(docker ps --filter name=celery_worker --format '{{.Names}}' | head -1)" 2>/dev/null || true
    sleep 2
    $dc_cmd -f "$COMPOSE_FILE" up -d celery_worker

    # Step 2: Restart Django web service (zero-downtime via docker-compose)
    log_info "Restarting web service..."
    $dc_cmd -f "$COMPOSE_FILE" up -d --no-deps --force-recreate web

    # Wait for new container to start
    sleep 5

    # Step 3: Reload Nginx configuration (no downtime)
    if docker ps --format '{{.Names}}' | grep -q "nginx"; then
        log_info "Reloading Nginx configuration..."
        local nginx_container
        nginx_container=$(docker ps --filter name=nginx --format '{{.Names}}' | head -1)
        docker exec "$nginx_container" nginx -t && docker exec "$nginx_container" nginx -s reload
        log_success "Nginx reloaded"
    fi

    log_success "Services restarted"
    return 0
}

# Function to verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would verify deployment"
        return 0
    fi

    log_info "Waiting 10 seconds for services to warm up..."
    sleep 10

    if ! wait_for_health "$(get_health_url)" 5 5; then
        log_error "Health check failed"
        return 4
    fi

    # Check Docker logs for errors
    log_info "Checking recent logs for errors..."
    local dc_cmd error_count
    dc_cmd=$(get_docker_compose_cmd)
    error_count=$($dc_cmd -f "$COMPOSE_FILE" logs --tail=50 web 2>&1 | grep -ci "error" || true)

    if [ "$error_count" -gt 5 ]; then
        log_warning "Found $error_count error messages in recent logs"
        log_warning "Review logs with: $dc_cmd -f $COMPOSE_FILE logs web"
    fi

    log_success "Deployment verification passed"
    return 0
}

# Function to rollback deployment
rollback() {
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would rollback to: $PREVIOUS_COMMIT"
        return 0
    fi

    if [ -z "$PREVIOUS_COMMIT" ]; then
        log_error "No previous commit to rollback to"
        return 1
    fi

    log_warning "Rolling back to commit: $PREVIOUS_COMMIT"

    if ! git reset --hard "$PREVIOUS_COMMIT"; then
        log_error "Git rollback failed"
        return 1
    fi

    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    log_info "Rebuilding previous version..."
    if ! $dc_cmd -f "$COMPOSE_FILE" build; then
        log_error "Rollback build failed"
        return 1
    fi

    log_info "Restarting services with previous version..."
    if ! $dc_cmd -f "$COMPOSE_FILE" up -d --force-recreate; then
        log_error "Rollback restart failed"
        return 1
    fi

    sleep 10
    if wait_for_health "$(get_health_url)" 5 5; then
        log_success "Rollback completed successfully"
        return 0
    else
        log_error "Rollback verification failed - manual intervention required"
        return 1
    fi
}

# Function to cleanup old Docker resources
post_deploy_cleanup() {
    log_info "Cleaning up old Docker resources..."

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would cleanup Docker resources"
        return 0
    fi

    cleanup_docker
    log_success "Cleanup completed"
    return 0
}

# Function to print deployment summary
print_summary() {
    local deploy_duration=$(($(date +%s) - DEPLOY_START_TIME))
    local minutes=$((deploy_duration / 60))
    local seconds=$((deploy_duration % 60))

    print_separator
    log_success "Deployment Completed Successfully!"
    print_separator

    echo ""
    echo "Deployment Summary:"
    echo "------------------"
    echo "Branch: $TARGET_BRANCH"
    echo "Commit: $(get_git_hash)"
    echo "Duration: ${minutes}m ${seconds}s"
    echo "Backup created: $BACKUP_CREATED"
    echo ""

    echo "Deployed Services:"
    echo "-----------------"
    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)
    $dc_cmd -f "$COMPOSE_FILE" ps 2>/dev/null | grep -E "(web|celery|nginx)" || true

    echo ""
    echo "Next Steps:"
    echo "----------"
    echo "1. Verify application in browser"
    echo "2. Check logs: $dc_cmd -f $COMPOSE_FILE logs -f web"
    echo "3. Monitor Celery: $dc_cmd -f $COMPOSE_FILE logs -f celery_worker"
    echo "4. Check health: curl http://localhost/api/health/"
    echo ""

    print_separator
}

# Main function
main() {
    print_separator
    log_info "QuietPage Deployment Script"
    log_info "Target branch: $TARGET_BRANCH"
    print_separator

    echo ""

    # Step 1: Validate branch
    log_info "Step 1/9: Validating branch name"
    if ! validate_branch "$TARGET_BRANCH"; then
        exit 1
    fi
    echo ""

    # Step 2: Pre-deployment backup
    log_info "Step 2/9: Creating pre-deployment backup"
    if ! pre_deploy_backup; then
        DEPLOYMENT_FAILED=true
        exit 1
    fi
    echo ""

    # Step 3: Pull code
    log_info "Step 3/9: Pulling latest code"
    if ! pull_code; then
        DEPLOYMENT_FAILED=true
        exit 1
    fi
    check_env_changes
    echo ""

    # Step 4: Build images
    log_info "Step 4/9: Building Docker images"
    if ! build_images; then
        DEPLOYMENT_FAILED=true
        exit 2
    fi
    echo ""

    # Step 5: Run migrations
    log_info "Step 5/9: Running database migrations"
    if ! run_migrations; then
        DEPLOYMENT_FAILED=true
        exit 3
    fi
    echo ""

    # Step 6: Collect static
    log_info "Step 6/9: Collecting static files"
    if ! collect_static; then
        DEPLOYMENT_FAILED=true
        exit 3
    fi
    echo ""

    # Step 7: Restart services
    log_info "Step 7/9: Restarting services"
    if ! restart_services; then
        DEPLOYMENT_FAILED=true
        exit 3
    fi
    echo ""

    # Step 8: Verify deployment
    log_info "Step 8/9: Verifying deployment"
    if ! verify_deployment; then
        DEPLOYMENT_FAILED=true
        exit 4
    fi
    echo ""

    # Step 9: Cleanup
    log_info "Step 9/9: Post-deployment cleanup"
    post_deploy_cleanup
    echo ""

    # Print summary
    print_summary

    # Deployment successful - disable rollback trap
    DEPLOYMENT_FAILED=false

    exit 0
}

# Run main function
main "$@"
