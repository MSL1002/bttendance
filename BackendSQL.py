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
    query = ("INSERT INTO scans "
            "(rfid_uid, timestamp, location)"
            "VALUES(%s, %s, %s)"
            )
    data_vals = (rfid, datetime.datetime.now(), location)

    try:
        cnx = mysql.connector.connect(**env)
        cursor = cnx.cursor()
        cursor.execute(query, data_vals)

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
    base += " ORDER BY s.location, s.timestamp DESC"

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