import sqlite3

from core.webui.model.Widget import Widget

from fritzconnection.lib.fritzcall import FritzCall


class Missedcalls(Widget):
	DEFAULT_OPTIONS: dict = dict()


	def __init__(self, data: sqlite3.Row):
		super().__init__(data)


	def getMissedCalls(self):
		fc = FritzCall(address=self.skillInstance.getConfig("ip"), user=self.skillInstance.getConfig("username"), password=self.skillInstance.getConfig("password"))
		calls = fc.get_missed_calls()
		ret = []
		for call in calls:
			ret.append({'id': call.Id, 'name': call.Caller if call.Name is None else call.Name, 'Date': call.Date, 'new': true})

		return ret


	def markRead(self, index : int ):
		self.logInfo(f"Marked {index} as read")

