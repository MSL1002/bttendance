# BTTENDANCE

*An RFID-based attendance tracking system for educational institutions*

---

## Project Description

Bttendance is an automated attendance tracking system designed to streamline classroom management and reduce administrative burden on instructors. The system utilizes RFID card scanning technology to automatically log student attendance, eliminating the need for manual quizzes or roll calls.

Students simply scan their RFID identification card at a reader positioned near the classroom entrance, and their attendance is instantly recorded in a centralized database. The system was developed specifically for Neumont University but is architected to be adaptable to other organizational environments.

### Key Features

- **Instant Attendance Logging:** RFID cards are scanned and logged to the database in real-time
- **Automated Data Storage:** All attendance records are automatically persisted to a MySQL database with timestamps
- **WiFi Connectivity:** Pico W microcontroller transmits scan data wirelessly to a backend server
- **Unknown Card Detection:** System identifies and logs unknown or unregistered RFID cards
---

## Team Members

- **Isabelle Johnson** - Project Lead, Full Stack Development

---

## Technologies Used

### Languages
- **Python 3** - Backend server and API development
- **MicroPython** - Pico W microcontroller firmware and application logic
- **SQL** - Database schema and queries

### Hardware
- **Raspberry Pi Pico W** - WiFi-enabled microcontroller managing RFID scanning and data transmission
- **RC522 RFID Reader Module** - 13.56MHz RFID card/fob detection and UID reading
- **RFID Cards/Tags** - Student identification tokens compatible with RC522 standard

### Software & Frameworks
- **MicroPython** - Runtime environment for Pico W
- **mfrc522.py** - RFID reader library for SPI communication
- **urequests** - MicroPython HTTP client for backend communication
- **Flask** - Python web framework for REST API endpoints
- **MySQL** - Relational database for attendance record storage
- **MySQL Connector/Python** - Python database driver for MySQL connectivity

### Development Tools
- **Visual Studio Code** - IDE
- **Pico-W-Go Extension** - VS Code extension for Pico W code management
- **Git & GitHub** - Version control and repository management
---

## Installation & Setup

### Prerequisites

Before beginning, ensure you have the following:

- **Hardware:** Raspberry Pi Pico W, RC522 RFID reader, RFID cards (13.56MHz), jumper wires, USB micro-cable, power adapter
- **Software:** Python 3.8+, pip, Git
- **Network:** WiFi network with WPA2 security
- **System:** Windows with administrator access

### Hardware Setup

#### Step 1: Wire the RC522 RFID Module

Connect the RC522 module to the Raspberry Pi Pico W

#### Step 2: Flash MicroPython Firmware

1. Download MicroPython firmware for Pico W: https://micropython.org/download/rp2-pico-w/
2. Hold **BOOTSEL** button on Pico W while connecting via USB
3. Device will appear as `RPI-RP2` storage
4. Drag and drop the `.uf2` firmware file onto the storage device
5. Pico W will reboot automatically

---

### Backend Server Setup

#### Step 1: Clone Repository

```bash
git clone https://github.com/MSL1002/bttendance.git
cd bttendance
```

#### Step 2: Set Up Python Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your terminal prompt.

#### Step 3: Install Backend Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` should contain:
```
Flask==2.3.0
mysql-connector-python==8.0.33
python-dotenv==1.0.0
```

#### Step 4: Install MySQL Database

Download and install MySQL from: https://dev.mysql.com/downloads/mysql/

Follow the installation wizard for your operating system.

#### Step 5: Create Database and Tables

Open MySQL CLI or MySQL Workbench and execute the following:

```sql
CREATE DATABASE bttendance;
USE bttendance;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rfid_uid VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    student_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rfid_uid VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(100),
    status ENUM('success', 'unknown_card', 'error') DEFAULT 'success',
    FOREIGN KEY (rfid_uid) REFERENCES users(rfid_uid)
);

CREATE INDEX idx_rfid_uid ON users(rfid_uid);
CREATE INDEX idx_scan_timestamp ON scans(timestamp);
CREATE INDEX idx_scan_location ON scans(location);

CREATE USER 'bttendance_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON bttendance.* TO 'bttendance_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Step 6: Configure Environment Variables

Create a `.env` file in the project's root directory:

```
DB_HOST=localhost
DB_USER=bttendance_user
DB_PASSWORD=secure_password
DB_NAME=bttendance
FLASK_ENV=development
FLASK_DEBUG=True
```

**Note:** Add `.env` to `.gitignore` to prevent committing sensitive credentials.

#### Step 7: Start Backend Server

```bash
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

### Pico W Setup

#### Step 1: Install VS Code and Extensions

1. Install Visual Studio Code: https://code.visualstudio.com/
2. Install **Pico-W-Go** extension (by Professor Whatley)
3. Install **Python** extension (by Microsoft)

#### Step 2: Configure Application

Edit `pico-w-code/config.py`:

```python
WIFI_SSID = "your_wifi_network"
WIFI_PASSWORD = "your_wifi_password"
BACKEND_URL = "http://192.168.X.X:5000"  # Your computer's local IP
LOCATION = "Classroom XYZ"
```

Find your local IP address:
- **Windows:** in a command prompt type `ipconfig` and look for "IPv4 Address"

#### Step 3: Upload Code to Pico W

1. Connect Pico W via USB
2. Open `main.py` in VS Code
3. Click **Run** in Pico-W-Go panel (Ctrl+Shift+F5)
4. Code will upload automatically

#### Step 4: Verify Serial Output

1. Click **Repl** in Pico-W-Go panel
2. Press reset button on Pico W
3. Verify output shows WiFi connection and RFID initialization
