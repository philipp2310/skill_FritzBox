import sqlite3
from typing import Dict, Union

from core.commons import constants
from core.device.model.Device import Device
from core.device.model.DeviceAbility import DeviceAbility
from typing import Optional
from pathlib import Path
from core.webui.model.DeviceClickReactionAction import DeviceClickReactionAction
from core.webui.model.OnDeviceClickReaction import OnDeviceClickReaction
from core.device.model.DeviceException import RequiresGuiSettings


class Fritzbox(Device):

	@classmethod
	def getDeviceTypeDefinition(cls) -> dict:
		return {
			'deviceTypeName'        : 'Fritzbox',
			'perLocationLimit'      : 1,
			'totalDeviceLimit'      : 1,
			'allowLocationLinks'    : False,
			'allowHeartbeatOverride': False,
			'heartbeatRate'         : 5,
			'abilities'             : [DeviceAbility.NONE]
		}


	def __init__(self, data: Union[sqlite3.Row, Dict]):
		super().__init__(data)


	def getDeviceIcon(self, path: Optional[Path] = None) -> Path:
		icon = ''
		if self.getConfig('ip'):
			try:
				if self.skillInstance.existsNewMissedCall():
					icon = Path(f'{self.Commons.rootDir()}/skills/{self.skillName}/devices/img/Fritzbox_callMissed.png')
				else:
					icon = Path(f'{self.Commons.rootDir()}/skills/{self.skillName}/devices/img/Fritzbox_ok.png')
			except:
				pass

		if not icon:
			icon = Path(f'{self.Commons.rootDir()}/skills/{self.skillName}/devices/img/Fritzbox_default.png')

		return super().getDeviceIcon(icon)

	def onUIClick(self) -> dict:
		"""
		Called whenever a device's icon is clicked on the UI
		:return:
		"""
		if not self.getConfig('ip') or not self.getConfig('password'):
			raise RequiresGuiSettings()

		if self.getConfig('ip') and self.getConfig('password') and not self.paired:
			self.pairingDone(uid=self.newSecret())

		mc = self.skillInstance.getFirstUnreadCall()
		if mc:
			self.skillInstance.updateConfig("lastRead", mc['id'])
			return OnDeviceClickReaction(action=DeviceClickReactionAction.INFO_NOTIFICATION.value, data=f"Missed call: {mc['date']} {mc['name']}").toDict()
			#todo: send device update for icon change

		return OnDeviceClickReaction(action=DeviceClickReactionAction.NAVIGATE.value, data=f'http://{self.getConfig("ip")}').toDict()
