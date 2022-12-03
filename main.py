__version__ = '1.0.0'

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

from kivy.properties import NumericProperty
from kivy.graphics.vertex_instructions import Rectangle, Ellipse, Line
from kivy.graphics.context_instructions import Color
from kivy.uix.label import Label
from kivy.uix.button import Button

import random
import threading
import requests
import time


URL_TO_PARSE = 'https://getmytemperature.pythonanywhere.com/cleardata'
TIMEOUT = 5


WINDOW_SIZE = (400, 600)
BORDERS = (50, 200)
MAIN_FIELD_SIZE = (WINDOW_SIZE[0] - BORDERS[0], WINDOW_SIZE[1] - BORDERS[1])
POS_MAIN_FIELD = (BORDERS[0] / 2 - 5, BORDERS[1] / 3 - 5)
degreesMax = 200

Window.size = (WINDOW_SIZE)


class MainField(Widget):
	data = []
	WORKING = False
	nowTemperature = 0
	classObj = None

	def getClassObj(self, classObj):
		self.classObj = classObj

	def on_touch_down(self, touch):
		self.drawScreen()

	def gettingData(self):
		while self.WORKING:
			try: self.data = list(map(float, requests.get(URL_TO_PARSE, timeout=TIMEOUT).text.split('<br>')[:-1]))
			except Exception as error: self.data = []
			
			self.nowTemperature = self.data[-1] if len(self.data) > 0 else 0

	def drawScreen(self):
		martixOfGraphic = []
		countOfDatas = len(self.data)

		self.classObj.changeText()

		for num in range(0, countOfDatas):
			gettedData = self.data[num] + 100
			if gettedData > degreesMax: gettedData = degreesMax

			martixOfGraphic.append((
				round(MAIN_FIELD_SIZE[0] / countOfDatas * num) + BORDERS[0] / 2, # X
				round(MAIN_FIELD_SIZE[1] / degreesMax * gettedData) + BORDERS[1] / 3 # Y
			))

		self.canvas.before.clear()
		self.canvas.after.clear()

		with self.canvas.before:
			Color(1, 1, 1, 0.07)
			Rectangle(
				pos=POS_MAIN_FIELD, 
				size=(MAIN_FIELD_SIZE[0] + 5, MAIN_FIELD_SIZE[1] + BORDERS[0] / 3 + 5)
			)

		with self.canvas.after:
			for position in martixOfGraphic:
				if martixOfGraphic[martixOfGraphic.index(position) - 1][1] < position[1] and martixOfGraphic.index(position) >= 0:
					Color(0, 1, 0, 1)
				else:
					Color(1, 0, 0, 1)

				Rectangle(pos=position, size=(5, 5))



class MainApp(App):
	WORKING = True
	parentWidget = GridLayout()

	def __init__(self, **kwargs):
		super(MainApp, self).__init__(**kwargs)
		Window.bind(on_request_close=self.close)

	def build(self):
		self.mainField = MainField()
		self.mainField.WORKING = True
		threading.Thread(target=self.mainField.gettingData).start()
		self.mainField.getClassObj(self)
		self.mainField.drawScreen()

		self.parentWidget.add_widget(self.mainField)
		self.parentWidget.add_widget(Label(
					text="0 -",
					pos=(
						round(-(BORDERS[0] / 2) - BORDERS[0] / 5 - 4), 
						round(POS_MAIN_FIELD[1] + MAIN_FIELD_SIZE[1] / 2.5)
					)
				)
			)

		self.parentWidget.add_widget(
				Button(
					text="DOWN",
					pos=(round(POS_MAIN_FIELD[0]), 5),
					size=(MAIN_FIELD_SIZE[0] / 3, round(BORDERS[1] / 3 - 20)),
					color=(0.5, 0.5, 0.5, 1)
				)
			)

		self.parentWidget.add_widget(
				Button(
					text="UP",
					pos=((WINDOW_SIZE[0] - BORDERS[0] / 2) - (MAIN_FIELD_SIZE[0] / 3), 5),
					size=(MAIN_FIELD_SIZE[0] / 3, round(BORDERS[1] / 3 - 20)),
					color=(0.5, 0.5, 0.5, 1)
				)
			)

		self.parentWidget.add_widget(
			Label(
				text=f"{str(self.mainField.nowTemperature)} °C",
				pos=(BORDERS[0] * 3, MAIN_FIELD_SIZE[1] + BORDERS[1] / 2.5),
				font_size=80
			)
		)

		return self.parentWidget

	def close(self, touch):
		self.mainField.WORKING = False
		self.WORKING = False

	def changeText(self):
		if self.parentWidget:
			for widg in self.parentWidget.children:
				self.parentWidget.remove_widget(widg)
				self.parentWidget.add_widget(
					Label(
						text=f"{str(self.mainField.nowTemperature)} °C",
						pos=(BORDERS[0] * 3, MAIN_FIELD_SIZE[1] + BORDERS[1] / 2.5),
						font_size=80
					)
				)

				break


if __name__ == '__main__': MainApp().run()
