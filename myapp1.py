import streamlit as st
import requests
import base64
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'otp_verified' not in st.session_state:
    st.session_state.otp_verified = False
if 'is_signup' not in st.session_state:
    st.session_state.is_signup = False
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode()
    return base64_image
def add_custom_css():
    base64_image = get_base64_image("background.jpg")
    st.markdown(
        f"""
        <style>
        .container {{
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}
        .left-section {{
            flex: 1;
            background-image: url(data:image/jpg;base64,{base64_image});
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }}
        .right-section {{
            flex: 1;
            background-color: rgba(0, 0, 0, 0.7);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            padding: 40px;
        }}
        h1, h2, h3 {{
            color: #faca2b;
        }}
        .stButton>button {{
            background-color: #3498db;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-family: Arial, Helvetica, sans-serif;
        }}
        .stTextInput>div>input {{
            border: 2px solid #faca2b;
            padding: 10px;
            border-radius: 5px;
            font-family: Arial, Helvetica, sans-serif;
            background-color: #2c3e50;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
add_custom_css()
def signup_login_page():
    st.markdown(
        """
        <div class="container">
            <div class="left-section"></div>
            <div class="right-section">
                <h1>Welcome to the Password Manager!</h1>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.is_signup:
        st.subheader("Create Your Account")
        signup_username = st.text_input("Choose a username", key="signup_username_input")
        signup_email = st.text_input("Enter your email", key="signup_email_input")
        signup_password = st.text_input("Choose a password", type="password", key="signup_password_input")

        if st.button("Create Account"):
            signup_data = {'username': signup_username, 'email': signup_email, 'password': signup_password}
            signup_response = requests.post('http://127.0.0.1:5000/signup', json=signup_data)

            if signup_response.status_code == 201:
                st.success("Account created successfully! Please log in.")
                st.session_state.is_signup = False  
                st.rerun()  
            else:
                try:
                    st.error(signup_response.json()["message"])
                except requests.exceptions.JSONDecodeError:
                    st.error("Invalid response from server. Please try again later.")
    else:
        st.subheader("Login to Your Account")
        username = st.text_input("Enter your username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")

        if st.button("Login"):
            login_data = {'username': username, 'password': password}
            response = requests.post('http://127.0.0.1:5000/login', json=login_data)
            if response.status_code == 200:
                try:
                    result = response.json()
                    st.session_state.user_id = result['user_id']
                    st.session_state.username = username
                    st.session_state.otp_sent = True  
                    st.session_state.logged_in = False  
                    st.session_state.otp_verified = False  
                    st.rerun()  
                except requests.exceptions.JSONDecodeError:
                    st.error("Invalid response from server. Please try again later.")
            else:
                try:
                    st.error(response.json()["message"])
                except requests.exceptions.JSONDecodeError:
                    st.error("Invalid response from server. Please try again later.")

    if st.session_state.is_signup:
        if st.button("Already have an account? Login"):
            st.session_state.is_signup = False  
            st.rerun()  
    else:
        if st.button("Don't have an account? Sign Up"):
            st.session_state.is_signup = True  
            st.rerun()  

    st.markdown('</div></div>', unsafe_allow_html=True)
def otp_verification_page():
    st.warning("Please verify OTP to proceed.")
    otp_code = st.text_input("Enter OTP sent to your email", key="otp_input")

    if st.button("Submit OTP"):
        otp_verification = requests.post(
            'http://127.0.0.1:5000/verify_otp',
            json={'username': st.session_state.username, 'otp_code': otp_code}
        )

        if otp_verification.status_code == 200:
            try:
                result = otp_verification.json()
                st.session_state.otp_verified = True  
                st.success("OTP verified successfully!")
                st.session_state.logged_in = True  
                st.rerun() 
            except requests.exceptions.JSONDecodeError:
                st.error("Invalid response from server. Please try again later.")
        else:
            st.error("Invalid OTP. Please try again.")
def welcome_page():
    st.markdown(f"<h1 style='text-align: center; color: #faca2b;'>Hello {st.session_state.username}!</h1>", unsafe_allow_html=True)
def password_manager_page():
    st.title("Manage Your Passwords")
    app_name = st.text_input("Application Name")
    app_username = st.text_input("App Username")
    app_password = st.text_input("App Password", type="password")

    if 'save_button_clicked' not in st.session_state:
        st.session_state.save_button_clicked = False

    if st.button("Save Password", disabled=st.session_state.save_button_clicked):
        st.session_state.save_button_clicked = True
        data = {
            'app_name': app_name,
            'app_username': app_username,
            'app_password': app_password,
            'user_id': st.session_state.user_id
        }
        response = requests.post('http://127.0.0.1:5000/save_password', json=data)
        if response.status_code == 200:
            try:
                result = response.json()
                st.success("Password saved successfully!")
            except requests.exceptions.JSONDecodeError:
                st.error("Invalid response from server. Please try again later.")
        else:
            try:
                st.error(response.json()["message"])
            except requests.exceptions.JSONDecodeError:
                st.error("Invalid response from server. Please try again later.")
        st.session_state.save_button_clicked = False  

    if st.button("Get Saved Passwords"):
        response = requests.post('http://127.0.0.1:5000/get_passwords', json={'user_id': st.session_state.user_id})
        if response.status_code == 200:
            try:
                passwords = response.json()
                if passwords:
                    for app in passwords:
                        col1, col2, col3 = st.columns([4, 1, 1])
                        with col1:
                            st.write(f"**App:** {app['app_name']}, **Username:** {app['app_username']}, **Password:** {app['app_password']}")
                        with col2:
                            if st.button(f"Update {app['app_name']}", key=f"update_{app['app_name']}"):
                                st.session_state['app_to_update'] = app
                                st.experimental_rerun()
                        with col3:
                            if st.button(f"Delete {app['app_name']}", key=f"delete_{app['app_name']}"):
                                delete_password(app['app_name'])
                                st.experimental_rerun()
                                                     
                           
                else:
                    st.warning("No passwords found")
            except requests.exceptions.JSONDecodeError:
                st.error("Invalid response from server. Please try again later")
        else:
            st.error("Failed to retrieve passwords. Please try again later.")
def update_password(app_name, new_password):
    response = requests.post('http://127.0.0.1:5000/update_password', json={
        'user_id': st.session_state.user_id,
        'app_name': app_name,
        'new_password': new_password
    })
    if response.status_code == 200:
        st.success("Password updated successfully!")
    else:
        st.error("Failed to update password. Please try again later.")
    if 'app_to_update' in st.session_state:
        st.subheader("Update Password")
        app_to_update = st.session_state['app_to_update']
        new_app_password = st.text_input("New Password", type="password", key="new_app_password")

        if st.button("Update"):
            update_password(app_to_update['app_name'], new_app_password)  
            del st.session_state['app_to_update']
            st.success("Password updated successfully!")
            st.experimental_rerun()  

def delete_password(app_name):
    response = requests.post('http://127.0.0.1:5000/delete_password', json={
        'user_id': st.session_state.user_id,
        'app_name': app_name
    })
    if response.status_code == 200:
        st.success("Password deleted successfully!")
    else:
        st.error("Failed to delete password. Please try again later.")


def main():
    if st.session_state.logged_in and st.session_state.otp_verified:
        welcome_page()
        password_manager_page()  
    elif st.session_state.otp_sent and not st.session_state.otp_verified:
        otp_verification_page()  
    else:
        signup_login_page()  
if __name__ == "__main__":
    main()
