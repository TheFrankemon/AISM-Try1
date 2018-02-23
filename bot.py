# bot.py
# -*- coding: utf-8 -*-
# speechrecognition, pyaudio, brew install portaudio
import sys
import random
sys.path.append("./")

import requests
import datetime as dt
import dateutil.parser
import json
import traceback
import time
from nlg import NLG
from speech import Speech
from vision import Vision
from firebase import Firebase

user_name = "Desconocido"
debugger_enabled = True
camera = 0
conf = None

class Bot(object):
	def __init__(self):
		global conf
		with open('config.json') as data_file:
			conf = json.load(data_file)
		self.nlg = NLG()
		self.speech = Speech(debugger_enabled=debugger_enabled)
		self.vision = Vision(camera=camera)
		self.firebase = Firebase()

	def start(self):
		"""
		Main loop.
		:return:
		"""
		while True:
			requests.get("http://localhost:8888/clear")
			requests.get("http://localhost:8888/keyboard?text=disable")
			if self.vision.recognize_face('c1'):
				print("Found face > Took Photo#1")
				self.__intro_action()
				requests.get("http://localhost:8888/keyboard?text=enable")

				flag = False
				sleeptime = 0
				while not flag:
					uname = requests.get('http://localhost:8888/uname').json()
					if uname[u'name'] == "":
						# must set a max of 20 secs, for example
						sleeptime += 1
						print('Total sleep time: ' + str(sleeptime))
						time.sleep(1)
					else:
						flag = not flag
						requests.get("http://localhost:8888/keyboard?text=disable")
						
				self.vision.recognize_face('c2')
				print("Found face > Took Photo#2")
				print("Username: " + uname[u'name'])
				global user_name
				user_name = uname['name']
				requests.get('http://localhost:8888/unameclear')
				self.__user_name_action()
				timestamp = dt.datetime.today().strftime('%d/%m/%y %H:%M:%S')
				self.firebase.add(user_name,"img/c1.jpg","img/c2.jpg", timestamp)
				print("User saved succesfully on DB")
				self.__goodbye_action()
				# should ask decide_action ??
				#self.__acknowledge_action()
				#self.decide_action()
				time.sleep(5)

	def decide_action(self):
		"""
		Recursively decides an action based on the intent.
		:return:
		"""
		recognizer, audio = self.speech.listen_for_audio()

		# received audio data, now we'll recognize it using Google Speech Recognition
		#speech = self.speech.google_speech_recognition(recognizer, audio)

		# received audio data, now we'll recognize it using Wit Speech API
		speech = self.speech.wit_speech_recognition(recognizer, audio, str(conf["tokens"]["wit_ai_token"]))

		if speech is not None:
			try:
				## Uncomment for HARDCODED SPEECH ##
				#speech = "torta UPB"
				print('Requesting WIT.AI [' + speech + ']')
				r = requests.get('https://api.wit.ai/message?v=20170403&q=%s' % speech, headers={'Authorization': str(conf["tokens"]["wit_ai_token"])})
				print('Text ' + r.text)
				#print r.headers['authorization']
				json_resp = json.loads(r.text)
				entities = None
				intent = None
				if 'entities' in json_resp and 'Intent' in json_resp['entities']:
					entities = json_resp['entities']
					intent = json_resp['entities']['Intent'][0]["value"]

				print(intent)
				if intent == 'appearance':
					self.__appearance_action()
				elif intent == 'insult':
					self.__insult_action()
					return
				elif intent == 'appreciation':
					self.__appreciation_action()
					return
				else: # No recognized intent
					self.__text_action("Perdón, aún estoy en kinder.")

			except Exception as e:
				print("Failed wit!")
				print(e)
				traceback.print_exc()
				self.__text_action("Perdón, no te entendí")
				return

			self.decide_action()

	# CUSTOM
	def __intro_action(self):
		intro_phrase = self.nlg.intro()

		if intro_phrase is None:
			self.__text_action("Me raye, contacta a un humano por favor")
		else:
			self.__text_action(intro_phrase)

	def __user_name_action(self):
		username_phrase = self.nlg.user_name(user_name)

		if user_name is None:
			self.__text_action("No pude guardar tu nombre, contacta a un humano por favor")
		else:
			self.__text_action(username_phrase)

	def __acknowledge_action(self):
		acknowledge = self.nlg.acknowledge(user_name)

		if acknowledge is not None:
			self.__text_action(acknowledge)
		else:
			self.__text_action("Me raye, contacta a un humano por favor")

	def __goodbye_action(self):
		goodbye = self.nlg.goodbye()

		if goodbye is not None:
			self.__text_action(goodbye)
		else:
			self.__text_action("Me raye, contacta a un humano por favor")

	def __appreciation_action(self):
		self.__text_action(self.nlg.appreciation())

	def __insult_action(self):
		self.__text_action(self.nlg.insult())

	def __appearance_action(self):
		requests.get("http://localhost:8888/face")

	def __text_action(self, text=None):
		if text is not None:
			requests.get("http://localhost:8888/statement?text=%s" % text)
			self.speech.synthesize_text(text)

if __name__ == "__main__":
	bot = Bot()
	bot.start()
