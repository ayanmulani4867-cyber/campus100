from sqlalchemy import inspect, text
from app.extensions import db


def ensure_schema_compatibility():
    """Add columns and tables introduced after the original schema without destroying data."""
    inspector = inspect(db.engine)
    additions = {
        "users": {"phone": "VARCHAR(20)"},
        "students": {
            "division": "VARCHAR(10) DEFAULT 'A'",
            "roll_number": "VARCHAR(30)",
            "prn": "VARCHAR(50)",
        },
        "study_materials": {
            "file_path": "VARCHAR(500)",
            "mime_type": "VARCHAR(150)",
            "department_id": "INTEGER REFERENCES departments(id)",
            "year_label": "VARCHAR(20)",
            "semester": "INTEGER",
            "division": "VARCHAR(10) DEFAULT 'All'",
        },
        "notices": {
            "department_id": "INTEGER REFERENCES departments(id)",
            "year_label": "VARCHAR(20)",
            "semester": "INTEGER",
            "division": "VARCHAR(10) DEFAULT 'All'",
        },
        "attendance_sessions": {
            "division": "VARCHAR(10) DEFAULT 'A'",
        },
    }
    existing_tables = set(inspector.get_table_names())
    with db.engine.begin() as conn:
        # 1. Add missing columns to existing tables
        for table, columns in additions.items():
            if table not in existing_tables:
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            for column, definition in columns.items():
                if column not in existing:
                    conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{column}" {definition}'))

        # 2. Create faculty_assignments table if it does not exist
        if "faculty_assignments" not in existing_tables:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS faculty_assignments (
                    id SERIAL PRIMARY KEY,
                    faculty_id INTEGER NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
                    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                    department_id INTEGER REFERENCES departments(id),
                    year_label VARCHAR(20) NOT NULL DEFAULT '1st Year',
                    semester INTEGER NOT NULL DEFAULT 1,
                    division VARCHAR(10) NOT NULL DEFAULT 'A',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT uq_faculty_course_sem_div UNIQUE (faculty_id, course_id, semester, division)
                );
            """))

        # 2b. Create user_sessions table if it does not exist
        if "user_sessions" not in existing_tables:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id VARCHAR(64) PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE
                );
                CREATE INDEX IF NOT EXISTS ix_user_sessions_user_id ON user_sessions(user_id);
                CREATE INDEX IF NOT EXISTS ix_user_sessions_is_active ON user_sessions(is_active);
            """))

        # 3. Backfill students division, prn, and roll_number if null
        if "students" in existing_tables:
            conn.execute(text("UPDATE students SET division = 'A' WHERE division IS NULL"))
            conn.execute(text("UPDATE students SET prn = student_code WHERE prn IS NULL"))
            conn.execute(text("""
                UPDATE students
                SET roll_number = COALESCE(NULLIF(SUBSTRING(student_code FROM 8), ''), id::text)
                WHERE roll_number IS NULL
            """))

        # 4. Backfill study_materials department_id and semester from course if null
        if "study_materials" in existing_tables and "courses" in existing_tables:
            conn.execute(text("""
                UPDATE study_materials sm
                SET department_id = c.department_id,
                    semester = c.semester,
                    division = COALESCE(sm.division, 'All')
                FROM courses c
                WHERE sm.course_id = c.id AND sm.department_id IS NULL
            """))

        # 5. Populate initial faculty_assignments from courses taught if none exist
        if "faculty_assignments" in existing_tables or True:
            try:
                count_res = conn.execute(text("SELECT COUNT(*) FROM faculty_assignments")).scalar()
                if count_res == 0 and "courses" in existing_tables:
                    conn.execute(text("""
                        INSERT INTO faculty_assignments (faculty_id, course_id, department_id, year_label, semester, division)
                        SELECT c.instructor_id, c.id, c.department_id,
                               CASE
                                   WHEN c.semester <= 2 THEN '1st Year'
                                   WHEN c.semester <= 4 THEN '2nd Year'
                                   WHEN c.semester <= 6 THEN '3rd Year'
                                   ELSE '4th Year'
                               END,
                               c.semester, 'A'
                        FROM courses c
                        WHERE c.instructor_id IS NOT NULL
                        ON CONFLICT DO NOTHING
                    """))
                    # Also add Div B for the first assignment of faculty 1 (P B Patil / Anita Sen demo)
                    conn.execute(text("""
                        INSERT INTO faculty_assignments (faculty_id, course_id, department_id, year_label, semester, division)
                        SELECT c.instructor_id, c.id, c.department_id,
                               CASE
                                   WHEN c.semester <= 2 THEN '1st Year'
                                   WHEN c.semester <= 4 THEN '2nd Year'
                                   WHEN c.semester <= 6 THEN '3rd Year'
                                   ELSE '4th Year'
                               END,
                               c.semester, 'B'
                        FROM courses c
                        WHERE c.instructor_id = 1 AND c.code = 'CS601'
                        ON CONFLICT DO NOTHING
                    """))
            except Exception:
                pass

