from flask import Flask, redirect, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    return render_template('login.html')

@app.route('/events', methods=['POST'])
def events():
    return render_template('events.html')

if __name__ == "__main__":
    app.run(debug=True)