# Event Management System
Coursework for UFCFES-30-1 Web Development and Databases - WORK IN PROGRESS
## Project description
Bristol Community Events (BCE) is a fictional organisation that would like to promote tourism in Bristol. BCE is looking for an event management system that can give a unified view of all events happening in the city, such as exhibitions, workshops, sports events, etc. BCE requires a website that can facilitate the creation of events, ticket booking, payment processing, invoice generation, and the ability to manage attendees.
## Criteria set out by Bristol Community Events
### End-user perspective
TBD
### Administrator perspective
TBD
### Organiser perspective
### Database constraints
TBD
### Additional requirements
TBD
## Tech Stack
### Frontend
The frontend uses vanilla HTML, CSS and JavaScript.
### Backend
The backend is a Python Flask web application, which handles business logic and transactions to the MySQL database.
## Deployment
### Prerequisistes
Please ensure you have the following installed on your system:
1. Python 3 (version >= 3.12.3)
2. MySQL (version >= 8.4)
3. MySQL Workbench (version >= 8.0)
### Build instructions
1. Clone the project and change directories using the following commands
~~~sh
git clone https://github.com/0x4bubakar/Event-Management-System.git
cd Event-Management-System/
~~~

2. Create and activate the Python virtual environment
On Windows:
~~~sh
python3 -m venv venv
venv\Scripts\activate 
~~~
On Mac OS/Linux:
~~~sh
python3 -m venv venv
source venv/bin/activate
~~~

3. Install all pip modules:
~~~sh
pip install -r requirements.txt
~~~

4. Create the database
This can be done several ways. MySQL Workbench is one, but I have had issues running it on Ubuntu. Thus I would recommend using the following command on Linux or Unix-like systems:
~~~sh
mysql -u {name of user} -p < init_db.sql
~~~

5. Create a .env file with values for the following environment variables:
- DB_HOST (the IP address of your database, usually 127.0.0.1 if localhost)
- DB_USERNAME
- DB_PASSWORD
- DB_NAME (in the case of init_db.sql, it is mydb)
- SECRET_KEY

6. Start the Flask server with `flask run`.

7. In order to create an admin user, first create a user account at `/login`, and then update the user's role to `admin` with the MySQL CLI or Workbench using the following command:
~~~sql
UPDATE user
SET role = 'admin'
WHERE user_id = {admin account user_id};
~~~