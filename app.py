from flask import Flask, render_template, request, redirect, url_for, flash, session, render_template_string
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import mysql.connector
from datetime import datetime as dt
from flask import json
from flask_mail import Mail, Message
from PIL import Image
from flask_compress import Compress
import os
import pandas as pd
import openai
import markdown
import ast
from flask_cors import CORS, cross_origin
openai.api_key = os.getenv("#INSERT OPENAI KEY HERE")
import stripe
stripe.api_key = 'sk_test_51ORp81SDzDKloi3cTX1N7YUQNiVdoyUbdwfnIu5sivGk1ZdsZgbsuGKkMezWfy7lDKAQpLo32SXCSmLwKqlSimVm00QfzkwKTp'
import qrcode
from io import BytesIO
import base64
app = Flask(__name__, static_url_path='/static')
app.secret_key = 'hotel'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'getawaymansion'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'u2109001@rajagiri.edu.in'
app.config['MAIL_PASSWORD'] = '#INSERT PASSWORD HERE'
app.config['MAIL_DEFAULT_SENDER'] = 'u2109001@rajagiri.edu.in'
mail = Mail(app)
Compress(app)
# Set the timeout value in seconds (adjust as needed)
app.config['MYSQL_CONNECT_TIMEOUT'] = 60000
mysql = MySQL(app)
bcrypt = Bcrypt(app)
CORS(app)

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS getawaymansion")
    cur.execute("USE getawaymansion")

    # Drop the tables in the following order
    cur.execute("DROP TABLE IF EXISTS cancellation")
    cur.execute("DROP TABLE IF EXISTS payments")
    cur.execute("DROP TABLE IF EXISTS roomallocation")
    cur.execute("DROP TABLE IF EXISTS booking")
    cur.execute("DROP TABLE IF EXISTS travelplan")
    cur.execute("DROP TABLE IF EXISTS rooms")
    cur.execute("DROP TABLE IF EXISTS customer")
    cur.execute("DROP TABLE IF EXISTS users")

    # Create user table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userid INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(60) NOT NULL,
            role ENUM('Admin', 'Customer') NOT NULL,
            status ENUM('Active', 'Inactive') NOT NULL
        )
    """)

    # Create rooms table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            roomsid INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(50) NOT NULL,
            rate INT NOT NULL,
            adultcount INT NOT NULL,
            childrencount INT NOT NULL
        )
    """)

    # Create customer table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            custid INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(10) NOT NULL,
            firstname VARCHAR(50) NOT NULL,
            lastname VARCHAR(50) NOT NULL,
            email VARCHAR(50) NOT NULL,
            phoneno VARCHAR(20) NOT NULL,
            country VARCHAR(50) NOT NULL,
            city VARCHAR(50) NOT NULL,
            userid INT NOT NULL,
            FOREIGN KEY (userid) REFERENCES users(userid)
        )
    """)

    # Create booking table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS booking (
            bookingid INT AUTO_INCREMENT PRIMARY KEY,
            checkindate DATETIME NOT NULL,
            checkoutdate DATETIME NOT NULL,
            status VARCHAR(50) NOT NULL,
            duration INT NOT NULL,
            roomsid INT NOT NULL,
            custid INT NOT NULL,
            FOREIGN KEY (custid) REFERENCES customer(custid),
            FOREIGN KEY (roomsid) REFERENCES rooms(roomsid)
        )
    """)

    # Create Payments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            paymentid INT AUTO_INCREMENT PRIMARY KEY,
            paymenttype VARCHAR(50) NOT NULL,
            amount INT NOT NULL,
            status VARCHAR(50) NOT NULL,
            bookingid INT NOT NULL,
            custid INT NOT NULL,
            FOREIGN KEY (bookingid) REFERENCES booking(bookingid),
            FOREIGN KEY (custid) REFERENCES customer(custid)
        )
    """)

    # Create Cancellation table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cancellation (
            cancellationid INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            time TIME NOT NULL,
            paymentid INT NOT NULL,
            bookingid INT NOT NULL,
            custid INT NOT NULL,
            FOREIGN KEY (paymentid) REFERENCES payments(paymentid),
            FOREIGN KEY (bookingid) REFERENCES booking(bookingid),
            FOREIGN KEY (custid) REFERENCES customer(custid)
        )
    """)

    # Create RoomAllocation table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS roomallocation (
            roomallocationid INT AUTO_INCREMENT PRIMARY KEY,
            roomsid INT NOT NULL,
            bookingid INT NOT NULL,
            FOREIGN KEY (roomsid) REFERENCES rooms(roomsid),
            FOREIGN KEY (bookingid) REFERENCES booking(bookingid)
        )
    """)

    # Create TravelPlan table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TravelPlan (
            travelplanid INT AUTO_INCREMENT PRIMARY KEY,
            preferences VARCHAR(255) NOT NULL,
            radius INT NOT NULL,
            rating FLOAT,
            link VARCHAR(255),
            custid INT NOT NULL,
            FOREIGN KEY (custid) REFERENCES customer(custid)
        )
    """)
    
    mysql.connection.commit()

    users_data = [
        {"email": "admin1@gmail.com", "password": "adminone", "role": "Admin", "status": "Active"},
        {"email": "john.doe@example.com", "password": "password1", "role": "Customer", "status": "Active"},
        {"email": "alice.smith@example.com", "password": "password2", "role": "Customer", "status": "Active"},
        {"email": "michael.johnson@example.com", "password": "password3", "role": "Customer", "status": "Active"},
        {"email": "emily.brown@example.com", "password": "password4", "role": "Customer", "status": "Active"},
        {"email": "robert.miller@example.com", "password": "password5", "role": "Customer", "status": "Active"},
        {"email": "sophia.davis@example.com", "password": "password6", "role": "Customer", "status": "Active"},
        # Add more user data as needed
    ]

    rooms_data = [
        {"type": "Penthouse", "rate": 190, "adultcount": 4, "childrencount": 3},
        {"type": "Penthouse", "rate": 190, "adultcount": 4, "childrencount": 3},
        {"type": "Penthouse", "rate": 190, "adultcount": 4, "childrencount": 3},
        {"type": "Presidential Suite", "rate": 160, "adultcount": 4, "childrencount": 3},
        {"type": "Presidential Suite", "rate": 160, "adultcount": 4, "childrencount": 3},
        {"type": "Presidential Suite", "rate": 160, "adultcount": 4, "childrencount": 3},
        {"type": "Executive Suite", "rate": 130, "adultcount": 4, "childrencount": 3},
        {"type": "Executive Suite", "rate": 130, "adultcount": 4, "childrencount": 3},
        {"type": "Executive Suite", "rate": 130, "adultcount": 4, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        # Add more room data as needed
    ]

    customers_data = [
        {"title": "Mr", "firstname": "John", "lastname": "Doe", "email": "john.doe@example.com", "phoneno": "1234567890", "country": "USA", "city": "New York", "userid": 2},
        {"title": "Ms", "firstname": "Alice", "lastname": "Smith", "email": "alice.smith@example.com", "phoneno": "9876543210", "country": "Canada", "city": "Toronto", "userid": 3},
        {"title": "Dr", "firstname": "Michael", "lastname": "Johnson", "email": "michael.johnson@example.com", "phoneno": "5551112233", "country": "UK", "city": "London", "userid": 4},
        {"title": "Mrs", "firstname": "Emily", "lastname": "Brown", "email": "emily.brown@example.com", "phoneno": "9998887777", "country": "Australia", "city": "Sydney", "userid": 5},
        {"title": "Mr", "firstname": "Robert", "lastname": "Miller", "email": "robert.miller@example.com", "phoneno": "1112223333", "country": "Germany", "city": "Berlin", "userid": 6},
        {"title": "Ms", "firstname": "Sophia", "lastname": "Davis", "email": "sophia.davis@example.com", "phoneno": "7776665555", "country": "France", "city": "Paris", "userid": 7},
        # Add more customer data as needed
    ]

    # Sample data for bookings
    booking_data = [
        {"checkindate": "2023-12-21", "checkoutdate": "2023-12-31", "status": "Confirmed", "duration": 10, "roomsid": 1, "custid": 1},
        {"checkindate": "2024-01-05", "checkoutdate": "2024-01-15", "status": "Confirmed", "duration": 10, "roomsid": 2, "custid": 2},
        {"checkindate": "2024-01-12", "checkoutdate": "2024-01-20", "status": "Cancelled", "duration": 8, "roomsid": 6, "custid": 3},
        {"checkindate": "2024-01-15", "checkoutdate": "2024-01-22", "status": "Confirmed", "duration": 7, "roomsid": 9, "custid": 4},
        {"checkindate": "2024-02-01", "checkoutdate": "2024-02-10", "status": "Cancelled", "duration": 9, "roomsid": 12, "custid": 5},
        {"checkindate": "2024-02-18", "checkoutdate": "2024-02-28", "status": "Confirmed", "duration": 10, "roomsid": 18, "custid": 6},
        # Add more booking data as needed
    ]

    # Sample data for payments
    payments_data = [
        {"paymenttype": "Credit Card", "amount": 190, "status": "completed", "bookingid": 1, "custid": 1},
        {"paymenttype": "Debit Card", "amount": 190, "status": "completed", "bookingid": 2, "custid": 2},
        {"paymenttype": "Credit Card", "amount": 160, "status": "completed", "bookingid": 3, "custid": 3},
        {"paymenttype": "Credit Card", "amount": 130, "status": "completed", "bookingid": 4, "custid": 4},
        {"paymenttype": "Debit Card", "amount": 90, "status": "completed", "bookingid": 5, "custid": 5},
        {"paymenttype": "Credit Card", "amount": 60, "status": "completed", "bookingid": 6, "custid": 6},
        # Add more payments data as needed
    ]

    # Sample data for cancellations
    cancellation_data = [
        {"date": "2024-01-10", "time": "14:30:00", "paymentid": 3, "bookingid": 3, "custid": 3},
        {"date": "2024-01-18", "time": "10:45:00", "paymentid": 5, "bookingid": 5, "custid": 5},
        # Add more cancellation data as needed
    ]   

    # Sample data for roomallocations
    roomallocation_data = [
        {"roomsid": 1, "bookingid": 1},
        {"roomsid": 2, "bookingid": 2},
        {"roomsid": 3, "bookingid": 3},
        {"roomsid": 4, "bookingid": 4},
        {"roomsid": 5, "bookingid": 5},
        {"roomsid": 6, "bookingid": 6},
        # Add more roomallocation data as needed
    ]

    # Sample data for TravelPlan
    travelplan_data = [
        {"preferences": "Nearby attractions", "radius": 10, "rating": 4.5, "link": "example.com", "custid": 1},
        {"preferences": "Quiet location", "radius": 5, "rating": 4.0, "link": "sample.com", "custid": 2},
        {"preferences": "City center", "radius": 8, "rating": 4.2, "link": "test.com", "custid": 3},
        {"preferences": "Scenic views", "radius": 12, "rating": 4.8, "link": "explore.com", "custid": 4},
        {"preferences": "Beachfront", "radius": 15, "rating": 5.0, "link": "beach.com", "custid": 5},
        {"preferences": "Mountain retreat", "radius": 20, "rating": 4.7, "link": "mountain.com", "custid": 6},
        # Add more travelplan data as needed
    ]

    # Insert sample data into users table
    insert_user_query = "INSERT INTO users (email, password, role, status) VALUES (%s, %s, %s, %s)"
    for user in users_data:
        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(user["password"]).decode('utf-8')
        values = (user["email"], hashed_password, user["role"], "Active")
        cur.execute(insert_user_query, values)

    # Insert sample data into rooms table
    insert_room_query = "INSERT INTO rooms (type, rate, adultcount, childrencount) VALUES (%s, %s, %s, %s)"
    for room in rooms_data:
        values = (room["type"], room["rate"], room["adultcount"], room["childrencount"])
        cur.execute(insert_room_query, values)

    # Insert sample data into customers table
    insert_customer_query = "INSERT INTO customer (title, firstname, lastname, email, phoneno, country, city, userid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    for customer in customers_data:
        values = (customer["title"], customer["firstname"], customer["lastname"], customer["email"], customer["phoneno"], customer["country"], customer["city"], customer["userid"])
        cur.execute(insert_customer_query, values)

    # Insert sample data into bookings table
    insert_booking_query = "INSERT INTO booking (checkindate, checkoutdate, status, duration, roomsid, custid) VALUES (%s, %s, %s, %s, %s, %s)"
    for booking in booking_data:
        values = (booking["checkindate"], booking["checkoutdate"], booking["status"], booking["duration"], booking["roomsid"], booking["custid"])
        cur.execute(insert_booking_query, values)

    # Insert sample data into payments table
    insert_payment_query = "INSERT INTO payments (paymenttype, amount, status, bookingid, custid) VALUES (%s, %s, %s, %s, %s)"
    for payment in payments_data:
        values = (payment["paymenttype"], payment["amount"], payment["status"], payment["bookingid"], payment["custid"])
        cur.execute(insert_payment_query, values)

    # Insert sample data into cancellations table
    insert_cancellation_query = "INSERT INTO cancellation (date, time, paymentid, bookingid, custid) VALUES (%s, %s, %s, %s, %s)"
    for cancellation in cancellation_data:
        values = (cancellation["date"], cancellation["time"], cancellation["paymentid"], cancellation["bookingid"], cancellation["custid"])
        cur.execute(insert_cancellation_query, values)

    # Insert sample data into roomallocation table
    insert_roomallocation_query = "INSERT INTO roomallocation (roomsid, bookingid) VALUES (%s, %s)"
    for roomallocation in roomallocation_data:
        values = (roomallocation["roomsid"], roomallocation["bookingid"])
        cur.execute(insert_roomallocation_query, values)

    # Insert sample data into TravelPlan table
    insert_travelplan_query = "INSERT INTO TravelPlan (preferences, radius, rating, link, custid) VALUES (%s, %s, %s, %s, %s)"
    for travelplan in travelplan_data:
        values = (travelplan["preferences"], travelplan["radius"], travelplan["rating"], travelplan["link"], travelplan["custid"])
        cur.execute(insert_travelplan_query, values)
    
    mysql.connection.commit()
    cur.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index', methods=['POST'])
def handle_form_submission():
    # Convert string dates to datetime objects for easier comparison
    checkin_date = dt.strptime(request.form['checkin_date'], '%Y-%m-%d').date()
    checkout_date = dt.strptime(request.form['checkout_date'], '%Y-%m-%d').date()
    # Query bookings for the specified dates
    booked_rooms = get_booked_rooms(checkin_date, checkout_date, status='Confirmed')
    # Query all available rooms
    available_rooms = get_available_rooms()
    # Exclude booked rooms from available rooms
    remaining_rooms = exclude_booked_rooms(available_rooms, booked_rooms)
    # Group remaining rooms by room type
    grouped_rooms = group_rooms_by_type(remaining_rooms)
    # Pass the data to the new template
    return render_template('enquiry.html', grouped_rooms=grouped_rooms, checkin_date=checkin_date, checkout_date=checkout_date)

def get_booked_rooms(checkin_date, checkout_date, status='Confirmed'):
    cursor = mysql.connection.cursor()
    query = """SELECT DISTINCT roomsid FROM booking WHERE checkoutdate > %s AND checkindate < %s AND status = %s"""
    cursor.execute(query, (checkin_date, checkout_date, status))
    booked_rooms = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return booked_rooms

def get_available_rooms():
    cursor = mysql.connection.cursor()
    query = "SELECT roomsid, type, rate, adultcount, childrencount FROM rooms"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        available_rooms = [dict(zip(columns, row)) for row in rows]
        return available_rooms
    except Exception as e:
        print(f"Error in get_available_rooms: {e}")
        return []
    finally:
        cursor.close()

def exclude_booked_rooms(available_rooms, booked_rooms):
    remaining_rooms = [room for room in available_rooms if room['roomsid'] not in booked_rooms]
    return remaining_rooms

def group_rooms_by_type(remaining_rooms):
    grouped_rooms = {}
    for room in remaining_rooms:
        room_type = room['type']
        if room_type not in grouped_rooms:
            grouped_rooms[room_type] = []
        grouped_rooms[room_type].append(room)

    return grouped_rooms

@app.route('/explore.html')
def explore():
    return render_template('explore.html')

@app.route('/rooms')
def rooms():
    return render_template('room.html')

@app.route('/room1.html')
def room1():
    return render_template('room1.html')

@app.route('/room2.html')
def room2():
    return render_template('room2.html')

@app.route('/room3.html')
def room3():
    return render_template('room3.html')

@app.route('/room4.html')
def room4():
    return render_template('room4.html')

@app.route('/room5.html')
def room5():
    return render_template('room5.html')

@app.route('/room6.html')
def room6():
    return render_template('room6.html')

@app.route('/aboutus.html')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus.html')
def contactus():
    return render_template('contactus.html')

@app.route('/privacypolicy.html')
def privacypolicy():
    return render_template('privacypolicy.html')

@app.route('/refundpolicy.html')
def refundpolicy():
    return render_template('refundpolicy.html')

@app.route('/faq.html')
def faq():
    return render_template('faq.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = 'Customer'  # Default role for new users
        status = 'Active'  # Default status for new users
        # Check if any of the form fields are empty
        if not email or not password or not confirm_password:
            flash("All fields must be filled.", "error")
            return redirect(url_for('signup'))
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match, try again.', category='error')
            return redirect(url_for('signup'))
        # Check if password is non-empty
        if not password:
            flash("Password must be non-empty. Please fill in a password.", "error")
            return redirect(url_for('signup'))
        # Check if password is longer than 4 characters
        if len(password)<4:
            flash("Password must be greater than 4 characters. Please fill in a secure password.", "error")
            return redirect(url_for('signup'))
        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            # Check if email already exists
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Email already exists. Please try again with a different email-id.', category='error')
                return redirect(url_for('signup'))
            # Insert user data into the 'users' table
            cur.execute("""INSERT INTO users (email, password, role, status) VALUES (%s, %s, %s, %s) """, (email, hashed_password, role, status))
            mysql.connection.commit()
            flash('Sign-up successful! Kindly Log in.', category='success')
            return redirect(url_for('signup'))
        except mysql.connector.Error as err:
            # Handle other errors
            print(err)
            flash("An error occurred. Please try again later.", "error")
            return redirect(url_for('signup'))
    cur.close()
    return render_template('signup.html')

@app.route('/adminsignup', methods=['GET', 'POST'])
def adminsignup():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        passkey = request.form['passkey']
        role = 'Admin'
        status = 'Active'
        # Check if passkey is correct
        if passkey != '1089':
            flash('Admin passkey is incorrect. Please try again.', category='error')
            return redirect(url_for('adminsignup'))
        # Check other form fields
        if not email or not password or not confirm_password:
            flash("All fields must be filled.", "error")
            return redirect(url_for('adminsignup'))
        if password != confirm_password:
            flash('Passwords do not match, try again.', category='error')
            return redirect(url_for('adminsignup'))
        if not password:
            flash("Password must be non-empty. Please fill in a password.", "error")
            return redirect(url_for('adminsignup'))
        if len(password) < 4:
            flash("Password must be greater than 4 characters. Please fill in a secure password.", "error")
            return redirect(url_for('adminsignup'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Email already exists. Please try again with a different email-id.', category='error')
                return redirect(url_for('adminsignup'))
            cur.execute("""INSERT INTO users (email, password, role, status) VALUES (%s, %s, %s, %s) """,
                        (email, hashed_password, role, status))
            mysql.connection.commit()
            flash('Admin sign-up successful! Kindly log in.', category='success')
            return redirect(url_for('adminsignup'))
        except mysql.connector.Error as err:
            print(err)
            flash("An error occurred. Please try again later.", "error")
            return redirect(url_for('adminsignup'))
    cur.close()
    return render_template('adminsignup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = None  # Initialize the cursor outside the try block
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check if email and password are provided
        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for('login'))
        try:
            cur = mysql.connection.cursor()
            # Check if user exists
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if user:
                # Check if the provided password matches the hashed password in the database
                if bcrypt.check_password_hash(user[2], password):
                    session['user_id'] = user[0]  # Store user ID in the session
                    if user[3] == 'Admin': 
                        return redirect(url_for('admin_dashboard'))
                    elif user[3] == 'Customer':
                        return redirect(url_for('customer_dashboard', userid=user[0]))  # Pass userid to customer_dashboard  
                else:
                    flash("Incorrect password. Please try again.", "error")
            else:
                flash("User not found. Please sign up.", "error")
        except Exception as e:
            print(f"Error in login: {e}")
            flash("An error occurred. Please try again later.", "error")
        finally:
            if cur:
                cur.close()
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    # Retrieve user details from the database based on user_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    return render_template('admin_dashboard.html', user_email=user_email, user_id=user_id)

@app.route('/customer_dashboard')
def customer_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    # Retrieve user details from the database based on user_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    email = cur.fetchone()[0]
    cur.close()

    return render_template('customer_dashboard.html', user_email=email, user_id=user_id)

@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return redirect(url_for('index'))

#ADMIN DASHBOARD FUNCTONALITIES
@app.route('/admin_view_rooms')
def admin_view_rooms():
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()
    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM rooms"
    cursor.execute(query)
    rooms_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Room ID", "Type", "Rate", "Adult Count", "Children Count", "Actions"]
    rooms_list = []
    for room in rooms_data:
        room_dict = {
            "Room ID": room[0],         
            "Type": room[1],         
            "Rate": room[2],      
            "Adult Count": room[3],     
            "Children Count": room[4],  
            "Actions": "<a href='{}'>Edit</a>".format(url_for('admin_edit_room', room_id=room[0]),room[0]
),
        }
        rooms_list.append(room_dict)
    rooms_json = json.dumps(rooms_list)

    return render_template('admin_view_rooms.html', headers=table_headers, rooms_data=rooms_json, user_email=user_email, user_id=user_id)

@app.route('/admin_edit_room/<int:room_id>', methods=['GET', 'POST'])
def admin_edit_room(room_id):
    
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    if request.method == 'POST':
        new_type = request.form.get('new_type')
        new_rate = request.form.get('new_rate')
        new_adult_count = request.form.get('new_adult_count')
        new_children_count = request.form.get('new_children_count')

        cursor = mysql.connection.cursor()
        query = """
            UPDATE rooms 
            SET type = %s, rate = %s, adultcount = %s, childrencount = %s
            WHERE roomsid = %s
        """
        cursor.execute(query, (new_type, new_rate, new_adult_count, new_children_count, room_id))
        mysql.connection.commit()
        cursor.close()

        flash("Room updated successfully.", "success")
        return redirect(url_for('admin_view_rooms'))

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM rooms WHERE roomsid = %s"
    cursor.execute(query, (room_id,))
    room_data = cursor.fetchone()
    cursor.close()

    if not room_data:
        flash("Room not found.", "error")
        return redirect(url_for('admin_view_rooms'))

    return render_template('admin_edit_room.html', room_data=room_data, user_email=user_email, user_id=user_id)


@app.route('/admin_add_room', methods=['GET', 'POST'])
def admin_add_room():
    if 'user_id' not in session:
        flash("You must be logged in as an admin to perform this action.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to perform this action.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    if request.method == 'POST':
        type = request.form.get('type')
        rate = request.form.get('rate')
        adult_count = request.form.get('adult_count')
        children_count = request.form.get('children_count')

        cursor = mysql.connection.cursor()
        query = """
            INSERT INTO rooms (type, rate, adultcount, childrencount)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (type, rate, adult_count, children_count))
        mysql.connection.commit()
        cursor.close()

        flash("Room added successfully.", "success")
        return redirect(url_for('admin_view_rooms'))

    return render_template('admin_add_room.html', user_email=user_email, user_id=user_id)

@app.route('/admin/view_bookings')  
def admin_view_bookings():
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    query = """
        SELECT
                b.bookingid,
                b.checkindate,
                b.checkoutdate,
                b.status,
                b.duration,
                b.roomsid,
                r.type AS room_type,
                b.custid,
                c.firstname,
                c.lastname
            FROM
                booking b
            JOIN
                rooms r ON b.roomsid = r.roomsid
            JOIN
                customer c ON b.custid = c.custid
    """
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    bookings_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Booking ID", "Check-in Date", "Check-out Date", "Status", "Duration", "Room ID","Room Type", "Customer ID", "Customer Name"]
    bookings_list = []
    for booking in bookings_data:
        booking_dict = {
            "Booking ID": booking[0],
            "Check-in Date": booking[1],
            "Check-out Date": booking[2],
            "Status": booking[3],
            "Duration": booking[4],
            "Room ID": booking[5],
            "Room Type": booking[6],
            "Customer ID": booking[7],
            "Customer Name": f"{booking[8]} {booking[9]}"
        }
        bookings_list.append(booking_dict)
    bookings_json = json.dumps(bookings_list)

    return render_template('admin_view_bookings.html', headers=table_headers, bookings_data=bookings_json, user_email=user_email, user_id=user_id)

@app.route('/admin_view_payments')
def admin_view_payments():
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM payments"
    cursor.execute(query)
    payments_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Payment ID", "Payment Type", "Amount", "Status", "Booking ID", "Customer ID"]

    payments_list = []
    for payments in payments_data:
        payments_dict = {
            "Payment ID": payments[0],
            "Payment Type": payments[1],
            "Amount": payments[2],
            "Status": payments[3],
            "Booking ID": payments[4],
            "Customer ID": payments[5]
        }
        payments_list.append(payments_dict)

    payments_json = json.dumps(payments_list)

    return render_template('admin_view_payments.html', headers=table_headers, payments_data=payments_json, user_email=user_email, user_id=user_id)

@app.route('/admin_view_room_allocations')
def admin_view_room_allocations():
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    query = """
        SELECT
                r.roomallocationid,
                r.roomsid,
                x.type,
                r.bookingid,
                b.checkindate,
                b.checkoutdate
            FROM
                roomallocation r
            JOIN
                rooms x ON r.roomsid = x.roomsid
            JOIN
                booking b ON r.bookingid = b.bookingid
    """

    cursor = mysql.connection.cursor()
    cursor.execute(query)
    roomallocation_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Room Allocation ID", "Room ID", "Room Type", "Booking ID", "Check In Date", "Check Out Date"]

    roomallocation_list = []
    for roomallocation in roomallocation_data:
        roomallocation_dict = {
            "Room Allocation ID": roomallocation[0],
            "Room ID": roomallocation[1],
            "Room Type": roomallocation[2],
            "Booking ID": roomallocation[3],
            "Check In Date": roomallocation[4],
            "Check Out Date": roomallocation[5]
        }
        roomallocation_list.append(roomallocation_dict)

    roomallocation_json = json.dumps(roomallocation_list)

    return render_template('admin_view_room_allocations.html', headers=table_headers, roomallocation_data=roomallocation_json, user_email=user_email, user_id=user_id)

@app.route('/admin_view_customer')
def admin_view_customer():
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM customer"
    cursor.execute(query)
    customer_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Customer ID", "Title", "First Name", "Last Name", "Email", "Phone no", "Country", "City", "User ID"]

    customer_list = []
    for customer in customer_data:
        customer_dict = {
            "Customer ID": customer[0],
            "Title": customer[1],
            "First Name": customer[2],
            "Last Name": customer[3],
            "Email": customer[4],
            "Phone no": customer[5],
            "Country": customer[6],
            "City": customer[7],
            "User ID": customer[8]
        }
        customer_list.append(customer_dict)

    customer_json = json.dumps(customer_list)

    return render_template('admin_view_customer.html', headers=table_headers, customer_data=customer_json, user_email=user_email, user_id=user_id)

@app.route('/admin_view_registered_users')
def admin_view_registered_users():
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()
    query = """
        SELECT
            u.userid,
            u.email,
            u.role,
            u.status
        FROM
            users u

    """
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    users_data = cursor.fetchall()
    cursor.close()
    table_headers = ["User ID", "Email", "Role", "Status"]
    users_list = []
    for users in users_data:
        users_dict = {
            "User ID": users[0],
            "Email": users[1],
            "Role": users[2],
            "Status": users[3]
        }
        users_list.append(users_dict)
    users_json = json.dumps(users_list)

    return render_template('admin_view_registered_users.html', headers=table_headers, users_data=users_json, user_email=user_email, user_id=user_id)

@app.route('/admin_view_travel_plans')
def admin_view_travel_plans():
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM TravelPlan"
    cursor.execute(query)
    travel_plans_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Travel Plan ID", "Preferences", "Radius", "Rating", "Link", "Customer ID"]

    travel_plans_list = []
    for travel_plan in travel_plans_data:
        travel_plan_dict = {
            "Travel Plan ID": travel_plan[0],
            "Preferences": travel_plan[1],
            "Radius": travel_plan[2],
            "Rating": travel_plan[3],
            "Link": travel_plan[4],
            "Customer ID": travel_plan[5]
        }
        travel_plans_list.append(travel_plan_dict)

    travel_plans_json = json.dumps(travel_plans_list)

    return render_template('admin_view_travel_plans.html', headers=table_headers, travel_plans_data=travel_plans_json, user_email=user_email, user_id=user_id)

@app.route('/admin_view_cancellation')
def admin_view_cancellation():
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM cancellation"
    cursor.execute(query)
    cancellation_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Cancellation ID", "Date", "Time", "Payment ID", "Booking ID", "Customer ID"]

    cancellation_list = []
    for cancellation in cancellation_data:
        cancellation_dict = {
            "Cancellation ID": cancellation[0],
            "Date": str(cancellation[1]),  
            "Time": str(cancellation[2]),  
            "Payment ID": cancellation[3],
            "Booking ID": cancellation[4],
            "Customer ID": cancellation[5]
        }
        cancellation_list.append(cancellation_dict)

    cancellation_json = json.dumps(cancellation_list)

    return render_template('admin_view_cancellation.html', headers=table_headers, cancellation_data=cancellation_json, user_email=user_email, user_id=user_id)


#CUSTOMER DASHBOARD FUNCTIONALITIES
@app.route('/customer/bookings/<int:userid>')  
def customer_view_bookings(userid):
    if 'user_id' not in session or session['user_id'] != userid:
        flash("You must be logged in as a user to view this page.", "error")
        return redirect(url_for('login'))

    user_id = userid
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()
    if role != 'Customer':
        flash("You must be logged in as a customer to view this page.", "error")
        return redirect(url_for('login'))
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    query = """
        SELECT
                b.bookingid,
                b.checkindate,
                b.checkoutdate,
                b.status,
                b.duration,
                b.roomsid,
                r.type AS room_type,
                b.custid,
                c.firstname,
                c.lastname,
                p.paymentid
            FROM
                booking b
            JOIN
                rooms r ON b.roomsid = r.roomsid
            JOIN
                customer c ON b.custid = c.custid
            JOIN
                users u ON c.userid = u.userid
            JOIN
                payments p ON b.bookingid = p.bookingid
            WHERE
                u.userid = %s
    """

    cursor = mysql.connection.cursor()
    cursor.execute(query, (user_id,))
    custbookings_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Booking ID", "Check-in Date", "Check-out Date", "Status", "Duration", "Room ID","Room Type", "Customer ID", "Customer Name", "Payment ID", "Actions"]

    custbookings_list = []
    for custbooking in custbookings_data:
        custbooking_dict = {
            "Booking ID": custbooking[0],
            "Check-in Date": custbooking[1],
            "Check-out Date": custbooking[2],
            "Status": custbooking[3],
            "Duration": custbooking[4],
            "Room ID": custbooking[5],
            "Room Type": custbooking[6],
            "Customer ID": custbooking[7],
            "Customer Name": f"{custbooking[8]} {custbooking[9]}",
            "Payment ID": custbooking[10],
            "Actions": "<a href='{}'>Cancel</a>".format(url_for('cancel_booking', booking_id=custbooking[0])),
        }
        custbookings_list.append(custbooking_dict)

    custbookings_json = json.dumps(custbookings_list)

    return render_template('customer_view_bookings.html', headers=table_headers, custbookings_data=custbookings_json, user_id=user_id, user_email=user_email)

@app.route('/cancel_booking/<int:booking_id>', methods=['GET', 'POST'])
def cancel_booking(booking_id):
    # Retrieve payment_id and cust_id from payments table
    select_query = "SELECT paymentid, custid FROM payments WHERE bookingid = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(select_query, (booking_id,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        payment_id, cust_id = result
    else:
        flash('Booking not found.', 'error')
        return redirect(url_for('customer_view_bookings', userid=session['user_id']))

    # Update booking status to 'Cancelled' in booking table
    update_query = "UPDATE booking SET status = 'Cancelled' WHERE bookingid = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(update_query, (booking_id,))
    mysql.connection.commit()
    cursor.close()

    # Insert a new record into the cancellation table
    insert_query = "INSERT INTO cancellation (date, time, paymentid, bookingid, custid) VALUES (CURDATE(), CURTIME(), %s, %s, %s)"
    cursor = mysql.connection.cursor()
    cursor.execute(insert_query, (payment_id, booking_id, cust_id))
    mysql.connection.commit()
    cursor.close()

    flash('Booking cancelled successfully.', 'success')
    return redirect(url_for('customer_view_bookings', userid=session['user_id']))

@app.route('/customer/travelplan/<int:userid>')  
def customer_view_travelplan(userid):
    if 'user_id' not in session or session['user_id'] != userid:
        flash("You must be logged in as a user to view this page.", "error")
        return redirect(url_for('login'))

    user_id = userid

    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Customer':
        flash("You must be logged in as a customer to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    query = """
        SELECT
                t.travelplanid,
                t.preferences,
                t.radius,
                t.rating,
                t.link,
                t.custid,
                c.firstname,
                c.lastname
            FROM
                TravelPlan t
            JOIN
                customer c ON t.custid = c.custid
            JOIN
                users u ON c.userid = u.userid
            WHERE
                u.userid = %s
    """

    cursor = mysql.connection.cursor()
    cursor.execute(query, (user_id,))
    custtravelplan_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Travel Plan ID", "Preferences", "Radius", "Rating", "Link", "Customer ID", "Customer Name"]

    custtravelplan_list = []
    for custtravelplan in custtravelplan_data:
        custtravelplan_dict = {
            "Travel Plan ID": custtravelplan[0],
            "Preferences": custtravelplan[1],
            "Radius": custtravelplan[2],
            "Rating": custtravelplan[3],
            "Link": custtravelplan[4],
            "Customer ID": custtravelplan[5],
            "Customer Name": f"{custtravelplan[6]} {custtravelplan[7]}"
        }
        custtravelplan_list.append(custtravelplan_dict)

    custtravelplan_json = json.dumps(custtravelplan_list)

    return render_template('customer_view_travelplan.html', headers=table_headers, custtravelplan_data=custtravelplan_json, user_email=user_email, user_id=user_id)

# Chat engine
def chat_with_chatgpt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=600,
        n=1,
        stop=None,
        temperature=0.5
    )
    message = response.choices[0].text.strip()
    return message

@app.route('/customertravelplan', methods=['GET', 'POST'])
def customertravelplan():

    if request.method == 'GET':

        coord = [103.8146499, 1.36219165]

        df2 = [[103.6580253, 1.346533], [104.006950, 1.349143]]
        
        return render_template('customertravelplan.html', df2=df2, origin=df2[0], midpt=coord)

    if request.method == 'POST':

        if request.form.get("textp") == "yes":

            text = request.form.to_dict(flat=True)
       
            add1 = "In the last paragraph, give the gps coordinates of each of these places in a Python dictionary."

            markdown_text_main = chat_with_chatgpt(text["textprompt"] + add1)
            html = markdown.markdown(markdown_text_main)

            listo = []
            keyo = []
            latlist = []
            lonlist = []
            coord = []

            try:

                ans = markdown_text_main.split("{")

                p1 = ans[1]

                pwhole = "{" + p1 

                print(pwhole)

                #dict1 = json.loads(pwhole)
                res_coord = ast.literal_eval(pwhole)

                print(res_coord, type(res_coord))   
                
                for key, value in res_coord.items():

                    print(key, value)

                    listo.append([value[1], value[0]])
                    keyo.append(key)
                    latlist.append(value[0])
                    lonlist.append(value[1])

                print(keyo, listo)

                print("latlist: ", latlist)
                print("lonlist: ", lonlist)

                lon_mid = sum(lonlist)/len(lonlist)

                print(lon_mid)

                lat_mid = sum(latlist)/len(latlist)

                print(lat_mid)

                coord = [lon_mid, lat_mid]

                print(coord)

            except:

                pass

            
            return render_template("customertravelplan.html", out=html, df2=listo, origin=listo, midpt=coord)

@app.route('/customer/payments/<int:userid>')  
def customer_view_payments(userid):
    if 'user_id' not in session or session['user_id'] != userid:
        flash("You must be logged in as a user to view this page.", "error")
        return redirect(url_for('login'))

    user_id = userid

    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Customer':
        flash("You must be logged in as a customer to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    query = """
        SELECT
                p.paymentid,
                p.paymenttype,
                p.amount,
                p.status,
                p.bookingid,
                p.custid,
                c.firstname,
                c.lastname
            FROM
                payments p
            JOIN
                customer c ON p.custid = c.custid
            JOIN
                users u ON c.userid = u.userid
            WHERE
                u.userid = %s
    """

    cursor = mysql.connection.cursor()
    cursor.execute(query, (user_id,))
    custpayments_data = cursor.fetchall()
    cursor.close()

    table_headers = ["Payment ID", "Payment Type", "Amount", "Status", "Booking ID", "Customer ID", "Customer Name"]

    custpayments_list = []
    for custpayments in custpayments_data:
        custpayments_dict = {
            "Payment ID": custpayments[0],
            "Payment Type": custpayments[1],
            "Amount": custpayments[2],
            "Status": custpayments[3],
            "Booking ID": custpayments[4],
            "Customer ID": custpayments[5],
            "Customer Name": f"{custpayments[6]} {custpayments[7]}"
        }
        custpayments_list.append(custpayments_dict)

    custpayments_json = json.dumps(custpayments_list)

    return render_template('customer_view_payments.html', headers=table_headers, custpayments_data=custpayments_json, user_email=user_email, user_id=user_id)


@app.route('/customer/booking1/<int:user_id>', methods=['GET', 'POST'])
def customer_booking1(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        flash("You must be logged in as a user to view this page.", "error")
        return redirect(url_for('login'))

    user_id = user_id

    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Customer':
        flash("You must be logged in as a customer to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    if request.method == 'POST':
        title = request.form.get('title')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        mobile_number = request.form.get('mobile_number')
        country = request.form.get('country')
        city = request.form.get('city')

        session['customer_details'] = {
            'title': title,
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'mobile_number': mobile_number,
            'country': country,
            'city': city
        }
        return render_template('customer_booking2.html', user_id=user_id,title=title, firstname=firstname, lastname=lastname, email=email,
            mobile_number=mobile_number, country=country, city=city, user_email=user_email)
    
    else:
        return render_template('customer_booking1.html', user_id=user_id, user_email=user_email)



@app.route('/customer/booking2<int:user_id>', methods=['POST'])
def customer_booking2(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        flash("You must be logged in as a user to view this page.", "error")
        return redirect(url_for('login'))

    user_id = user_id

    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Customer':
        flash("You must be logged in as a customer to view this page.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()
    
    if request.method == 'POST':
        return handle_form_submission(user_id)
    

    return render_template('customer_booking2.html', user_id=user_id, user_email=user_email)

def handle_form_submission(user_id):
    checkin_date = dt.strptime(request.form['checkin_date'], '%Y-%m-%d').date()
    checkout_date = dt.strptime(request.form['checkout_date'], '%Y-%m-%d').date()
    duration = (checkout_date - checkin_date).days

    booked_rooms = get_booked_rooms(checkin_date, checkout_date, status='Confirmed')
    available_rooms = get_available_rooms()
    remaining_rooms = exclude_booked_rooms(available_rooms, booked_rooms)
    grouped_rooms = group_rooms_by_type(remaining_rooms)

    session['booking_data'] = {
        'grouped_rooms': grouped_rooms,
        'checkin_date': checkin_date,
        'checkout_date': checkout_date,
        'duration': duration,
        'user_id': user_id
    }

    user_details = session.get('customer_details', {})
    title = user_details.get('title')
    firstname = user_details.get('firstname')
    lastname = user_details.get('lastname')
    email = user_details.get('email')
    mobile_number = user_details.get('mobile_number')
    country = user_details.get('country')
    city = user_details.get('city')

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    # Check if required booking data exists in the session
    if not all([title, firstname, lastname, email, mobile_number, country, city]):
        flash("Missing some user details. Please start the booking process again.", "error")
        return redirect(url_for('customer_booking1', userid=user_id))

    return render_template('customer_booking3.html', grouped_rooms=grouped_rooms, checkin_date=checkin_date, checkout_date=checkout_date, duration=duration, user_id=user_id,
        title=title, firstname=firstname, lastname=lastname, email=email, mobile_number=mobile_number, country=country, city=city, user_email=user_email)

def get_booked_rooms(checkin_date, checkout_date, status='Confirmed'):
    cursor = mysql.connection.cursor()
    query = """SELECT DISTINCT roomsid FROM booking WHERE checkoutdate > %s AND checkindate < %s AND status = %s"""
    cursor.execute(query, (checkin_date, checkout_date, status))
    booked_rooms = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return booked_rooms

def get_available_rooms():
    cursor = mysql.connection.cursor()
    query = "SELECT roomsid, type, rate, adultcount, childrencount FROM rooms"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        available_rooms = [dict(zip(columns, row)) for row in rows]

        return available_rooms
    except Exception as e:
        print(f"Error in get_available_rooms: {e}")
        return []
    finally:
        cursor.close()

def exclude_booked_rooms(available_rooms, booked_rooms):
    remaining_rooms = [room for room in available_rooms if room['roomsid'] not in booked_rooms]
    return remaining_rooms

def group_rooms_by_type(remaining_rooms):
    grouped_rooms = {}
    for room in remaining_rooms:
        room_type = room['type']
        if room_type not in grouped_rooms:
            grouped_rooms[room_type] = []
        grouped_rooms[room_type].append(room)

    return grouped_rooms

room_type_price_ids = {
    'Penthouse': 'price_1ORpVdSDzDKloi3chV6nsaKv',
    'Presidential Suite': 'price_1ORpXESDzDKloi3c8xlkgH2K',
    'Executive Suite': 'price_1ORpYASDzDKloi3ckHgy2r6Q',
    'Studio': 'price_1ORpZYSDzDKloi3cpMw8s7D7',
    'Deluxe Room': 'price_1ORpaASDzDKloi3cU1QBeLyt',
    'Standard Room': 'price_1ORpbDSDzDKloi3cHHc2v90A',
}

@app.route('/customer/booking3/<int:user_id>', methods=['POST'])
def customer_booking3(user_id):
    selected_room_type = request.form.get('selectedRoomType')
    price_id = room_type_price_ids.get(selected_room_type)

    session['room_data'] = {
        'room_type': selected_room_type
    }

    if price_id:
        user_details = session.get('customer_details', {})

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            billing_address_collection='required',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
            customer_email=user_details.get('email', ''),

        )
        # 4000003560000008  STRIPE TEST CARD FOR INDIA
        return render_template('stripe_checkout.html', session_id=checkout_session.id, user_id=user_id, )
    else:
        flash('Invalid room type selected.', 'error')
        return redirect(url_for('customer_booking1', user_id=user_id))


@app.route('/booking/success')
def success():
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]

    user_details = session.get('customer_details', {})
    booking_data = session.get('booking_data', {})
    room_data = session.get('room_data', {})
    user_id = booking_data.get('user_id')
    checkin_date = booking_data.get('checkin_date')
    checkout_date = booking_data.get('checkout_date')
    duration = booking_data.get('duration')
    room_type = room_data.get('room_type')
    title = user_details.get('title')
    firstname = user_details.get('firstname')
    lastname = user_details.get('lastname')
    email = user_details.get('email')
    mobile_number = user_details.get('mobile_number')
    country = user_details.get('country')
    city = user_details.get('city')

    checkin_date = dt.strptime(checkin_date, '%a, %d %b %Y %H:%M:%S GMT').date()
    checkout_date = dt.strptime(checkout_date, '%a, %d %b %Y %H:%M:%S GMT').date()
    booked_rooms = get_booked_rooms(checkin_date, checkout_date, status='Confirmed')
    available_rooms = get_available_rooms()
    remaining_rooms = exclude_booked_rooms(available_rooms, booked_rooms)
    grouped_rooms = group_rooms_by_type(remaining_rooms)
    selected_rooms = grouped_rooms.get(room_type, [])
    
    if selected_rooms:
        room_id = selected_rooms[0]['roomsid']
    else:
        room_id = None

    if room_id is not None:  
        cur.execute("""
            INSERT INTO customer (title, firstname, lastname, email, phoneno, country, city, userid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, firstname, lastname, email, mobile_number, country, city, user_id))

        cust_id = cur.lastrowid
    
        cur.execute("""
            INSERT INTO booking (checkindate, checkoutdate, status, duration, roomsid, custid)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (checkin_date, checkout_date, 'Confirmed', duration, room_id, cust_id))

        booking_id = cur.lastrowid
        session['booking_id']=booking_id
    
        room_rate = next((room['rate'] for room in available_rooms if room['roomsid'] == room_id), None)
        # Store room_rate in the session
        session['room_rate'] = room_rate

        cur.execute("""
            INSERT INTO payments (paymenttype, amount, status, bookingid, custid)
            VALUES (%s, %s, %s, %s, %s)
        """, ('Credit Card', room_rate, 'Completed', booking_id, cust_id))

        cur.execute("SELECT paymentid FROM payments WHERE bookingid = %s", (booking_id,))
        payment_id = cur.fetchone()[0]
        session['payment_id']=payment_id


        cur.execute("""
            INSERT INTO roomallocation (roomsid, bookingid)
            VALUES (%s, %s)
        """, (room_id, booking_id))

        mysql.connection.commit()
        cur.close()

        qr_data = f"Booking Details:\n\nUser ID: {user_id}\nCheck-in Date: {checkin_date}\nCheck-out Date: {checkout_date}\nDuration: {duration} days\nRoom Type: {room_type}\n\nCustomer Details:\nTitle: {title}\nFirst Name: {firstname}\nLast Name: {lastname}\nEmail: {email}\nMobile Number: {mobile_number}\nCountry: {country}\nCity: {city}\n\nAdditional Details:\nUser Email: {user_email}\nBooking ID: {booking_id}\nPayment ID: {payment_id}\nPayment Type: Credit Card\nRoom Rate: {room_rate}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        # Create a PIL image
        img = qr.make_image(fill_color="black", back_color="white")
        # Save the image to a BytesIO object
        img_bytes_io = BytesIO()
        img.save(img_bytes_io, format="PNG")
        # Encode the image as a base64 string
        img_base64 = base64.b64encode(img_bytes_io.getvalue()).decode("utf-8")
        # Store img_base64 in the session
        session['img_base64'] = img_base64

        return render_template('success.html', user_id=user_id, checkin_date=checkin_date, checkout_date=checkout_date,
            duration=duration, room_type=room_type, title=title, firstname=firstname, lastname=lastname,
            email=email, mobile_number=mobile_number, country=country, city=city,
            qr_code=img_base64, user_email=user_email,
            booking_id=booking_id, payment_id=payment_id, payment_type='Credit Card', room_rate=room_rate)
    else:
        flash('No available rooms for the selected type and dates.', 'error')
        return redirect(url_for('customer_booking1', user_id=user_id))



@app.route('/send_email', methods=['POST'])
def send_email():
    user_details = session.get('customer_details', {})
    booking_data = session.get('booking_data', {})
    room_data = session.get('room_data', {})
    booking_id = session.get('booking_id')
    payment_id = session.get('payment_id')
    room_rate = session.get('room_rate')

    # Compose email content
    email_content = f"Booking Confirmation Details:<br><br>"
    email_content += f"Customer Name: {user_details.get('firstname')} {user_details.get('lastname')}<br>"
    email_content += f"Customer Email: {user_details.get('email')}<br>"
    email_content += f"Customer Mobile Number: {user_details.get('mobile_number')}<br>"
    email_content += f"Customer Country: {user_details.get('country')}<br>"
    email_content += f"Customer City: {user_details.get('city')}<br><br>"
    email_content += f"Room Type: {room_data.get('room_type')}<br>"
    email_content += f"Check-in Date: {booking_data.get('checkin_date')}<br>"
    email_content += f"Check-out Date: {booking_data.get('checkout_date')}<br>"
    email_content += f"Duration: {booking_data.get('duration')} days<br>"
    email_content += f"Booking ID: {booking_id}<br>"
    email_content += f"Payment ID: {payment_id}<br>"
    email_content += f"Payment Type: Credit Card<br>"
    email_content += f"Payment Amount: {room_rate}<br>"

    # Send email with attachment
    msg = Message(subject='Booking Confirmation - The Getaway Mansion', sender='u2109001@rajagiri.edu.in', recipients=[user_details.get('email')])

    # Attach QR code image
    # Retrieve img_base64 from the session
    qr_image_data = session.get('img_base64')
    # Check if qr_image_data is not None before proceeding
    if qr_image_data:
        # Decode the base64 image data
        qr_image = Image.open(BytesIO(base64.b64decode(qr_image_data)))
        img_bytes_io = BytesIO()
        qr_image.save(img_bytes_io, format="PNG")
        img_bytes = img_bytes_io.getvalue()
        msg.attach('qrcode.png', 'image/png', img_bytes)
    else:
        print("Error: img_base64 is None")

    email_template = """
    <html>
    <head>
        <style>
            .header {
                background-color: #FFF7F5;
                color: #ff0000;
                padding: 20px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }

            .content {
                padding: 20px;
                font-size: 16px;
                color: #333;
            }

            .footer {
                background-color: #FFF7F5;
                color: #ff0000;
                padding: 20px;
                text-align: center;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h3>The Getaway Mansion - Booking Confirmation</h3>
        </div>

        <div class="content">
            <p>{{ email_content | safe }}</p>
        </div>

        <div class="footer">
            <p>Thank you for choosing The Getaway Mansion!</p>
        </div>
    </body>
    </html>
    """
    rendered_email = render_template_string(email_template, email_content=email_content)
    msg.html = rendered_email

    mail.send(msg)
    return "Email sent successfully!"

@app.route('/booking/cancel')
def cancel():
    user_id = session['user_id']
    # Retrieve user details from the database based on user_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    return render_template('cancel.html', user_email=user_email, user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)
