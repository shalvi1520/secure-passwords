from flask import Flask, request, jsonify
import mysql.connector
import hashlib
import base64
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app = Flask(__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="bye7788@@@",
    database="password_manager"
)
cursor = db.cursor()
salt_key = "fixed_salt_key"
def saltify(password: str, salt: str) -> str:
    salt_bytes = salt.encode('utf-8')
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, 100000)
    return base64.b64encode(hash_obj).decode('utf-8')
def verifyPassword(password: str, salt: str, storedPassword: str) -> bool:
    new_hash = saltify(password, salt)
    return new_hash == storedPassword
def send_otp(email, otp):
    sender_email = "khareshalvi77@gmail.com"
    password = "crtvwihdgzzoroyg"  

    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = email
        message['Subject'] = "Your OTP Code"

        body = f"Your OTP code is: {otp}"
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            text = message.as_string()
            server.sendmail(sender_email, email, text)

        print(f"OTP sent to {email}: {otp}")
    except Exception as e:
        print(f"Error sending email: {e}")
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({"message": "Invalid credentials!"}), 409

    hashed_password = saltify(password, salt_key)

    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
    db.commit()

    return jsonify({"message": "Account created successfully! Please log in to receive your OTP."}), 201
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and verifyPassword(password, salt_key, user[2]):
        otp = ''.join(random.choices(string.digits, k=6))
        otp_storage[username] = otp
        email = user[3]
        send_otp(email, otp)
        return jsonify({
            "message": "Login successful. OTP sent to your email!",
            "user_id": user[0]
        }), 200

    return jsonify({"message": "Invalid username or password"}), 401
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    username = data['username']
    otp_code = data['otp_code']

    if otp_storage.get(username) == otp_code:
        del otp_storage[username]
        return jsonify({"message": "OTP verified successfully! You can now log in."}), 200
    else:
        return jsonify({"message": "Invalid OTP!"}), 400
@app.route('/save_password', methods=['POST'])
def save_password():
    data = request.get_json()
    app_name = data['app_name']
    app_username = data['app_username']
    app_password = data['app_password']
    user_id = data['user_id']

    cursor.execute(
        "INSERT INTO passwords (user_id, app_name, app_username, app_password) VALUES (%s, %s, %s, %s)",
        (user_id, app_name, app_username, app_password)
    )
    db.commit()

    return jsonify({"message": "Password saved successfully!"}), 200
@app.route('/get_passwords', methods=['POST'])
def get_passwords():
    data = request.get_json()
    user_id = data['user_id']

    cursor.execute("SELECT app_name, app_username, app_password FROM passwords WHERE user_id = %s", (user_id,))
    passwords = cursor.fetchall()

    passwords_list = [
        {"app_name": app_name, "app_username": app_username, "app_password": app_password}
        for app_name, app_username, app_password in passwords
    ]

    return jsonify(passwords_list), 200

@app.route('/update_password', methods=['PUT'])
def update_password():
    data = request.get_json()
    password_id = data['password_id']
    new_app_name = data['app_name']
    new_app_username = data['app_username']
    new_app_password = data['app_password']

    cursor.execute("""
        UPDATE passwords 
        SET app_name = %s, app_username = %s, app_password = %s 
        WHERE id = %s
    """, (new_app_name, new_app_username, new_app_password, password_id))
    db.commit()

    return jsonify({"message": "Password updated successfully!"}), 200

@app.route('/delete_password', methods=['DELETE'])
def delete_password():
    data = request.get_json()
    password_id = data['password_id']

    cursor.execute("DELETE FROM passwords WHERE id = %s", (password_id,))
    db.commit()

    return jsonify({"message": "Password deleted successfully!"}), 200

otp_storage = {}
if __name__ == '__main__':
    app.run(debug=True)
