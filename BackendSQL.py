import mysql.connector
import datetime
import json

try:
    with open("config.json") as f:
        env = json.load(f)
except json.decoder.JSONDecodeError as e:
    print("ERROR:\nPlease set up \'config.json\', then try again.")
    exit()

def log_attendance(rfid, location):
    query = ("INSERT INTO scans "
            "(rfid_uid, timestamp, location)"
            "VALUES(%s, %s, %s)"
            )
    data_vals = (rfid, datetime.datetime.now(), location)

    try:
        cnx = mysql.connector.connect(env)
        cursor = cnx.cursor()
        cursor.execute(query, data_vals)

        cnx.commit()

        print("attendance log success.")

        cursor.close()
        cnx.close()
        
    except mysql.connector.Error as err:
        print("Insert failed.")
        print(err)
        return err

def insert_into_db(rfid, fName, lName, id):
    add_student = ("INSERT INTO users "
                "(rfid_uid, first_name, last_name, student_id)"
                "VALUES (%s, %s, %s, %s)")
    data_student = (rfid, fName, lName, id)
    try:
        cnx = mysql.connector.connect(env)
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
        cnx = mysql.connector.connect(env)
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