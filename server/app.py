import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource
from models import db, User, Event, UserEvent, Ticket
import re

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Set JWT secret key

# Initialize CORS
CORS(app)

# Initialize JWT Manager
jwt = JWTManager(app)

# Initialize database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-RESTful API
api = Api(app)

# Configure logging
if not app.debug:
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

# Middleware to handle current user
@app.before_request
def get_current_user():
    token = request.headers.get('Authorization')
    if token:
        token = token.replace('Bearer ', '')
        try:
            request.user = get_jwt_identity()  # Get current user from JWT
        except Exception:
            request.user = None
    else:
        request.user = None

# Helper function for database commit
def handle_db_commit(session):
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return str(e), 500
    return None

# Email validation function
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# Resources
class Home(Resource):
    def get(self):
        return {'message': "Welcome to the Events RESTful API"}, 200

class Users(Resource):
    def get(self):
        data = request.json
        email = data.get('email').lower()
        password = data.get('password')

        if not email or not password:
            return {'error': 'Missing email or password'}, 400

        if not validate_email(email):
            return {'error': 'Invalid email format'}, 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return {'error': 'Invalid email or password'}, 401

        return user.to_dict(), 200

    def post(self):
        data = request.json
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not username or not email or not password:
            return {'error': 'Missing required fields'}, 400

        if not validate_email(email):
            return {'error': 'Invalid email format'}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'error': 'User already exists with this email'}, 409

        is_admin = email.endswith('@admin.com')
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash, is_admin=is_admin)
        
        db.session.add(user)
        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to create user: ' + error[0]}, error[1]

        return user.to_dict(), 201

class Login(Resource):
    def post(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity={'id': user.id, 'username': user.username})
            return {'access_token': access_token, 'message': f'Welcome back {user.username}!'}, 200
        else:
            return {'message': 'Invalid email or password!'}, 401

class Events(Resource):
    def get(self):
        events = Event.query.all()
        return [event.to_dict() for event in events], 200

    @jwt_required()
    def post(self):
        if not request.user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        data = request.json
        if not all([data.get('name'), data.get('image'), data.get('location'), data.get('description'), data.get('capacity'), data.get('number_of_tickets')]):
            return {'error': 'Missing required fields'}, 400

        event = Event(
            image=data['image'],
            name=data['name'],
            datetime=data.get('datetime'),
            location=data['location'],
            capacity=data['capacity'],
            description=data['description'],
            number_of_tickets=data['number_of_tickets']
        )
        db.session.add(event)
        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to create event: ' + error[0]}, error[1]
        return event.to_dict(), 201

    @jwt_required()
    def patch(self):
        if not request.user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

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
        if 'number_of_tickets' in data:
            event.number_of_tickets = data['number_of_tickets']

        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to update event: ' + error[0]}, error[1]
        return event.to_dict(), 200
    
    @jwt_required()
    def delete(self):
        if not request.user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

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

    def get_user_events(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        user_events = UserEvent.query.filter_by(user_id=user_id).all()
        events = [user_event.event.to_dict() for user_event in user_events]
        return events, 200

class Tickets(Resource):
    def get(self):
        tickets = Ticket.query.all()
        return [ticket.to_dict() for ticket in tickets], 200

    @jwt_required()
    def post(self):
        if not request.user:
            return {'error': 'User not authenticated'}, 401

        data = request.json
        event_id = data.get('event_id')
        phone_number = data.get('phone_number')

        if not event_id or not phone_number:
            return {'error': 'Missing event_id or phone_number'}, 400

        event = Event.query.get(event_id)
        if not event:
            return {'error': 'Event not found'}, 404

        if event.capacity <= 0 or event.number_of_tickets <= 0:
            return {'error': 'No tickets available'}, 400

        ticket = Ticket(
            user_id=request.user['id'],
            event_id=event_id,
            phone_number=phone_number
        )

        event.number_of_tickets -= 1
        error = handle_db_commit(db.session)
        if error:
            return {'error': 'Failed to purchase ticket: ' + error[0]}, error[1]

        return {'message': 'Ticket purchased successfully'}, 200

# Register resources with the API
api.add_resource(Home, '/')
api.add_resource(Users, '/users')
api.add_resource(Login, '/login')
api.add_resource(Events, '/events')
api.add_resource(UserEvents, '/user_events')
api.add_resource(Tickets, '/tickets')

if __name__ == '__main__':
    app.run(debug=True)
