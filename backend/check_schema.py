#!/usr/bin/env python
import sys

sys.path.insert(0, "/app")

import os

os.environ["SQLALCHEMY_DATABASE_URL"] = (
    "postgresql://app_user:app_password@postgres:5432/file2learning"
)

from sqlalchemy import inspect, create_engine

engine = create_engine("postgresql://app_user:app_password@postgres:5432/file2learning")
inspector = inspect(engine)

# Check if table exists
if "notifications" in inspector.get_table_names():
    columns = {c["name"]: c for c in inspector.get_columns("notifications")}
    needed_cols = ["daily_plan_id", "schedule_id", "source_type", "action_url"]
    missing = [c for c in needed_cols if c not in columns]

    if missing:
        print(f"Missing columns: {missing}")
        print("Applying migration manually...")

        # Run the SQL commands directly
        from sqlalchemy import text

        with engine.begin() as conn:
            # Add missing columns
            if "daily_plan_id" not in columns:
                conn.execute(
                    text("ALTER TABLE notifications ADD COLUMN daily_plan_id INTEGER")
                )
                print("  ✓ Added: daily_plan_id")
            if "schedule_id" not in columns:
                conn.execute(
                    text("ALTER TABLE notifications ADD COLUMN schedule_id INTEGER")
                )
                print("  ✓ Added: schedule_id")
            if "source_type" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE notifications ADD COLUMN source_type VARCHAR DEFAULT 'system'"
                    )
                )
                print("  ✓ Added: source_type")
            if "action_url" not in columns:
                conn.execute(
                    text("ALTER TABLE notifications ADD COLUMN action_url VARCHAR")
                )
                print("  ✓ Added: action_url")

            # Add foreign keys (with error handling)
            try:
                conn.execute(
                    text(
                        """
                ALTER TABLE notifications ADD CONSTRAINT fk_notifications_daily_plan_id 
                FOREIGN KEY(daily_plan_id) REFERENCES daily_study_plans(id) ON DELETE CASCADE
            """
                    )
                )
                print("  ✓ Added FK: daily_plan_id")
            except Exception as e:
                print(f"  ⚠ FK daily_plan_id: {str(e)[:50]}")

            try:
                conn.execute(
                    text(
                        """
                ALTER TABLE notifications ADD CONSTRAINT fk_notifications_schedule_id 
                FOREIGN KEY(schedule_id) REFERENCES study_schedules(id) ON DELETE CASCADE
            """
                    )
                )
                print("  ✓ Added FK: schedule_id")
            except Exception as e:
                print(f"  ⚠ FK schedule_id: {str(e)[:50]}")

            # Add indexes
            try:
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_notifications_daily_plan_id ON notifications(daily_plan_id, user_id)"
                    )
                )
                print("  ✓ Added index: daily_plan_id")
            except Exception as e:
                print(f"  ⚠ Index error: {str(e)[:50]}")

            try:
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_notifications_schedule_id ON notifications(schedule_id, user_id)"
                    )
                )
                print("  ✓ Added index: schedule_id")
            except Exception as e:
                print(f"  ⚠ Index error: {str(e)[:50]}")

            try:
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_notifications_source_type ON notifications(user_id, source_type, created_at)"
                    )
                )
                print("  ✓ Added index: source_type")
            except Exception as e:
                print(f"  ⚠ Index error: {str(e)[:50]}")

        print("✅ Migration applied and committed!")
    else:
        print("All columns already present!")
else:
    print("Notifications table not found!")
