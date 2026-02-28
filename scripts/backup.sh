#!/bin/bash
# Backup script for ai-artiste application

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_FILE="./data/artist_venue.db"

mkdir -p "$BACKUP_DIR"

if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/artist_venue_${TIMESTAMP}.db"
    echo "Database backed up to $BACKUP_DIR/artist_venue_${TIMESTAMP}.db"
else
    echo "Database file not found: $DB_FILE"
    exit 1
fi

# Keep only last 10 backups
ls -t "$BACKUP_DIR"/artist_venue_*.db | tail -n +11 | xargs -r rm
echo "Backup complete. Keeping last 10 backups."
