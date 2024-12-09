from flask import Flask, flash, jsonify, redirect, render_template, request, session
from datetime import datetime

# Configure application
app = Flask(__name__)



@app.route('/')
def homepage():
    return render_template("index.html", year=datetime.now().year)

@app.route('/register')
def register():
    return render_template("login.html")

@app.route('/login')
def login():
    return render_template("login.html")