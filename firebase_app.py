import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import os
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
person = {"is_logged_in": False, "name": "", "email": "", "uid": "", "chat_id": "", "user_id": ""}

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

@app.route("/userdata", methods = ["POST", "GET"])
def sendData():
    if request.method == "POST":   
        result = request.form      
        userData = result["user_data"]
        #send via api to the server with the user's chat id, stored in global person
        # person["chat_id"]
        print(userData, person["chat_id"])
    return render_template("welcome.html", email = person["email"], name = person["name"])


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
            person["info"] = data.val()[person["uid"]]["info"]
            person["age"] = data.val()[person["uid"]]["age"]
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
        info = result["info"]
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
            person["info"] = info
            person["name"] = name
            person["age"] = age
            #Append data to the firebase realtime database
            data = {"name": name, "email": email, "age": age, "user id": user_id, "chat_id": chat_id, "info" : info, "user_data": ''}
            db.child("users").child(person["uid"]).set(data)
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            return redirect(url_for('oops'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('/'))

if __name__ == "__main__":
    app.run()
