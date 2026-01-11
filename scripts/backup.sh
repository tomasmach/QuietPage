#!/usr/bin/env bash
#
# QuietPage Backup Script
# Creates backups of PostgreSQL database and media files with rotation
#
# Usage:
#   ./backup.sh [OPTIONS]
#
# Options:
#   --pre-deploy        Tag backup as pre-deployment
#   --db-only           Backup database only
#   --media-only        Backup media files only
#   --list              List all existing backups
#   --cleanup           Only perform backup rotation (no new backup)
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
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
MIN_BACKUPS_TO_KEEP=3
LOG_FILE="$PROJECT_ROOT/logs/deployment.log"

# Flags
PRE_DEPLOY=false
DB_ONLY=false
MEDIA_ONLY=false
LIST_ONLY=false
CLEANUP_ONLY=false
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --pre-deploy)
            PRE_DEPLOY=true
            shift
            ;;
        --db-only)
            DB_ONLY=true
            shift
            ;;
        --media-only)
            MEDIA_ONLY=true
            shift
            ;;
        --list)
            LIST_ONLY=true
            shift
            ;;
        --cleanup)
            CLEANUP_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            head -n 20 "$0" | grep "^#" | sed 's/^# //' | sed 's/^#//'
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

# Function to list all backups
list_backups() {
    print_separator
    log_info "Listing all backups in $BACKUP_DIR"
    print_separator

    if [ ! -d "$BACKUP_DIR" ]; then
        log_warning "Backup directory does not exist: $BACKUP_DIR"
        return 0
    fi

    local total_size=0
    local backup_count=0

    # Database backups
    echo ""
    echo "Database Backups:"
    echo "----------------"
    if compgen -G "$BACKUP_DIR/db_*.dump.gz" > /dev/null; then
        for backup in "$BACKUP_DIR"/db_*.dump.gz; do
            local size
            size=$(stat -f%z "$backup" 2>/dev/null || stat -c%s "$backup" 2>/dev/null)
            local age_days
            age_days=$(( ($(date +%s) - $(stat -f%m "$backup" 2>/dev/null || stat -c%Y "$backup" 2>/dev/null)) / 86400 ))
            echo "  $(basename "$backup") - $(format_size "$size") - ${age_days} days old"
            total_size=$((total_size + size))
            ((backup_count++))
        done
    else
        echo "  No database backups found"
    fi

    # Media backups
    echo ""
    echo "Media Backups:"
    echo "-------------"
    if compgen -G "$BACKUP_DIR/media_*.tar.gz" > /dev/null; then
        for backup in "$BACKUP_DIR"/media_*.tar.gz; do
            local size
            size=$(stat -f%z "$backup" 2>/dev/null || stat -c%s "$backup" 2>/dev/null)
            local age_days
            age_days=$(( ($(date +%s) - $(stat -f%m "$backup" 2>/dev/null || stat -c%Y "$backup" 2>/dev/null)) / 86400 ))
            echo "  $(basename "$backup") - $(format_size "$size") - ${age_days} days old"
            total_size=$((total_size + size))
            ((backup_count++))
        done
    else
        echo "  No media backups found"
    fi

    # Summary
    echo ""
    print_separator
    echo "Total: $backup_count backups, $(format_size "$total_size")"

    # Disk space
    local available_kb
    available_kb=$(df -k "$BACKUP_DIR" | tail -1 | awk '{print $4}')
    local available_gb=$((available_kb / 1024 / 1024))
    echo "Available disk space: ${available_gb}GB"

    if [ "$available_gb" -lt 5 ]; then
        log_warning "Low disk space! Less than 5GB available"
    fi
    print_separator
}

# Function to cleanup old backups
cleanup_backups() {
    log_info "Cleaning up backups older than $BACKUP_RETENTION_DAYS days..."

    if [ ! -d "$BACKUP_DIR" ]; then
        log_info "No backup directory to clean"
        return 0
    fi

    local cutoff_timestamp=$(($(date +%s) - (BACKUP_RETENTION_DAYS * 86400)))
    local deleted_count=0

    # Find all backup files
    local all_backups=()
    if compgen -G "$BACKUP_DIR/db_*.dump.gz" > /dev/null; then
        all_backups+=("$BACKUP_DIR"/db_*.dump.gz)
    fi
    if compgen -G "$BACKUP_DIR/media_*.tar.gz" > /dev/null; then
        all_backups+=("$BACKUP_DIR"/media_*.tar.gz)
    fi
    if compgen -G "$BACKUP_DIR/db_*.meta.json" > /dev/null; then
        all_backups+=("$BACKUP_DIR"/db_*.meta.json)
    fi
    if compgen -G "$BACKUP_DIR/media_*.meta.json" > /dev/null; then
        all_backups+=("$BACKUP_DIR"/media_*.meta.json)
    fi

    # Sort backups by modification time (newest first)
    local sorted_backups=()
    if [ ${#all_backups[@]} -gt 0 ]; then
        IFS=$'\n' sorted_backups=($(ls -t "${all_backups[@]}" 2>/dev/null))
        unset IFS
    fi

    # Keep at least MIN_BACKUPS_TO_KEEP newest backups
    local kept_count=0
    for backup in "${sorted_backups[@]}"; do
        local file_time
        file_time=$(stat -f%m "$backup" 2>/dev/null || stat -c%Y "$backup" 2>/dev/null)

        if [ "$file_time" -lt "$cutoff_timestamp" ] && [ "$kept_count" -ge "$MIN_BACKUPS_TO_KEEP" ]; then
            if [ "$DRY_RUN" = true ]; then
                log_info "[DRY RUN] Would delete: $(basename "$backup")"
            else
                log_info "Deleting old backup: $(basename "$backup")"
                rm -f "$backup"
            fi
            ((deleted_count++))
        else
            ((kept_count++))
        fi
    done

    if [ "$deleted_count" -gt 0 ]; then
        log_success "Cleaned up $deleted_count old backup files"
    else
        log_info "No old backups to clean up"
    fi
}

# Function to backup PostgreSQL database
backup_database() {
    local timestamp="$1"
    local backup_file="$BACKUP_DIR/db_${timestamp}.dump"
    local compressed_file="${backup_file}.gz"
    local meta_file="$BACKUP_DIR/db_${timestamp}.meta.json"

    log_info "Starting database backup..."

    # Load environment variables
    if ! check_env_file; then
        return 2
    fi

    # Get docker-compose command
    local dc_cmd
    dc_cmd=$(get_docker_compose_cmd)

    # Check if db container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^quietpage.*db"; then
        log_error "Database container is not running"
        return 2
    fi

    # Get database container name
    local db_container
    db_container=$(docker ps --format '{{.Names}}' | grep "^quietpage.*db" | head -1)

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would backup database to: $compressed_file"
        return 0
    fi

    # Create pg_dump inside container
    log_info "Creating PostgreSQL dump..."
    if ! docker exec "$db_container" pg_dump -U "${DB_USER:-quietpage}" -d "${DB_NAME:-quietpage}" -F c -f /tmp/backup.dump; then
        log_error "pg_dump failed"
        return 2
    fi

    # Copy dump from container
    if ! docker cp "$db_container:/tmp/backup.dump" "$backup_file"; then
        log_error "Failed to copy backup from container"
        docker exec "$db_container" rm -f /tmp/backup.dump
        return 2
    fi

    # Cleanup temp file in container
    docker exec "$db_container" rm -f /tmp/backup.dump

    # Compress backup
    log_info "Compressing backup..."
    if ! gzip "$backup_file"; then
        log_error "Failed to compress backup"
        return 2
    fi

    # Verify compressed file
    if ! gzip -t "$compressed_file"; then
        log_error "Backup compression verification failed"
        return 2
    fi

    # Calculate checksum
    local checksum
    checksum=$(get_checksum "$compressed_file")

    # Get file size
    local file_size
    file_size=$(stat -f%z "$compressed_file" 2>/dev/null || stat -c%s "$compressed_file" 2>/dev/null)

    # Create metadata file
    cat > "$meta_file" <<EOF
{
  "type": "database",
  "timestamp": "$timestamp",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "size": $file_size,
  "size_human": "$(format_size "$file_size")",
  "checksum": "$checksum",
  "git_hash": "$(get_git_hash)",
  "git_branch": "$(get_git_branch)",
  "pre_deploy": $PRE_DEPLOY,
  "db_name": "${DB_NAME:-quietpage}",
  "db_user": "${DB_USER:-quietpage}"
}
EOF

    log_success "Database backup created: $(basename "$compressed_file") ($(format_size "$file_size"))"
    log_info "Checksum: $checksum"

    # Quick verification using pg_restore
    if command -v pg_restore &> /dev/null; then
        if gunzip -c "$compressed_file" | pg_restore --list > /dev/null 2>&1; then
            log_success "Backup verification passed"
        else
            log_warning "Backup verification failed, but file was created"
        fi
    fi

    return 0
}

# Function to backup media files
backup_media() {
    local timestamp="$1"
    local backup_file="$BACKUP_DIR/media_${timestamp}.tar.gz"
    local meta_file="$BACKUP_DIR/media_${timestamp}.meta.json"

    log_info "Starting media backup..."

    if [ ! -d "$PROJECT_ROOT/media" ]; then
        log_warning "Media directory does not exist, skipping media backup"
        return 0
    fi

    # Count files in media directory
    local file_count
    file_count=$(find "$PROJECT_ROOT/media" -type f | wc -l | tr -d ' ')

    if [ "$file_count" -eq 0 ]; then
        log_info "Media directory is empty, skipping backup"
        return 0
    fi

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would backup $file_count media files to: $backup_file"
        return 0
    fi

    # Create tar.gz archive
    log_info "Archiving $file_count media files..."
    if ! tar -czf "$backup_file" -C "$PROJECT_ROOT" media/; then
        log_error "Failed to create media archive"
        return 3
    fi

    # Verify archive
    if ! tar -tzf "$backup_file" > /dev/null 2>&1; then
        log_error "Media archive verification failed"
        return 3
    fi

    # Calculate checksum
    local checksum
    checksum=$(get_checksum "$backup_file")

    # Get file size
    local file_size
    file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)

    # Create metadata file
    cat > "$meta_file" <<EOF
{
  "type": "media",
  "timestamp": "$timestamp",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "size": $file_size,
  "size_human": "$(format_size "$file_size")",
  "file_count": $file_count,
  "checksum": "$checksum",
  "git_hash": "$(get_git_hash)",
  "git_branch": "$(get_git_branch)",
  "pre_deploy": $PRE_DEPLOY
}
EOF

    log_success "Media backup created: $(basename "$backup_file") ($(format_size "$file_size"), $file_count files)"
    log_info "Checksum: $checksum"

    return 0
}

# Function to upload to S3 (optional)
upload_to_s3() {
    if [ -z "${S3_BACKUP_BUCKET:-}" ]; then
        log_info "S3_BACKUP_BUCKET not set, skipping remote backup"
        return 0
    fi

    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI not installed, skipping remote backup"
        return 0
    fi

    log_info "Uploading backups to S3 bucket: $S3_BACKUP_BUCKET"

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would upload to s3://$S3_BACKUP_BUCKET/quietpage/"
        return 0
    fi

    if aws s3 cp "$BACKUP_DIR/" "s3://$S3_BACKUP_BUCKET/quietpage/" --recursive --exclude "*" --include "*.dump.gz" --include "*.tar.gz" --include "*.meta.json"; then
        log_success "Backups uploaded to S3"
    else
        log_error "Failed to upload backups to S3"
        return 1
    fi

    return 0
}

# Main function
main() {
    print_separator
    log_info "QuietPage Backup Script"
    print_separator

    # Handle list-only mode
    if [ "$LIST_ONLY" = true ]; then
        list_backups
        exit 0
    fi

    # Check disk space (minimum 2GB required)
    if ! check_disk_space 2; then
        exit 4
    fi

    # Create backup directory
    if [ "$DRY_RUN" = false ]; then
        if ! mkdir -p "$BACKUP_DIR"; then
            log_error "Failed to create backup directory: $BACKUP_DIR"
            exit 1
        fi
        # Set restrictive permissions on backup directory
        chmod 700 "$BACKUP_DIR"
    fi

    # Handle cleanup-only mode
    if [ "$CLEANUP_ONLY" = true ]; then
        cleanup_backups
        exit 0
    fi

    # Generate timestamp for this backup run
    local timestamp
    timestamp=$(get_backup_timestamp)

    log_info "Backup timestamp: $timestamp"
    if [ "$PRE_DEPLOY" = true ]; then
        log_info "This is a pre-deployment backup"
    fi

    # Perform backups
    local db_result=0
    local media_result=0

    if [ "$MEDIA_ONLY" = false ]; then
        backup_database "$timestamp"
        db_result=$?
    fi

    if [ "$DB_ONLY" = false ]; then
        backup_media "$timestamp"
        media_result=$?
    fi

    # Check if any backup failed
    if [ $db_result -ne 0 ] || [ $media_result -ne 0 ]; then
        log_error "Backup failed"
        exit $((db_result > media_result ? db_result : media_result))
    fi

    # Upload to S3 if configured
    upload_to_s3

    # Perform cleanup
    cleanup_backups

    # Final report
    print_separator
    log_success "Backup completed successfully"
    echo ""
    list_backups

    exit 0
}

# Run main function
main "$@"
