from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("index.html")