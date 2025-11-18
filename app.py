from flask import Flask, redirect, render_template, url_for

from flask import render_template

EVENTS = {
    1: {
        "title": "Bristol City vs Bristol Rovers",
        "image": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Ashton_Gate_-_Lansdown_Stand.jpg",
        "date": "18/12/2025",
        "price": "£20-£79",
        "venue": "Ashton Gate Stadium",
        "conditions": "Sportswear allowed",
        "tickets_left": 325,
        "deadline": "30/08/2026",
        "description": "Experience the intense Bristol derby live at Ashton Gate. Two days of football excitement with fan activities, food stalls, and live music."
    },

    2: {
        "title": "BSides Bristol 2026",
        "image": "https://static.wixstatic.com/media/baa13f_ca703cdeae914522bae2e03f190c8857~mv2.png/v1/fit/w_2500,h_1330,al_c/baa13f_ca703cdeae914522bae2e03f190c8857~mv2.png",
        "date": "01/09/2026 - 02/09/2026",
        "price": "£5.50-£11.65",
        "venue": "Bristol Business School",
        "conditions": "Bring student ID if applicable",
        "tickets_left": 80,
        "deadline": "15/12/2025",
        "description": "A cyber security conference featuring workshops, talks, and networking with professionals in the field."
    },

    3: {
        "title": "Bristol Film Festival",
        "image": "https://images.squarespace-cdn.com/content/v1/5f1811b47a7edc2eea4892b4/e8f62d07-b77e-4a0e-8071-65de4e22a1d0/Black+Logo+Plain+Large.png",
        "date": "October - December 2025",
        "price": "£11-£16",
        "venue": "The Planetarium, We The Curious",
        "conditions": "No food inside the planetarium",
        "tickets_left": 120,
        "deadline": "30/09/2025",
        "description": "A multi-month celebration of film, featuring screenings of classics, indie films, and special planetarium experiences."
    },

    4: {
        "title": "Bristol Balloon Fiesta 2026",
        "image": "https://upload.wikimedia.org/wikipedia/commons/e/ee/Bristol_International_Balloon_Fiesta_August_14_2004.JPG",
        "date": "07/08/2026",
        "price": "Free",
        "venue": "Ashton Court",
        "conditions": None,
        "tickets_left": "Unlimited",
        "deadline": "N/A",
        "description": "Europe’s largest annual hot air balloon event. Enjoy morning ascents, evening night glows, live entertainment, and markets."
    }
}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.route("/events/<int:event_id>")
def event_details(event_id):
    event = EVENTS.get(event_id)
    if not event:
        return "Event not found", 404
    return render_template("event-details.html", event=event)

@app.route("/category/<name>")
def category(name):
    return f"Category page for {name}"

if __name__ == "__main__":
    app.run(debug=True)