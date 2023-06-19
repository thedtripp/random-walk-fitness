from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
from flask import render_template, request, redirect, url_for
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Define your database model here
class ExerciseEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    repetitions = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Exercise {self.name}>"
    
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    min_repetitions = db.Column(db.Integer, nullable=False)
    max_repetitions = db.Column(db.Integer, nullable=False)
    min_weight = db.Column(db.Float, nullable=False)
    max_weight = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Exercise {self.name}>"

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/insert/<name>/<repetitions>/<weight>')
def insert_exercise(name, repetitions, weight):
    exercise = ExerciseEntry(name=name, repetitions=repetitions, weight=weight)
    db.session.add(exercise)
    db.session.commit()
    return f"Exercise '{exercise.name}' inserted into the database."

@app.route('/my-exercises')
def get_my_exercises():
    exercises = ExerciseEntry.query.all()
    return render_template('my-exercises.html', exercises=exercises)

@app.route('/exercises')
def get_exercises():
    all_exercises = Exercise.query.all()
    return render_template('exercises.html', exercises=all_exercises)

# Route for displaying a random exercise and interaction options
@app.route('/random', methods=['GET', 'POST'])
def random_exercise():
    # Get a random exercise from the database
    random_exercise = Exercise.query.order_by(func.random()).first()

    if request.method == 'POST':
        # Handle form submission
        if 'done' in request.form:
            # Mark the exercise as done and save to the database
            exercise_entry = ExerciseEntry(
                name=random_exercise.name,
                repetitions=0,
                weight=0,
                timestamp=datetime.utcnow()
            )
            db.session.add(exercise_entry)
            db.session.commit()
            return redirect(url_for('random_exercise'))
        elif 'skip' in request.form:
            # Generate a different random exercise
            return redirect(url_for('random_exercise'))
        elif 'attempt' in request.form:
            # Display the form to enter the number of repetitions completed
            return render_template('attempt_form.html', exercise=random_exercise)

    # Generate random weight as a multiple of 2.5 within the range
    weight_range = range(int(random_exercise.min_weight * 2), int(random_exercise.max_weight * 2) + 1)
    random_weight = round(random.choice(weight_range) / 2, 2)

    random_reps = random.randint(random_exercise.min_repetitions, random_exercise.max_repetitions)

    return render_template('random_exercise.html', exercise=random_exercise, weight=random_weight, repetitions=random_reps)

@app.route('/done', methods=['GET', 'POST'])
def done():
    if request.method == 'POST':
        exercise_name = request.form['exercise_name']
        repetitions = request.form['repetitions']
        weight = request.form['weight']
        
        exercise_entry = ExerciseEntry(name=exercise_name, repetitions=repetitions, weight=weight)
        db.session.add(exercise_entry)
        db.session.commit()

        return redirect(url_for('done'))  # Replace 'index' with the appropriate endpoint for redirection
    else:
        return render_template('done.html')


@app.route('/skip')
def skip():
    return redirect(url_for('random_exercise'))

@app.route('/attempt', methods=['GET', 'POST'])
def attempt():
    if request.method == 'POST':
        # Process the form data
        exercise_name = request.form['exercise_name']
        repetitions = request.form['repetitions']
        weight = request.form['weight']

        exercise_entry = ExerciseEntry(
            name=exercise_name,
            repetitions=repetitions,
            weight=weight,
            timestamp=datetime.utcnow()
        )

        db.session.add(exercise_entry)
        db.session.commit()

        return redirect(url_for('attempt'))
    else:
        return render_template('attempt.html')


if __name__ == '__main__':
    app.run(debug=True)




