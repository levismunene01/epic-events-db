from app import app
from models import db, Role, User, Event, UserEvent, Feedback, Ticket, EventOrganizer

with app.app_context():
    print("Deleting data...")
    Role.query.delete()
    User.query.delete()
    Event.query.delete()
    UserEvent.query.delete()
    Feedback.query.delete()
    Ticket.query.delete()
    EventOrganizer.query.delete()
    
    db.session.commit()

    print("Creating roles...")
    roles = [
        Role(name='Admin'),
        Role(name='User')
    ]

    db.session.add_all(roles)
    db.session.commit()

    print("Creating users...")
    users = [
        User(email='admin@example.com', username='admin', password_hash='password', role_id=1),
        User(email='user@example.com', username='user', password_hash='password', role_id=2)
    ]

    db.session.add_all(users)
    db.session.commit()

    print("Creating events...")
    events = [
        Event(image=b'event1_image', name='Event 1', date=datetime.date(2023, 3, 1), time=datetime.time(10, 0, 0), location=(40.7128, -74.0060), capacity=100, description='Event 1 description'),
        Event(image=b'event2_image', name='Event 2', date=datetime.date(2023, 3, 15), time=datetime.time(14, 0, 0), location=(34.0522, -118.2437), capacity=200, description='Event 2 description')
    ]

    db.session.add_all(events)
    db.session.commit()

    print("Creating user events...")
    user_events = [
        UserEvent(user_id=1, event_id=1, ticket_number=1),
        UserEvent(user_id=1, event_id=2, ticket_number=2)
    ]

    db.session.add_all(user_events)
    db.session.commit()

    print("Creating feedback...")
    feedbacks = [
        Feedback(user_id=1, event_id=1, feedback='Great event!', created_at=datetime.datetime(2023, 3, 2, 10, 0, 0)),
        Feedback(user_id=1, event_id=2, feedback='Awesome event!', created_at=datetime.datetime(2023, 3, 16, 14, 0, 0))
    ]

    db.session.add_all(feedbacks)
    db.session.commit()

    print("Creating tickets...")
    tickets = [
        Ticket(event_id=1, ticket_number=1, price=20.0),
        Ticket(event_id=2, ticket_number=2, price=30.0)
    ]

    db.session.add_all(tickets)
    db.session.commit()

    print("Creating event organizers...")
    event_organizers = [
        EventOrganizer(event_id=1, organizer_id=1),
        EventOrganizer(event_id=2, organizer_id=1)
    ]

    db.session.add_all(event_organizers)
    db.session.commit()

    print("Seeding complete!")