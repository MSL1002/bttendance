# BTTENDANCE

*An RFID-based attendance tracking system for educational institutions*

---

## Project Description

Bttendance is an automated attendance tracking system designed to reduce administrative burden on instructors. Students scan their RFID identification card at a reader near the classroom entrance, and their attendance is instantly recorded in a centralized MySQL database. The system was developed for Neumont University.

### Key Features

- **Instant Attendance Logging:** RFID scans are logged to the database in real-time with duplicate detection (30-second window)
- **Web Dashboard:** Single-page frontend served by the Flask backend for viewing attendance, managing students, instructors, and classes
- **WiFi Connectivity:** Pico W microcontroller transmits scan data wirelessly to the backend server
- **Unknown Card Handling:** Unregistered RFID cards are flagged; new students can be enrolled through the web UI
- **Analytics:** Attendance analytics available through the dashboard

---

## Team Members

- **Isabelle Johnson** - Project Lead, Full Stack Development

---

## Technologies Used

### Languages
- **Python 3** - Backend server, API, and database logic
- **MicroPython** - Pico W firmware
- **SQL** - Database schema and queries
- **HTML/CSS/JavaScript** - Single-page web frontend

### Hardware
- **Raspberry Pi Pico W** - WiFi-enabled microcontroller managing RFID scanning and data transmission
- **RC522 RFID Reader Module** - 13.56MHz RFID card detection and UID reading
- **RFID Cards/Tags** - Student identification tokens compatible with RC522

### Software & Frameworks
- **Flask** - REST API and static file serving
- **MySQL** - Relational database for attendance records
- **MySQL Connector/Python** - Python database driver
- **mfrc522-python** - RFID reader library
- **urequests** - MicroPython HTTP client

---

## Project Structure

```
bttendance/
├── app.py                    # Flask server — API endpoints and frontend serving
├── BackendSQL.py             # All database operations
├── config.json               # MySQL connection credentials (not committed)
├── requirements.txt          # Python dependencies
├── bttendance_frontend/
│   └── index.html            # Web dashboard (single-page app)
└── bttendance_pico/
    ├── main.py               # RFID scan loop and WiFi logic
    ├── mfrc522.py            # RFID reader library for SPI
    ├── new_student.py        # Student enrollment flow
    ├── env.json              # Pico WiFi and server config (not committed)
    └── test_backend.py       # Backend connectivity test
```

---

## Installation & Setup

### Prerequisites

- **Hardware:** Raspberry Pi Pico W, RC522 RFID reader, RFID cards (13.56MHz), jumper wires, USB micro-cable
- **Software:** Python 3.8+, pip, Git, MySQL Server
- **Network:** WiFi network the Pico W can connect to

---

### 1. Clone the Repository

```bash
git clone https://github.com/MSL1002/bttendance.git
cd bttendance
```

---

### 2. Set Up the Python Backend

#### Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

#### Install dependencies

```bash
pip install -r requirements.txt
```

Dependencies: `Flask`, `mysql-connector-python`, `python-dotenv`, `mfrc522-python`

---

### 3. Set Up MySQL

Install MySQL Server if you haven't already: https://dev.mysql.com/downloads/mysql/

Open MySQL CLI or MySQL Workbench and run:

```sql
CREATE DATABASE bttendance;
USE bttendance;

CREATE TABLE users (
    rfid_uid VARCHAR(255) NOT NULL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    student_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rfid_uid VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(100)
);

CREATE TABLE instructors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255)
);

CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(255) NOT NULL,
    instructor_id INT,
    location VARCHAR(100),
    FOREIGN KEY (instructor_id) REFERENCES instructors(id)
);

CREATE TABLE class_enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    rfid_uid VARCHAR(255) NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (rfid_uid) REFERENCES users(rfid_uid)
);
```

---

### 4. Configure the Backend

Create `config.json` in the project root:

```json
{
    "user": "root",
    "password": "your_mysql_password",
    "host": "127.0.0.1",
    "database": "bttendance"
}
```

> **Note:** `config.json` is in `.gitignore` — do not commit credentials.

---

### 5. Start the Backend Server

```bash
python app.py
```

The server runs at `http://127.0.0.1:5000`. Open that URL in a browser to access the web dashboard.

---

### 6. Set Up the Pico W

#### Flash MicroPython Firmware

1. Download MicroPython firmware for Pico W: https://micropython.org/download/rp2-pico-w/
2. Hold **BOOTSEL** on the Pico W while connecting via USB — it appears as `RPI-RP2` storage
3. Drag the `.uf2` file onto the drive; the Pico W reboots automatically

#### Install VS Code Extensions

- **Pico-W-Go** (by Professor Whatley) — upload and run code on the Pico
- **Python** (by Microsoft)

#### Configure the Pico

Edit `bttendance_pico/env.json`:

```json
{
    "SERVER_IP": "192.168.X.X",
    "SERVER_PORT": "5000",
    "SSID": "your_wifi_network",
    "PASSWORD": "your_wifi_password",
    "LOCATION": "your_classroom"
}
```

`SERVER_IP` is your computer's local IP address. Find it on Windows with `ipconfig` — look for "IPv4 Address".

#### Upload and Run

1. Connect the Pico W via USB
2. Open `bttendance_pico/main.py` in VS Code
3. Use the Pico-W-Go panel to upload and run (Ctrl+Shift+F5)
4. Open the REPL to confirm WiFi connects and the RFID reader initializes

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the web dashboard |
| `POST` | `/log-scan` | Log an RFID scan (called by Pico W) |
| `GET` | `/get-user` | Get student info by RFID UID |
| `GET` | `/get-all-users` | List all students |
| `POST` | `/start-enrollment` | Begin RFID enrollment session |
| `POST` | `/enroll-rfid` | Enroll a new RFID card |
| `GET` | `/enrollment-stream` | SSE stream for enrollment status |
| `DELETE` | `/delete-user` | Remove a student |
| `GET/POST` | `/add-instructor` | List or add an instructor |
| `DELETE` | `/delete-instructor` | Remove an instructor |
| `GET/POST` | `/add-class` | List or add a class |
| `DELETE` | `/delete-class` | Remove a class |
| `GET` | `/get-class-enrollments` | Get students enrolled in a class |
| `POST` | `/enroll-student` | Enroll a student in a class |
| `GET` | `/get-attendance` | Query attendance records |
| `GET` | `/get-analytics` | Attendance analytics |
| `GET` | `/test` | Health check |
