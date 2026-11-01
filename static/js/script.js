"use strict";

/* =========================================================
   SMART AI STUDY PLANNER
   MAIN JAVASCRIPT
   ========================================================= */

/* =========================================================
   CONFIG
   ========================================================= */

const API_BASE = "/api";

const STORAGE_KEYS = {
    USER_ID: "smart_study_user_id",
    USER: "smart_study_user"
};


/* =========================================================
   GLOBAL STATE
   ========================================================= */

let currentUser = null;
let subjects = [];
let currentPlan = null;


/* =========================================================
   INIT
   ========================================================= */

document.addEventListener("DOMContentLoaded", async () => {

    console.log(
        "Smart AI Study Planner started"
    );

    loadStoredUser();

    setupNavigation();
    setupProfileForm();
    setupSubjectForm();
    setupAIButtons();
    setupProgressHandlers();

    await initializePage();

});


/* =========================================================
   PAGE INITIALIZATION
   ========================================================= */

async function initializePage() {

    const userId = getUserId();

    if (!userId) {

        console.log(
            "No user found."
        );

        return;
    }

    try {

        await loadProfile(userId);

        await loadSubjects(userId);

        await loadDashboard(userId);

        await loadLatestPlan(userId);

    } catch (error) {

        console.error(
            "Initialization error:",
            error
        );

    }
}


/* =========================================================
   API HELPER
   ========================================================= */

async function apiRequest(
    endpoint,
    options = {}
) {

    try {

        const response =
            await fetch(
                `${API_BASE}${endpoint}`,
                {
                    headers: {
                        "Content-Type":
                            "application/json",

                        ...(options.headers || {})
                    },

                    ...options
                }
            );

        let data;

        try {

            data =
                await response.json();

        } catch {

            data = {
                success: false,
                error:
                    "Invalid server response"
            };

        }

        if (!response.ok) {

            throw new Error(
                data.error ||
                data.message ||
                `HTTP ${response.status}`
            );

        }

        return data;

    } catch (error) {

        console.error(
            "API Error:",
            endpoint,
            error
        );

        showNotification(
            error.message ||
            "خطا در ارتباط با سرور",
            "error"
        );

        throw error;

    }

}


/* =========================================================
   USER STORAGE
   ========================================================= */

function saveUser(user) {

    if (!user)
        return;

    currentUser =
        user;

    localStorage.setItem(
        STORAGE_KEYS.USER_ID,
        user.id
    );

    localStorage.setItem(
        STORAGE_KEYS.USER,
        JSON.stringify(user)
    );

}


function loadStoredUser() {

    const userJSON =
        localStorage.getItem(
            STORAGE_KEYS.USER
        );

    const userId =
        localStorage.getItem(
            STORAGE_KEYS.USER_ID
        );

    if (userJSON) {

        try {

            currentUser =
                JSON.parse(
                    userJSON
                );

        } catch {

            currentUser =
                null;

        }

    }

    if (
        !currentUser &&
        userId
    ) {

        currentUser = {
            id: userId
        };

    }

}


function getUserId() {

    return (
        currentUser?.id ||
        localStorage.getItem(
            STORAGE_KEYS.USER_ID
        )
    );

}


function clearUser() {

    currentUser =
        null;

    subjects =
        [];

    currentPlan =
        null;

    localStorage.removeItem(
        STORAGE_KEYS.USER_ID
    );

    localStorage.removeItem(
        STORAGE_KEYS.USER
    );

}


/* =========================================================
   PROFILE
   ========================================================= */

function setupProfileForm() {

    const form =
        document.querySelector(
            "#profileForm"
        );

    if (!form)
        return;

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const name =
                getInputValue(
                    form,
                    [
                        "#name",
                        "[name='name']"
                    ]
                );

            const age =
                getInputValue(
                    form,
                    [
                        "#age",
                        "[name='age']"
                    ]
                );

            const grade =
                getInputValue(
                    form,
                    [
                        "#grade",
                        "[name='grade']"
                    ]
                );

            const dailyHours =
                getInputValue(
                    form,
                    [
                        "#daily_hours",
                        "#dailyHours",
                        "[name='daily_hours']"
                    ]
                );

            const goal =
                getInputValue(
                    form,
                    [
                        "#goal",
                        "[name='goal']"
                    ]
                );

            if (!name) {

                showNotification(
                    "لطفاً نام را وارد کنید.",
                    "error"
                );

                return;
            }

            const button =
                form.querySelector(
                    "button[type='submit']"
                );

            try {

                setButtonLoading(
                    button,
                    true,
                    "در حال ذخیره..."
                );

                const result =
                    await apiRequest(
                        "/profile",
                        {
                            method: "POST",

                            body:
                                JSON.stringify({

                                    name:
                                        name,

                                    age:
                                        Number(age) || 0,

                                    grade:
                                        grade || "",

                                    daily_hours:
                                        Number(
                                            dailyHours
                                        ) || 2,

                                    goal:
                                        goal || ""

                                })
                        }
                    );

                if (
                    result.success &&
                    result.user
                ) {

                    saveUser(
                        result.user
                    );

                    showNotification(
                        "پروفایل با موفقیت ساخته شد.",
                        "success"
                    );

                    updateUserUI(
                        result.user
                    );

                    setTimeout(
                        () => {
                            window.location.href =
                                "/dashboard";
                        },
                        700
                    );

                }

            } catch (error) {

                console.error(
                    error
                );

            } finally {

                setButtonLoading(
                    button,
                    false
                );

            }

        }
    );

}


async function loadProfile(
    userId
) {

    if (!userId)
        return null;

    try {

        const result =
            await apiRequest(
                `/profile/${encodeURIComponent(
                    userId
                )}`
            );

        if (
            result.success &&
            result.user
        ) {

            saveUser(
                result.user
            );

            subjects =
                result.subjects || [];

            updateUserUI(
                result.user
            );

            renderSubjects(
                subjects
            );

        }

        return result;

    } catch (error) {

        console.error(
            "Profile loading failed:",
            error
        );

        return null;

    }

}


/* =========================================================
   UPDATE USER UI
   ========================================================= */

function updateUserUI(
    user
) {

    if (!user)
        return;

    setText(
        [
            "#userName",
            "#profileName",
            ".user-name",
            "[data-user-name]"
        ],
        user.name || ""
    );

    setText(
        [
            "#userAge",
            "[data-user-age]"
        ],
        user.age || "-"
    );

    setText(
        [
            "#userGrade",
            "[data-user-grade]"
        ],
        user.grade || "-"
    );

    setText(
        [
            "#userGoal",
            "[data-user-goal]"
        ],
        user.goal || "-"
    );

    setInputValue(
        [
            "#name",
            "[name='name']"
        ],
        user.name
    );

    setInputValue(
        [
            "#age",
            "[name='age']"
        ],
        user.age
    );

    setInputValue(
        [
            "#grade",
            "[name='grade']"
        ],
        user.grade
    );

    setInputValue(
        [
            "#daily_hours",
            "#dailyHours",
            "[name='daily_hours']"
        ],
        user.daily_hours
    );

    setInputValue(
        [
            "#goal",
            "[name='goal']"
        ],
        user.goal
    );

}


/* =========================================================
   SUBJECTS
   ========================================================= */

function setupSubjectForm() {

    const form =
        document.querySelector(
            "#subjectForm"
        );

    if (!form)
        return;

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const userId =
                getUserId();

            if (!userId) {

                showNotification(
                    "ابتدا یک کاربر بسازید.",
                    "error"
                );

                return;
            }

            const name =
                getInputValue(
                    form,
                    [
                        "#subjectName",
                        "#name",
                        "[name='name']"
                    ]
                );

            const importance =
                getInputValue(
                    form,
                    [
                        "#importance",
                        "[name='importance']"
                    ]
                );

            const requiredHours =
                getInputValue(
                    form,
                    [
                        "#requiredHours",
                        "#required_hours",
                        "[name='required_hours']"
                    ]
                );

            if (!name) {

                showNotification(
                    "نام درس را وارد کنید.",
                    "error"
                );

                return;
            }

            const button =
                form.querySelector(
                    "button[type='submit']"
                );

            try {

                setButtonLoading(
                    button,
                    true,
                    "در حال ذخیره..."
                );

                const result =
                    await apiRequest(
                        "/subjects",
                        {
                            method: "POST",

                            body:
                                JSON.stringify({

                                    user_id:
                                        userId,

                                    name:
                                        name,

                                    importance:
                                        Number(
                                            importance
                                        ) || 3,

                                    required_hours:
                                        Number(
                                            requiredHours
                                        ) || 2

                                })
                        }
                    );

                if (
                    result.success
                ) {

                    showNotification(
                        "درس اضافه شد.",
                        "success"
                    );

                    form.reset();

                    await loadSubjects(
                        userId
                    );

                    await loadDashboard(
                        userId
                    );

                }

            } catch (error) {

                console.error(
                    error
                );

            } finally {

                setButtonLoading(
                    button,
                    false
                );

            }

        }
    );

}


async function loadSubjects(
    userId
) {

    if (!userId)
        return;

    try {

        const result =
            await apiRequest(
                `/subjects/${encodeURIComponent(
                    userId
                )}`
            );

        if (
            result.success
        ) {

            subjects =
                result.subjects || [];

            renderSubjects(
                subjects
            );

        }

        return result;

    } catch (error) {

        console.error(
            "Subjects loading failed:",
            error
        );

        return null;

    }

}


/* =========================================================
   RENDER SUBJECTS
   ========================================================= */

function renderSubjects(
    list
) {

    const containers =
        document.querySelectorAll(
            "#subjectsList, #subjectList, .subjects-list"
        );

    if (!containers.length)
        return;

    containers.forEach(
        container => {

            if (!list.length) {

                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">
                            📚
                        </div>

                        <p>
                            هنوز درسی اضافه نشده است.
                        </p>
                    </div>
                `;

                return;
            }

            container.innerHTML =
                list.map(
                    subject => {

                        const progress =
                            Number(
                                subject.progress
                            ) || 0;

                        const importance =
                            Number(
                                subject.importance
                            ) || 3;

                        return `
                            <div
                                class="subject-card"
                                data-subject-id="${subject.id}"
                            >

                                <div
                                    class="subject-card-header"
                                >

                                    <div>

                                        <h3>
                                            ${escapeHTML(
                                                subject.name
                                            )}
                                        </h3>

                                        <span>
                                            اهمیت:
                                            ${importance}/5
                                        </span>

                                    </div>

                                    <button
                                        class="delete-subject"
                                        data-id="${subject.id}"
                                        type="button"
                                    >
                                        🗑️
                                    </button>

                                </div>

                                <div
                                    class="subject-info"
                                >

                                    <span>
                                        ⏱️
                                        ${subject.required_hours}
                                        ساعت
                                    </span>

                                    <span>
                                        📈
                                        ${progress}%
                                    </span>

                                </div>

                                <div
                                    class="progress-wrapper"
                                >

                                    <div
                                        class="progress-bar"
                                    >

                                        <div
                                            class="progress-fill"
                                            style="
                                                width:${progress}%
                                            "
                                        ></div>

                                    </div>

                                </div>

                            </div>
                        `;

                    }
                ).join("");

            container
                .querySelectorAll(
                    ".delete-subject"
                )
                .forEach(
                    button => {

                        button.addEventListener(
                            "click",
                            () => {

                                deleteSubject(
                                    button.dataset.id
                                );

                            }
                        );

                    }
                );

        }
    );

}


/* =========================================================
   DELETE SUBJECT
   ========================================================= */

async function deleteSubject(
    subjectId
) {

    if (!subjectId)
        return;

    if (
        !confirm(
            "آیا از حذف این درس مطمئن هستید؟"
        )
    ) {
        return;
    }

    try {

        const result =
            await apiRequest(
                `/subjects/${subjectId}`,
                {
                    method: "DELETE"
                }
            );

        if (
            result.success
        ) {

            showNotification(
                "درس حذف شد.",
                "success"
            );

            await loadSubjects(
                getUserId()
            );

            await loadDashboard(
                getUserId()
            );

        }

    } catch (error) {

        console.error(
            error
        );

    }

}


/* =========================================================
   DASHBOARD
   ========================================================= */

async function loadDashboard(
    userId
) {

    if (!userId)
        return;

    try {

        const result =
            await apiRequest(
                `/dashboard/${encodeURIComponent(
                    userId
                )}`
            );

        if (
            !result.success
        ) {
            return;
        }

        updateDashboard(
            result
        );

        return result;

    } catch (error) {

        console.error(
            "Dashboard loading failed:",
            error
        );

        return null;

    }

}


function updateDashboard(
    data
) {

    const stats =
        data.statistics || {};

    setText(
        [
            "#plannedMinutes",
            "[data-planned]"
        ],
        formatMinutes(
            stats.planned_minutes || 0
        )
    );

    setText(
        [
            "#completedMinutes",
            "[data-completed]"
        ],
        formatMinutes(
            stats.completed_minutes || 0
        )
    );

    setText(
        [
            "#remainingMinutes",
            "[data-remaining]"
        ],
        formatMinutes(
            stats.remaining_minutes || 0
        )
    );

    setText(
        [
            "#overallProgress",
            "[data-progress]"
        ],
        `${stats.progress || 0}%`
    );

    setText(
        "#dashboardCompleted",
        formatMinutes(
            stats.completed_minutes || 0
        )
    );

    setText(
        "#dashboardRemaining",
        formatMinutes(
            stats.remaining_minutes || 0
        )
    );

    setText(
        "#circleProgress",
        `${stats.progress || 0}%`
    );

    updateProgressBars(
        stats.progress || 0
    );

    if (data.subjects) {

        renderDashboardSubjects(
            data.subjects
        );

    }

    if (data.sessions) {

        renderTodaySessions(
            data.sessions
        );

    }

}


/* =========================================================
   DASHBOARD SUBJECTS
   ========================================================= */

function renderDashboardSubjects(
    list
) {

    const container =
        document.querySelector(
            "#dashboardSubjects"
        );

    if (!container)
        return;

    if (!list.length) {

        container.innerHTML = `
            <p class="empty-state">
                هنوز درسی ثبت نشده است.
            </p>
        `;

        return;
    }

    container.innerHTML =
        list.map(
            subject => {

                const progress =
                    Number(
                        subject.progress
                    ) || 0;

                return `
                    <div
                        class="dashboard-subject"
                    >

                        <div
                            class="dashboard-subject-top"
                        >

                            <strong>
                                ${escapeHTML(
                                    subject.name
                                )}
                            </strong>

                            <span>
                                ${progress}%
                            </span>

                        </div>

                        <div
                            class="progress-bar"
                        >

                            <div
                                class="progress-fill"
                                style="
                                    width:${progress}%
                                "
                            ></div>

                        </div>

                    </div>
                `;

            }
        ).join("");

}


/* =========================================================
   TODAY SESSIONS
   ========================================================= */

function renderTodaySessions(sessions) {

    const container =
        document.querySelector("#todaySessions");

    if (!container) return;

    if (!sessions || !sessions.length) {

        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📚</div>
                <p>برای امروز برنامه‌ای وجود ندارد.</p>
            </div>
        `;

        return;
    }

    container.innerHTML = sessions
        .map(session => {

            const completed =
                Number(session.completed) === 1;

            const start =
                session.start_time || "";

            const end =
                session.end_time || "";

            return `
                <div class="study-session ${
                    completed ? "completed" : ""
                }">

                    <div class="session-time">

                        <strong>
                            ${escapeHTML(start)}
                        </strong>

                        <span>
                            تا ${escapeHTML(end)}
                        </span>

                    </div>

                    <div class="session-content">

                        <h4>
                            ${escapeHTML(
                                session.subject_name ||
                                (
                                    session.session_type === "break"
                                        ? "استراحت"
                                        : "مطالعه"
                                )
                            )}
                        </h4>

                        <span>
                            ${Number(session.duration) || 0}
                            دقیقه
                        </span>

                    </div>

                    <button
                        class="session-complete"
                        data-session-id="${session.id}"
                        type="button"
                        aria-label="تکمیل جلسه"
                    >
                        ${
                            completed
                                ? "✓"
                                : "○"
                        }
                    </button>

                </div>
            `;
        })
        .join("");
}


/* =========================================================
   AI BUTTONS
   ========================================================= */

function setupAIButtons() {

    document.addEventListener(
        "click",
        event => {

            const generateButton =
                event.target.closest(
                    "#generatePlan, #generateAIPlan, [data-action='generate-plan']"
                );

            if (generateButton) {

                generateAIPlan(
                    generateButton
                );

                return;
            }


            const optimizeButton =
                event.target.closest(
                    "#optimizePlan, [data-action='optimize']"
                );

            if (optimizeButton) {

                optimizePlan(
                    optimizeButton
                );

                return;
            }


            const rebalanceButton =
                event.target.closest(
                    "#rebalancePlan, [data-action='rebalance']"
                );

            if (rebalanceButton) {

                rebalancePlan(
                    rebalanceButton
                );

            }

        }
    );

}


/* =========================================================
   GENERATE AI PLAN
   ========================================================= */

async function generateAIPlan(
    button = null
) {

    const userId =
        getUserId();

    if (!userId) {

        showNotification(
            "ابتدا پروفایل کاربر را بسازید.",
            "error"
        );

        return;
    }

    if (!subjects.length) {

        await loadSubjects(
            userId
        );

    }

    if (!subjects.length) {

        showNotification(
            "ابتدا حداقل یک درس اضافه کنید.",
            "error"
        );

        return;
    }

    try {

        setButtonLoading(
            button,
            true,
            "در حال ساخت برنامه..."
        );

        const result =
            await apiRequest(
                "/ai/generate-plan",
                {
                    method: "POST",

                    body:
                        JSON.stringify({
                            user_id:
                                userId
                        })
                }
            );

        if (
            result.success
        ) {

            currentPlan =
                result.plan;

            showNotification(
                "برنامه مطالعه با موفقیت ساخته شد 🤖",
                "success"
            );

            renderPlan(
                result.plan
            );

            await loadLatestPlan(
                userId
            );

            await loadDashboard(
                userId
            );

        }

        return result;

    } catch (error) {

        console.error(
            "AI plan error:",
            error
        );

    } finally {

        setButtonLoading(
            button,
            false
        );

    }

}


/* =========================================================
   OPTIMIZE PLAN
   ========================================================= */

async function optimizePlan(
    button = null
) {

    const userId =
        getUserId();

    if (!userId) {

        showNotification(
            "کاربر پیدا نشد.",
            "error"
        );

        return;
    }

    try {

        setButtonLoading(
            button,
            true,
            "در حال بهینه‌سازی..."
        );

        const result =
            await apiRequest(
                "/ai/optimize",
                {
                    method: "POST",

                    body:
                        JSON.stringify({
                            user_id:
                                userId
                        })
                }
            );

        if (
            result.success
        ) {

            currentPlan =
                result.plan ||
                result.optimized_plan;

            renderPlan(
                currentPlan
            );

            showNotification(
                "برنامه بهینه شد ✨",
                "success"
            );

            await loadDashboard(
                userId
            );

        }

        return result;

    } catch (error) {

        console.error(
            "Optimize error:",
            error
        );

    } finally {

        setButtonLoading(
            button,
            false
        );

    }

}


/* =========================================================
   REBALANCE PLAN
   ========================================================= */

async function rebalancePlan(
    button = null
) {

    const userId =
        getUserId();

    if (!userId)
        return;

    try {

        setButtonLoading(
            button,
            true,
            "در حال تنظیم مجدد..."
        );

        const result =
            await apiRequest(
                "/ai/rebalance",
                {
                    method: "POST",

                    body:
                        JSON.stringify({
                            user_id:
                                userId
                        })
                }
            );

        if (
            result.success
        ) {

            currentPlan =
                result.plan ||
                result.rebalanced_plan;

            renderPlan(
                currentPlan
            );

            showNotification(
                "برنامه مجدداً تنظیم شد 🔄",
                "success"
            );

            await loadDashboard(
                userId
            );

        }

        return result;

    } catch (error) {

        console.error(
            "Rebalance error:",
            error
        );

    } finally {

        setButtonLoading(
            button,
            false
        );

    }

}


/* =========================================================
   LOAD LATEST PLAN
   ========================================================= */

async function loadLatestPlan(
    userId
) {

    if (!userId)
        return;

    try {

        const result =
            await apiRequest(
                `/plans/${encodeURIComponent(
                    userId
                )}/latest`
            );

        if (
            result.success
        ) {

            currentPlan =
                result.plan;

            renderPlan(
                result.plan
            );

        }

        return result;

    } catch {

        console.log(
            "No latest plan."
        );

        return null;

    }

}


/* =========================================================
   RENDER PLAN
   ========================================================= */

function renderPlan(
    plan
) {

    if (!plan)
        return;

    const container =
        document.querySelector(
            "#studyPlan, #planContainer, .study-plan"
        );

    if (!container)
        return;

    /*
       بعضی نسخه‌های planner.py ممکن است
       plan را داخل result.plan برگردانند.
    */

    if (
        plan.plan &&
        typeof plan.plan === "object"
    ) {

        plan =
            plan.plan;

    }

    const week =
        plan.week ||
        plan.days ||
        [];

    if (!Array.isArray(week)) {

        container.innerHTML = `
            <div class="empty-state">
                <p>
                    ساختار برنامه معتبر نیست.
                </p>
            </div>
        `;

        return;
    }

    if (!week.length) {

        container.innerHTML = `
            <div class="empty-state">
                <p>
                    برنامه‌ای برای نمایش وجود ندارد.
                </p>
            </div>
        `;

        return;
    }

    container.innerHTML =
        week.map(
            day => {

                const sessions =
                    day.sessions ||
                    day.schedule ||
                    [];

                return `
                    <div
                        class="plan-day"
                    >

                        <div
                            class="plan-day-header"
                        >

                            <h3>
                                📅
                                ${escapeHTML(
                                    day.day ||
                                    day.date ||
                                    "روز"
                                )}
                            </h3>

                        </div>

                        <div
                            class="plan-sessions"
                        >

                            ${
                                sessions.length
                                    ? sessions
                                        .map(
                                            session =>
                                                renderPlanSession(
                                                    session
                                                )
                                        )
                                        .join("")
                                    : `
                                        <p>
                                            برنامه‌ای ثبت نشده.
                                        </p>
                                    `
                            }

                        </div>

                    </div>
                `;

            }
        ).join("");

}


/* =========================================================
   PLAN SESSION
   ========================================================= */

function renderPlanSession(
    session
) {

    const type =
        session.type ||
        session.session_type ||
        "study";

    const isBreak =
        type === "break" ||
        type === "استراحت" ||
        type === "rest";

    return `
        <div
            class="plan-session ${
                isBreak
                    ? "break-session"
                    : ""
            }"
        >

            <div
                class="plan-session-time"
            >

                <strong>
                    ${
                        session.start ||
                        session.start_time ||
                        ""
                    }
                </strong>

                <span>
                    -
                </span>

                <strong>
                    ${
                        session.end ||
                        session.end_time ||
                        ""
                    }
                </strong>

            </div>

            <div
                class="plan-session-info"
            >

                <h4>

                    ${
                        isBreak
                            ? "☕ استراحت"
                            : `📚 ${
                                escapeHTML(
                                    session.subject ||
                                    session.subject_name ||
                                    "مطالعه"
                                )
                            }`
                    }

                </h4>

                <span>
                    ${
                        session.duration ||
                        0
                    }
                    دقیقه
                </span>

            </div>

        </div>
    `;

}


/* =========================================================
   PROGRESS
   ========================================================= */

function setupProgressHandlers() {

    document.addEventListener(
        "click",
        event => {

            const button =
                event.target.closest(
                    ".session-complete"
                );

            if (!button)
                return;

            const sessionId =
                button.dataset.sessionId;

            if (!sessionId)
                return;

            markSessionComplete(
                sessionId
            );

        }
    );

}


/*
   فعلاً endpoint تکمیل session در نسخه
   فعلی app.py مشخص نشده؛ بنابراین این تابع
   درخواست ساختگی ارسال نمی‌کند.
*/

async function markSessionComplete(
    sessionId
) {

    console.log(
        "Complete session:",
        sessionId
    );

    showNotification(
        "این قابلیت بعد از اضافه شدن API جلسه فعال می‌شود.",
        "info"
    );

}


/* =========================================================
   UPDATE SUBJECT PROGRESS
   ========================================================= */

async function updateSubjectProgress(
    subjectId,
    progress
) {

    const userId =
        getUserId();

    if (
        !userId ||
        !subjectId
    ) {
        return;
    }

    try {

        const result =
            await apiRequest(
                "/progress",
                {
                    method: "POST",

                    body:
                        JSON.stringify({

                            user_id:
                                userId,

                            subject_id:
                                Number(
                                    subjectId
                                ),

                            progress:
                                Number(
                                    progress
                                )

                        })
                }
            );

        if (
            result.success
        ) {

            showNotification(
                "پیشرفت ذخیره شد.",
                "success"
            );

            await loadSubjects(
                userId
            );

            await loadDashboard(
                userId
            );

        }

        return result;

    } catch (error) {

        console.error(
            error
        );

    }

}


/* =========================================================
   PROGRESS BARS
   ========================================================= */

function updateProgressBars(
    progress
) {

    document
        .querySelectorAll(
            ".overall-progress-fill, [data-progress-bar]"
        )
        .forEach(
            bar => {

                const value =
                    Math.max(
                        0,
                        Math.min(
                            100,
                            Number(progress) || 0
                        )
                    );

                bar.style.width =
                    `${value}%`;

            }
        );

}


/* =========================================================
   NAVIGATION
   ========================================================= */

function setupNavigation() {

    document.addEventListener(
        "click",
        event => {

            const link =
                event.target.closest(
                    "[data-page]"
                );

            if (!link)
                return;

            const page =
                link.dataset.page;

            if (!page)
                return;

            const routes = {

                home:
                    "/",

                dashboard:
                    "/dashboard",

                profile:
                    "/profile",

                subjects:
                    "/subjects",

                planner:
                    "/planner"

            };

            if (
                routes[page]
            ) {

                event.preventDefault();

                window.location.href =
                    routes[page];

            }

        }
    );

}


/* =========================================================
   NOTIFICATION
   ========================================================= */

function showNotification(
    message,
    type = "info"
) {

    let container =
        document.querySelector(
            "#notifications"
        );

    if (!container) {

        container =
            document.createElement(
                "div"
            );

        container.id =
            "notifications";

        container.className =
            "notifications";

        document.body.appendChild(
            container
        );

    }

    const notification =
        document.createElement(
            "div"
        );

    notification.className =
        `notification notification-${type}`;

    notification.textContent =
        message;

    container.appendChild(
        notification
    );

    setTimeout(
        () => {

            notification.classList.add(
                "hide"
            );

            setTimeout(
                () => {
                    notification.remove();
                },
                300
            );

        },
        3000
    );

}


/* =========================================================
   BUTTON LOADING
   ========================================================= */

function setButtonLoading(
    button,
    loading,
    loadingText = "در حال پردازش..."
) {

    if (!button)
        return;

    if (loading) {

        button.dataset.originalText =
            button.innerHTML;

        button.disabled =
            true;

        button.innerHTML = `
            <span class="loading-spinner"></span>
            ${loadingText}
        `;

    } else {

        button.disabled =
            false;

        if (
            button.dataset.originalText
        ) {

            button.innerHTML =
                button.dataset.originalText;

        }

    }

}


/* =========================================================
   DOM HELPERS
   ========================================================= */

function getInputValue(
    parent,
    selectors
) {

    for (
        const selector of selectors
    ) {

        const element =
            parent.querySelector(
                selector
            );

        if (element) {

            return (
                element.value || ""
            ).trim();

        }

    }

    return "";

}


function setText(
    selectors,
    value
) {

    if (
        !Array.isArray(
            selectors
        )
    ) {

        selectors =
            [selectors];

    }

    selectors.forEach(
        selector => {

            document
                .querySelectorAll(
                    selector
                )
                .forEach(
                    element => {

                        element.textContent =
                            value ?? "";

                    }
                );

        }
    );

}


function setInputValue(
    selectors,
    value
) {

    if (
        !Array.isArray(
            selectors
        )
    ) {

        selectors =
            [selectors];

    }

    selectors.forEach(
        selector => {

            const element =
                document.querySelector(
                    selector
                );

            if (element) {

                element.value =
                    value ?? "";

            }

        }
    );

}


/* =========================================================
   FORMAT
   ========================================================= */

function formatMinutes(
    minutes
) {

    minutes =
        Number(minutes) || 0;

    const hours =
        Math.floor(
            minutes / 60
        );

    const mins =
        minutes % 60;

    if (!hours) {

        return `${mins} دقیقه`;

    }

    if (!mins) {

        return `${hours} ساعت`;

    }

    return (
        `${hours} ساعت و ${mins} دقیقه`
    );

}


/* =========================================================
   HTML SECURITY
   ========================================================= */

function escapeHTML(
    value
) {

    return String(
        value ?? ""
    )
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


/* =========================================================
   EXPORT
   ========================================================= */

window.StudyPlanner = {

    getUserId,

    getUser:
        () => currentUser,

    getSubjects:
        () => subjects,

    getPlan:
        () => currentPlan,

    loadProfile,

    loadSubjects,

    loadDashboard,

    generateAIPlan,

    optimizePlan,

    rebalancePlan,

    updateSubjectProgress,

    deleteSubject,

    clearUser

};


console.log(
    "Study Planner JS loaded successfully."
);