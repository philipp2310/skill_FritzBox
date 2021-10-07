from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzcall import FritzCall
from fritzconnection.core.fritzmonitor import FritzMonitor
from fritzconnection.lib.fritzphonebook import FritzPhonebook
import queue
import time
from core.commons import constants

class FritzBox(AliceSkill):
	"""
	Author: philipp2310
	Description: Control your fritz!box, and show its status!
	"""

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._device = None
		self._fc = None
		self._fp = None


	def onStart(self):
		super().onStart()
		self.runCallMonitor()


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


	@property
	def fp(self):
		if not self._fp:
			self._fp = FritzPhonebook(address=self.device.getConfig("ip"),
			                          user=self.device.getConfig("username"),
			                          password=self.device.getConfig("password"))
		return self._fp


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


	def getNameForNumber(self,number):
		books = self.fp.phonebook_ids
		for book in books:
			try:
				name = self.fp.lookup_names(id=book, number=number)
			except Exception as e:
				pass
			else:
				return name
		# no name found - try without leading 0
		if number[0] == "0":
			number = "+49" + number[1:]
		self.getNameForNumber(number=number)


	def runCallMonitor(self):
		try:
			# as a context manager FritzMonitor will shut down the monitor thread
			if not self.device:
				self.logInfo("Deferring call to FritzMonitor.")
				self.ThreadManager.doLater(interval=5, func=self.runCallMonitor)
				return
			with FritzMonitor(address=self.device.getConfig("ip")) as monitor:
				self.logInfo(f'Connected to Fritz!Box {self.device.getConfig("ip")}')
				event_queue = monitor.start()
				self.ThreadManager.newThread(name='fritzbox', target=self.process_events, args=[monitor, event_queue])
		except OSError as err:
			self.logError(err)

	def process_events(self, monitor, event_queue):
		while True:
			try:
				event = event_queue.get(timeout=10)
			except queue.Empty:
				# check health:
				if not monitor.is_alive:
					monitor.stop()
					event_queue = monitor.start()
					self.logWarning("Error: fritzmonitor connection failed - reconnecting")
				else:
					self.broadcast(method=constants.EVENT_DEVICE_HEARTBEAT, exceptions=[self.name], propagateToSkills=True, uid=self.device.uid, deviceUid=self.device.id)
			else:
				# do event processing here:
				#07.10.21 22: 06:14; RING; 0; 015xxxxxx;20996272;SIP0;  # 015#033[0m
				#07.10.21 22:06:18;DISCONNECT;0;0;#015#033[0m
				self.broadcast(method=constants.EVENT_DEVICE_HEARTBEAT, exceptions=[self.name], propagateToSkills=True, uid=self.device.uid, deviceUid=self.device.id)

				events = event.split(';')
				if events[1] == 'RING':
					caller = self.getNameForNumber(number=events[3]) or events[3]
					self.logInfo(f"Incoming Call! {caller}")
					self.say(text=self.randomTalk(text="incomingCall", replace=[caller]), deviceUid=constants.ALL)
					self.device.updateParam("status", "ringing")
				elif events[1] == 'CONNECT':
					self.logInfo("Call Answered")
					self.device.updateParam("status", "callActive")
				elif events[1] == 'DISCONNECT':
					self.logInfo("Call Ended")
					self.device.updateParam("status", "idle")
				else:
					self.logInfo(f"Unknown FritzStatus: {event}")

