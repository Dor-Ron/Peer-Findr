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
                email      = form.email.data,
                first      = form.first.data,
                second     = form.second.data,
                third      = form.third.data,
                fourth     = form.fourth.data,
                fifth      = form.fifth.data,
                sixth      = form.sixth.data)
        session['logged_in'] = True
        session['username'] = form.username.data
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.Classmate.get(models.Classmate.username == form.username.data)
        except models.DoesNotExist:
            flash('Your email or password do not match!', 'error')
        else:
            if user.password == md5(form.password.data).hexdigest():
                session['logged_in'] = True
                session['username'] = form.username.data
                flash("You've successfully logged in!")
                return redirect(url_for('class_check'))
            else:
                flash('Your email or password do not match!', 'error')
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
        student_courses.append(lst.strip("()").translate(None, "'u ").split(','))

    first_class = student_courses[0][0]
    second_class = student_courses[0][1]
    third_class = student_courses[0][2]
    fourth_class = student_courses[0][3]
    fifth_class = student_courses[0][4]
    if student_courses[0][5] != "NoClass":
        sixth_class = student_courses[0][5]
    else:
        sixth_class = 'somethingcompletelyrandomnoonewillwritedown'

    classes_tuple = (first_class, session['username'], second_class, session['username'], third_class, session['username'], fourth_class, session['username'], fifth_class, session['username'], sixth_class, session['username'],)
    matched_students_list = []
    for row in c.execute('''SELECT first_name, last_name, first, second, third, fourth, fifth, sixth 
                            FROM classmate 
                            WHERE first = ? 
                            AND username <> ?
                            OR second = ?
                            AND username <> ?
                            OR third = ?
                            AND username <> ?
                            OR fourth = ?
                            AND username <> ?
                            OR fifth = ?
                            AND username <> ?
                            OR sixth = ?
                            AND username <> ?;''', classes_tuple):
        matched_students_list.append(str(row))

    matched_students = []
    for lst in matched_students_list:
        matched_students.append(lst.strip("()").translate(None, "' ").split(','))

    #print matched_students_list
    print matched_students

    return render_template('class_check.html', user = student_courses, others = matched_students)
    



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
            username = "FuckMeMariana",
            email='dor.rondel@gmail.com',
            password='123456',
            admin=True,
            first_name='Dor',
            last_name="Rondel",
            first = "calc",
            second = "bio",
            third = "engl",
            fourth = "speech",
            fifth = "psych",
            sixth = "No Class"
        )
    except ValueError:
        pass
    app.run(debug = True)