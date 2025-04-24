from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Lynn060386!@localhost/fitness_center_db'
db = SQLAlchemy(app)
ma=Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.Integer(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("name", "age")

class WorkoutSessionSchema(ma.Schema):
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    duration_minutes = fields.Integer(required=True, validate=validate.Range(min=1))
    calories_burned = fields.Integer(required=True, validate=validate.Range(min=1))

    class Meta:
        fields = ("member_id", "session_date", "duration_minutes", "calories_burned")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

workoutsession_schema = WorkoutSessionSchema()
workoutsessions_schema = WorkoutSessionSchema(many=True)

class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    workoutsessions = db.relationship('WorkoutSessions', backref='member')

class WorkoutSessions(db.Model):
    __tablename__ = 'WorkoutSessions'
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))
    session_date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)


@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Member(name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "Member added successfully"}), 201

@app.route('/workoutsessions', methods=['POST'])
def schedule_workout():
    try:
        workout_data = workoutsession_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_workout = WorkoutSessions(member_id=workout_data['member_id'], sesion_date=workout_data['session_date'], duration_minutes=workout_data['duration_minutes'], calories_burned=workout_data['calories_burned'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({"messages": "Workout scheduled successfully."}), 201

@app.route('/members', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member updated successfully"}), 200

@app.route('/workoutsessions', methods=['PUT'])
def update_workout(session_id):
    workout = WorkoutSessions.query.get_or_404(session_id)
    try:
        workout_data = workoutsession_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    workout.member_id = workout_data['member_id']
    workout.session_date = workout_data['session_date']
    workout.duration_minutes = workout_data['duration_minutes']
    workout.calories_burned = workout_data['calories_burned']

@app.route('/members', methods=['GET'])
def view_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route('/workoutsesssions', methods=['GET'])
def view_workouts():
    workouts = WorkoutSessions.query.all()
    return workoutsessions_schema.jsonify(workouts)

@app.route('/members', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member deleted successfully"}), 200

@app.route('/workoutsessions/<int:member_id>', methods=['GET'])
def workouts_by_member():
    member_id = request.args.get('member_id')
    workouts = WorkoutSessions.query.filter_by(member_id=member_id).all()
    if workouts:
        return workoutsessions_schema.jsonify(workouts)
    else:
        return jsonify({"message": "Member not found"}), 404



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
