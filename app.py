from flask import Flask, request, jsonify, render_template
import BackendSQL

app = Flask(__name__, template_folder='bttendance_frontend')

@app.route("/")
def index():
    return render_template("index.html")

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
            return status, 404
        if(status):
            return status, 404 
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

@app.route("/get-all-users", methods=['GET'])
def get_all_users():
    users = BackendSQL.get_all_users()
    if users is None:
        return jsonify({"error": "Database error"}), 500
    for u in users:
        if u.get('created_at'):
            u['created_at'] = str(u['created_at'])
    return jsonify(users), 200

@app.route("/get-attendance", methods=['GET'])
def get_attendance():
    student_id = request.args.get('id')
    location = request.args.get('location')
    date = request.args.get('date')
    records = BackendSQL.get_attendance(student_id, location, date)
    if records is None:
        return jsonify({"error": "Database error"}), 500
    for r in records:
        if r.get('timestamp'):
            r['timestamp'] = str(r['timestamp'])
    return jsonify(records), 200

@app.route("/test", methods=['GET'])
def test():
    return "Backend is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)