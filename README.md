# Bardia AI Planner

#### Description:

Bardia AI Planner is a web-based intelligent study and productivity planner designed to help users organize their tasks, manage their available time, track their progress, and generate personalized daily schedules using a locally running AI model.

The main purpose of this project is to solve a common productivity problem: users may have many tasks to complete but may not know how to organize them efficiently throughout the day. A traditional to-do list only shows what needs to be done. Bardia AI Planner goes further by allowing users to provide detailed information about their tasks and then using an AI model to create a structured daily schedule.

This project was developed as my Final Project for CS50x.

The application was built using Python, Flask, JavaScript, HTML, CSS, LocalStorage, JSON, HTTP requests, Ollama, and the Qwen 2.5 7B language model.

The application is designed primarily as a local personal productivity tool. It does not require an external AI API key for its core AI planner functionality. The AI scheduling system communicates with an Ollama server running locally on the user's computer.

---

## Features

### Task Management

Users can create tasks and provide information about them, including:

- Task title
- Category
- Priority
- Duration
- Preferred time
- Deadline
- Description

Users can also:

- Edit tasks
- Delete tasks
- Mark tasks as completed
- Filter tasks
- View pending tasks
- View completed tasks
- View task statistics

The application does not use a predefined list of tasks. Tasks are created by the user and are then provided to the AI planner.

---

## AI Planner

The main feature of Bardia AI Planner is its AI-powered daily scheduling system.

The user creates tasks and provides the available time for the day.

The application sends the task information and available time to the Flask backend.

The backend creates a structured prompt and sends it to the locally running Qwen 2.5 7B model through Ollama.

The AI analyzes the tasks according to factors such as:

- Priority
- Duration
- Deadline
- Category
- Description
- Estimated difficulty
- Concentration requirements
- Logical task order
- Available time

The AI is instructed to create a practical schedule using the user's tasks.

It is also instructed to:

- Use all provided tasks
- Avoid duplicate tasks
- Avoid overlapping times
- Respect the available start and end times
- Prioritize important tasks
- Consider approaching deadlines
- Schedule demanding tasks during suitable focus periods
- Schedule lighter tasks during lower-energy periods
- Include reasonable breaks
- Divide long tasks into reasonable sessions when necessary

The generated schedule is returned as JSON.

The Flask backend validates the AI response before sending it to the frontend.

The frontend then displays the generated schedule in a visual timeline.

---

## AI Architecture

The main AI workflow is:

```text
User
  |
  v
Create Tasks
  |
  v
Select Available Time
  |
  v
JavaScript Frontend
  |
  v
Flask Backend
  |
  v
Prompt Generation
  |
  v
Ollama
  |
  v
Qwen 2.5 7B
  |
  v
JSON Response
  |
  v
JSON Cleaning
  |
  v
Plan Validation
  |
  v
Flask Response
  |
  v
JavaScript
  |
  v
Visual Daily Schedule
```

The schedule is dynamically generated from the tasks entered by the user.

---

## Ollama and Qwen 2.5 7B

The AI functionality uses Ollama to run a language model locally.

The configured model is:

```text
qwen2.5:7b
```

The Flask backend communicates with the local Ollama API through:

```text
http://127.0.0.1:11434/api/generate
```

The project does not require a cloud AI API key for its core planner functionality.

Using a local model also allows the application to operate as a local productivity tool without depending on an external AI service.

---

## AI Output Validation

Language models can sometimes return unexpected or malformed output.

For this reason, the backend does not directly trust the raw AI response.

The application first cleans the model response and extracts the JSON object.

The backend then validates the generated plan.

It checks that:

- The response is a valid JSON object.
- The `plan` field exists.
- The `plan` field is a list.
- Generated task IDs belong to tasks supplied by the user.
- Required fields are present.
- Tasks are not unexpectedly duplicated.
- All required user tasks are represented in the generated plan.

This provides an additional validation layer between the AI model and the frontend.

---

## English AI Output

The AI planner is configured to generate all AI-created explanatory text in English.

This includes:

- Schedule summaries
- Task reasons
- Break reasons

User-provided task titles are not automatically translated because they are entered directly by the user.

This allows the user to keep the original task title while keeping AI-generated explanations in English.

---

## Weighted Progress System

The application includes a weighted progress system.

Instead of treating every task as equally important, task priority affects the progress calculation.

The priority weights are:

```text
High   = 3
Medium = 2
Low    = 1
```

The progress percentage is calculated using the total priority weight of completed tasks compared with the total priority weight of all tasks.

For example:

```text
Math       High      Completed
English    Low       Pending
Physics    Medium    Pending
```

The completed high-priority task contributes more to the overall progress than a low-priority task would.

This makes the progress indicator more representative of task importance.

---

## Dashboard

The dashboard provides an overview of the user's productivity.

It includes statistics such as:

- Total Tasks
- Completed
- Pending
- Progress
- High Priority
- Focus Minutes
- Completion Rate
- AI Status

These values are calculated dynamically from the user's tasks and application state.

The dashboard is designed to provide a quick overview without requiring the user to inspect every task individually.

---

## Pomodoro Timer

The application includes a Pomodoro-style focus timer.

The timer provides:

- Focus sessions
- Break sessions
- Start
- Pause
- Reset
- 25-minute focus mode
- 50-minute focus mode
- 5-minute break mode

The timer runs directly in the browser using JavaScript.

It is integrated into the productivity dashboard so users can manage tasks and focus sessions in one application.

---

## LocalStorage

The application uses browser LocalStorage for task persistence.

This allows the application to:

- Preserve tasks after page reloads
- Work without a remote database
- Run locally
- Store task information in the browser
- Avoid unnecessary backend database configuration

The data is stored locally on the browser and device being used.

---

# Technologies Used

The project uses:

- Python
- Flask
- JavaScript
- HTML5
- CSS3
- LocalStorage
- JSON
- HTTP
- Requests
- Ollama
- Qwen 2.5 7B

---

## Python

Python is used for the backend application.

The backend is responsible for receiving requests, communicating with Ollama, processing AI responses, validating schedules, and returning structured JSON.

---

## Flask

Flask is used to create the local web server and API endpoints.

It connects the frontend with the local AI model.

---

## JavaScript

JavaScript provides the client-side functionality.

It handles:

- Task creation
- Task editing
- Task deletion
- Task completion
- Task filtering
- LocalStorage
- Progress calculation
- Dashboard statistics
- AI plan generation
- Communication with Flask
- Rendering the AI schedule
- Pomodoro functionality

---

## HTML5

HTML5 provides the structure of the web application.

The project uses a single main HTML file containing the application interface.

---

## CSS3

CSS3 provides:

- Layout
- Responsive design
- Dashboard cards
- Animations
- Dark theme
- Visual timeline
- Buttons
- Forms
- Modal interfaces

---

## LocalStorage

LocalStorage provides local persistence for user-created tasks.

No external database is required for the main task-management functionality.

---

## JSON

JSON is used to communicate between:

```text
JavaScript
      |
      v
Flask
      |
      v
Ollama
```

It is also used for structured AI schedule responses.

---

## Requests

Python's `requests` library is used by Flask to communicate with the local Ollama API.

---

## Ollama

Ollama provides the local runtime used to execute the AI model.

---

## Qwen 2.5 7B

Qwen 2.5 7B is the language model used to generate daily schedules.

---

# Project Structure

The project contains the following main files:

```text
Bardia-AI-Planner/
│
├── app.py
├── index.html
└── README.md
```

---

## app.py

`app.py` is the backend of the application.

Its main responsibilities include:

1. Starting the Flask server.
2. Serving the frontend.
3. Checking Ollama availability.
4. Checking whether the configured model is installed.
5. Receiving task information.
6. Receiving the available daily time.
7. Creating the AI prompt.
8. Sending the prompt to Ollama.
9. Receiving the AI response.
10. Cleaning the response.
11. Parsing the response as JSON.
12. Validating the generated schedule.
13. Returning the final result to the frontend.
14. Handling errors and timeouts.

The application runs locally through Flask.

---

## index.html

`index.html` contains the frontend.

It includes:

- HTML
- CSS
- JavaScript

The frontend handles the user interface and communicates with the Flask backend.

---

## README.md

This file documents the project, its purpose, architecture, technologies, installation process, usage, limitations, and design decisions.

---

# API

The Flask backend provides API functionality for the frontend.

## Status Endpoint

```text
GET /api/status
```

This endpoint checks whether Ollama is available and whether the configured AI model is installed.

---

## Generate Plan Endpoint

```text
POST /api/generate-plan
```

This endpoint receives the user's tasks and available time.

Example request:

```json
{
    "tasks": [
        {
            "id": "1",
            "title": "Study Mathematics",
            "priority": "High",
            "duration": 60,
            "category": "Study"
        },
        {
            "id": "2",
            "title": "Practice Programming",
            "priority": "Medium",
            "duration": 90,
            "category": "Programming"
        }
    ],
    "start": "08:00",
    "end": "20:00"
}
```

The backend sends the information to the AI model and returns a structured schedule.

---

# Installation

## Requirements

The project requires:

- Python 3
- Flask
- Requests
- Ollama
- Qwen 2.5 7B
- A modern web browser

---

## Install Python Dependencies

Open a terminal in the project directory and run:

```bash
pip install flask requests
```

---

## Install Ollama

Install Ollama on the computer.

Then download the model:

```bash
ollama pull qwen2.5:7b
```

Make sure Ollama is running before using the AI Planner.

---

# Running the Application

Open a terminal in the project directory.

Run:

```bash
python app.py
```

The Flask application will run locally.

Open:

```text
http://127.0.0.1:5000
```

in a web browser.

For AI planning, Ollama must also be running with:

```text
qwen2.5:7b
```

installed.

---

# Example Workflow

A typical workflow is:

1. Start Ollama.
2. Start the Flask application.
3. Open the web application.
4. Create tasks.
5. Set task priorities.
6. Set task durations.
7. Add deadlines when needed.
8. Add task descriptions.
9. Review the dashboard.
10. Select the available start and end time.
11. Generate an AI plan.
12. Flask sends the tasks to Ollama.
13. Qwen 2.5 7B analyzes the tasks.
14. The AI generates a structured schedule.
15. Flask validates the response.
16. JavaScript displays the schedule.
17. The user completes tasks.
18. The progress statistics update automatically.

---

# Error Handling

The application includes error handling for several situations.

If Ollama is unavailable, the application reports that Ollama needs to be started.

If the configured model is not installed, the application reports the missing model.

If the AI response times out, the backend reports the timeout.

If the AI returns invalid JSON, the backend attempts to clean and parse the response and reports an error if valid JSON cannot be obtained.

The backend also validates task IDs and the structure of the generated schedule.

---

# Design Decisions

One of the main design decisions was to use a local AI model instead of a cloud-based AI API.

Ollama was selected because it allows the model to run locally and removes the need for an external AI API key.

Flask was selected because it provides a lightweight Python backend that can communicate with the frontend and the local AI model.

LocalStorage was selected because the application is designed as a local personal productivity tool. A remote database is not required for the core task-management functionality.

Another important design decision was the weighted progress system.

A simple to-do list could calculate progress by dividing completed tasks by total tasks. However, this treats every task as equally important.

The weighted system instead considers task priority, making high-priority tasks contribute more to the user's progress.

JSON was selected as the communication format because it provides a structured way to transfer tasks and schedules between JavaScript, Flask, and the AI model.

---

# Limitations

The current version has several limitations.

The application is primarily designed as a local personal productivity tool.

It does not currently provide:

- User accounts
- Cloud synchronization
- Multi-device synchronization
- Remote database storage
- Calendar integration
- Push notifications
- Automatic mobile notifications
- Multi-user collaboration

Because tasks are stored in LocalStorage, they are associated with the browser and device being used.

The AI planner also depends on Ollama and the Qwen 2.5 7B model being installed locally.

If Ollama is not running, the AI scheduling feature cannot generate a new plan.

The quality of the generated schedule also depends on the capabilities of the selected language model.

---

# Future Improvements

Possible future improvements include:

- User authentication
- Cloud synchronization
- SQLite database support
- Multiple user profiles
- Calendar integration
- Automatic reminders
- Notifications
- Automatic rescheduling
- More advanced scheduling algorithms
- Stronger schedule validation
- Weekly productivity reports
- Monthly productivity reports
- Historical progress tracking
- Support for additional AI models
- Personalized scheduling based on previous behavior
- Mobile application support

---

# Privacy

The application is designed to run locally.

User tasks are stored in the browser's LocalStorage.

AI requests are sent to the local Ollama service running on the same computer.

The local Ollama endpoint is:

```text
127.0.0.1:11434
```

The application does not require an external AI API key for its core AI planner functionality.

---

# Academic Honesty and AI Assistance

This project was developed as my Final Project for CS50x.

AI-based programming assistants were used during development as development aids for activities such as explaining programming concepts, debugging, reviewing code, and discussing implementation approaches.

The project idea, implementation decisions, integration, testing, configuration, and final project were completed and reviewed by me.

AI tools were used as assistants and not as a replacement for understanding the project.

---

👨‍💻 Developer
Bardia Mirzaei

AI & Software Development Enthusiast

GitHub: @bardiamirzaei2012-dev
Website: bardiamirzaei.com

