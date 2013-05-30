#### FLASK IMPORTS #####
from flask import Flask, render_template, url_for, \
				  g, session, request, redirect

#### SQL IMPORTS  #####
from flaskext.mysql import MySQL

from jinja2 import Template, Environment, PackageLoader

import os
app = Flask(__name__)

#####################################################
################### Jinja2 setup ####################

env = Environment(loader=PackageLoader('app','templates'))
env.globals["site_name"] = "TwitPoll"
env.globals["logged_in"] = False
#####################################################

# get environment variables for database information

app.config['MYSQL_DATABASE_HOST'] 		= os.environ['MYSQL_DATABASE_HOST']
app.config['MYSQL_DATABASE_PORT'] 		= int(os.environ['MYSQL_DATABASE_PORT'])
app.config['MYSQL_DATABASE_USER'] 		= os.environ['MYSQL_DATABASE_USER']
app.config['MYSQL_DATABASE_PASSWORD'] 	= os.environ['MYSQL_DATABASE_PASSWORD']
app.config['MYSQL_DATABASE_DB'] 		= os.environ['MYSQL_DATABASE_DB']

# connect database to our app
mysql = MySQL()
mysql.init_app(app)

######################################################

@app.before_request
def before():
	g.db = mysql.connect()
	
@app.teardown_request
def after(ex):
	if ex: print ex
	g.db.close()

######################################################
#################### QUERIES #########################
######################################################



def get_users():
	q = "select * from User limit 10;"
	cursor = g.db.cursor()
	num_results = cursor.execute(q)
	print "result = ", num_results
	data = [dict((cursor.description[idx][0], value) for idx, value in enumerate(row)) for row in cursor.fetchall()]
   	return data

env.globals.update(get_all_users= get_users)


# def render_template(source, vars = {}):
# 	template = env.get_template(source)
# 	return template.render(vars)


######################################################

def set_active(page):
	env.globals.update(navclass = {page: 'active'})

@app.route("/")
def hello():
	set_active("home")
	template = env.get_template("home.html")
	return template.render()

@app.route("/users", methods=["GET", "POST"])
def show_users():
	if request.method == "GET":
		set_active("users")
		return env.get_template("users.html").render()
	else: # make a new user account
		print request.args
		return redirect(url_for('signup'))

@app.route("/signup")
def signup():
	set_active("signup")
	return env.get_template("signup.html").render()

if __name__ == "__main__":
	debug = bool(os.environ.get("DEBUG", False))
	port = int(os.environ.get("PORT", 5000))
	app.run(debug=debug, port=port, host='0.0.0.0')