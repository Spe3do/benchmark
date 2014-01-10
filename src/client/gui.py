# -*- coding: utf-8 -*-
# Author: Tamas Marton

import sys
import time
import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.logger import Logger
from kivy.properties import ObjectProperty, ListProperty
from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition


from kivy.adapters.dictadapter import DictAdapter
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.uix.listview import ListItemButton, ListItemLabel, CompositeListItem, ListView

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image

'''Fixing OSX Mavericks stupid locale bug'''
import platform
if platform.system() == "Darwin":
	import locale
	lc = locale.getlocale()
	if lc[0]== None and lc[1]== None:
		locale.setlocale(locale.LC_ALL, 'en_US')


class TasksScreen(Screen):
	pass

class ExecutingScreen(Screen):
	pass

class NoTaskSelectedDialog(Popup):
	pass

class MyButton(Button):
	pass


class GUI(BoxLayout):

	text_ipToConnect = ObjectProperty(None)
	label_Connected = ObjectProperty(None)
	tabbed_Panel = ObjectProperty(None)
	panelHeader_Connect = ObjectProperty(None)
	panelHeader_Tasks = ObjectProperty(None)
	panelHeader_Results = ObjectProperty(None)

	def __init__(self,  **kwargs):
		super(GUI,self).__init__(**kwargs)
		Logger.info('GUI: Main GUI created')

		self.screenManager.transition = SlideTransition(direction="left")

		self.listOfTask = self.taskToBeExecute
		self.controller = App.get_running_app()


	def getAdapter(self):
		task_args_converter = lambda row_index, rec: {
			'orientation': 'vertical',
			'text': rec['name'],
			'size_hint_y': None,
			'height': '150sp',
			'spacing': 0,
			'cls_dicts': [{'cls': ListItemButton,
						   'kwargs':{'text': rec['name'],
						   			 'is_representing_cls': True, 'size_hint_y': 0.2, 'markup': True, 'deselected_color':[1., 1., 0., 1], 'selected_color':[0., 1., 0., 1]}},
							{'cls': ListItemLabel,
							 'kwargs':{'text': rec['desc'], 'size_hint_y': 0.8, 'markup': True}} ]}

		tdata = App.get_running_app().model.getTasksListOfDict()

		item_strings = ["{0}".format(index) for index in range(len(tdata))]

		tasks_dict_adapter = DictAdapter(
			sorted_keys=item_strings,
			data=tdata,
			args_converter = task_args_converter,
			selection_mode='multiple',
			cls=CompositeListItem)

		return tasks_dict_adapter
		

	def close(self):
		sys.exit(0)
		

	def connect(self, ip):
		self.connectpopup = Popup(title='Connecting', size_hint=(None, None), height=60, width=350, auto_dismiss=True)
		Logger.info('SOCKET: Connecting to '+ip)
		self.controller.SERVERIP = ip
		self.connectpopup.open()
		self.controller.communication.connectToServer()

		self.screenManager.current = 'tasks_selection'


	def switchToTab(self, name):
		if self.tabbed_Panel.current_tab.text != name:
			if name == "Connect":
				self.tabbed_Panel.switch_to(self.panelHeader_Connect)
			elif name == "Tasks":
				self.listOfTask.adapter = self.getAdapter()
				self.tabbed_Panel.switch_to(self.panelHeader_Tasks)
			elif name == "Results":
				self.tabbed_Panel.switch_to(self.panelHeader_Results)
			else:
				Logger.error('switchToTab: Invalid PanelHeader name received: '+name)


	def executeTasks(self):
		if self.controller.STATE == "IDLE":
			selected_task_list = []

			for i in self.listOfTask.adapter.selection:
				selected_task_list.append(i.text)

			if len(selected_task_list) != 0:
				self.controller.STATE = "RUNNING"
				self.controller.sendTasksToServer(selected_task_list)
				self.progressbar_ExecutingScreen.max = len(selected_task_list)
				self.screenManager.current = self.screenManager.next()
			else:
				p=NoTaskSelectedDialog()
				p.open()


	def getResults(self):
		temp_text=""

		for value in self.controller.getResults().itervalues():
			temp_text+=(value['name']+
'''
-------------------------------------------


**Result:**


::

'''+value['result']+
'''

''')
			if value['image'] != None:
				temp_text+=(
'''


**System load during the task:**


.. image:: '''+value['image']+'''

''')

		self.rst_result.text= temp_text

		self.screenManager.current = 'tasks_selection'
		self.switchToTab("Results")



	def setConnectionStatus(self,connected):
		if connected:
			self.label_Connected.text = "Status: [color=#00ff00][b]Connected[/b][/color]"
		else:
			self.label_Connected.text = "Status: [color=#ff0000][b]Disconnected[/b][/color]"


	def updateExecutionStatus(self, task):
		if task != None:
			self.textinput_Log.text = ''
			temptext = "[size=24][color=#36acd8][b]Current Task[b]: [/size][/color][size=18]"+str(task.NAME)+"[/size]\n"
			temptext +="[size=24][color=#36acd8][b]Description[b]: [/size][/color][size=18]\n"+str(task.DESCRIPTION)+"[/size]"
			self.label_RunningTask.text = temptext


	def updateProgressBar(self, percent):
		self.progressbar_ExecutingScreen.value=percent


	def goBackButtonHandler(self):
		self.controller.STATE= "IDLE"
		self.switchToTab("Tasks")


	def sendToLog(self, message):
		self.textinput_Log.text += message+"\n"


