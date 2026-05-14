import mysql.connector

config = {
    'user': 'root',
    'password': 'admin',
    'host': '127.0.0.1',
    'database': 'bttendance',
    'raise_on_warnings': True
}

def insert_into_db(rfid, fName, lName, id):
    add_student = ("INSERT INTO users "
                "(rfid_uid, first_name, last_name, student_id)"
                "VALUES (%s, %s, %s, %s)")
    data_student = (rfid, fName, lName, id)
    try:
        cnx = mysql.connector.connect(**config)
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
        cnx = mysql.connector.connect(**config)
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