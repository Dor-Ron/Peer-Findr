#!usr/bin/python

from flask.ext.login import UserMixin
from peewee import *
from hashlib import md5

DATABASE = SqliteDatabase('classmates.db')

class BaseModel(Model):
	'''Schema blueprint for other tables to inherit'''

	class Meta:
		database = DATABASE  # make the tables in classmates.db


class Classmate(UserMixin, BaseModel):
	'''Table with student information'''
	username = CharField(max_length = 20,  unique = True)
	password = CharField(max_length = 18)
	first_name = CharField(max_length = 20)
	last_name = CharField(max_length = 20)
	is_admin = BooleanField(default = False)
	first = CharField(max_length = 20)
	second = CharField(max_length = 20)
	third = CharField(max_length = 20)
	fourth = CharField(max_length = 20)
	fifth = CharField(max_length = 20)
	sixth = CharField(max_length = 20)

	'''
	Basically in SQL:    CREATE TABLE Classmate (id INTEGER AUTO_INCREMENT PRIMARY KEY, 
												 username VARCHAR(20) UNIQUE,
												 password VARCHAR(18),  
												 first_name VARCHAR(20),
												 last_name VARCHAR(20),
												 is_admin BOOLEAN DEFAULT FALSE,
												 first VARCHAR(20),
												 second VARCHAR(20),
												 third VARCHAR(20),
												 fourth VARCHAR(20),
												 fifth VARCHAR(20),
												 sixth VARCHAR(20))
	'''  
	# Note that peewee automatically creates an id row, so there's no need to actually declare it.


	@classmethod  # To allow creating a user without creating an instance of the class
	def create_user(cls, username, password, first_name, last_name, first, second, third, fourth, fifth, sixth, admin = False):
		'''add classmate to Classmate table. Note engineering students are permitted to take up to six clasess'''
		try:
			with DATABASE.transaction():  # Basically, try creating a user, if it works great, otherwise forget everything you just tried
				cls.create(
					first_name = first_name,
					last_name = last_name,
					username = username,
					password = md5(password).hexdigest(),
					first = first,
					second = second,
					third = third,
					fourth = fourth,
					fifth = fifth,
					sixth = sixth,
					is_admin = admin)
		except IntegrityError:
		    raise ValueError('User already exists')

	class Meta:
		'''table design'''
		order_by = ('last_name',)

def initialize():
	'''Boot up database'''
	DATABASE.connect()
	DATABASE.create_tables([Classmate], safe = True)
	DATABASE.close()