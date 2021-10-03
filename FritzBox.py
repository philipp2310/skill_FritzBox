from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzcall import FritzCall


class FritzBox(AliceSkill):
	"""
	Author: philipp2310
	Description: Control your fritz!box, and show its status!
	"""

	def __init__(self):
		super().__init__()
		self._device = None
		self._fc = None


	@property
	def device(self):
		if not self._device:
			dt = self.DeviceManager.getDeviceType(skillName=self.name, deviceType="Fritzbox")
			devices = self.DeviceManager.getDevicesBySkill(skillName=self.name, deviceType=dt, connectedOnly=False)
			if len(devices) != 1:
				return None
			self._device = devices[0]
		return self._device


	@property
	def fc(self):
		if not self._fc:
			self._fc = FritzCall(address=self.device.getConfig("ip"), user=self.device.getConfig("username"), password=self.device.getConfig("password"))
		return self._fc


	def getMissedCalls(self):
		lastRead = int(self.getConfig("lastRead"))
		calls = self.fc.get_missed_calls()
		ret = []
		for call in calls:
			ret.append({'id': call.Id, 'name': call.Caller if call.Name is None else call.Name, 'date': call.Date, 'new': lastRead < int(call.Id)})

		return ret


	def getLastMissedCall(self):
		try:
			return self.getMissedCalls()[0]
		except Exception as e:
			return None

	def getFirstUnreadCall(self):
		try:
			prev = None
			for call in self.getMissedCalls():
				if call['new']:
					prev = call
				else:
					return prev
		except Exception as e:
			return None


	def existsNewMissedCall(self):
		try:
			return self.getLastMissedCall()["new"]
		except Exception as e:
			return False
