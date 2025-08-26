import streamlit as st
import pandas as pd
import pyodbc
import datetime as dt
import streamlit_authenticator as stauth
import os

 
st.set_page_config(page_title='PA Utilization Portal', layout='wide', initial_sidebar_state='expanded')
 
# # Database connection
# conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
#         +st.secrets['server']
#         +';DATABASE='
#         +st.secrets['database']
#         +';UID='
#         +st.secrets['username']
#         +';PWD='
#         +st.secrets['password']
#         ) 

# conn1 = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
#         +st.secrets['server1']
#         +';DATABASE='
#         +st.secrets['database1']
#         +';UID='
#         +st.secrets['username1']
#         +';PWD='
#         +st.secrets['password1']
#         ) 

server = os.environ.get('server_name')
database = os.environ.get('db_name')
username = os.environ.get('db_username')
password = os.environ.get('password')
conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
        + server
        +';DATABASE='
        + database
        +';UID='
        + username
        +';PWD='
        + password
        )
#assign credentials for the avon flex DB credentials
server1 = os.environ.get('server_name1')
database1 = os.environ.get('db_name1')
username1 = os.environ.get('db_username1')
password1 = os.environ.get('password1')
conn1 = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
        + server1
        +';DATABASE='
        + database1
        +';UID='
        + username1
        +';PWD='
        + password1
        )

def login_user(username,password):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * from tbl_utilization_portal_users WHERE UserName = ?", username)
        user = cursor.fetchone()
        if user:
            if password:
                return user[1], user[2], user[4], user[6]
            else:
                return None, None, None, None
        else:
            return None, None, None, None
        
# Initialize session state variables if they don't exist
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'password' not in st.session_state:
    st.session_state['password'] = None
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None


if st.session_state['authentication_status']:
    st.title("PA Utilization Portal")
    st.success(f"Welcome {st.session_state['name']} 👋")
    st.write(f"You are logged in as **{st.session_state['name']}** ({st.session_state['username']})")

    #sidebar navigation
    st.sidebar.title("Navigation")
    if st.session_state['username'].startswith("admin"):
        choice = st.sidebar.segmented_control("Select Module", ["Enrollee Module", "Client Module","Provider Module", 'Report Module',
                                                        "Enrollee After-Care Satisfaction Survey Module", "Referral Module"])
    elif st.session_state['username'].startswith("contact"):
        choice = st.sidebar.segmented_control("Select Module", ["Enrollee Module", "Referral Module"])
    elif st.session_state['username'].startswith("medical"):
        choice = st.sidebar.segmented_control("Select Module", ["Enrollee Module", "Provider Module"])
    elif st.session_state['username'].startswith("audit"):
        choice = st.sidebar.segmented_control("Select Module", ["Enrollee Module", "Client Module", "Provider Module", "Report Module"])
    elif st.session_state['username'].startswith("luqman"):
        choice = st.sidebar.segmented_control("Select Module", ["Enrollee Module", "Client Module", "Provider Module", "Report Module"])
    else:
        st.error('Access Denied: Invalid Role.')
    
        # --- Load Module Dynamically ---
    try:
        def execute_module(module_name):
            with open(module_name) as file:
                module_code = file.read()
            module_namespace = {'conn': conn, 'conn1': conn1, 'st': st, 'pd': pd, 'dt': dt}
            exec(module_code, module_namespace)

        if choice == "Enrollee Module":
            execute_module("EnrolleeModule.py")
        elif choice == "Referral Module":
            execute_module("Referral Module.py")
        elif choice == "Client Module":
            execute_module("Client Module.py")
        elif choice == "Provider Module":
            execute_module("Provider Module.py")
        elif choice == "Report Module":
            execute_module("Report Module.py")
        elif choice == "Enrollee After-Care Satisfaction Survey Module":
            st.info("This module is under development.")
            # execute_module("aftercaresurvey.py")
        
    except FileNotFoundError as e:
        st.error(f"Error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

    # --- Logout Button ---
    # Add the logout button in the sidebar
    with st.sidebar:
        if st.button('Logout'):
            st.session_state['name'] = None
            st.session_state['authentication_status'] = None
            st.session_state['username'] = None
            st.rerun()

elif st.session_state['authentication_status'] is False:
    st.error("❌ Username/password is incorrect")

elif st.session_state['authentication_status'] is None:
    st.warning("⚠️ Please enter your username and password")

#     # Display the login page
    st.sidebar.title("Home Page")
    st.sidebar.write("Welcome to the PA Utilization Portal!")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username and password:  # only proceed if both are entered
            login_username, name, user_role, login_password = login_user(username, password)

            if username == login_username and password == login_password: 
                st.session_state['authentication_status'] = True
                st.session_state['name'] = name
                st.session_state['username'] = login_username
                st.session_state['password'] = login_password
                st.session_state['user_role'] = user_role
                st.rerun()
            else:
                st.warning("⚠️ Username/password is incorrect")
        else:
            st.info("ℹ️ Please enter both username and password")

    
    