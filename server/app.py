#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''


@app.get('/campers')
def get_campers():
    all_campers = Camper.query.all()
    return [ camper.to_dict( rules=("-signups",) ) for camper in all_campers ], 200


@app.get('/campers/<int:id>')
def get_camper_by_id(id):
    found_camper = Camper.query.where(Camper.id == id).first()
    if found_camper:
        return found_camper.to_dict(), 200
    else:
        return { "error": "Camper not found" }, 404


@app.post('/campers')
def post_camper():
    data = request.json

    try:
        new_camper = Camper( name=data.get('name'), age=data.get('age') )
        db.session.add(new_camper)
        db.session.commit()
        return new_camper.to_dict(rules=["-signups"]), 201

    except ValueError as error:
        return { "error": f"{error}" }, 406

    except:
        return { "error": "Invalid data" }, 406
    

@app.patch('/campers/<int:id>')
def update_camper(id):
    data = request.json
    found_camper = Camper.query.where(Camper.id == id).first()

    if found_camper:
        try:
            for key in data:
                setattr(found_camper, key, data[key])
            db.session.commit()

            return found_camper.to_dict(rules=["-signups"]), 202

        except ValueError as error:
            return { "error": f"{error}"}, 406
        
        except:
            return { "error": "Invalid camper" }, 406

    else:
        return { "error": "Camper not found" }, 404 
    

@app.get('/activities')
def get_activities():
    all_activities = Activity.query.all()
    return [ activity.to_dict( rules=("-signups",) ) for activity in all_activities ], 200


# BONUS DELETE!!!! #
@app.delete('/activities')
def delete_all_activities():
    Activity.query.delete()
    db.session.commit()
    return {}, 204    
# BONUS DELETE!!!! #


@app.delete('/activities/<int:id>')
def delete_activity(id):
    found_activity = Activity.query.where(Activity.id == id).first()

    if found_activity:
        db.session.delete(found_activity)
        db.session.commit()

        return {}, 204
    
    else:
        return { "error": "Activity not found" }, 404


@app.post('/signups')
def add_signups():
    data = request.json


    try:
        new_signup = Signup(
            time=data.get('time'), 
            activity_id=data.get('activity_id'), 
            camper_id=data.get('camper_id')
        )
        db.session.add(new_signup)
        db.session.commit()
        return new_signup.to_dict(), 201

    except ValueError as error:
        return { "error": f"{error}" }, 406
    
    except:
        return { "error": "Invalid data" }, 406


if __name__ == '__main__':
    app.run(port=5555, debug=True)