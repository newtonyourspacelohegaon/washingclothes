from flask import Flask, render_template, request, redirect, url_for,jsonify
from pymongo import MongoClient,errors
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
    
    data = {
    'user_id': first_name,
    'dateSelect': dateSelect,
    'timeSelect': timeSelect 
    }
    result = ""
    try:
        result = collection.insert_one(data)
        print(f"Document inserted with ID: {result.inserted_id}")
    except errors.DuplicateKeyError:
        print("Insertion failed: 'user_id' must be unique")
    return f"Form submitted successfully!<br>First Name: {first_name}<br>Last Name: {dateSelect}<br>Floor: {timeSelect}<br>Document inserted with ID: {result}"







