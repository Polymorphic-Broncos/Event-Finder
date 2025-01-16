from flask import Blueprint, render_template, request, flash, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from flask import render_template_string
from .models import Event, User, bookmarks
from . import db
import json
import datetime
import uuid
from sqlalchemy import func, cast, Date, Time

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':

        filter = request.form.get("filter")
        search = request.form.get("search")
        print(f"User searched: {filter}: {search}")

        events = []

        if filter == "Name":
            events = db.session.query(Event).filter(Event.name == search).all()

        elif filter == "Date":
            try:
                # Convert the search string to a date object
                search_date = datetime.datetime.strptime(search, "%Y-%m-%d").date()
                # Query events for the specific date
                events = db.session.query(Event).filter(
                    func.date(Event.dateTime) == search_date
                ).all()
            except ValueError:
                flash('Please enter date in YYYY-MM-DD format', category='error')
                events = []

        elif filter == "Time":
            try:
                # Convert the search string to a time object with seconds
                search_time = datetime.datetime.strptime(search, "%H:%M:%S").time()
                
                # Extract hour and minute for comparison
                events = db.session.query(Event).filter(
                    func.extract('hour', Event.dateTime) == search_time.hour,
                    func.extract('minute', Event.dateTime) == search_time.minute
                ).all()
            except ValueError:
                flash('Please enter time in HH:MM:SS format (24-hour)', category='error')
                events = []

        elif filter == "Location":
            events = db.session.query(Event).filter(Event.location == search).all()

        elif filter == "Category":
            events = db.session.query(Event).filter(Event.category == search).all()

        else:
            print("Error")

        print(events)
        if len(events) == 0:
            flash('No results found', category='error')
        else:
            flash(f"{len(events)} results found", category='success')
            return render_template("search_results.html", user=current_user, resultList=events)


    # Recommended
    recommendedList = Event.query.all()

    return render_template("home.html", user=current_user, eventList=recommendedList)

@views.route('/create-event', methods=['GET', 'POST'])
@login_required
def createEvent():
    if request.method == 'POST': 

        eventName = request.form.get("eventName")
        eventDate = request.form.get("eventDate")
        eventTime = request.form.get("eventTime")
        eventLocation = request.form.get("eventLocation")
        eventCategory = request.form.get("eventCategory")

        if eventName and eventDate and eventTime and eventLocation and eventCategory:

            dateTimeObj = datetime.datetime.strptime(eventDate + " " + eventTime, "%Y-%m-%d %H:%M")

            print(f"Create event with: {eventName}, {dateTimeObj}, {eventLocation}, {eventCategory}")

            newEvent = Event(name=eventName, dateTime=dateTimeObj, location=eventLocation, category=eventCategory, userID=current_user.id)
            db.session.add(newEvent)
            db.session.commit()
            flash('Event Created!', category='success')

            return render_template("my_events.html", user=current_user)
        
        else:
            flash('Please fill out all the fields', category='error')

    return render_template("create_event.html", user=current_user)

@views.route('/my-events', methods=['GET', 'POST'])
@login_required
def myEvents():
    # Show only events created by the user
    created_events = Event.query.filter_by(userID=current_user.id).all()
    return render_template("my_events.html", user=current_user, eventList=created_events)

@views.route('/delete-event', methods=['POST'])
@login_required
def delete_event():  
    eventDict = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    eventId = uuid.UUID(eventDict['eventId'])
    #print(f"Event ID: {eventId}")
    #print(f"Event ID type: {type(eventId)}")
    event = Event.query.get(eventId)
    if event:
        if event.userID == current_user.id:
            db.session.delete(event)
            db.session.commit()
    else:
        print("Event not found!")

    return jsonify({})

@views.route('/send-event', methods=['POST'])
@login_required
def send_event():  
    eventDict = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    eventIDString = eventDict['eventId']
    #print(f"Event ID String: {eventIDString}")
    session["eventID"] = eventIDString

    return jsonify({})

@views.route('/view-event', methods=['GET', 'POST'])
@login_required
def viewEvent():
    eventID = uuid.UUID(session['eventID'])
    event = Event.query.get(eventID)

    if request.method == 'POST': 
        # Check if event is already bookmarked
        user = User.query.get(current_user.id)
        if event not in user.bookmarkedEvents:
            user.bookmarkedEvents.append(event)
            db.session.commit()
            flash('Event bookmarked successfully!', category='success')
            print(f"Event: {event.name} bookmarked!")
        else:
            flash('Event already bookmarked!', category='error')
    
    return render_template("view-event.html", user=current_user, viewedEvent=event)

@views.route('/bookmarked-events', methods=['GET', 'POST'])
@login_required
def bookmarkedEvents():
    # Show only bookmarked events
    bookmarked = current_user.bookmarkedEvents
    return render_template("bookmarked_events.html", user=current_user, bookmarkedList=bookmarked)

@views.route('/remove-bookmark', methods=['POST'])
@login_required
def remove_bookmark():
    eventDict = json.loads(request.data)
    eventId = uuid.UUID(eventDict['eventId'])
    event = Event.query.get(eventId)
    user = User.query.get(current_user.id)
    
    if event and event in user.bookmarkedEvents:
        user.bookmarkedEvents.remove(event)
        db.session.commit()
        flash('Event removed from bookmarks!', category='success')
    
    return jsonify({})

@views.route('/cleanup', methods=['GET'])
def cleanup():
    # Delete all events first (due to foreign key constraints)
    Event.query.delete()
    # Delete the bookmarks table entries
    db.session.execute(bookmarks.delete())
    # Delete all users
    User.query.delete()
    # Commit the changes
    db.session.commit()
    flash('Database cleaned!', category='success')
    return redirect(url_for('auth.login'))
