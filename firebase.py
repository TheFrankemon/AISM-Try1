# -*- coding: utf-8 -*-
import pyrebase
import json
import os

fireconfig = ""
firebase = None
fileDir = os.path.dirname(os.path.realpath('__file__'))

class Firebase(object):
	def __init__(self):
		with open('config.json') as data_file:
			conf = json.load(data_file)
		global fireconfig
		fireconfig = conf["conn"]["fireconfig"]
		self.connect()

		##Uncomment for individual use##
		"""
		course = "Finanzas 2"
		parallels = self.get_DB_course_parallels(course)
		print(("Existen {} paralelos de {}...").format(len(parallels), course))
		for parallel in parallels:
			professor = parallel['professor']
			classroom = parallel['classroom']
			period = parallel['period']
			print(("{}. Las clases son en {} en horario {}").format(professor, classroom, period))
		
		course = "Finanzas 2"
		professor = "Juan Jose Jordan Sanchez"
		parallels = self.get_DB_course_parallels(course, professor)
		print(("Existen {} paralelos de {} con {}...").format(len(parallels), course, professor))
		index = 1
		for parallel in parallels:
			classroom = parallel['classroom']
			period = parallel['period']
			print(("Paralelo {}. Las clases son en {} en horario {}").format(index, classroom, period))
			index += 1
		"""

	def connect(self):
		try:
			print("Connecting...")
			global firebase
			firebase = pyrebase.initialize_app(fireconfig)
			print("Connected to DB: " + fireconfig["databaseURL"])
		except Exception as e:
			print("Failed connection to DB!")
			print(e)
			return

	def get_DB_upblocationurl(self, upblocation = None):
		try:
			db = firebase.database()
			data = db.child("upblocations").child(upblocation).child("cs_url").get().val()
			if data is None:
				return None
			return data

		except Exception as e:
			print(e)
			return

	def get_DB_career(self, career = None):
		try:
			db = firebase.database()
			data = db.child("careers").child(career).get().val()
			if data is None:
				return None
			return data

		except Exception as e:
			print(e)
			return

	def get_DB_course_parallels(self, course = None, professor = None):
		try:
			db = firebase.database()
			data = db.child("courses").child(course).child("parallels").get().val()
			if data is None:
				return None

			if professor is None:
				return data
			else:
				filtered_data = []
				for parallel in data:
					if professor == parallel['professor']:
						filtered_data.append(parallel)

				return filtered_data

		except Exception as e:
			print(e)
			return

##Uncomment for individual use##
"""
if __name__ == "__main__": 
	firebase = Firebase()
"""
