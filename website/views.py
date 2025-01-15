from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
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

        # TEMP
        events = Event.query.all()
        for event in events:
            print(event)

    return render_template("home.html", user=current_user)

@views.route('/create-event', methods=['GET', 'POST'])
@login_required
def createEvent():
    if request.method == 'POST': 

        eventName = request.form.get("eventName")
        eventDate = request.form.get("eventDate")
        eventTime = request.form.get("eventTime")
        eventLocation = request.form.get("eventLocation")
        eventCategory = request.form.get("eventCategory")

        dateTimeObj = datetime.datetime.strptime(eventDate + " " + eventTime, "%Y-%m-%d %H:%M")

        print(f"Create event with: {eventName}, {dateTimeObj}, {eventLocation}, {eventCategory}")

        newEvent = Event(name=eventName, dateTime=dateTimeObj, location=eventLocation, category=eventCategory, userID=current_user.id)
        db.session.add(newEvent)
        db.session.commit()
        flash('Event Created!', category='success')

        return render_template("my_events.html", user=current_user)
    
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
