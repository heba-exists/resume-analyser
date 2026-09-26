from flask import Flask, request, session, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret_string"

CORS(app, supports_credentials=True)

FAKE_USERS = {
    "test@example.com": "password123"
}


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if email in FAKE_USERS and FAKE_USERS[email] == password:
        session["user_id"] = email
        return jsonify({"message": "Login successful", "user_id": email}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"}), 200


@app.route("/verify-session", methods=["GET"])
def verify_session():
    user_id = session.get("user_id")
    if user_id:
        return jsonify({"valid": True, "user_id": user_id}), 200
    else:
        return jsonify({"valid": False}), 401


if __name__ == "__main__":
    app.run(debug=True, port=5000)