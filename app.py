import requests
from flask import Flask, redirect, url_for ,render_template ,request  , jsonify,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)   # Flask constructor 

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flaskdbv1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    physics = db.Column(db.Integer, unique=False, nullable=False)
    chemistry = db.Column(db.Integer, unique=False, nullable=False)
    mathamatics = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return f'<Students {self.student_name}>'
  
# A decorator used to tell the application 
# which URL is associated function 
@app.route('/')       
def index(): 
    return render_template('index.html') 

@app.route('/students-api', methods=['GET'])
def get_students_from_api():
    try:
        # Make a GET request to the API
        response = requests.get('https://api.websl.lk/api/student')
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        students = response.json()
        
        # Render a template or return the data as JSON
        return render_template('students-api.html', students=students)
        # Alternatively, return JSON response
        # return jsonify(students)
        
    except requests.exceptions.RequestException as e:
        # Handle errors (e.g., network issues, invalid responses)
        return f"An error occurred: {e}"

@app.route('/add-student-api', methods=['GET', 'POST'])
def add_student_to_api():
    if request.method == 'POST':
        student_data = {
            'student_name': request.form['student_name'],
            'physics': request.form['physics'],
            'chemistry': request.form['chemistry'],
            'mathamatics': request.form['mathamatics']
        }

        try:
            # Make a POST request to the API
            response = requests.post('https://api.websl.lk/api/student', json=student_data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Handle the response
            if response.status_code == 201:  # Assuming 201 Created for successful post
                return redirect(url_for('get_students_from_api'))
            else:
                return f"Failed to add student: {response.status_code}"
        
        except requests.exceptions.RequestException as e:
            # Handle errors
            return f"An error occurred: {e}"
    
    return render_template('add-student.html')

@app.route('/students')       
def students(): 
    students = Students.query.all()
    return render_template('students.html', students=students) 

@app.route('/add-student')       
def add_student(): 
    return render_template('add-student.html') 

@app.route('/studnt-result', methods=['POST', 'GET'])
def result():
    #if request.method == 'POST':
     #   result = request.form
      #  return render_template("student-results.html", result=result)  
    if request.method == 'POST':
        # Get the data from the form
        student_name = request.form['Name']
        physics = request.form['Physics']
        chemistry = request.form['chemistry']
        mathamatics = request.form['Maths']
        
        # Create a new student record
        new_student = Students(student_name=student_name, physics=physics, chemistry=chemistry, mathamatics=mathamatics)
        
        try:
            # Add the new student to the database
            db.session.add(new_student)
            db.session.commit()
            return render_template("/student-results.html", result=request.form)
        except:
            # Handle the error if the insertion fails
            db.session.rollback()
            return "There was an issue adding the student's data"
    
    return render_template("add-student.html")

@app.route('/admin')  # decorator for route(argument) function
def hello_admin():  # binding to hello_admin call
    return 'Hello Admin'


@app.route('/guest/<guest>')
def hello_guest(guest):  # binding to hello_guest call
    return 'Hello %s as Guest' % guest


@app.route('/user/<name>')
def hello_user(name):
    if name == 'admin':  # dynamic binding of URL to function
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest=name))


# if __name__ == '__main__':
# app.run(debug=True)

if __name__=='__main__': 
   app.run(debug=True) 