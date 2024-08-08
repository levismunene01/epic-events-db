from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from .models import db, User, Event, UserEvent, Feedback, Ticket, EventOrganizer
from flask_cors import CORS
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


app = Flask(__name__)
os.environ['DATABASE_URL'] = 'postgresql://epic_events_z6wl_user:CndecxpLEos242Bi80iODMgrvMSoymqC@dpg-cqplpv5svqrc73fu470g-a.oregon-postgres.render.com/epic_events_z6wl'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

cors = CORS(app, origins='*')

api = Api(app)

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
        if 'username' not in data or 'email' not in data:
            return {'error': 'Missing required fields'}, 400
        user = User(username=data['username'], email=data['email'],password_hash=data['password_hash'])
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201

class Events(Resource):
    def get(self):
        events = Event.query.all()
        return [event.to_dict() for event in events], 200

    def post(self):
        data = request.json
        if 'capacity' not in data or 'name' not in data or 'image' not in data or 'location' not in data or 'description' not in data:
            return {'error': 'Missing required fields'}, 400
        event = Event(image=data['image'],name=data['name'], datetime=data['datetime'], location=data['location'], capacity=data['capacity'], description=data['description'])
        db.session.add(event)
        db.session.commit()
        return event.to_dict(), 201

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
        db.session.commit()
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
        db.session.commit()
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