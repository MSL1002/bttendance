from flask import Flask, request, jsonify, render_template, Response
import BackendSQL
import queue
import threading

app = Flask(__name__, template_folder='bttendance_frontend')

# Single enrollment slot — only one student can be enrolled at a time
_enrollment_lock = threading.Lock()
_pending_enrollment = None  # dict with fName, lName, id, queue — or None

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

@app.route("/start-enrollment", methods=['POST'])
def start_enrollment():
    global _pending_enrollment
    fName = request.args.get('fName')
    lName = request.args.get('lName')
    student_id = request.args.get('id')

    with _enrollment_lock:
        _pending_enrollment = {
            'fName': fName,
            'lName': lName,
            'id': student_id,
            'queue': queue.Queue(),
        }

    return 'OK', 200


@app.route("/enrollment-stream")
def enrollment_stream():
    def event_stream():
        with _enrollment_lock:
            enrollment = _pending_enrollment
        if not enrollment:
            yield "data: error\n\n"
            return
        try:
            result = enrollment['queue'].get(timeout=120)
            yield f"data: {result}\n\n"
        except queue.Empty:
            yield "data: timeout\n\n"

    return Response(event_stream(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


@app.route("/enroll-rfid", methods=['POST'])
def enroll_rfid():
    global _pending_enrollment
    rfid = request.args.get('rfid')

    with _enrollment_lock:
        enrollment = _pending_enrollment

    if not enrollment:
        return 'No pending enrollment', 404

    try:
        BackendSQL.insert_into_db(rfid, enrollment['fName'], enrollment['lName'], enrollment['id'])
    except Exception as e:
        enrollment['queue'].put('error')
        return str(e), 500

    enrollment['queue'].put('success')

    with _enrollment_lock:
        _pending_enrollment = None

    return 'Enrolled', 201

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

@app.route("/delete-user", methods=['DELETE'])
def delete_user():
    student_id = request.args.get('id')
    affected = BackendSQL.delete_student(student_id)
    if affected is None:
        return 'Database error', 500
    if affected == 0:
        return 'Student not found', 404
    return 'Deleted', 200

@app.route("/get-all-instructors", methods=['GET'])
def get_all_instructors():
    result = BackendSQL.get_all_instructors()
    if result is None:
        return jsonify({"error": "Database error"}), 500
    return jsonify(result), 200

@app.route("/add-instructor", methods=['POST'])
def add_instructor():
    first_name = request.args.get('fName', '').strip()
    last_name  = request.args.get('lName', '').strip()
    if not first_name or not last_name:
        return 'Missing name fields', 400
    new_id = BackendSQL.add_instructor(first_name, last_name)
    if new_id is None:
        return 'Database error', 500
    return jsonify({'id': new_id}), 201

@app.route("/delete-instructor", methods=['DELETE'])
def delete_instructor():
    instructor_id = request.args.get('id')
    affected = BackendSQL.delete_instructor(instructor_id)
    if affected is None:
        return 'Database error', 500
    if affected == 0:
        return 'Instructor not found', 404
    return 'Deleted', 200

@app.route("/get-all-classes", methods=['GET'])
def get_all_classes():
    result = BackendSQL.get_all_classes()
    if result is None:
        return jsonify({"error": "Database error"}), 500
    return jsonify(result), 200

@app.route("/add-class", methods=['POST'])
def add_class():
    name          = request.args.get('name', '').strip()
    instructor_id = request.args.get('instructor_id')
    location      = request.args.get('location', '').strip()
    days          = request.args.get('days', '').strip().upper()
    start_time    = request.args.get('start_time')
    end_time      = request.args.get('end_time')
    start_date    = request.args.get('start_date')
    end_date      = request.args.get('end_date')
    if not all([name, instructor_id, location, days, start_time, end_time, start_date, end_date]):
        return 'Missing required fields', 400
    new_id = BackendSQL.add_class(name, instructor_id, location, days, start_time, end_time, start_date, end_date)
    if new_id is None:
        return 'Database error', 500
    return jsonify({'id': new_id}), 201

@app.route("/delete-class", methods=['DELETE'])
def delete_class():
    class_id = request.args.get('id')
    affected = BackendSQL.delete_class(class_id)
    if affected is None:
        return 'Database error', 500
    if affected == 0:
        return 'Class not found', 404
    return 'Deleted', 200

@app.route("/get-class-enrollments", methods=['GET'])
def get_class_enrollments():
    class_id = request.args.get('class_id')
    result = BackendSQL.get_class_enrollments(class_id)
    if result is None:
        return jsonify({"error": "Database error"}), 500
    return jsonify(result), 200

@app.route("/enroll-student", methods=['POST'])
def enroll_student():
    class_id = request.args.get('class_id')
    user_id  = request.args.get('user_id')
    ok = BackendSQL.enroll_student_in_class(class_id, user_id)
    return ('OK', 200) if ok else ('Database error', 500)

@app.route("/unenroll-student", methods=['DELETE'])
def unenroll_student():
    class_id = request.args.get('class_id')
    user_id  = request.args.get('user_id')
    ok = BackendSQL.unenroll_student_from_class(class_id, user_id)
    return ('OK', 200) if ok else ('Database error', 500)

@app.route("/get-analytics", methods=['GET'])
def get_analytics():
    result = BackendSQL.get_analytics()
    if result is None:
        return jsonify({"error": "Database error"}), 500
    return jsonify(result), 200

@app.route("/test", methods=['GET'])
def test():
    return "Backend is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)