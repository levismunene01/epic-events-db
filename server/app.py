from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, User, Event, UserEvent, Feedback, Ticket, EventOrganizer
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os
import sys
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app)

# Utility functions for validation and error handling
def validate_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

def handle_db_commit(session):
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return str(e), 500

# Resources
class Home(Resource):
    def get(self):
        response_dict = {
            "message": "Welcome to the Events RESTful API",
        }
        return make_response(response_dict, 200)

class Users(Resource):
    def get(self):
        users = User.query.all()
        return [user.to_dict() for user in users], 200

    def post(self):
        data = request.json
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not username or not email or not password:
            return {'error': 'Missing required fields'}, 400

        if not validate_email(email):
            return {'error': 'Invalid email format'}, 400

        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to create user: ' + error[0]}, error[1]
        return user.to_dict(), 201

class Events(Resource):
    def get(self):
        events = Event.query.all()
        return [event.to_dict() for event in events], 200

    def post(self):
        data = request.json
        if not all([data.get('name'), data.get('image'), data.get('location'), data.get('description'), data.get('capacity')]):
            return {'error': 'Missing required fields'}, 400

        event = Event(
            image=data['image'],
            name=data['name'],
            datetime=data.get('datetime'),
            location=data['location'],
            capacity=data['capacity'],
            description=data['description']
        )
        db.session.add(event)
        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to create event: ' + error[0]}, error[1]
        return event.to_dict(), 201

    def patch(self):
        data = request.json
        id = data.get('id')
        if id is None:
            return {'error': 'Missing event ID'}, 400

        event = Event.query.get(id)
        if event is None:
            return {'error': 'Event not found'}, 404

        if 'name' in data:
            event.name = data['name']
        if 'image' in data:
            event.image = data['image']
        if 'datetime' in data:
            event.datetime = data['datetime']
        if 'location' in data:
            event.location = data['location']
        if 'description' in data:
            event.description = data['description']
        if 'capacity' in data:
            event.capacity = data['capacity']

        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to update event: ' + error[0]}, error[1]
        return event.to_dict(), 200
    
    def delete(self):
        data = request.json
        id = data.get('id')
        if id is None:
            return {'error': 'Missing event ID'}, 400

        event = Event.query.get(id)
        if event is None:
            return {'error': 'Event not found'}, 404

        db.session.delete(event)
        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to delete event: ' + error[0]}, error[1]
        return {'message': 'Event deleted successfully'}, 200

class UserEvents(Resource):
    def get(self):
        user_events = UserEvent.query.all()
        return [user_event.to_dict() for user_event in user_events], 200

class Feedbacks(Resource):
    def get(self):
        feedbacks = Feedback.query.all()
        return [feedback.to_dict() for feedback in feedbacks], 200

    def post(self):
        data = request.json
        if 'event_id' not in data or 'feedback' not in data or 'user_id' not in data:
            return {'error': 'Missing required fields'}, 400
        feedback = Feedback(feedback=data['feedback'], event_id=data['event_id'], user_id=data['user_id'])
        db.session.add(feedback)
        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to create feedback: ' + error[0]}, error[1]
        return feedback.to_dict(), 201

class Tickets(Resource):
    def get(self):
        tickets = Ticket.query.all()
        return [ticket.to_dict() for ticket in tickets], 200

    def post(self):
        data = request.json
        if 'price' not in data or 'event_id' not in data:
            return {'error': 'Missing required fields'}, 400
        ticket = Ticket(price=data['price'], ticket_number=data['ticket_number'], event_id=data['event_id'])
        db.session.add(ticket)
        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to create ticket: ' + error[0]}, error[1]
        return ticket.to_dict(), 201

class EventOrganizers(Resource):
    def get(self):
        event_organizers = EventOrganizer.query.all()
        return [event_organizer.to_dict() for event_organizer in event_organizers], 200

api.add_resource(Home, '/')
api.add_resource(Users, '/users')
api.add_resource(Events, '/events')
api.add_resource(UserEvents, '/user_events')
api.add_resource(Feedbacks, '/feedbacks')
api.add_resource(Tickets, '/tickets')
api.add_resource(EventOrganizers, '/event_organizers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
