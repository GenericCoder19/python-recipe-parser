import flask
from flask import render_template, request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

firstName = "tempFirst"
lastName = "tempLast"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def processForm():
    firstName = ''
    lastName = ''
    firstName = request.form['fname']
    lastName = request.form['lname']
    return render_template('index.html',fname = firstName, lname = lastName)

app.run()