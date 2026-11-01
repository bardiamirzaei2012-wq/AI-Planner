# ============================================================
# SMART AI STUDY PLANNER
# app.py
#
# Flask + SQLite + AI Planner + ML Personalization
# ============================================================

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

import sqlite3
import os
import uuid
import json
import traceback

from datetime import datetime


# ============================================================
# APP CONFIG
# ============================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

CORS(app)


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE = os.path.join(
    BASE_DIR,
    "study_planner.db"
)

PORT = 8000


# ============================================================
# DATABASE
# ============================================================

def get_db():

    conn = sqlite3.connect(
        DATABASE,
        timeout=30
    )

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


def init_db():

    conn = get_db()

    cursor = conn.cursor()

    # ========================================================
    # USERS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id TEXT PRIMARY KEY,

            name TEXT NOT NULL,

            age INTEGER DEFAULT 0,

            grade TEXT,

            daily_hours REAL DEFAULT 2,

            goal TEXT,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL
        )
    """)

    # ========================================================
    # SUBJECTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id TEXT NOT NULL,

            name TEXT NOT NULL,

            importance INTEGER DEFAULT 3,

            required_hours REAL DEFAULT 2,

            progress REAL DEFAULT 0,

            created_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # ========================================================
    # STUDY PLANS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id TEXT NOT NULL,

            plan_json TEXT NOT NULL,

            source TEXT DEFAULT 'ai',

            created_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # ========================================================
    # STUDY SESSIONS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id TEXT NOT NULL,

            subject_id INTEGER,

            subject_name TEXT,

            day TEXT,

            start_time TEXT,

            end_time TEXT,

            duration INTEGER DEFAULT 0,

            session_type TEXT DEFAULT 'study',

            completed INTEGER DEFAULT 0,

            created_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # ========================================================
    # ACTIVITY LOG
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id TEXT NOT NULL,

            action TEXT NOT NULL,

            details TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()

    conn.close()


init_db()


# ============================================================
# HELPERS
# ============================================================

def now():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def get_json():

    return request.get_json(
        silent=True
    )


def error_response(
    message,
    status=400
):

    return jsonify({
        "success": False,
        "error": message
    }), status


def log_activity(
    user_id,
    action,
    details=""
):

    try:

        conn = get_db()

        conn.execute("""
            INSERT INTO activity_log
            (
                user_id,
                action,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            action,
            details,
            now()
        ))

        conn.commit()

        conn.close()

    except Exception as e:

        print(
            "Activity error:",
            e
        )


def user_exists(user_id):

    conn = get_db()

    row = conn.execute("""
        SELECT id
        FROM users
        WHERE id = ?
    """, (
        user_id,
    )).fetchone()

    conn.close()

    return row is not None


# ============================================================
# FRONTEND PAGES
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route("/index.html")
def index():

    return render_template(
        "index.html"
    )


@app.route("/dashboard")
@app.route("/dashboard.html")
def dashboard_page():

    return render_template(
        "dashboard.html"
    )


@app.route("/profile")
@app.route("/profile.html")
def profile_page():

    return render_template(
        "profile.html"
    )


@app.route("/subjects")
@app.route("/subjects.html")
def subjects_page():

    return render_template(
        "subjects.html"
    )


@app.route("/planner")
@app.route("/planner.html")
def planner_page():

    return render_template(
        "planner.html"
    )


# ============================================================
# API HOME
# ============================================================

@app.route("/api")
def api_home():

    return jsonify({

        "success": True,

        "message":
            "Smart AI Study Planner API is running",

        "status":
            "ok",

        "port":
            PORT,

        "database":
            DATABASE,

        "pages": {

            "home":
                "/",

            "dashboard":
                "/dashboard",

            "profile":
                "/profile",

            "subjects":
                "/subjects",

            "planner":
                "/planner"

        },

        "endpoints": {

            "profile":
                "/api/profile",

            "profile_get":
                "/api/profile/<user_id>",

            "subjects":
                "/api/subjects",

            "subjects_get":
                "/api/subjects/<user_id>",

            "generate_plan":
                "/api/ai/generate-plan",

            "optimize":
                "/api/ai/optimize",

            "rebalance":
                "/api/ai/rebalance",

            "dashboard":
                "/api/dashboard/<user_id>",

            "plans":
                "/api/plans/<user_id>",

            "latest_plan":
                "/api/plans/<user_id>/latest",

            "progress":
                "/api/progress",

            "sessions":
                "/api/sessions/<user_id>",

            "session_complete":
                "/api/sessions/<session_id>/complete"

        }

    })


# ============================================================
# HEALTH
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    try:

        conn = get_db()

        conn.execute(
            "SELECT 1"
        )

        conn.close()

        return jsonify({

            "success": True,

            "status":
                "healthy",

            "database":
                "connected"

        })

    except Exception as e:

        return error_response(
            str(e),
            500
        )


# ============================================================
# CREATE PROFILE
# ============================================================

@app.route(
    "/api/profile",
    methods=["POST"]
)
def create_profile():

    try:

        data = get_json()

        if not data:

            return error_response(
                "JSON ارسال نشده است."
            )

        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()

        if not name:

            return error_response(
                "نام الزامی است."
            )

        try:

            age = int(
                data.get(
                    "age",
                    0
                )
            )

        except:

            age = 0

        age = max(
            0,
            min(
                120,
                age
            )
        )

        grade = str(
            data.get(
                "grade",
                ""
            )
        ).strip()

        try:

            daily_hours = float(
                data.get(
                    "daily_hours",
                    2
                )
            )

        except:

            daily_hours = 2

        daily_hours = max(
            0.5,
            min(
                12,
                daily_hours
            )
        )

        goal = str(
            data.get(
                "goal",
                ""
            )
        ).strip()

        user_id = str(
            uuid.uuid4()
        )

        created = now()

        conn = get_db()

        conn.execute("""
            INSERT INTO users
            (
                id,
                name,
                age,
                grade,
                daily_hours,
                goal,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            user_id,
            name,
            age,
            grade,
            daily_hours,
            goal,
            created,
            created

        ))

        conn.commit()

        conn.close()

        log_activity(
            user_id,
            "create_profile"
        )

        return jsonify({

            "success":
                True,

            "message":
                "کاربر ساخته شد.",

            "user": {

                "id":
                    user_id,

                "name":
                    name,

                "age":
                    age,

                "grade":
                    grade,

                "daily_hours":
                    daily_hours,

                "goal":
                    goal

            }

        }), 201

    except Exception as e:

        traceback.print_exc()

        return error_response(
            str(e),
            500
        )


# ============================================================
# GET PROFILE
# ============================================================

@app.route(
    "/api/profile/<user_id>",
    methods=["GET"]
)
def get_profile(user_id):

    try:

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE id = ?
        """, (
            user_id,
        )).fetchone()

        if not user:

            conn.close()

            return error_response(
                "کاربر پیدا نشد.",
                404
            )

        subjects = conn.execute("""
            SELECT *
            FROM subjects
            WHERE user_id = ?
            ORDER BY importance DESC, name ASC
        """, (
            user_id,
        )).fetchall()

        conn.close()

        return jsonify({

            "success":
                True,

            "user":
                dict(user),

            "subjects": [

                dict(subject)

                for subject
                in subjects

            ]

        })

    except Exception as e:

        return error_response(
            str(e),
            500
        )


# ============================================================
# UPDATE PROFILE
# ============================================================

@app.route(
    "/api/profile/<user_id>",
    methods=["PUT"]
)
def update_profile(user_id):

    try:

        data = get_json()

        if not data:

            return error_response(
                "JSON ارسال نشده."
            )

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE id = ?
        """, (
            user_id,
        )).fetchone()

        if not user:

            conn.close()

            return error_response(
                "کاربر پیدا نشد.",
                404
            )

        name = str(
            data.get(
                "name",
                user["name"]
            )
        ).strip()

        age = data.get(
            "age",
            user["age"]
        )

        try:

            age = int(age)

        except:

            age = user["age"]

        grade = str(
            data.get(
                "grade",
                user["grade"]
            )
        ).strip()

        try:

            daily_hours = float(
                data.get(
                    "daily_hours",
                    user["daily_hours"]
                )
            )

        except:

            daily_hours = user[
                "daily_hours"
            ]

        daily_hours = max(
            0.5,
            min(
                12,
                daily_hours
            )
        )

        goal = str(
            data.get(
                "goal",
                user["goal"] or ""
            )
        ).strip()

        conn.execute("""
            UPDATE users

            SET

                name = ?,

                age = ?,

                grade = ?,

                daily_hours = ?,

                goal = ?,

                updated_at = ?

            WHERE id = ?
        """, (

            name,
            age,
            grade,
            daily_hours,
            goal,
            now(),
            user_id

        ))

        conn.commit()

        conn.close()

        log_activity(
            user_id,
            "update_profile"
        )

        return jsonify({

            "success":
                True,

            "message":
                "پروفایل بروزرسانی شد."

        })

    except Exception as e:

        traceback.print_exc()

        return error_response(
            str(e),
            500
        )


# ============================================================
# ADD SUBJECT
# ============================================================

@app.route(
    "/api/subjects",
    methods=["POST"]
)
def add_subject():

    try:

        data = get_json()

        if not data:

            return error_response(
                "JSON ارسال نشده."
            )

        user_id = str(
            data.get(
                "user_id",
                ""
            )
        ).strip()

        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()

        if not user_id or not name:

            return error_response(
                "user_id و name الزامی هستند."
            )

        if not user_exists(
            user_id
        ):

            return error_response(
                "کاربر پیدا نشد.",
                404
            )

        try:

            importance = int(
                data.get(
                    "importance",
                    3
                )
            )

        except:

            importance = 3

        try:

            required_hours = float(
                data.get(
                    "required_hours",
                    2
                )
            )

        except:

            required_hours = 2

        importance = max(
            1,
            min(
                5,
                importance
            )
        )

        required_hours = max(
            0.5,
            min(
                50,
                required_hours
            )
        )

        conn = get_db()

        # جلوگیری از درس تکراری
        existing = conn.execute("""
            SELECT id
            FROM subjects
            WHERE user_id = ?
            AND LOWER(name) = LOWER(?)
        """, (
            user_id,
            name
        )).fetchone()

        if existing:

            conn.close()

            return error_response(
                "این درس قبلاً اضافه شده است.",
                409
            )

        cursor = conn.execute("""
            INSERT INTO subjects
            (
                user_id,
                name,
                importance,
                required_hours,
                progress,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (

            user_id,
            name,
            importance,
            required_hours,
            0,
            now()

        ))

        subject_id = cursor.lastrowid

        conn.commit()

        conn.close()

        log_activity(
            user_id,
            "add_subject",
            name
        )

        return jsonify({

            "success":
                True,

            "message":
                "درس اضافه شد.",

            "subject": {

                "id":
                    subject_id,

                "user_id":
                    user_id,

                "name":
                    name,

                "importance":
                    importance,

                "required_hours":
                    required_hours,

                "progress":
                    0

            }

        }), 201

    except Exception as e:

        traceback.print_exc()

        return error_response(
            str(e),
            500
        )


# ============================================================
# GET SUBJECTS
# ============================================================

@app.route(
    "/api/subjects/<user_id>",
    methods=["GET"]
)
def get_subjects(user_id):

    try:

        conn = get_db()

        subjects = conn.execute("""
            SELECT *
            FROM subjects

            WHERE user_id = ?

            ORDER BY
                importance DESC,
                name ASC
        """, (
            user_id,
        )).fetchall()

        conn.close()

        return jsonify({

            "success":
                True,

            "subjects": [

                dict(subject)

                for subject
                in subjects

            ]

        })

    except Exception as e:

        return error_response(
            str(e),
            500
        )


# ============================================================
# UPDATE SUBJECT
# ============================================================

@app.route(
    "/api/subjects/<int:subject_id>",
    methods=["PUT"]
)
def update_subject(subject_id):

    try:

        data = get_json()

        if not data:

            return error_response(
                "JSON ارسال نشده."
            )

        conn = get_db()

        subject = conn.execute("""
            SELECT *
            FROM subjects
            WHERE id = ?
        """, (
            subject_id,
        )).fetchone()

        if not subject:

            conn.close()

            return error_response(
                "درس پیدا نشد.",
                404
            )

        name = str(
            data.get(
                "name",
                subject["name"]
            )
        ).strip()

        try:

            importance = int(
                data.get(
                    "importance",
                    subject["importance"]
                )
            )

        except:

            importance = subject[
                "importance"
            ]

        try:

            required_hours = float(
                data.get(
                    "required_hours",
                    subject["required_hours"]
                )
            )

        except:

            required_hours = subject[
                "required_hours"
            ]

        try:

            progress = float(
                data.get(
                    "progress",
                    subject["progress"]
                )
            )

        except:

            progress = subject[
                "progress"
            ]

        importance = max(
            1,
            min(
                5,
                importance
            )
        )

        required_hours = max(
            0.5,
            min(
                50,
                required_hours
            )
        )

        progress = max(
            0,
            min(
                100,
                progress
            )
        )

        conn.execute("""
            UPDATE subjects

            SET

                name = ?,

                importance = ?,

                required_hours = ?,

                progress = ?

            WHERE id = ?
        """, (

            name,
            importance,
            required_hours,
            progress,
            subject_id

        ))

        conn.commit()

        conn.close()

        return jsonify({

            "success":
                True,

            "message":
                "درس بروزرسانی شد."

        })

    except Exception as e:

        traceback.print_exc()

        return error_response(
            str(e),
            500
        )


# ============================================================
# DELETE SUBJECT
# ============================================================

@app.route(
    "/api/subjects/<int:subject_id>",
    methods=["DELETE"]
)
def delete_subject(subject_id):

    try:

        conn = get_db()

        subject = conn.execute("""
            SELECT *
            FROM subjects
            WHERE id = ?
        """, (
            subject_id,
        )).fetchone()

        if not subject:

            conn.close()

            return error_response(
                "درس پیدا نشد.",
                404
            )

        conn.execute("""
            DELETE FROM subjects
            WHERE id = ?
        """, (
            subject_id,
        ))

        conn.commit()

        conn.close()

        log_activity(
            subject["user_id"],
            "delete_subject",
            subject["name"]
        )

        return jsonify({

            "success":
                True,

            "message":
                "درس حذف شد."

        })

    except Exception as e:

        return error_response(
            str(e),
            500
        )


# ============================================================
# USER DATA FOR AI
# ============================================================

def get_user_data(user_id):

    conn = get_db()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (
        user_id,
    )).fetchone()

    if not user:

        conn.close()

        return None

    subjects = conn.execute("""
        SELECT
            id,
            name,
            importance,
            required_hours,
            progress

        FROM subjects

        WHERE user_id = ?

        ORDER BY importance DESC
    """, (
        user_id,
    )).fetchall()

    conn.close()

    return {

        "id":
            user["id"],

        "name":
            user["name"],

        "age":
            user["age"],

        "grade":
            user["grade"],

        "daily_hours":
            user["daily_hours"],

        "goal":
            user["goal"],

        "subjects": [

            {

                "id":
                    s["id"],

                "name":
                    s["name"],

                "importance":
                    s["importance"],

                "required_hours":
                    s["required_hours"],

                "performance":
                    s["progress"]

            }

            for s in subjects

        ]

    }


# ============================================================
# HISTORY FOR ML
# ============================================================

def get_learning_history(
    user_id
):

    conn = get_db()

    sessions = conn.execute("""
        SELECT
            subject_id,
            subject_name,
            duration,
            completed,
            session_type

        FROM study_sessions

        WHERE user_id = ?

        AND session_type = 'study'

        ORDER BY id ASC
    """, (
        user_id,
    )).fetchall()

    subjects = conn.execute("""
        SELECT
            id,
            importance,
            progress

        FROM subjects

        WHERE user_id = ?
    """, (
        user_id,
    )).fetchall()

    conn.close()

    subject_map = {

        s["id"]: s

        for s in subjects

    }

    history = []

    for session in sessions:

        subject = subject_map.get(
            session["subject_id"]
        )

        importance = (
            subject["importance"]
            if subject
            else 3
        )

        performance = (
            subject["progress"]
            if subject
            else 50
        )

        completed = (
            1
            if session["completed"]
            else 0
        )

        history.append({

            "importance":
                importance,

            "performance":
                performance,

            "completed_ratio":
                completed,

            "difficulty":
                3,

            "duration":
                session["duration"] or 0,

            "success":
                completed

        })

    return history


# ============================================================
# SAVE PLAN
# ============================================================

def save_plan(
    user_id,
    result
):

    plan = result.get(
        "plan"
    )

    if not plan:

        return None

    source = result.get(
        "source",
        "ai"
    )

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO study_plans
        (
            user_id,
            plan_json,
            source,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (

        user_id,

        json.dumps(
            plan,
            ensure_ascii=False
        ),

        source,

        now()

    ))

    plan_id = cursor.lastrowid

    # ========================================================
    # Delete old generated sessions
    #
    # We keep completed sessions.
    # ========================================================

    conn.execute("""
        DELETE FROM study_sessions

        WHERE user_id = ?

        AND completed = 0
    """, (
        user_id,
    ))

    # ========================================================
    # Subject ID lookup
    # ========================================================

    subjects = conn.execute("""
        SELECT id, name
        FROM subjects
        WHERE user_id = ?
    """, (
        user_id,
    )).fetchall()

    subject_map = {

        str(s["name"]).strip().lower():
            s["id"]

        for s in subjects

    }

    # ========================================================
    # Save sessions
    # ========================================================

    week = plan.get(
        "week",
        []
    )

    if isinstance(
        week,
        list
    ):

        for day in week:

            if not isinstance(
                day,
                dict
            ):

                continue

            day_name = str(
                day.get(
                    "day",
                    ""
                )
            )

            sessions = day.get(
                "sessions",
                []
            )

            if not isinstance(
                sessions,
                list
            ):

                continue

            for session in sessions:

                if not isinstance(
                    session,
                    dict
                ):

                    continue

                session_type = str(
                    session.get(
                        "type",
                        "study"
                    )
                ).lower()

                subject_name = str(
                    session.get(
                        "subject",
                        ""
                    )
                ).strip()

                if not subject_name:

                    continue

                subject_id = subject_map.get(
                    subject_name.lower()
                )

                try:

                    duration = int(
                        session.get(
                            "duration",
                            0
                        )
                    )

                except:

                    duration = 0

                duration = max(
                    0,
                    duration
                )

                conn.execute("""
                    INSERT INTO study_sessions
                    (
                        user_id,
                        subject_id,
                        subject_name,
                        day,
                        start_time,
                        end_time,
                        duration,
                        session_type,
                        completed,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (

                    user_id,

                    subject_id,

                    subject_name,

                    day_name,

                    str(
                        session.get(
                            "start",
                            ""
                        )
                    ),

                    str(
                        session.get(
                            "end",
                            ""
                        )
                    ),

                    duration,

                    session_type,

                    0,

                    now()

                ))

    conn.commit()

    conn.close()

    return plan_id


# ============================================================
# GENERATE AI PLAN
# ============================================================

@app.route(
    "/api/ai/generate-plan",
    methods=["POST"]
)
def generate_ai_plan():

    try:

        data = get_json()

        if not data:

            return error_response(
                "JSON ارسال نشده."
            )

        user_id = str(
            data.get(
                "user_id",
                ""
            )
        ).strip()

        if not user_id:

            return error_response(
                "user_id الزامی است."
            )

        user_data = get_user_data(
            user_id
        )

        if not user_data:

            return error_response(
                "کاربر پیدا نشد.",
                404
            )

        history = get_learning_history(
            user_id
        )

        performance = {

            "reason":
                "new_plan",

            "history_count":
                len(history)

        }

        from ai.planner import generate_plan

        result = generate_plan(

            user_data,

            use_fallback=True,

            history=history,

            performance=performance

        )

        if not result.get(
            "success"
        ):

            return jsonify(
                result
            ), 500

        plan_id = save_plan(
            user_id,
            result
        )

        result["plan_id"] = plan_id

        log_activity(

            user_id,

            "generate_plan",

            json.dumps(
                {
                    "source":
                        result.get(
                            "source"
                        ),

                    "ml_enabled":
                        result.get(
                            "ml_enabled",
                            False
                        )
                },
                ensure_ascii=False
            )

        )

        return jsonify(
            result
        )

    except Exception as e:

        traceback.print_exc()

        return error_response(
            str(e),
            500
        )


# ============================================================
# REBALANCE
# ============================================================

@app.route(
    "/api/ai/rebalance",
    methods=["POST"]
)
def ai_rebalance():

    try:

        data = get_json()

        if not data:

            return error_response(
                "JSON ارسال نشده."
            )

        user_id = str(
            data.get(
                "user_id",
                ""
            )
        ).strip()

        if not user_id:

            return error_response(
                "user_id الزامی است."
            )

        user_data = get_user_data(
            user_id
        )

        if not user_data:

            return error_response(
                "کاربر پیدا نشد.",
                404
            )

        try:

            completed = int(
                data.get(
                    "completed_sessions",
                    0
                )
            )

        except:

            completed = 0

        try:

            missed = int(
                data.get(
                    "missed_sessions",
                    0
                )
            )

        except:

            missed = 0

        history = get_learning_history(
            user_id
        )

        conn = get_db()

        latest = conn.execute("""
            SELECT plan_json
            FROM study_plans

            WHERE user_id = ?

            ORDER BY id DESC

            LIMIT 1
        """, (
            user_id,
        )).fetchone()

        conn.close()

        previous_plan = None

        if latest:

            try:

                previous_plan = json.loads(
                    latest["plan_json"]
                )

            except:

                previous_plan = None

        from ai.planner import rebalance_plan

        result = rebalance_plan(

            user_data,

            completed_sessions=
                completed,

            missed_sessions=
                missed,

            previous_plan=
                previous_plan,

            history=
                history

        )

        if result.get(
            "success"
        ):

            plan_id = save_plan(
                user_id,
                result
            )

            result[
                "plan_id"
            ] = plan_id

        log_activity(

            user_id,

            "rebalance_plan",

            json.dumps(
                {
                    "completed":
                        completed,

                    "missed":
                        missed
                },
                ensure_ascii=False
            )

        )

        return jsonify(
            result
        )

    except Exception as e:

        traceback.print_exc()

        return error_response(
            str(e),
            500
        )


# ============================================================
# OPTIMIZE NEXT WEEK
# ============================================================

@app.route(
    "/api/ai/optimize",
    methods=["POST"]
)
def ai_optimize():

    try:

        data = get_json()

        if not data:

            return error_response(
                "JSON ارسال نشده."
            )

        user_id = str(
            data.get(
                "user_id",
                ""
            )
        ).strip()

        if not user_id:

            return error_response(
                "user_id الزامی است."
            )

        user_data = get_user_data(
            user_id
        )

        if not user_data:

            return error_response(
                "کاربر پیدا نشد.",
                404
            )

        history = get_learning_history(
            user_id
        )

        # ====================================================
        # Calculate real performance
        # ====================================================

        total = len(
            history
        )

        completed = sum(

            1

            for row
            in history

            if row.get(
                "success",
                0
            ) >= 1

        )

        completion_ratio = (

            completed /
            total

            if total

            else 0

        )

        performance = {

            "total_sessions":
                total,

            "completed_sessions":
                completed,

            "completion_ratio":
                completion_ratio,

            "optimization":
                True

        }

        from ai.planner import optimize_next_week

        result = optimize_next_week(

            user_data,

            performance=
                performance,

            history=
                history

        )

        if result.get(
            "success"
        ):

            plan_id = save_plan(
                user_id,
                result
            )

            result[
                "plan_id"
            ] = plan_id

        log_activity(

            user_id,

            "optimize_next_week",

            json.dumps(
                performance,
                ensure_ascii=False
            )

        )

        return jsonify(
            result
        )

    except Exception as e:

        traceback.print_exc()

        return error_response(
            str(e),
            500
        )


# ============================================================
# GET PLANS
# ============================================================

@app.route(
    "/api/plans/<user_id>",
    methods=["GET"]
)
def get_plans(user_id):

    try:

        conn = get_db()

        plans = conn.execute("""
            SELECT *
            FROM study_plans

            WHERE user_id = ?

            ORDER BY id DESC
        """, (
            user_id,
        )).fetchall()

        conn.close()

        result = []

        for p in plans:

            try:

                plan = json.loads(
                    p["plan_json"]
                )

            except:

                plan = {}

            result.append({

                "id":
                    p["id"],

                "source":
                    p["source"],

                "created_at":
                    p["created_at"],

                "plan":
                    plan

            })

        return jsonify({

            "success":
                True,

            "plans":
                result

        })

    except Exception as e:

        return error_response(
            str(e),
            500
        )


# ============================================================
# LATEST PLAN
# ============================================================

@app.route(
    "/api/plans/<user_id>/latest",
    methods=["GET"]
)
def latest_plan(user_id):

    try:

        conn = get_db()

        plan = conn.execute("""
            SELECT *
            FROM study_plans

            WHERE user_id = ?

            ORDER BY id DESC

            LIMIT 1
        """, (
            user_id,
        )).fetchone()

        conn.close()

        if not plan:

            return error_response(
                "برنامه‌ای وجود ندارد.",
                404
            )

        try:

            plan_json = json.loads(
                plan["plan_json"]
            )

        except:

            plan_json = {}

        return jsonify({

            "success":
                True,

            "id":
                plan["id"],

            "source":
                plan["source"],

            "created_at":
                plan["created_at"],

            "plan":
                plan_json

        })

    except Exception as e:

        return error_response(
            str(e),
            500
        )


# ============================================================
# GET SESSIONS
# ============================================================

@app.route(
    "/api/sessions/<user_id>",
    methods=["GET"]
)
def get_sessions(user_id):

    try:

        conn = get_db()

        sessions = conn.execute("""
            SELECT *
            FROM study_sessions

            WHERE user_id = ?

            ORDER BY id ASC
        """, (
            user_id,
        )).fetchall()

        conn.close()

        return jsonify({

            "success":
                True,

            "sessions": [

                dict(s)

                for s in sessions

            ]

        })

    except Exception as e:

        return error_response(
            str(e),
            500
        )


# ============================================================
# COMPLETE SESSION
# ============================================================

@app.route(
    "/api/sessions/<int:session_id>/complete",
    methods=["POST"]
)
def complete_session(session_id):

    try:

        conn = get_db()

        session = conn.execute("""
            SELECT *
            FROM study_sessions

            WHERE id = ?
        """, (
            session_id,
        )).fetchone()

        if not session:

            conn.close()

            return error_response(
                "جلسه پیدا نشد.",
                404
            )

        conn.execute("""
            UPDATE study_sessions

            SET completed = 1

            WHERE id = ?
        """, (
            session_id,
        ))

        # ====================================================
        # Update subject progress
        # ====================================================

        if session["subject_id"]:

            subject = conn.execute("""
                SELECT *
                FROM subjects

                WHERE id = ?
            """, (
                session["subject_id"],
            )).fetchone()

            if subject:

                # هر جلسه کامل شده،
                # progress را کمی افزایش می‌دهد.
                #
                # بعداً می‌توانیم فرمول ML دقیق‌تری
                # برای این قسمت قرار دهیم.

                current = float(
                    subject["progress"] or 0
                )

                increment = min(
                    10,
                    max(
                        1,
                        (
                            session["duration"] or 30
                        ) / 60 * 5
                    )
                )

                new_progress = min(
                    100,
                    current + increment
                )

                conn.execute("""
                    UPDATE subjects

                    SET progress = ?

                    WHERE id = ?
                """, (

                    new_progress,

                    session["subject_id"]

                ))

        conn.commit()

        conn.close()

        log_activity(

            session["user_id"],

            "complete_session",

            str(session_id)

        )

        return jsonify({

            "success":
                True,

            "message":
                "جلسه با موفقیت انجام شد."

        })

    except Exception as e:

        traceback.print_exc()

        return error_response(
            str(e),
            500
        )


# ============================================================
# UPDATE PROGRESS
# ============================================================

@app.route(
    "/api/progress",
    methods=["POST"]
)
def update_progress():

    try:

        data = get_json()

        if not data:

            return error_response(
                "JSON ارسال نشده."
            )

        user_id = str(
            data.get(
                "user_id",
                ""
            )
        ).strip()

        subject_id = data.get(
            "subject_id"
        )

        if not user_id or subject_id is None:

            return error_response(
                "user_id و subject_id الزامی هستند."
            )

        try:

            progress = float(
                data.get(
                    "progress",
                    0
                )
            )

        except:

            progress = 0

        progress = max(
            0,
            min(
                100,
                progress
            )
        )

        conn = get_db()

        cursor = conn.execute("""
            UPDATE subjects

            SET progress = ?

            WHERE id = ?

            AND user_id = ?
        """, (

            progress,
            subject_id,
            user_id

        ))

        if cursor.rowcount == 0:

            conn.close()

            return error_response(
                "درس پیدا نشد.",
                404
            )

        conn.commit()

        conn.close()

        log_activity(

            user_id,

            "update_progress",

            json.dumps(
                {
                    "subject_id":
                        subject_id,

                    "progress":
                        progress
                }
            )

        )

        return jsonify({

            "success":
                True,

            "progress":
                progress

        })

    except Exception as e:

        return error_response(
            str(e),
            500
        )


# ============================================================
# DASHBOARD
# ============================================================

@app.route(
    "/api/dashboard/<user_id>",
    methods=["GET"]
)
def dashboard_data(user_id):

    try:

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users

            WHERE id = ?
        """, (
            user_id,
        )).fetchone()

        if not user:

            conn.close()

            return error_response(
                "کاربر پیدا نشد.",
                404
            )

        subjects = conn.execute("""
            SELECT *
            FROM subjects

            WHERE user_id = ?

            ORDER BY importance DESC
        """, (
            user_id,
        )).fetchall()

        sessions = conn.execute("""
            SELECT *
            FROM study_sessions

            WHERE user_id = ?

            ORDER BY id DESC
        """, (
            user_id,
        )).fetchall()

        # ====================================================
        # Latest plan
        # ====================================================

        latest = conn.execute("""
            SELECT *
            FROM study_plans

            WHERE user_id = ?

            ORDER BY id DESC

            LIMIT 1
        """, (
            user_id,
        )).fetchone()

        conn.close()

        # ====================================================
        # Statistics
        # ====================================================

        study_sessions = [

            s

            for s in sessions

            if s["session_type"]
            == "study"

        ]

        total_planned = sum(

            s["duration"] or 0

            for s
            in study_sessions

        )

        total_completed = sum(

            s["duration"] or 0

            for s
            in study_sessions

            if s["completed"] == 1

        )

        remaining = max(

            0,

            total_planned -
            total_completed

        )

        if total_planned:

            progress = round(

                (
                    total_completed /
                    total_planned
                ) * 100,

                1

            )

        else:

            progress = 0

        # ====================================================
        # Subject progress
        # ====================================================

        subject_stats = []

        for subject in subjects:

            subject_sessions = [

                s

                for s in study_sessions

                if s["subject_id"]
                == subject["id"]

            ]

            planned = sum(

                s["duration"] or 0

                for s
                in subject_sessions

            )

            completed = sum(

                s["duration"] or 0

                for s
                in subject_sessions

                if s["completed"] == 1

            )

            if planned:

                session_progress = round(

                    completed /
                    planned *
                    100,

                    1

                )

            else:

                session_progress = (
                    subject["progress"]
                    or 0
                )

            subject_stats.append({

                "id":
                    subject["id"],

                "name":
                    subject["name"],

                "importance":
                    subject["importance"],

                "required_hours":
                    subject["required_hours"],

                "progress":
                    round(
                        float(
                            subject["progress"]
                            or 0
                        ),
                        1
                    ),

                "session_progress":
                    session_progress,

                "planned_minutes":
                    planned,

                "completed_minutes":
                    completed

            })

        # ====================================================
        # Missed / completed
        # ====================================================

        total_sessions = len(
            study_sessions
        )

        completed_sessions = sum(

            1

            for s
            in study_sessions

            if s["completed"] == 1

        )

        missed_sessions = (

            total_sessions -
            completed_sessions

        )

        # ====================================================
        # Latest plan
        # ====================================================

        latest_plan = None

        if latest:

            try:

                latest_plan = {

                    "id":
                        latest["id"],

                    "source":
                        latest["source"],

                    "created_at":
                        latest["created_at"],

                    "plan":
                        json.loads(
                            latest["plan_json"]
                        )

                }

            except:

                latest_plan = None

        return jsonify({

            "success":
                True,

            "user":
                dict(user),

            "statistics": {

                "planned_minutes":
                    total_planned,

                "completed_minutes":
                    total_completed,

                "remaining_minutes":
                    remaining,

                "progress":
                    progress,

                "total_sessions":
                    total_sessions,

                "completed_sessions":
                    completed_sessions,

                "missed_sessions":
                    missed_sessions

            },

            "subjects":
                subject_stats,

            "sessions": [

                dict(s)

                for s
                in sessions

            ],

            "latest_plan":
                latest_plan

        })

    except Exception as e:

        traceback.print_exc()

        return error_response(
            str(e),
            500
        )


# ============================================================
# ACTIVITY
# ============================================================

@app.route(
    "/api/activity/<user_id>",
    methods=["GET"]
)
def get_activity(user_id):

    try:

        conn = get_db()

        activities = conn.execute("""
            SELECT *
            FROM activity_log

            WHERE user_id = ?

            ORDER BY id DESC

            LIMIT 50
        """, (
            user_id,
        )).fetchall()

        conn.close()

        return jsonify({

            "success":
                True,

            "activities": [

                dict(a)

                for a
                in activities

            ]

        })

    except Exception as e:

        return error_response(
            str(e),
            500
        )


# ============================================================
# 404
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    if request.path.startswith(
        "/api/"
    ):

        return jsonify({

            "success":
                False,

            "error":
                "API endpoint پیدا نشد.",

            "path":
                request.path

        }), 404

    return render_template(
        "index.html"
    )


# ============================================================
# GLOBAL ERROR
# ============================================================

@app.errorhandler(500)
def internal_error(error):

    return jsonify({

        "success":
            False,

        "error":
            "خطای داخلی سرور."

    }), 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("              SMART AI STUDY PLANNER")
    print("=" * 65)

    print()

    print(
        "Website:"
    )

    print(
        "http://127.0.0.1:8000/"
    )

    print()

    print(
        "Dashboard:"
    )

    print(
        "http://127.0.0.1:8000/dashboard"
    )

    print()

    print(
        "Profile:"
    )

    print(
        "http://127.0.0.1:8000/profile"
    )

    print()

    print(
        "Subjects:"
    )

    print(
        "http://127.0.0.1:8000/subjects"
    )

    print()

    print(
        "Planner:"
    )

    print(
        "http://127.0.0.1:8000/planner"
    )

    print()

    print(
        "API:"
    )

    print(
        "http://127.0.0.1:8000/api"
    )

    print()

    print(
        "Health:"
    )

    print(
        "http://127.0.0.1:8000/api/health"
    )

    print()

    print("=" * 65)

    app.run(

        host="0.0.0.0",

        port=PORT,

        debug=True

    )