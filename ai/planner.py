# ============================================================
# SMART AI STUDY PLANNER
# ai/planner.py
#
# Hybrid AI:
#   1. LLM for intelligent planning
#   2. Machine Learning for personalization
#   3. Deterministic optimizer for schedule safety
#
# ============================================================

import os
import json
import re
import math
import urllib.request
import urllib.error

from datetime import datetime, timedelta


# ============================================================
# OPTIONAL MACHINE LEARNING
# ============================================================

try:
    from sklearn.ensemble import RandomForestRegressor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


# ============================================================
# CONFIG
# ============================================================

AI_API_URL = os.getenv(
    "AI_API_URL",
    "http://localhost:11434/v1/chat/completions"
)

AI_API_KEY = os.getenv(
    "AI_API_KEY",
    ""
)

AI_MODEL = os.getenv(
    "AI_MODEL",
    "llama3.2"
)

AI_TIMEOUT = int(
    os.getenv("AI_TIMEOUT", "120")
)


# ============================================================
# DAYS
# ============================================================

DAYS = [
    "Saturday",
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday"
]


# ============================================================
# TIME CONFIG
# ============================================================

DEFAULT_START_HOUR = 16

MIN_SESSION = 25
MAX_SESSION = 90

SHORT_BREAK = 10
LONG_BREAK = 20


# ============================================================
# SAFE CONVERTERS
# ============================================================

def safe_int(value, default=0):

    try:

        if value is None:
            return default

        return int(float(value))

    except (ValueError, TypeError):

        return default


def safe_float(value, default=0.0):

    try:

        if value is None:
            return default

        return float(value)

    except (ValueError, TypeError):

        return default


# ============================================================
# CLAMP
# ============================================================

def clamp(value, minimum, maximum):

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


# ============================================================
# NORMALIZE USER
# ============================================================

def normalize_user_data(user_data):

    if not isinstance(user_data, dict):

        raise ValueError(
            "user_data must be a dictionary"
        )

    name = str(
        user_data.get(
            "name",
            "Student"
        )
    ).strip()

    age = safe_int(
        user_data.get("age"),
        0
    )

    grade = str(
        user_data.get(
            "grade",
            user_data.get(
                "education_level",
                ""
            )
        )
    ).strip()

    daily_hours = safe_float(
        user_data.get(
            "daily_hours",
            user_data.get(
                "study_hours",
                2
            )
        ),
        2
    )

    daily_hours = clamp(
        daily_hours,
        0.5,
        12
    )

    goal = str(
        user_data.get(
            "goal",
            "Improve academic performance"
        )
    ).strip()

    subjects = user_data.get(
        "subjects",
        []
    )

    if not isinstance(subjects, list):

        subjects = []

    normalized = []

    for subject in subjects:

        if isinstance(subject, str):

            normalized.append({
                "name": subject.strip(),
                "importance": 3,
                "required_hours": 2,
                "performance": 50
            })

            continue

        if not isinstance(subject, dict):

            continue

        name_value = str(
            subject.get(
                "name",
                ""
            )
        ).strip()

        if not name_value:

            continue

        importance = safe_int(
            subject.get(
                "importance",
                3
            ),
            3
        )

        required_hours = safe_float(
            subject.get(
                "required_hours",
                2
            ),
            2
        )

        performance = safe_float(
            subject.get(
                "performance",
                subject.get(
                    "score",
                    50
                )
            ),
            50
        )

        importance = clamp(
            importance,
            1,
            5
        )

        required_hours = clamp(
            required_hours,
            0.5,
            30
        )

        performance = clamp(
            performance,
            0,
            100
        )

        normalized.append({

            "name": name_value,

            "importance": importance,

            "required_hours":
                required_hours,

            "performance":
                performance

        })

    return {

        "name": name,

        "age": age,

        "grade": grade,

        "daily_hours":
            daily_hours,

        "goal": goal,

        "subjects":
            normalized
    }


# ============================================================
# STUDY LOAD
# ============================================================

def analyze_study_load(user_data):

    data = normalize_user_data(
        user_data
    )

    daily = data[
        "daily_hours"
    ]

    weekly_available = (
        daily * 7
    )

    weekly_required = sum(

        subject[
            "required_hours"
        ]

        for subject
        in data["subjects"]

    )

    if weekly_available <= 0:

        ratio = 999

    else:

        ratio = (
            weekly_required /
            weekly_available
        )

    if ratio <= 0.75:

        status = "light"

    elif ratio <= 1:

        status = "balanced"

    elif ratio <= 1.25:

        status = "heavy"

    else:

        status = "overloaded"

    return {

        "daily_available_hours":
            round(
                daily,
                2
            ),

        "weekly_available_hours":
            round(
                weekly_available,
                2
            ),

        "weekly_required_hours":
            round(
                weekly_required,
                2
            ),

        "load_ratio":
            round(
                ratio,
                2
            ),

        "status":
            status
    }


# ============================================================
# ML PERSONALIZATION
# ============================================================

def calculate_subject_ai_score(subject):

    importance = (
        safe_float(
            subject.get(
                "importance",
                3
            )
        ) / 5
    )

    required = safe_float(
        subject.get(
            "required_hours",
            2
        )
    )

    performance = safe_float(
        subject.get(
            "performance",
            50
        )
    ) / 100

    weakness = 1 - performance

    score = (

        importance * 0.40

        +

        weakness * 0.40

        +

        min(
            required / 10,
            1
        ) * 0.20

    )

    return round(
        score,
        4
    )


def personalize_subjects(subjects):

    result = []

    for subject in subjects:

        item = dict(
            subject
        )

        item[
            "ai_score"
        ] = calculate_subject_ai_score(
            item
        )

        result.append(
            item
        )

    result.sort(
        key=lambda x:
            x["ai_score"],
        reverse=True
    )

    return result


# ============================================================
# TRAIN PERSONALIZATION MODEL
# ============================================================

def train_personalization_model(
    history
):

    """
    history example:

    [
        {
            "importance": 5,
            "performance": 40,
            "completed_ratio": 0.6,
            "difficulty": 4,
            "duration": 60,
            "success": 0.5
        }
    ]
    """

    if not ML_AVAILABLE:

        return None

    if not isinstance(
        history,
        list
    ):

        return None

    X = []
    y = []

    for row in history:

        if not isinstance(
            row,
            dict
        ):

            continue

        features = [

            safe_float(
                row.get(
                    "importance",
                    3
                )
            ),

            safe_float(
                row.get(
                    "performance",
                    50
                )
            ),

            safe_float(
                row.get(
                    "completed_ratio",
                    0.5
                )
            ),

            safe_float(
                row.get(
                    "difficulty",
                    3
                )
            ),

            safe_float(
                row.get(
                    "duration",
                    60
                )
            )

        ]

        target = safe_float(
            row.get(
                "success",
                0.5
            )
        )

        X.append(
            features
        )

        y.append(
            target
        )

    if len(X) < 10:

        return None

    model = RandomForestRegressor(

        n_estimators=100,

        max_depth=6,

        random_state=42

    )

    model.fit(
        X,
        y
    )

    return model


# ============================================================
# ML PREDICT
# ============================================================

def predict_session_success(
    model,
    subject,
    duration=60,
    completed_ratio=0.5,
    difficulty=3
):

    if model is None:

        return 0.5

    try:

        features = [[

            safe_float(
                subject.get(
                    "importance",
                    3
                )
            ),

            safe_float(
                subject.get(
                    "performance",
                    50
                )
            ),

            safe_float(
                completed_ratio
            ),

            safe_float(
                difficulty
            ),

            safe_float(
                duration
            )

        ]]

        prediction = model.predict(
            features
        )[0]

        return clamp(
            float(prediction),
            0,
            1
        )

    except Exception:

        return 0.5


# ============================================================
# PREPARE AI PROMPT
# ============================================================

def prepare_prompt(
    user_data,
    performance=None,
    history=None
):

    data = normalize_user_data(
        user_data
    )

    analysis = analyze_study_load(
        data
    )

    subjects = personalize_subjects(
        data["subjects"]
    )

    if performance is None:

        performance = {}

    if history is None:

        history = []

    subject_lines = []

    for subject in subjects:

        subject_lines.append(

            "- "
            + subject["name"]
            + "\n"
            + "  importance: "
            + str(
                subject["importance"]
            )
            + "/5\n"
            + "  required weekly hours: "
            + str(
                subject["required_hours"]
            )
            + "\n"
            + "  current performance: "
            + str(
                subject["performance"]
            )
            + "%\n"
            + "  AI priority score: "
            + str(
                subject["ai_score"]
            )

        )

    subject_text = "\n".join(
        subject_lines
    )

    performance_text = json.dumps(
        performance,
        ensure_ascii=False
    )

    prompt = f"""
You are the intelligence engine of a
professional AI Study Planner.

Your job is to create a personalized,
realistic and adaptive weekly study plan.

STUDENT:

Name:
{data["name"]}

Age:
{data["age"]}

Grade:
{data["grade"]}

Goal:
{data["goal"]}

Daily available study:
{data["daily_hours"]} hours

Weekly available study:
{analysis["weekly_available_hours"]} hours

Weekly requested study:
{analysis["weekly_required_hours"]} hours

Workload:
{analysis["status"]}

SUBJECTS:

{subject_text}

PREVIOUS PERFORMANCE:

{performance_text}

AI RULES:

1. Prioritize weak subjects.

2. Prioritize important subjects.

3. Never exceed realistic daily study time.

4. Do not schedule more than 90 minutes
   continuously.

5. Add breaks.

6. Include revision.

7. Include easier sessions after difficult
   sessions.

8. Avoid burnout.

9. If a subject has low performance,
   increase its priority.

10. If a subject has high performance,
    maintain but reduce unnecessary time.

11. Spread difficult subjects across
    different days.

12. Use active recall and practice.

13. Include at least one light day.

14. Do not invent subjects.

15. Return exactly 7 days.

16. Return ONLY JSON.

JSON FORMAT:

{{
    "summary": {{
        "total_study_hours": 0,
        "estimated_completion": 0,
        "difficulty": "balanced",
        "main_focus": ""
    }},

    "week": [

        {{
            "day": "Saturday",

            "sessions": [

                {{
                    "subject": "Math",
                    "start": "16:00",
                    "end": "17:00",
                    "duration": 60,
                    "type": "study",
                    "method": "active_recall"
                }},

                {{
                    "subject": "Break",
                    "start": "17:00",
                    "end": "17:15",
                    "duration": 15,
                    "type": "break",
                    "method": "rest"
                }}

            ]
        }}

    ],

    "recommendations": []

}}
"""

    return prompt


# ============================================================
# CALL AI
# ============================================================

def call_ai_api(prompt):

    payload = {

        "model":
            AI_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    (
                        "You are a professional "
                        "AI study planner. "
                        "Return valid JSON only."
                    )
            },

            {
                "role":
                    "user",

                "content":
                    prompt
            }

        ],

        "temperature":
            0.2,

        "max_tokens":
            8000
    }

    body = json.dumps(
        payload,
        ensure_ascii=False
    ).encode(
        "utf-8"
    )

    headers = {

        "Content-Type":
            "application/json",

        "Accept":
            "application/json"
    }

    if AI_API_KEY:

        headers[
            "Authorization"
        ] = (
            "Bearer "
            + AI_API_KEY
        )

    request = urllib.request.Request(

        AI_API_URL,

        data=body,

        headers=headers,

        method="POST"

    )

    try:

        with urllib.request.urlopen(

            request,

            timeout=AI_TIMEOUT

        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            return json.loads(
                raw
            )

    except urllib.error.HTTPError as error:

        body = ""

        try:

            body = error.read().decode(
                "utf-8"
            )

        except Exception:

            pass

        raise RuntimeError(
            f"AI HTTP {error.code}: {body}"
        )

    except urllib.error.URLError as error:

        raise RuntimeError(
            f"AI connection error: {error}"
        )

    except TimeoutError:

        raise RuntimeError(
            "AI request timed out"
        )


# ============================================================
# EXTRACT AI MESSAGE
# ============================================================

def extract_ai_message(
    response
):

    if not isinstance(
        response,
        dict
    ):

        raise ValueError(
            "Invalid AI response"
        )

    choices = response.get(
        "choices"
    )

    if choices:

        first = choices[0]

        message = first.get(
            "message",
            {}
        )

        content = message.get(
            "content"
        )

        if content:

            return content

        text = first.get(
            "text"
        )

        if text:

            return text

    if "response" in response:

        return response[
            "response"
        ]

    if "content" in response:

        return response[
            "content"
        ]

    raise ValueError(
        "AI message not found"
    )


# ============================================================
# EXTRACT JSON
# ============================================================

def extract_json(text):

    if not text:

        raise ValueError(
            "AI returned empty response"
        )

    text = text.strip()

    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*",
        "",
        text
    )

    text = text.strip()

    try:

        return json.loads(
            text
        )

    except json.JSONDecodeError:

        pass

    start = text.find(
        "{"
    )

    end = text.rfind(
        "}"
    )

    if start == -1:

        raise ValueError(
            "JSON object not found"
        )

    if end == -1:

        raise ValueError(
            "Incomplete JSON"
        )

    json_text = text[
        start:
        end + 1
    ]

    try:

        return json.loads(
            json_text
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid AI JSON: {error}"
        )


# ============================================================
# TIME HELPERS
# ============================================================

def parse_time(value):

    try:

        return datetime.strptime(
            value,
            "%H:%M"
        )

    except Exception:

        return None


def format_time(value):

    return value.strftime(
        "%H:%M"
    )


def calculate_duration(
    start,
    end
):

    start_dt = parse_time(
        start
    )

    end_dt = parse_time(
        end
    )

    if not start_dt or not end_dt:

        return 0

    if end_dt <= start_dt:

        end_dt += timedelta(
            days=1
        )

    return int(
        (
            end_dt -
            start_dt
        ).total_seconds()
        / 60
    )


# ============================================================
# VALIDATE SESSION
# ============================================================

def validate_session(
    session,
    subjects
):

    if not isinstance(
        session,
        dict
    ):

        return None

    session_type = str(
        session.get(
            "type",
            "study"
        )
    ).lower()

    if session_type not in [
        "study",
        "break"
    ]:

        session_type = "study"

    subject = str(
        session.get(
            "subject",
            ""
        )
    ).strip()

    if session_type == "break":

        subject = "Break"

    valid_names = {

        subject["name"]

        for subject
        in subjects
    }

    if (
        session_type == "study"
        and subject not in valid_names
    ):

        return None

    start = str(
        session.get(
            "start",
            ""
        )
    )

    end = str(
        session.get(
            "end",
            ""
        )
    )

    duration = safe_int(
        session.get(
            "duration",
            0
        )
    )

    calculated = calculate_duration(
        start,
        end
    )

    if calculated > 0:

        duration = calculated

    duration = clamp(
        duration,
        5,
        120
    )

    method = str(
        session.get(
            "method",
            "focused_study"
        )
    )

    return {

        "subject":
            subject,

        "start":
            start,

        "end":
            end,

        "duration":
            duration,

        "type":
            session_type,

        "method":
            method
    }


# ============================================================
# VALIDATE PLAN
# ============================================================

def validate_plan(
    plan,
    user_data
):

    data = normalize_user_data(
        user_data
    )

    if not isinstance(
        plan,
        dict
    ):

        raise ValueError(
            "AI plan must be object"
        )

    week = plan.get(
        "week",
        []
    )

    if not isinstance(
        week,
        list
    ):

        week = []

    day_map = {}

    for day in week:

        if not isinstance(
            day,
            dict
        ):

            continue

        name = str(
            day.get(
                "day",
                ""
            )
        ).strip()

        if name in DAYS:

            day_map[
                name
            ] = day

    final_week = []

    for day_name in DAYS:

        source = day_map.get(
            day_name,
            {}
        )

        sessions = source.get(
            "sessions",
            []
        )

        if not isinstance(
            sessions,
            list
        ):

            sessions = []

        valid_sessions = []

        for session in sessions:

            valid = validate_session(

                session,

                data[
                    "subjects"
                ]

            )

            if valid:

                valid_sessions.append(
                    valid
                )

        final_week.append({

            "day":
                day_name,

            "sessions":
                valid_sessions
        })

    # ========================================================
    # REAL STUDY HOURS
    # ========================================================

    total_minutes = 0

    for day in final_week:

        for session in day[
            "sessions"
        ]:

            if session[
                "type"
            ] == "study":

                total_minutes += (
                    session[
                        "duration"
                    ]
                )

    total_hours = round(
        total_minutes / 60,
        2
    )

    available = (
        data[
            "daily_hours"
        ] * 7
    )

    if available > 0:

        completion = round(

            min(
                100,
                (
                    total_hours /
                    available
                ) * 100
            ),

            1

        )

    else:

        completion = 0

    subjects = personalize_subjects(
        data["subjects"]
    )

    main_focus = (
        subjects[0]["name"]
        if subjects
        else ""
    )

    summary = plan.get(
        "summary",
        {}
    )

    if not isinstance(
        summary,
        dict
    ):

        summary = {}

    recommendations = plan.get(
        "recommendations",
        []
    )

    if not isinstance(
        recommendations,
        list
    ):

        recommendations = []

    recommendations = [

        str(x).strip()

        for x in recommendations

        if str(x).strip()

    ][:10]

    return {

        "summary": {

            "total_study_hours":
                total_hours,

            "estimated_completion":
                completion,

            "difficulty":
                summary.get(
                    "difficulty",
                    "balanced"
                ),

            "main_focus":
                main_focus

        },

        "week":
            final_week,

        "recommendations":
            recommendations
    }


# ============================================================
# LOCAL SMART FALLBACK
# ============================================================

def generate_local_plan(
    user_data
):

    data = normalize_user_data(
        user_data
    )

    subjects = personalize_subjects(
        data["subjects"]
    )

    if not subjects:

        return {

            "summary": {

                "total_study_hours":
                    0,

                "estimated_completion":
                    0,

                "difficulty":
                    "light",

                "main_focus":
                    ""

            },

            "week": [

                {
                    "day":
                        day,

                    "sessions":
                        []
                }

                for day in DAYS
            ],

            "recommendations": [

                "ابتدا درس‌های خود را اضافه کنید."

            ]

        }

    daily_minutes = int(

        data[
            "daily_hours"
        ] * 60

    )

    daily_minutes = max(
        30,
        daily_minutes
    )

    final_week = []

    subject_index = 0

    for day_index, day in enumerate(
        DAYS
    ):

        sessions = []

        remaining = daily_minutes

        current_minutes = (
            DEFAULT_START_HOUR * 60
        )

        session_count = 0

        while remaining >= MIN_SESSION:

            subject = subjects[
                subject_index %
                len(subjects)
            ]

            # weak subjects get longer sessions
            if subject[
                "ai_score"
            ] >= 0.65:

                duration = 60

            else:

                duration = 45

            duration = min(
                duration,
                remaining
            )

            if duration < MIN_SESSION:

                break

            start = (
                f"{current_minutes // 60:02d}:"
                f"{current_minutes % 60:02d}"
            )

            end_minutes = (
                current_minutes +
                duration
            )

            end = (
                f"{(end_minutes // 60) % 24:02d}:"
                f"{end_minutes % 60:02d}"
            )

            sessions.append({

                "subject":
                    subject["name"],

                "start":
                    start,

                "end":
                    end,

                "duration":
                    duration,

                "type":
                    "study",

                "method":
                    (
                        "active_recall"
                        if subject[
                            "performance"
                        ] < 60
                        else
                        "practice"
                    )

            })

            remaining -= duration

            current_minutes = end_minutes

            subject_index += 1

            session_count += 1

            if (
                remaining >= SHORT_BREAK
                and
                session_count < 3
            ):

                break_duration = (
                    LONG_BREAK
                    if session_count == 2
                    else SHORT_BREAK
                )

                break_start = (
                    f"{current_minutes // 60:02d}:"
                    f"{current_minutes % 60:02d}"
                )

                current_minutes += (
                    break_duration
                )

                break_end = (
                    f"{current_minutes // 60:02d}:"
                    f"{current_minutes % 60:02d}"
                )

                sessions.append({

                    "subject":
                        "Break",

                    "start":
                        break_start,

                    "end":
                        break_end,

                    "duration":
                        break_duration,

                    "type":
                        "break",

                    "method":
                        "rest"

                })

            if session_count >= 3:

                break

        final_week.append({

            "day":
                day,

            "sessions":
                sessions

        })

    return validate_plan(

        {
            "week":
                final_week,

            "summary":
                {
                    "difficulty":
                        "balanced"
                },

            "recommendations":
                [
                    "از Active Recall استفاده کنید.",
                    "بین جلسات استراحت داشته باشید.",
                    "درس‌های ضعیف‌تر را در ابتدای زمان مطالعه قرار دهید."
                ]

        },

        data

    )


# ============================================================
# GENERATE PLAN
# ============================================================

def generate_plan(

    user_data,

    use_fallback=True,

    history=None,

    performance=None

):

    data = normalize_user_data(
        user_data
    )

    prompt = prepare_prompt(

        data,

        performance,

        history

    )

    try:

        response = call_ai_api(
            prompt
        )

        text = extract_ai_message(
            response
        )

        raw_plan = extract_json(
            text
        )

        final_plan = validate_plan(

            raw_plan,

            data

        )

        return {

            "success":
                True,

            "source":
                "ai",

            "ai_model":
                AI_MODEL,

            "ml_enabled":
                ML_AVAILABLE,

            "plan":
                final_plan

        }

    except Exception as error:

        if not use_fallback:

            return {

                "success":
                    False,

                "source":
                    "ai",

                "error":
                    str(error)

            }

        fallback = generate_local_plan(
            data
        )

        return {

            "success":
                True,

            "source":
                "fallback",

            "warning":
                str(error),

            "ml_enabled":
                ML_AVAILABLE,

            "plan":
                fallback

        }


# ============================================================
# REBALANCE
# ============================================================

def rebalance_plan(

    user_data,

    completed_sessions=0,

    missed_sessions=0,

    previous_plan=None,

    history=None

):

    performance = {

        "completed_sessions":
            safe_int(
                completed_sessions
            ),

        "missed_sessions":
            safe_int(
                missed_sessions
            ),

        "completion_ratio":
            (
                safe_int(
                    completed_sessions
                )
                /
                max(
                    1,
                    (
                        safe_int(
                            completed_sessions
                        )
                        +
                        safe_int(
                            missed_sessions
                        )
                    )
                )
            )

    }

    if previous_plan:

        performance[
            "previous_plan"
        ] = previous_plan

    return generate_plan(

        user_data,

        use_fallback=True,

        history=history,

        performance=performance

    )


# ============================================================
# OPTIMIZE NEXT WEEK
# ============================================================

def optimize_next_week(

    user_data,

    performance=None,

    history=None

):

    if performance is None:

        performance = {}

    performance = dict(
        performance
    )

    performance[
        "optimization"
    ] = True

    return generate_plan(

        user_data,

        use_fallback=True,

        history=history,

        performance=performance

    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_user = {

        "name":
            "Student",

        "age":
            13,

        "grade":
            "7",

        "daily_hours":
            4,

        "goal":
            "آمادگی برای امتحانات",

        "subjects": [

            {
                "name":
                    "ریاضی",

                "importance":
                    5,

                "required_hours":
                    8,

                "performance":
                    45
            },

            {
                "name":
                    "علوم",

                "importance":
                    4,

                "required_hours":
                    6,

                "performance":
                    65
            },

            {
                "name":
                    "انگلیسی",

                "importance":
                    3,

                "required_hours":
                    4,

                "performance":
                    80
            },

            {
                "name":
                    "فارسی",

                "importance":
                    3,

                "required_hours":
                    4,

                "performance":
                    70
            }

        ]

    }

    result = generate_plan(

        test_user,

        use_fallback=True

    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    )