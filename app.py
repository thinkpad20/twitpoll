#### FLASK IMPORTS #####
from flask import Flask, render_template, url_for, g, session

#### SQL IMPORTS  #####
from flaskext.mysql import MySQL
import os
app = Flask(__name__)


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



def show_users():
	q = "select * from User limit 10;"
	cursor = g.db.cursor()
	num_results = cursor.execute(q)
	print "result = ", num_results
	data = [dict((cursor.description[idx][0], value) for idx, value in enumerate(row)) for row in cursor.fetchall()]
	print data
   	return data





######################################################


@app.route("/")
def hello():
	show_users()
	ret = render_template("home.html")
	return ret

if __name__ == "__main__":
	app.run(debug=True)