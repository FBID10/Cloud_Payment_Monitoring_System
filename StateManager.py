import sqlite3
from datetime import datetime


class StateManager:
    """
    State Manager: Coordinates with the database to track instances that are missing tags.
    It acts as the "brain" that determines if we've caught a specific instance before.
    """

    def __init__(self, db_path="instance_state.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Create the database table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flagged_instances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instance_id TEXT UNIQUE NOT NULL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    missing_tags TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)
            conn.commit()

    def is_instance_seen_before(self, instance_id):
        """
        Check if we've encountered this instance before.
        Returns True if the instance is in the database, False otherwise.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM flagged_instances WHERE instance_id = ?",
                (instance_id,)
            )
            return cursor.fetchone() is not None

    def record_flagged_instance(self, instance_id, missing_tags):
        """
        Record a flagged instance in the database or update if it already exists.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            missing_tags_str = ",".join(missing_tags)
            
            try:
                cursor.execute("""
                    INSERT INTO flagged_instances (instance_id, missing_tags)
                    VALUES (?, ?)
                """, (instance_id, missing_tags_str))
            except sqlite3.IntegrityError:
                # Instance already exists, update last_seen timestamp
                cursor.execute("""
                    UPDATE flagged_instances 
                    SET last_seen = CURRENT_TIMESTAMP, missing_tags = ?
                    WHERE instance_id = ?
                """, (missing_tags_str, instance_id))
            
            conn.commit()

    def get_all_flagged_instances(self):
        """Retrieve all flagged instances from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT instance_id, missing_tags, first_seen, last_seen 
                FROM flagged_instances 
                WHERE is_active = 1
                ORDER BY last_seen DESC
            """)
            rows = cursor.fetchall()
            
            return [
                {
                    "InstanceId": row[0],
                    "MissingTags": row[1].split(","),
                    "FirstSeen": row[2],
                    "LastSeen": row[3],
                }
                for row in rows
            ]

    def mark_instance_resolved(self, instance_id):
        """Mark an instance as resolved (tags have been added)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE flagged_instances 
                SET is_active = 0
                WHERE instance_id = ?
            """, (instance_id,))
            conn.commit()

    def get_instance_history(self, instance_id):
        """Get the history of a specific instance."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT instance_id, missing_tags, first_seen, last_seen, is_active
                FROM flagged_instances
                WHERE instance_id = ?
            """, (instance_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "InstanceId": row[0],
                    "MissingTags": row[1].split(","),
                    "FirstSeen": row[2],
                    "LastSeen": row[3],
                    "IsActive": bool(row[4]),
                }
            return None

    def clear_database(self):
        """Clear all records from the database (useful for testing)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM flagged_instances")
            conn.commit()
