from flask import Flask, render_template, request, redirect, url_for,jsonify
from pymongo import MongoClient,errors
from datetime import datetime, timedelta

# Replace the connection string with your MongoDB Atlas credentials
uri = "mongodb+srv://newuserforlife:newuserforlife@cluster0.fginm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to the MongoDB Atlas cluster
client = MongoClient(uri)

# Select your database
db = client['washingMachine']

# Select your collection
collection = db['floor1']


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book.html')
def booking():
    return render_template('book.html')

@app.route('/newUser.html')
def sign_up():
    return render_template('newUser.html')

@app.route('/get_available_slots')
def get_available_slots():
    # Get the selected date from the query string
    selected_date = request.args.get('date')
    
    # Define all possible time slots
    all_time_slots = [
        "12:00 AM - 1:00 AM", "1:00 AM - 2:00 AM", "2:00 AM - 3:00 AM",
        "3:00 AM - 4:00 AM", "4:00 AM - 5:00 AM", "5:00 AM - 6:00 AM",
        "6:00 AM - 7:00 AM", "7:00 AM - 8:00 AM", "8:00 AM - 9:00 AM",
        "9:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM",
        "12:00 PM - 1:00 PM", "1:00 PM - 2:00 PM", "2:00 PM - 3:00 PM",
        "3:00 PM - 4:00 PM", "4:00 PM - 5:00 PM", "5:00 PM - 6:00 PM",
        "6:00 PM - 7:00 PM", "7:00 PM - 8:00 PM", "8:00 PM - 9:00 PM",
        "9:00 PM - 10:00 PM", "10:00 PM - 11:00 PM", "11:00 PM - 12:00 AM"
    ]

    # Query MongoDB to find booked time slots for the selected date
    booked_slots = collection.find({"dateSelect": selected_date}, {"timeSelect": 1, "_id": 0})
    booked_slots = [slot['timeSelect'] for slot in booked_slots]  # Extract time slots from the result

    # Filter out booked time slots from all available time slots
    available_slots = [slot for slot in all_time_slots if slot not in booked_slots]

    # Return the available slots as a JSON response
    return jsonify(available_slots)

@app.route('/action_page.php', methods=['POST'])
def handle_form():
    first_name = request.form.get('name')
    dateSelect = request.form.get('date')
    timeSelect = request.form.get('time')

    if collection.find_one({"dateSelect": dateSelect, "timeSelect": timeSelect}):
        return "Error: Time slot already booked."
    nam = collection.find_one({"user_id": first_name})
    if not nam:
        return "User Name not in database"
    
    original_date = datetime.strptime(dateSelect, "%Y-%m-%d")

    new_date = original_date + timedelta(days=4)

    data = {
    'dateSelect': dateSelect,
    'timeSelect': timeSelect,
    'resetDate':new_date.strftime("%Y-%m-%d")
    }

    try:
        if collection.find_one({"user_id": first_name,"resetDate":{"$exists": True}}):
            if datetime.today() >= datetime.strptime(collection.find({"user_id": first_name})[0]["resetDate"],"%Y-%m-%d"):
                result = collection.update_one(
                    {'user_id': first_name},
                    {'$set': data}
                )
                return (f"Document updated with ID: {result}")
            else:
                tempDateSelect=collection.find({"user_id": first_name})[0]["resetDate"]
                tempDateBooked = collection.find({"user_id": first_name})[0]["dateSelect"]
                temptimeSelect = collection.find({"user_id": first_name})[0]["timeSelect"]
                return f"Error: you can book after {tempDateSelect},you have booked the slot for{temptimeSelect} on {tempDateBooked}"
        else:
            result = collection.update_one(
            {'user_id': first_name},
            {'$set': data}
        )
            return (f"Document inserted with ID: {result}")
    except errors.DuplicateKeyError:
        return ("Insertion failed: 'user_id' must be unique")
    return f"Form submitted successfully!<br>First Name: {first_name}<br>Last Name: {dateSelect}<br>Floor: {timeSelect}<br>{result}"

@app.route('/sign_up.php', methods=['POST'])
def handle_sign():
    first_name = request.form.get('name')
    hostelFloor = request.form.get('floor')
    hostelRoom = request.form.get('room')

    if collection.find_one({"user_id": first_name}):
        return "Error: The User Already Exist."
    
    data = {
    'user_id': first_name,
    'floor': hostelFloor,
    'room': hostelRoom
    }

    # new_field = {
    # 'new_field_name': 'new_field_value'  # replace with your field name and value
    # }


    try:
        # result = collection.update_one(
        #     {'user_id': first_name},
        #     {'$set': new_field}
        # )
        result = collection.insert_one(data)
        print(f"Document inserted with ID: {result.inserted_id}")
    except errors.DuplicateKeyError:
        print("Insertion failed: 'user_id' must be unique")
    return f"Form submitted successfully!<br>User ID: {first_name}<br>Floor: {hostelFloor}<br>Room: {hostelRoom}<br>inserted with Id:-{result.inserted_id}"




