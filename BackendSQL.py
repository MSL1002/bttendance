import mysql.connector
from mysql.connector import errorcode
import datetime
import json

try:
    with open("config.json") as f:
        env = json.load(f)
except json.decoder.JSONDecodeError as e:
    print("ERROR:\nPlease set up \'config.json\', then try again.")
    print(e)
    exit()

def log_attendance(rfid, location):
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()

        cursor.execute(
            "SELECT 1 FROM scans WHERE rfid_uid = %s "
            "AND timestamp > NOW() - INTERVAL 30 SECOND LIMIT 1",
            (rfid,)
        )
        if cursor.fetchone():
            print("Duplicate scan ignored (within 30s).")
            cursor.close()
            cnx.close()
            return

        cursor.execute(
            "INSERT INTO scans (rfid_uid, timestamp, location) VALUES (%s, NOW(), %s)",
            (rfid, location)
        )
        cnx.commit()
        print("attendance log success.")

        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        print("Insert failed.")
        print(err)
        if err.errno in (errorcode.ER_NO_REFERENCED_ROW_2, errorcode.ER_ROW_IS_REFERENCED_2):
            return "RFID not found in database."
        else:
            return "Something went wrong, try again later."

def insert_into_db(rfid, fName, lName, id):
    add_student = ("INSERT INTO users "
                "(rfid_uid, first_name, last_name, student_id)"
                "VALUES (%s, %s, %s, %s)")
    data_student = (rfid, fName, lName, id)
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute(add_student, data_student)

        cnx.commit()

        print("Student input success.")

        cursor.close()
        cnx.close()
        
    except mysql.connector.Error as err:
        print("Insert failed.")
        print(err)

    cursor.close()
    cnx.close()

def get_from_db(id):
    get_student = "SELECT * FROM users WHERE student_id = %s"
    data = (id, )
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute(get_student, data)

        result = cursor.fetchall()

        print(result)

        cursor.close()
        cnx.close()

        return(result[0])

    except mysql.connector.Error as err:
        print("Insert failed.")
        print(err)

    cursor.close()
    cnx.close()

def get_all_users():
    query = "SELECT id, rfid_uid, first_name, last_name, student_id FROM users ORDER BY last_name, first_name"
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        return result
    except mysql.connector.Error as err:
        print(err)
        return None

def delete_student(student_id):
    query = "DELETE FROM users WHERE student_id = %s"
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute(query, (student_id,))
        cnx.commit()
        affected = cursor.rowcount
        cursor.close()
        cnx.close()
        return affected
    except mysql.connector.Error as err:
        print(err)
        return None

_DAY_TO_MYSQL_DOW  = {'M': 2, 'T': 3, 'W': 4, 'R': 5, 'F': 6, 'S': 7, 'U': 1}
_DAY_TO_PY_WEEKDAY = {'M': 0, 'T': 1, 'W': 2, 'R': 3, 'F': 4, 'S': 5, 'U': 6}

def _days_to_mysql_dow(days_str):
    return [_DAY_TO_MYSQL_DOW[d] for d in days_str.upper() if d in _DAY_TO_MYSQL_DOW]

def _count_sessions(start_date, end_date, days_str):
    py_weekdays = {_DAY_TO_PY_WEEKDAY[d] for d in days_str.upper() if d in _DAY_TO_PY_WEEKDAY}
    end = min(end_date, datetime.date.today())
    if start_date > end:
        return 0
    count = 0
    d = start_date
    while d <= end:
        if d.weekday() in py_weekdays:
            count += 1
        d += datetime.timedelta(days=1)
    return count

def _td_to_time(val):
    if isinstance(val, datetime.timedelta):
        s = int(val.total_seconds())
        return datetime.time(s // 3600, (s % 3600) // 60, s % 60)
    return val

_TIME_SLOTS = [
    ('Morning',   datetime.time(8,  0), datetime.time(11, 59)),
    ('Afternoon', datetime.time(13, 0), datetime.time(16, 59)),
    ('Night',     datetime.time(17, 0), datetime.time(20,  0)),
]

def _time_slot(t):
    for label, start, end in _TIME_SLOTS:
        if start <= t <= end:
            return label
    return None

def get_all_instructors():
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, first_name, last_name FROM instructors ORDER BY last_name, first_name")
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        return result
    except mysql.connector.Error as err:
        print(err)
        return None

def add_instructor(first_name, last_name):
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO instructors (first_name, last_name) VALUES (%s, %s)", (first_name, last_name))
        cnx.commit()
        new_id = cursor.lastrowid
        cursor.close()
        cnx.close()
        return new_id
    except mysql.connector.Error as err:
        print(err)
        return None

def delete_instructor(instructor_id):
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM instructors WHERE id = %s", (instructor_id,))
        cnx.commit()
        affected = cursor.rowcount
        cursor.close()
        cnx.close()
        return affected
    except mysql.connector.Error as err:
        print(err)
        return None

def get_all_classes():
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.id, c.name, c.location, c.days_of_week,
                c.start_time, c.end_time, c.start_date, c.end_date,
                i.id as instructor_id,
                CONCAT(i.first_name, ' ', i.last_name) as instructor,
                COUNT(ce.user_id) as enrolled_count
            FROM classes c
            JOIN instructors i ON c.instructor_id = i.id
            LEFT JOIN class_enrollments ce ON ce.class_id = c.id
            GROUP BY c.id, i.id
            ORDER BY c.name
        """)
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        for row in result:
            row['start_time'] = str(_td_to_time(row['start_time']))[:5]
            row['end_time']   = str(_td_to_time(row['end_time']))[:5]
            row['start_date'] = str(row['start_date'])
            row['end_date']   = str(row['end_date'])
        return result
    except mysql.connector.Error as err:
        print(err)
        return None

def add_class(name, instructor_id, location, days_of_week, start_time, end_time, start_date, end_date):
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute(
            "INSERT INTO classes "
            "(name, instructor_id, location, days_of_week, start_time, end_time, start_date, end_date) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (name, instructor_id, location, days_of_week, start_time, end_time, start_date, end_date)
        )
        cnx.commit()
        new_id = cursor.lastrowid
        cursor.close()
        cnx.close()
        return new_id
    except mysql.connector.Error as err:
        print(err)
        return None

def delete_class(class_id):
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM classes WHERE id = %s", (class_id,))
        cnx.commit()
        affected = cursor.rowcount
        cursor.close()
        cnx.close()
        return affected
    except mysql.connector.Error as err:
        print(err)
        return None

def get_class_enrollments(class_id):
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id, u.first_name, u.last_name, u.student_id
            FROM class_enrollments ce
            JOIN users u ON ce.user_id = u.id
            WHERE ce.class_id = %s
            ORDER BY u.last_name, u.first_name
        """, (class_id,))
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        return result
    except mysql.connector.Error as err:
        print(err)
        return None

def enroll_student_in_class(class_id, user_id):
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute(
            "INSERT IGNORE INTO class_enrollments (class_id, user_id) VALUES (%s, %s)",
            (class_id, user_id)
        )
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(err)
        return False

def unenroll_student_from_class(class_id, user_id):
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute(
            "DELETE FROM class_enrollments WHERE class_id = %s AND user_id = %s",
            (class_id, user_id)
        )
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(err)
        return False

def get_analytics():
    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT c.id, c.name, c.location, c.days_of_week,
                   c.start_time, c.end_time, c.start_date, c.end_date,
                   i.id as instructor_id,
                   CONCAT(i.first_name, ' ', i.last_name) as instructor,
                   COUNT(ce.user_id) as enrolled_count
            FROM classes c
            JOIN instructors i ON c.instructor_id = i.id
            LEFT JOIN class_enrollments ce ON ce.class_id = c.id
            GROUP BY c.id, i.id
            ORDER BY c.name
        """)
        classes = cursor.fetchall()

        by_class = []
        instructor_totals = {}
        time_totals = {label: {'label': label, 'classes': 0, 'total_attended': 0, 'total_possible': 0}
                       for label, _, __ in _TIME_SLOTS}

        for cls in classes:
            days_str = cls['days_of_week']
            dow_list = _days_to_mysql_dow(days_str)
            start_t  = _td_to_time(cls['start_time'])
            end_t    = _td_to_time(cls['end_time'])
            start_d  = cls['start_date']
            end_d    = cls['end_date']
            enrolled = cls['enrolled_count']
            sessions = _count_sessions(start_d, end_d, days_str)

            attended = 0
            if enrolled > 0 and sessions > 0 and dow_list:
                ph = ','.join(['%s'] * len(dow_list))
                cursor.execute(
                    f"""SELECT COUNT(DISTINCT u.id, DATE(s.timestamp)) as attended
                        FROM scans s
                        JOIN users u ON s.rfid_uid = u.rfid_uid
                        JOIN class_enrollments ce ON ce.user_id = u.id AND ce.class_id = %s
                        WHERE s.location = %s
                        AND TIME(s.timestamp) BETWEEN %s AND %s
                        AND DATE(s.timestamp) BETWEEN %s AND LEAST(%s, CURDATE())
                        AND DAYOFWEEK(s.timestamp) IN ({ph})""",
                    [cls['id'], cls['location'], start_t, end_t, start_d, end_d] + dow_list
                )
                row = cursor.fetchone()
                attended = int(row['attended']) if row and row['attended'] else 0

            total_possible = sessions * enrolled
            rate = round(attended / total_possible, 4) if total_possible > 0 else None

            by_class.append({
                'class_id':                cls['id'],
                'class_name':              cls['name'],
                'instructor':              cls['instructor'],
                'instructor_id':           cls['instructor_id'],
                'location':                cls['location'],
                'schedule':                f"{days_str} {str(start_t)[:5]}–{str(end_t)[:5]}",
                'sessions_held':           sessions,
                'enrolled':                enrolled,
                'attended_student_sessions': attended,
                'attendance_rate':         rate,
            })

            iid = cls['instructor_id']
            if iid not in instructor_totals:
                instructor_totals[iid] = {
                    'instructor_id': iid,
                    'instructor':    cls['instructor'],
                    'classes':       0,
                    'total_attended': 0,
                    'total_possible': 0,
                }
            instructor_totals[iid]['classes']        += 1
            instructor_totals[iid]['total_attended']  += attended
            instructor_totals[iid]['total_possible']  += total_possible

            slot = _time_slot(start_t)
            if slot:
                time_totals[slot]['classes']        += 1
                time_totals[slot]['total_attended']  += attended
                time_totals[slot]['total_possible']  += total_possible

        by_instructor = []
        for stats in instructor_totals.values():
            tp = stats['total_possible']
            by_instructor.append({
                'instructor_id':   stats['instructor_id'],
                'instructor':      stats['instructor'],
                'classes':         stats['classes'],
                'attendance_rate': round(stats['total_attended'] / tp, 4) if tp > 0 else None,
            })
        by_instructor.sort(key=lambda x: (x['attendance_rate'] is None, -(x['attendance_rate'] or 0)))

        by_time = []
        for label, *_ in _TIME_SLOTS:
            s = time_totals[label]
            tp = s['total_possible']
            by_time.append({
                'slot':            label,
                'classes':         s['classes'],
                'attendance_rate': round(s['total_attended'] / tp, 4) if tp > 0 else None,
            })

        cursor.close()
        cnx.close()
        return {'by_class': by_class, 'by_instructor': by_instructor, 'by_time': by_time}

    except mysql.connector.Error as err:
        print(err)
        return None

def get_attendance(student_id=None, location=None, date=None):
    base = (
        "SELECT u.first_name, u.last_name, u.student_id, "
        "s.timestamp, s.location "
        "FROM scans s "
        "LEFT JOIN users u ON s.rfid_uid = u.rfid_uid "
    )
    conditions = []
    data = []
    if student_id:
        conditions.append("u.student_id = %s")
        data.append(student_id)
    if location:
        conditions.append("s.location = %s")
        data.append(location)
    if date:
        conditions.append("DATE(s.timestamp) = %s")
        data.append(date)

    if conditions:
        base += " WHERE " + " AND ".join(conditions)
    base += " ORDER BY s.timestamp DESC"

    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(base, data if data else None)
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        return result
    except mysql.connector.Error as err:
        print(err)
        return None