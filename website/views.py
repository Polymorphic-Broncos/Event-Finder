from flask import Blueprint, render_template, request, flash, jsonify, session
from flask_login import login_required, current_user
from flask import render_template_string
from .models import Event
from . import db
import json
import datetime
import uuid

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
            #search = datetime.date(search)
            events = db.session.query(Event).filter(Event.dateTime == search).all() # Date and time incomplete!

        elif filter == "Time":
            events = db.session.query(Event).filter(Event.dateTime == search).all() # Date and time incomplete!

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
    if request.method == 'POST': 
        pass
    
    return render_template("my_events.html", user=current_user)

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
    #print(f"Event ID: {eventID}")
    event = Event.query.get(eventID)

    # NEED TO IMPLEMENT BOOKMARKING
    if request.method == 'POST': 
        print(f"Event: {event.name} bookmarked!")

    
    return render_template("view-event.html", user=current_user, viewedEvent=event)

@views.route('/bookmarked-events', methods=['GET', 'POST'])
@login_required
def bookmarkedEvents():
    if request.method == 'POST': 
        pass
    
    return render_template("bookmarked_events.html", user=current_user)

'''
@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
'''
