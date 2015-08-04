#!usr/bin/env python

#########################################
################ Imports ################
#########################################

from flask import (Flask, render_template, url_for, redirect, 
				   flash, g, request, session)
from hashlib import md5
from functools import wraps
import sqlite3
import gc

import models
import forms
from courses import (bio_one_one, bio_one_two, bio_two, chem_one_one, 
                     chem_one_two,chem_one_three, chem_one_four, chem_one_five, 
                     chem_one_six, chem_two_one, chem_two_two, chem_two_three,
                     physics_one_one, physics_one_two,  physics_one_three,
                     physics_two_one, physics_two_two, architecture,
                     humanities_one, humanities_two, psychology_one,
                     psychology_two, political_science, compsci_one, compsci_two)


#########################################
############### Setup ###################
#########################################


app = Flask(__name__)
app.secret_key = 'AAAAB3NzaC1yc2EAAAADAQABAAjh4f35g434wfc23xq23'


@app.before_request
def before_request():
    '''Connect to a database before each request.'''
    g.db = models.DATABASE
    g.db.connect()

@app.after_request
def after_request(response):
    '''Close the database connection after each request.'''
    g.db.close()
    return response

def login_required(f):
    '''decorator to check if user is logged in, if they're not it redirects them to the login page'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if session['username'] == False:
                flash('You need to login inorder to view this page')
                return redirect(url_for('login', next=request.url))
        except KeyError:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

conn = sqlite3.connect("classmates.db", check_same_thread=False)
c = conn.cursor()


#########################################
############## Routing ##################
#########################################


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/about/')
def about_page():
    return render_template('about.html')

@app.route('/register/',  methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you've registered succesfully!", "success")
        models.Classmate.create_user(
                first_name = form.first_name.data,
                last_name  = form.last_name.data,
                username   = form.username.data,
                password   = form.password.data,
                first      = form.first.data,
                second     = form.second.data,
                third      = form.third.data,
                fourth     = form.fourth.data,
                fifth      = form.fifth.data,
                sixth      = form.sixth.data)
        session['logged_in'] = True
        session['username'] = form.username.data
        return redirect(url_for('class_check'))
    return render_template('register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.Classmate.get(models.Classmate.username == form.username.data)
        except models.DoesNotExist:
            flash('Your username or password do not match!', 'error')
        else:
            if user.password == md5(form.password.data).hexdigest():
                session['logged_in'] = True
                session['username'] = form.username.data
                flash("You've successfully logged in!")
                return redirect(url_for('class_check'))
            else:
                flash('Your username or password do not match!', 'error')
    return render_template('login.html', form=form)



@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    session.clear()
    flash('You have been logged out.')
    gc.collect()
    return redirect(url_for('index'))


@app.route('/class_codes/')
def class_codes():
    return render_template('class_codes.html')


@app.route('/class_check/')
@login_required
def class_check():

    student = (session['username'],)
    student_courses_string = []
    for row in c.execute('SELECT first, second, third, fourth, fifth, sixth FROM classmate WHERE username=?', student):
        student_courses_string.append(str(row))

    student_courses = []  
    for lst in student_courses_string:
        student_courses.append(lst.strip("()").translate(None, "' ").split(','))

    first_class = student_courses[0][0][1:]
    second_class = student_courses[0][1][1:]
    third_class = student_courses[0][2][1:]
    fourth_class = student_courses[0][3][1:]
    fifth_class = student_courses[0][4][1:]
    if student_courses[0][5] != "none":
        sixth_class = student_courses[0][5][1:]
    else:
        sixth_class = 'somethingcompletelyrandomnoonewillwritedown'

    user = session['username']

    #--------------SQL query design ----------------------

    def make_second_query(lst, usr, first, third, fourth, fifth, sixth):
        '''query for when only the second class is in science class list'''
        query = """SELECT first_name, last_name, first, second, third, fourth, fifth, sixth 
                 FROM classmate
                 WHERE first = '{}' 
                 AND username <> '{}' 
                 """.format(first, usr)
                 
        for i in lst:
            query += "OR second = '" + i + "'" + " AND username <> '{}' ".format(usr)
            
        query += '''OR third = '{}'
                    AND username <> '{}'
                    OR fourth = '{}'
                    AND username <> '{}'
                    OR fifth = '{}'
                    AND username <> '{}'
                    OR sixth = '{}'
                    AND username <> '{}';'''.format(third, usr,
                                                 fourth, usr,
                                                 fifth, usr,
                                                 sixth, usr)
                                            
        return query


    def make_sixth_elective_query(lst, usr, first, second, third, fourth, fifth):
        '''query for when only the sixth class is in elective list'''
        query = """SELECT first_name, last_name, first, second, third, fourth, fifth, sixth 
                   FROM classmate
                   WHERE first = '{}'
                   AND username <> '{}' 
                   OR second = '{}'
                   AND username <> '{}'
                   OR third = '{}'
                   AND username <> '{}'
                   OR fourth = '{}'
                   AND username <> '{}'
                   OR fifth = '{}'
                   AND username <> '{}'
                """.format(first, usr, second, usr, third, usr, fourth, usr, fifth, usr)

        for i in lst:
            query += "OR sixth = '" + i + "'" + " AND username <> '{}' ".format(usr)

        query += ";"

        return query


    def make_second_sixth_query(lst1, lst2, usr, first, third, fourth, fifth):
        '''query for when second and sixth class are from list'''
        query = """SELECT first_name, last_name, first, second, third, fourth, fifth, sixth 
                   FROM classmate
                   WHERE first = '{}' 
                   AND username <> '{}' 
                """.format(first, usr)

        for i in lst1:
            query += "OR second = '" + i + "'" + " AND username <> '{}' ".format(usr)

        query += """OR third = '{}'
                   AND username <> '{}'
                   OR fourth = '{}'
                   AND username <> '{}'
                   OR fifth = '{}'
                   AND username <> '{}' """.format(third, usr, fourth, usr, fifth, usr)

        for i in lst2:
            query += "OR sixth = '" + i + "'" + " AND username <> '{}' ".format(usr)

        query += ";"

        return query


    def default_query(usr, first, second, third, fourth, fifth, sixth):
        '''query for when none of the classes are in a list'''
        query =  """SELECT first_name, last_name, first, second, third, fourth, fifth, sixth 
                    FROM classmate
                    WHERE first = '{}' 
                    AND username <> '{}' 
                    OR second = '{}'
                    AND username <> '{}'
                    OR third = '{}'
                    AND username <> '{}'
                    OR fourth = '{}'
                    AND username <> '{}'
                    OR fifth = '{}'
                    AND username <> '{}'
                    OR sixth = '{}'
                    AND username <> '{}';""".format(first, usr, second, usr, third, usr, 
                                                    fourth, usr, fifth, usr, sixth, usr)

        return query

    #----------------- End query design -----------------

    SCIENCE_LIST = [bio_one_one, bio_one_two, bio_two, chem_one_one, 
                    chem_one_two,chem_one_three, chem_one_four, chem_one_five, 
                    chem_one_six, chem_two_one, chem_two_two, chem_two_three,
                    physics_one_one, physics_one_two,  physics_one_three,
                    physics_two_one, physics_two_two, compsci_one, compsci_two]

    ELECTIVE_LIST = [architecture, humanities_one, humanities_two, psychology_one,
                     psychology_two, political_science]


    def check_proper_query(usr, first, second, third, fourth, fifth, sixth):
        '''check which query to useon db'''
        is_second = False
        correct_second_list = None
        for lst in SCIENCE_LIST:
            if second in lst:
                is_second = True
                correct_second_list = lst

        is_sixth = False
        correct_sixth_list = None
        for lst in ELECTIVE_LIST:
            if sixth in lst:
                is_sixth = True
                correct_sixth_list = lst

        query_list = [usr, first, second, third, fourth, fifth, sixth, "0"]  # default case
        if is_second and not is_sixth:
            query_list = [correct_second_list, usr, first, third, fourth, fifth, sixth, "2"]  # if only 2
        elif is_sixth and not is_second:
            query_list = [correct_sixth_list, usr, first, second, third, fourth, fifth, "6"]  # if only 6
        elif is_second and is_sixth:
            query_list = [correct_second_list, correct_sixth_list, usr, first, third, fourth, fifth, "26"]  # if 2 and 6
            
        return query_list    

    #---------------------------------------------------

    list_of_args = check_proper_query(user, first_class, second_class, third_class, fourth_class, fifth_class, sixth_class)
    
    
    matched_students_list = []    
    if list_of_args[-1] == "0":
        for row in c.execute(default_query(list_of_args[0], list_of_args[1], list_of_args[2], list_of_args[3],
                                            list_of_args[4], list_of_args[5], list_of_args[6])):
            matched_students_list.append(str(row))
    elif list_of_args[-1] == "2":
        for row in c.execute(make_second_query(list_of_args[0], list_of_args[1], list_of_args[2], list_of_args[3],
                                               list_of_args[4], list_of_args[5], list_of_args[6])):
            matched_students_list.append(str(row))
    elif list_of_args[-1] == "6":
        for row in c.execute(make_sixth_elective_query(list_of_args[0], list_of_args[1], list_of_args[2], list_of_args[3],
                                                       list_of_args[4], list_of_args[5], list_of_args[6])):
            matched_students_list.append(str(row))
    elif list_of_args[-1] == "26":
        for row in c.execute(make_second_sixth_query(list_of_args[0], list_of_args[1], list_of_args[2], list_of_args[3],
                                                       list_of_args[4], list_of_args[5], list_of_args[6])):
            matched_students_list.append(str(row))
    else: 
        pass


    matched_students = []
    for lst in matched_students_list:
        matched_students.append(lst.strip("()").translate(None, "' ").split(','))


    students_in_math_class = []
    for student in matched_students:
        if student[2][1:] == first_class:
            students_in_math_class.append(student)

    student_science_list = []
    for lst in SCIENCE_LIST:
        if second_class in lst or student[3][1:] == second_class:
            student_science_list = lst
            break

    students_in_science_class = []
    for student in matched_students:
        for person in student_science_list:
            if student[3][1:] in person:
                students_in_science_class.append(student)

    students_in_english_class = []
    for student in matched_students:
        if student[4][1:] == third_class:
            students_in_english_class.append(student)

    students_in_speech_class = []
    for student in matched_students:
        if student[5][1:] == fourth_class:
            students_in_speech_class.append(student)

    students_in_fifth = []
    for student in matched_students:
        if student[6][1:] == fifth_class:
            students_in_fifth.append(student)


    student_six_list = []
    for lst in ELECTIVE_LIST:
        if sixth_class in lst:
            student_six_list = lst
            break
        else:
            student_six_list = []

    students_in_sixth = []
    for student in matched_students:
        if student[7][1:] in student_six_list or student[7][1:] == sixth_class:
                students_in_sixth.append(student)




    return render_template('class_check.html', user = student_courses, one = students_in_math_class,
                            two = students_in_science_class, three = students_in_english_class, 
                            four = students_in_speech_class, five = students_in_fifth, six = students_in_sixth)
    


#########################################
########### Error Handling ##############
#########################################


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html")



if __name__ == '__main__':
    models.initialize()
    try:
        models.Classmate.create_user(
            username = "Test",
            password='123456',
            admin=False,
            first_name='Test',
            last_name="McTest",
            first = "CalculusIII10101",
            second = "ChemistryI20202",
            third = "English00000",
            fourth = "EngineeringDesign00000",
            fifth = "PoliticalScience00000",
            sixth = "none"
        )
    except ValueError:
        pass
    app.run(debug = True)
