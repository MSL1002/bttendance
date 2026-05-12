import mysql.connector

config = {
    'user': 'root',
    'password': 'admin',
    'host': '127.0.0.1',
    'database': 'bttendance',
    'raise_on_warnings': True
}

def take_user_input():
    strFName = input("Enter student's first name: ")
    strLName = input("Enter stident's last name: ")
    strID = input("Enter student's ID: ")

    return strFName, strLName, strID

def insert_into_db(fName, lName, id):
    add_student = ("INSERT INTO users "
                "(rfid_uid, first_name, last_name, student_id)"
                "VALUES (0000, %s, %s, %s)")
    data_student = (fName, lName, id)
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute(add_student, data_student)

        cnx.commit()

        print("Student input success!!!")

        cursor.close()
        cnx.close()
        
    except mysql.connector.Error as err:
        print("Didn't work :(")
        print(err)

    cursor.close()
    cnx.close()

def main():
    fName, lName, id = take_user_input()
    insert_into_db(fName, lName, id)

main()