from flask import Blueprint,flash,render_template, request, redirect,url_for, jsonify
from flask_login import login_required,current_user
from .models import Note
from . import db
import json
views_bp=Blueprint('views',__name__, static_folder="static", template_folder="templates")      # view object to blueprint

@views_bp.route('/', methods=['GET','POST'])
@login_required  # you cannot get to the homepage unless succesfully loggedin
def home():
    if request.method=="POST":
        note=request.form.get("note")
        #check length of note to be posted
        if len(note)< 1:
            flash('Note is too short',category='error')
        else:
            #Add new note to dtabase
            new_note=Note(message=note, user_id=current_user.id) 
            db.session.add(new_note)
            db.session.commit()
            flash('Note added',category='successful')
            # afterwards we return to the same page
    
    return render_template("home.html",user=current_user) # current_user holds all info about the currently loggedin user 



@views_bp.route('/delete-note', methods=['POST'])
def delete_note():
    note=json.loads(request.data)  # retrieve json dictionary of the message to be deleted (the 'POST' javascript message )
    noteId=note["noteId"]
    note=Note.query.get(noteId)
    if note:   
        # here we make sure only the notes that belongs to the user can be deleted
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    
    return jsonify({})  #return nothing
    
        
    
                                         
