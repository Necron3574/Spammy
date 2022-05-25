from flask import *
from flask_session import Session
import sqlite3 as sql
import uuid
import smtplib, ssl, sys
import spammer_util as spamy

app = Flask(__name__)
conn = None
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class Email:
	def __init__(self, email, uid, subject, nums, tlist, body):
		self.email = email
		self.uid = uid
		self.sub = subject
		self.nums = nums
		self.tlist = tlist
		self.body = body

@app.route("/", methods = ["GET", "POST"])
def index_page():
	if session.get("email"):
		return redirect('/home')
	elif request.method == "POST":
		email = request.form.get("signInEmail")
		password =  request.form.get("signInPassword")

		#check validity
		try:
			port = 465
			server = smtplib.SMTP_SSL("smtp.gmail.com", port, context = ssl.create_default_context())
			server.login(email,password)
		except Exception as e:
			print(e)
			flash("Sign in error", 'SIE')
			return redirect('/')
		#check validity

		session["email"] = email
		session["password"] = password
		return redirect('/home')
	return render_template('loginpage.html')

@app.route("/home", methods = ["POST", "GET"])
def home_page():
	if not session.get("email"):
		return redirect('/')
	elif request.method == "POST":
		vals = [None for i in range(4)]
		vals[0] = request.form.get("tlist")
		vals[1] = request.form.get("sub")
		vals[2] = request.form.get("body")
		vals[3] = request.form.get("nums")
		flag = 1
		for v in vals:
			if not v or v == "":
				flag = 0
				flash("invalid data", 'IBD')
				break
		if flag:
			db = sql.connect('emails.db')
			email = session.get('email')
			pwd = session.get('password')
			uid = str(uuid.uuid4().hex)
			curr_mail = Email(email, uid, vals[1], vals[3], vals[0], vals[2])
			#print("INSERT INTO EMAIL VALUES('"+curr_mail.email+"','"+curr_mail.uid+"',"+curr_mail.sub+"',"+curr_mail.nums+",'"+curr_mail.tlist+"','"+curr_mail.body+"')")
			print(email, pwd)
			lst = curr_mail.tlist.split(',')
			spamy.Email_sender(email, lst, pwd, curr_mail.body, curr_mail.sub, int(curr_mail.nums))
			db.execute("INSERT INTO EMAIL VALUES('"+curr_mail.email+"','"+curr_mail.uid+"','"+curr_mail.sub+"',"+curr_mail.nums+",'"+curr_mail.tlist+"','"+curr_mail.body+"')")
			db.commit()
			return redirect('/manage')
	return render_template("create-mail.html")

@app.route("/manage")
def manage_posts():
	if not session.get("email"):
		return redirect('/')
	db = sql.connect('emails.db')
	cursor = db.execute("SELECT * FROM EMAIL")
	mails = []
	for x in cursor:
		if session.get("email") == x[0]:
			thmail = {"uid": x[1], "sub":x[2]}
			mails.append(thmail)
	return render_template("Manage-Posts.html", mails = mails)

@app.route("/edit/<uid>", methods = ["GET", "POST"])
def Edit_post(uid):
	if not session.get("email"):
		return redirect('/')
	db = sql.connect('emails.db')
	cursor = db.execute("SELECT * FROM EMAIL WHERE UID = '"+str(uid)+"'")
	req = None
	for x in cursor:
		req = x
	thmail = {"tlist": req[4], 'sub': req[2] , 'body':req[5] , 'nums': req[3]}
	if request.method == "POST":
		vals = [None for i in range(4)]
		vals[0] = request.form.get("etlist")
		vals[1] = request.form.get("esub")
		vals[2] = request.form.get("ebody")
		vals[3] = request.form.get("enums")
		flag = 1
		for v in vals:
			if not v or v == "":
				flag = 0
				flash("invalid data", 'IBD')
				break
		if flag:
			db = sql.connect('emails.db')
			email = session.get('email')
			pwd = session.get('password')
			curr_mail = Email(email, uid, vals[1], vals[3], vals[0], vals[2])
			#print("INSERT INTO EMAIL VALUES('"+curr_mail.email+"','"+curr_mail.uid+"',"+curr_mail.sub+"',"+curr_mail.nums+",'"+curr_mail.tlist+"','"+curr_mail.body+"')")
			lst = curr_mail.tlist.split(',')
			spamy.Email_sender(email, lst, pwd, curr_mail.body, curr_mail.sub, int(curr_mail.nums))
			db.execute("DELETE FROM EMAIL WHERE UID = '"+str(uid)+"'")
			db.execute("INSERT INTO EMAIL VALUES('"+curr_mail.email+"','"+curr_mail.uid+"','"+curr_mail.sub+"',"+curr_mail.nums+",'"+curr_mail.tlist+"','"+curr_mail.body+"')")
			db.commit()
			return redirect('/manage')

	return render_template("Edit-Post.html", mail = thmail)

@app.route("/delete/<uid>")
def delete_post(uid):
	if not session.get("email"):
		return redirect('/')
	db = sql.connect('emails.db')
	print(str(uid))
	db.execute("DELETE FROM EMAIL WHERE UID = '"+str(uid)+"'")
	db.commit()
	return redirect('/manage')



@app.route("/logout")
def logout():
	if not session.get("email"):
		return redirect('/')
	session["email"] = None
	session["password"] = None
	return redirect('/')

@app.route("/random", methods = ["GET", "POST"])
def random_send():

	if request.method == "POST":
		vals = [None for i in range(4)]
		vals[0] = request.form.get("tlist")
		vals[1] = request.form.get("sub")
		vals[2] = request.form.get("body")
		vals[3] = request.form.get("nums")
		flag = 1
		for v in vals:
			if not v or v == "":
				flag = 0
				flash("invalid data", 'IBD')
				break
		if flag:
			email = "testuser7943@gmail.com"
			pwd = "thisisasafepassword"
			uid = str(uuid.uuid4().hex)
			curr_mail = Email(email, uid, vals[1], vals[3], vals[0], vals[2])
			#print("INSERT INTO EMAIL VALUES('"+curr_mail.email+"','"+curr_mail.uid+"',"+curr_mail.sub+"',"+curr_mail.nums+",'"+curr_mail.tlist+"','"+curr_mail.body+"')")
			print(email, pwd)
			lst = curr_mail.tlist.split(',')
			spamy.Email_sender(email, lst, pwd, curr_mail.body, curr_mail.sub, int(curr_mail.nums))
			return redirect('/manage')

	return render_template("create-mail.html")

if __name__ == "__main__":
	db = sql.connect('emails.db')
	conn = db.execute(''' CREATE TABLE IF NOT EXISTS EMAIL(
						   EMAIL TEXT NOT NULL,
						   UID TEXT PRIMARY KEY,
						   SUBJECT TEXT NOT NULL,
						   NUMS INT NOT NULL,
						   TARGETS TEXT NOT NULL,
						   BODY TEXT NOT NULL); ''')
	db.commit()
	app.run(debug = True)