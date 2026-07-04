# Event Management System
Coursework for UFCFES-30-1 Web Development and Databases - WORK IN PROGRESS
## Project description
Bristol Community Events (BCE) is a fictional organisation that would like to promote tourism in Bristol. BCE is looking for an event management system that can give a unified view of all events happening in the city, such as exhibitions, workshops, sports events, etc. BCE requires a website that can facilitate the creation of events, ticket booking, payment processing, invoice generation, and the ability to manage attendees.
## Criteria set out by Bristol Community Events
Note: the following requirements have been taken from the assessment briefs offered by the module leaders. Subtle adjustments have been made for the sake of clarity.
### End-user perspective
- [x] End user features include Register/Login/Logout/password update; create, view, update and cancel booking.
- [x] System should allow end users to sign up and login to book an event and view all past and future bookings.
- [x] Users should be able to filter events based on specific categories e.g., exhibitions, workshops, sports events, etc. 
- [x] The search criteria could be single date, dates range/months, event category, free events, etc.
- [x] Users should be able to view the details of the selected event(s). These details will include event name, date(s), ticket price (which can be zero for some events), event venue, any conditions (e.g., formal dress), remaining tickets left, deadline to book tickets by.
- [ ] Continue with booking by singing up/login and generating and downloading booking receipt OR repeat the first step.
- [] Bookings can be made up to 2 months before the deadline. Advance booking discounts are allocated as follows:

|Number of days booked before the deadline|Discount|
|---|---|
|Greater than 60 days|No discount|
|Between 50 and 60 days|20%|
|Between 35 and 50 days|15%|
|Between 25 and 35 days|10%|
|Between 15 and 25 days|5%|
|Less than 15 days|No discount|

- [x] Some events can run on multiple days, and each day incurs part of the cost. For instance, Bristol Balloon fiesta may run for a week. If the total price for a week is £70, then each day costs £10 for attendees. Therefore, the price per day can be calculated by the total price divided by the number of days.

- [x] If all tickets have been booked for an event, then the user is automatically placed on a waiting list alongside a timestamp. If x more spaces become available (i.e. someone cancels their booking or if more spaces are added) - then the first x people who are on the waiting list are booked.

- [ ] A user can choose to cancel a booking prior to the deadline - but note that they may be subjected to the following charges:

|Days before deadline|Cancellation charge|
|---|---|
|Over 40 days|No charge - user receives a full refund|
|Between 25 and 39 days|Up to 40% of the booking price|
|Under 25 days|100% of the booking price|

- [x] 10% student discount if the account is created with a .ac.uk email.

### Administrator perspective
- [x] Admins should be able to login/logout and update password for admin as well as other users on the system
- [] Admins should be able to to add/update/remove/edit details of events, price constraints, number of available tickets, venues, as well as end user details
- [ ] Admins should be able to check the status of specific bookings and specific events (such as whether the event is fully booked or not, amount of people currently waitlisted).
- [ ] Admins should be able to generate admin reports - e.g. profit earned in an event, number of bookings for a specific event, number of successful events in a specific year, number of tickets available for a specific event, upcoming events on a specific venue, etc.
- [ ] The number of tickets per event is contingent on the capacity of the venue. For instance, if venue A has a maximum capacity of x, an event can have y tickets - where y <= x.
- [ ] If less than 50% of bookings are made within 10 days of an event, admin should be able to lower the ticket price by at least 25%.

### Event Organiser perspective
- [ ] An event organiser should be able to register/Login/Logout/password update.
- [ ] An event organiser should be able to create/update/cancel event on BCE website; set price constraints, discounts, number of available tickets, venue, dates, etc.
- [ ] There is a fixed fee of £100 for hosting an event via the BCE website. After the event has been created the event organiser should be prompted to pay the fee before publishing.
- [ ] Event is saved as a "draft" that can be edited until the organiser chooses to publish the event.

### Database Design
Entity Relationship Diagram to be uploaded soon!

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