from flask import Flask, request

app = Flask(__name__)

@app.route("/log-scan", methods=['POST'])
def handle_login():
    if request.method == 'POST' and request.form.get('name'):
        name = request.form.get('name')
        return 'Scan Success', 201
    return 'Scan err', 404

@app.route("/get-user", methods=['GET'])
def get():
    return "get user!"

@app.route("/test", methods=['GET'])
def test():
    return "Backend is running."
