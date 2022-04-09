from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import sqlite3
from datetime import datetime

con = sqlite3.connect('CrimeReport.db', check_same_thread=False)

cursor = con.cursor()

Report_table = con.execute("SELECT name from sqlite_master WHERE type='table' AND name='REPORTS'").fetchall()
user_table = con.execute("SELECT name from sqlite_master WHERE type='table' AND name='USERS'").fetchall()

if Report_table:
    print("Table Already Exists ! ")
else:
    con.execute(''' CREATE TABLE REPORTS(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            NAME TEXT DEFAULT "Guest" NOT NULL,
                            DESCRIPTION TEXT,
                            REMARKS TEXT,
                            DATE TEXT ); ''')
    print("Table has created")

if user_table:
    print("Table Already Exists ! ")
else:
    con.execute(''' CREATE TABLE USERS(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            NAME TEXT,
                            ADDRESS TEXT,
                            EMAIL TEXT,
                            PHONE TEXT,
                            PASSWORD TEXT ); ''')
    print("Table has created")

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("Home.html")


@app.route("/login-admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        getUsername = request.form["uname"]
        getPswd = request.form["pswd"]
        if getUsername == "admin" and getPswd == "12345":
            return redirect("/view-crimes")
    return render_template("admin_login.html")


@app.route("/login-user", methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        getEmail = request.form["email"]
        getPswd = request.form["pswd"]
        # print(getEmail)
        # print(getPswd)
        try:
            query = "SELECT * FROM USERS WHERE EMAIL = '" + getEmail + "' AND PASSWORD = '" + getPswd + "'"
            cursor.execute(query)
            result = cursor.fetchall()
            print(result)
            if len(result) == 0:
                print("Invalid User")
            else:
                for i in result:
                    getName = i[1]
                    getid = i[0]

                    session["name"] = getName
                    session["id"] = getid
                return redirect("/complaint-report")
        except Exception as e:
            print(e)
    return render_template("user_login.html")


@app.route("/register-user", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        getname = request.form["name"]
        getAddr = request.form["address"]
        getEmail = request.form["email"]
        getPhone = request.form["mno"]
        getPswd = request.form["pswd"]

        print(getname)
        print(getAddr)
        print(getEmail)
        print(getPhone)
        print(getPswd)

        try:
            data = (getname, getAddr, getEmail, getPhone, getPswd)
            insert_query = '''INSERT INTO USERS(NAME, ADDRESS, EMAIL, PHONE, PASSWORD) 
                                VALUES (?,?,?,?,?)'''

            cursor.execute(insert_query, data)
            con.commit()
            print("User added successfully")
            return redirect("/login-user")

        except Exception as e:
            print(e)
    return render_template("user_register.html")


@app.route("/complaint-report", methods=["GET", "POST"])
def complaint_report():
    if not session.get("name"):
        return redirect("/login-user")
    else:
        if request.method == "POST":
            getName = session["name"]
            getDescription = request.form["description"]
            getRemarks = request.form["remarks"]
            curr_date = datetime.now().date()

            print(getDescription)
            print(getRemarks)
            print(curr_date)
            print(getName)

            try:
                data = (getName, getDescription, getRemarks, curr_date)
                insert_query = '''INSERT INTO REPORTS(NAME, DESCRIPTION, REMARKS, DATE) 
                                    VALUES (?,?,?,?)'''

                cursor.execute(insert_query, data)
                con.commit()
                print("Reported successfully")
                return render_template("user_home.html")

            except Exception as e:
                print(e)
        return render_template("complaint_report.html")


@app.route("/complaint-report-guest", methods=["GET", "POST"])
def complaintreportGuest():
    if request.method == "POST":
        getDescription = request.form["description"]
        getRemarks = request.form["remarks"]
        curr_date = datetime.now().date()
        # getName = ""

        print(getDescription)
        print(getRemarks)
        print(curr_date)

        try:
            data = (getDescription, getRemarks, curr_date)
            insert_query = '''INSERT INTO REPORTS(DESCRIPTION, REMARKS, DATE) 
                                VALUES (?,?,?)'''

            cursor.execute(insert_query, data)
            con.commit()
            print("Reported successfully")
            return render_template("guest_home.html")

        except Exception as e:
            print(e)
    return render_template("complaint_report_guest.html")


@app.route("/update-user", methods=["GET", "POST"])
def update():
    if not session.get("name"):
        return redirect("/login-user")
    else:
        if request.method == "POST":
            getName = request.form["Name"]
            getAddress = request.form["address"]
            getEmail = request.form["email"]
            getPhone = request.form["mno"]
            try:
                data = (getName, getAddress, getEmail, getPhone, getName)
                insert_query = '''UPDATE USERS SET NAME = ?,ADDRESS=?,EMAIL=?,PHONE=?
                                   where NAME = ?'''

                cursor.execute(insert_query, data)
                print("SUCCESSFULLY UPDATED!")
                con.commit()
                return render_template("updateuser.html")
            except Exception as e:
                print(e)
        else:
            getName = session["name"]
            print(getName)
            try:
                cursor.execute("SELECT* FROM USERS WHERE NAME= '" + getName + "'")
                print("SUCCESSFULLY SELECTED!")
                result = cursor.fetchall()
                if len(result) == 0:
                    print("Invalid Data")
                else:
                    print(result)
                    return render_template("user_update.html", user=result)
            except Exception as e:
                print(e)

    return render_template("/user_update.html")


@app.route("/view-crimes")
def View():
    cursor.execute("SELECT * FROM REPORTS")
    result = cursor.fetchall()
    return render_template("view_crimes.html", crimes=result)


@app.route("/viewcrimes-date", methods=["GET", "POST"])
def ViewCrimesBydate():
    if request.method == "POST":
        getDate = request.form["date"]
        print(getDate)
        try:
            cursor.execute("SELECT * FROM REPORTS WHERE DATE = '" + getDate + "'")
            print("SUCCESSFULLY SELECTED!")
            result = cursor.fetchall()
            print(result)
            if len(result) == 0:
                print("no record found")
            else:
                print(len(result))
                return render_template("crimesbydate.html", crime=result, status=True)
        except Exception as e:
            print(e)

    return render_template("crimesbydate.html", crime=[])


@app.route("/logout-user", methods=["GET", "POST"])
def userlogout():
    if not session.get("name"):
        return redirect("/login-user")
    else:
        session["name"] = None
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
