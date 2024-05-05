import pyrebase
from flask import Flask, session, flash, redirect, render_template, request, session, abort, url_for
import os
import json
import requests
app = Flask(__name__)       #Initialze flask constructor

#Add your own details
config = {
    "apiKey": os.environ.get('FIREBASE_AUTH_KEY'),
    "authDomain": "sb-flask.firebaseapp.com",
    "databaseURL": "https://sb-flask-default-rtdb.firebaseio.com",
    "projectId": "sb-flask",
    "storageBucket": "sb-flask.appspot.com",
    "messagingSenderId": "537358433568",
    "appId": "1:537358433568:web:a0425f0a4445bafcd7eb45"
}

#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

#Initialze person as dictionary
person = {
    "is_logged_in": False, 
    "name": "", 
    "age":"", 
    "height":"", 
    "weight":"", 
    "email": "", 
    "uid": "", 
    "chat_id": "", 
    "user_id": "",
    "blood_pressure":"",
    "blood_sugar":"",
    "extra_info":"",
    "heart_history":"",
    "responses":""
}

#Login
@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/oops")
def oops():
    return render_template("wrong.html")

@app.route("/logout")
def logout():
    global person
    person = {
    "is_logged_in": False, 
    "name": "", 
    "age":"", 
    "height":"", 
    "weight":"", 
    "email": "", 
    "uid": "", 
    "chat_id": "", 
    "user_id": "",
    "blood_pressure":"",
    "blood_sugar":"",
    "extra_info":"",
    "heart_history":"",
    "responses":""
    }    
    return redirect(url_for('login'))

@app.route("/userdata", methods = ["POST", "GET"])
def sendData():
    if request.method == "POST":   
        result = request.form      
        userData = result["user_data"]
        try:
            send = json.loads(userData)
            print(send)
            response = requests.post('https://telegrambot-green-beta.vercel.app/api', json=send)
            print(response.json())
        except ValueError:
            pass
    return redirect(url_for('welcome'))

#Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("welcome.html", email = person["email"], name = person["name"])
    else:
        return redirect(url_for('login'))
    
#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            #Get the name of the user
            data = db.child("users").get()
            print(data.val()[person["uid"]])
            person["name"] = data.val()[person["uid"]]["name"]
            person["user_id"] = data.val()[person["uid"]]["user id"]
            person["chat_id"] = data.val()[person["uid"]]["chat_id"]
            person["extra_info"] = data.val()[person["uid"]]["extra_info"]
            person["age"] = data.val()[person["uid"]]["age"]
            person["height"] = data.val()[person["uid"]]["height"]
            person["weight"] = data.val()[person["uid"]]["weight"]
            person["blood_sugar"] = data.val()[person["uid"]]["blood_sugar"]
            person["blood_pressure"] = data.val()[person["uid"]]["blood_pressure"]
            person["heart_history"] = data.val()[person["uid"]]["heart_history"]
            #Redirect to welcome page
            return redirect(url_for('welcome'))
        except Exception as e:
            return redirect(url_for('oops'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        age = result["age"] 
        user_id = result["id"]
        chat_id = result["chat_id"]
        extra_info = result["info"]
        blood_sugar = result["blood_sugar"]
        blood_pressure = result["blood_pressure"]
        heart_history = result["heart_history"]
        height = result["height"]
        weight = result["weight"]
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["user_id"] = user_id
            person["chat_id"] = chat_id
            person["info"] = extra_info
            person["name"] = name
            person["age"] = age
            person["height"] = height
            person["weight"] = weight
            person["blood_sugar"] = blood_sugar
            person["blood_pressure"] = blood_pressure
            person["heart_history"] = heart_history
            #Append data to the firebase realtime database
            data = {
                "name": name, 
                "email": email, 
                "age": age, 
                "user id": user_id, 
                "chat_id": chat_id, 
                "height": height, 
                "weight": weight,
                "blood_sugar":blood_sugar,
                "blood_pressure":blood_pressure,
                "heart_history":heart_history,
                "responses": '',
                "extra_info": extra_info
            }
            db.child("users").child(person["uid"]).set(data)
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            return redirect(url_for('oops'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('oops'))

if __name__ == "__main__":
    app.run()
