# 🤖 Smart AI Study Planner


## 📌 Overview

**Smart AI Study Planner** is an intelligent educational platform designed to help students organize their study schedules, manage academic priorities, and improve their learning performance.

Unlike traditional study planners, this system combines Artificial Intelligence, Machine Learning personalization, and rule-based scheduling optimization to generate adaptive weekly study plans.

The application analyzes student profiles, available study hours, subject importance, academic performance, and previous study activity to create personalized learning schedules.

## ✨ Key Features

### 🧠 AI-Powered Study Planning
- Generate personalized weekly study plans.
- Analyze student goals and academic information.
- Prioritize subjects based on importance and performance.
- Automatically distribute available study hours.
- Include revision sessions and breaks.
- Generate realistic and balanced schedules.

### 📊 Intelligent Dashboard
- Monitor daily and weekly study progress.
- View total study hours.
- Track completed and pending sessions.
- Analyze subject performance.
- Monitor study activity.
- Display personalized statistics.

### 📚 Subject Management
- Add and manage academic subjects.
- Set subject importance (1–5).
- Define required study hours.
- Track subject progress.
- Automatically calculate AI priority scores.

### ⚡ AI Optimization
- Optimize existing study schedules.
- Rebalance study hours between subjects.
- Adapt schedules based on student progress.
- Prioritize weaker subjects.
- Reduce unrealistic workloads.

### 🤖 Machine Learning Personalization
- Calculate personalized subject priority scores.
- Analyze previous learning performance.
- Use Random Forest Regression for session-success prediction when sufficient historical data is available.
- Adapt scheduling decisions using available performance information.

### 📈 Progress Tracking
- Mark study sessions as completed.
- Record learning activity.
- Track completed study time.
- Monitor individual subject progress.
- Store generated study plans.

### 👤 Student Profile
- Personal information management.
- Educational level and grade selection.
- Daily available study hours.
- Academic goals.
- Personalized planning preferences.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Flask | Backend and REST API |
| SQLite | Database management |
| Ollama | Local AI model integration |
| Llama 3.2 | AI-powered plan generation |
| Scikit-learn | Machine Learning |
| Random Forest | Performance prediction |
| JavaScript | Frontend interactions |
| HTML5 | Application structure |
| CSS3 | Responsive UI design |
| Fetch API | Asynchronous API communication |

## 🧠 AI Architecture

The application uses a hybrid intelligence architecture combining three components:

**1. Large Language Model (LLM)**

Generates personalized study plans using student information, goals, subject priorities, and performance data.

**2. Machine Learning**

Uses Random Forest Regression to estimate study-session success when sufficient historical training data is available.

**3. Rule-Based Optimization**

Ensures generated schedules follow practical constraints, including study duration, available hours, breaks, and workload limits.

### System Architecture

```text
           Student Information
                   |
                   v
            Flask REST API
                   |
                   v
          Student Data Analysis
                   |
          +--------+--------+
          |        |        |
          v        v        v
         LLM       ML    Rule-Based
          |        |     Optimizer
          +--------+--------+
                   |
                   v
          Personalized Planner
                   |
                   v
          Weekly Study Schedule
                   |
                   v
          SQLite Database
                   |
                   v
          Progress Dashboard
```

## 📁 Project Structure

```text
Smart-AI-Study-Planner/
│
├── app.py
├── database.py
├── requirements.txt
├── study_planner.db
│
├── ai/
│   ├── __init__.py
│   └── planner.py
│
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── subjects.html
│   └── planner.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── script.js
```

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/Smart-AI-Study-Planner.git

cd Smart-AI-Study-Planner
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Configure Ollama

Download Ollama:

https://ollama.com/

Pull the default AI model:

```bash
ollama pull llama3.2
```

Make sure Ollama is running locally.

### 5. Configure Environment Variables

Default configuration:

```env
AI_API_URL=http://localhost:11434/v1/chat/completions
AI_MODEL=llama3.2
AI_TIMEOUT=120
```

These settings can be customized depending on your AI provider.

### 6. Run the Application

```bash
python app.py
```

### 7. Open the Application

```text
http://127.0.0.1:8000
```

## 🔌 REST API

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Check application status |
| `/api/profile` | POST | Create student profile |
| `/api/profile/<user_id>` | GET | Retrieve student profile |
| `/api/profile/<user_id>` | PUT | Update student profile |
| `/api/subjects` | POST | Add a subject |
| `/api/subjects/<user_id>` | GET | Retrieve student subjects |
| `/api/subjects/<int:subject_id>` | PUT | Update a subject |
| `/api/subjects/<int:subject_id>` | DELETE | Delete a subject |
| `/api/ai/generate-plan` | POST | Generate AI study plan |
| `/api/ai/optimize` | POST | Optimize study schedule |
| `/api/ai/rebalance` | POST | Rebalance study sessions |
| `/api/plans/<user_id>` | GET | Retrieve study plans |
| `/api/plans/<user_id>/latest` | GET | Retrieve latest plan |
| `/api/sessions/<user_id>` | GET | Retrieve study sessions |
| `/api/sessions/<int:session_id>/complete` | POST | Complete a study session |
| `/api/progress` | POST | Update study progress |
| `/api/dashboard/<user_id>` | GET | Retrieve dashboard statistics |
| `/api/activity/<user_id>` | GET | Retrieve activity history |

## 🔄 Study Planning Workflow

```text
Student Creates Profile
          |
          v
Adds Academic Subjects
          |
          v
Defines Daily Study Hours
          |
          v
AI Analyzes Student Data
          |
          v
Calculates Subject Priorities
          |
          v
Generates Weekly Study Plan
          |
          v
Optimizer Validates Schedule
          |
          v
Student Follows Study Plan
          |
          v
Progress and Performance Tracking
          |
          v
Future Plans Get Improved
```

## 🔮 Future Improvements

- [ ] Advanced learning analytics.
- [ ] Automatic exam preparation mode.
- [ ] Calendar synchronization.
- [ ] Smart notifications and reminders.
- [ ] More advanced performance prediction models.
- [ ] Long-term learning trend analysis.
- [ ] Export study schedules to PDF.
- [ ] Multi-user authentication.
- [ ] Mobile application integration.
- [ ] Advanced AI-based learning recommendations.

## 🔒 Data & Privacy

The application uses SQLite to store student profiles, subjects, study plans, sessions, and activity information.

The AI integration supports local model processing through Ollama, helping users run AI-powered planning without relying on external cloud AI services.

## 👨‍💻 Developer

**Bardia Mirzaei**

AI & Software Development Enthusiast

- GitHub: [@bardiamirzaei2012-dev](https://github.com/bardiamirzaei2012-dev)
- Website: [bardiamirzaei.com](https://bardiamirzaei.com)

## 📄 License

This project is developed for educational and research purposes. Add an appropriate open-source license before distributing the project.
