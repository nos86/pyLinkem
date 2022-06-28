import requests 
import json

class LinkemRouter:
    host = ""
    username = ""
    password = ""
    device_name = ""
    model_id = ""
    serial_id = ""
    IMEI = ""
    ICCID = ""
    service_provider = ""
    firmware_version = ""
    IAD_firmware_version = ""
    firmware_created_on = ""
    bootrom_version = ""
    bootrom_created_on = ""
    LTE_supported_bands = []
    wan_ip = ""
    lan_ip = ""
    
        
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.login()
        self.getDeviceInfo()
        self.getIpInfo()
        
        
    def debug(self, page, action, data={}, parse_response=True): #FIXME: remove it
        return self.__call_api(page, action, data, parse_response)
        
    def getIpInfo(self):
        data = self.__call_api(action="init")
        self.wan_ip = data['wan_ip']
        self.lan_ip = data['now_info']['lan_ip']

    def getCurrentSpeed(self):
        data = self.__call_api(action="mobile_status_Info",)
        return {'up': data['Up_Down_Link']['up_UL_Rate'], 'down': data['Up_Down_Link']['dl_DL_Rate']}

    def getDeviceInfo(self):
        html = self.__call_api(page="control_panel_about.asp", action="request", parse_response=False)
        info = list(filter( lambda x: x.startswith('var multipleParameters'), html.content.decode().split('\n')))[0].split('"')[1]
        (_, self.device_name, self.model_id, _, self.serial_id, self.service_provider,
            self.firmware_version, self.IAD_firmware_version, self.bootrom_version,
            self.firmware_created_on, self.bootrom_created_on, LTE_supported_bands, 
            self.IMEI, _, _, self.ICCID, _) = info.split('\t')
        if LTE_supported_bands == "0":
            self.LTE_supported_bands = ['Not available']
        else:
            self.LTE_supported_bands = LTE_supported_bands.split(',')

    def getMobileStatus(self):
        data = self.__call_api(action="mobile_Signal_Strength")
        return {
            'signal': data['signal'],
            'link strength': data['val_rsrp'],
            'link quality': data['val_cinr']
        }

    def isNewFirmwareAvailable(self):
        return self.__call_api(action='chkFwUpgrade', parse_response=False).content != b"Nothing"
        
    def getDeviceStatus(self):
        data = self.__call_api(action="status_system")
        ans = {
            "cpu": float(data['cpu_current_usage']),
            "mem": float(data['mem_current_usage']),
            "data_rate": float(data['tf'].split(",")[0]),
            "firewall": data['firewall']=="ON",
            'uptime': int(data['uptime_secs']),
            'last_reboot_reason': data['ui_reboot_reason']
        }
        return ans
    
    def login(self):
        data = {"user_name":self.username, "user_passwd":self.password}
        return self.__call_api(page="login.asp",  action="login", data = data, parse_response=False)
    
    def __call_api(self, action, data={}, page='ajax.asp', parse_response=True):
        baseurl = f"https://{self.host}/cgi-bin/sysconf.cgi"
        query= {'page': page, 'action': action}
        if data:
            response = self.session.post(baseurl, params=query, data = data, verify=False)
        else:
            response = self.session.get(baseurl, params=query, verify=False)
        
        if parse_response:
            return json.loads(response.content.decode().replace("'",'"'))
        else:
            return response