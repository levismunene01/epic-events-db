from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Role, User, Event, UserEvent, Feedback, Ticket, EventOrganizer
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, origins='*')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Home(Resource):
    def get(self):
        response_dict = {
            "message": "Welcome to the Events RESTful API",
        }
        return make_response(response_dict, 200)

class Roles(Resource):
    def get(self):
        roles = Role.query.all()
        return [role.to_dict() for role in roles], 200

class Users(Resource):
    def get(self):
        users = User.query.all()
        return [user.to_dict() for user in users], 200

class Events(Resource):
    def get(self):
        events = Event.query.all()
        return [event.to_dict() for event in events], 200

class UserEvents(Resource):
    def get(self):
        user_events = UserEvent.query.all()
        return [user_event.to_dict() for user_event in user_events], 200

class Feedbacks(Resource):
    def get(self):
        feedbacks = Feedback.query.all()
        return [feedback.to_dict() for feedback in feedbacks], 200

class Tickets(Resource):
    def get(self):
        tickets = Ticket.query.all()
        return [ticket.to_dict() for ticket in tickets], 200

class EventOrganizers(Resource):
    def get(self):
        event_organizers = EventOrganizer.query.all()
        return [event_organizer.to_dict() for event_organizer in event_organizers], 200

api.add_resource(Home, '/')
api.add_resource(Roles, '/roles')
api.add_resource(Users, '/users')
api.add_resource(Events, '/events')
api.add_resource(UserEvents, '/user_events')
api.add_resource(Feedbacks, '/feedbacks')
api.add_resource(Tickets, '/tickets')
api.add_resource(EventOrganizers, '/event_organizers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)