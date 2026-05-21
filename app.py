from flask import Flask, request
import BackendSQL

app = Flask(__name__)

@app.route("/log-scan", methods=['POST'])
def handle_login():
    if request.method == 'POST':
        try:
            rfid = request.args.get('rfid')
            local = request.args.get('location')
            #TODO:
            # check if rfid exists in db, if not set status as "unknown_card"
            status = BackendSQL.log_attendance(rfid, local)
        except Exception as e:
            
            print(e)
            return 'Scan err', 404
        if(status):
            return 'logging error', 404 
        else:
            return 'Success', 201
    return 'Scan err', 404

@app.route("/get-user", methods=['GET'])
def get():
    if request.method == 'GET':
        try:
            sID = request.args.get('id')
            student = BackendSQL.get_from_db(sID)

            return str(student), 200
        except Exception as e:
            return 'Get error\n' + type(e).__name__, 404
    return 'Get err', 404

@app.route("/create-user", methods=['POST'])
def create():
    if request.method == 'POST':
        try:

            rfid = request.args.get('rfid')
            fName = request.args.get('fName')
            lName = request.args.get('lName')
            id = request.args.get('id')

            BackendSQL.insert_into_db(rfid, fName, lName, id)
        except Exception as e:
            return e, 404
        return 'Input Success', 201
    return 'Error', 404

@app.route("/test", methods=['GET'])
def test():
    return "Backend is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)