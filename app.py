from flask import Flask
from flask import render_template, redirect, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/generazione")
def generate():
    return render_template('generazione.html')
