import sqlite3

from core.webui.model.Widget import Widget



class Missedcalls(Widget):

	def __init__(self, data: sqlite3.Row):
		super().__init__(data)


	def getMissedCalls(self):
		return self.skillInstance.getMissedCalls()


	def markRead(self, index: int):
		self.skillInstance.updateConfig("lastRead", index)

