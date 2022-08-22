import json
import requests
requests.packages.urllib3.disable_warnings()

class BigIQ(object):
	def __init__(self, config):
		self.config = config
		self.session = requests.Session()
		self.session.trust_env = False
		headers = {
			'Content-Type': 'application/json',
		}
		self.session.headers = headers
		if not config:
			print('[E] No configuration filename not provided')
		else:
			pass
			#self.auto_login()
		return
	
	def load_configuration(self, config):
		import os
		config_file = 'configuration.json'
		__file__ = 'bigiq.py'
		path = os.path.abspath(__file__)
		dir_path = os.path.dirname(path)
		with open(f'{dir_path}/{config_file}','r') as f:
			raw_file = f.read()
		config_raw = json.loads(raw_file)
		if config not in config_raw:
			print(f'[E] Configuration not found in configuration.json ({self.config})')
			output = {
				'host': '',
				'username': '',
				'password': '',
			}
			return output
		else:
			connection_info = config_raw[config]
			self.host = connection_info['host']
			self.base_url = f'https://{self.host}'
			output = {
				'host': self.host,
				'username': connection_info['username'],
				'password': connection_info['password'],
			}
			return output
		return
	
	def login(self):
		connection_info = self.load_configuration(self.config)
		path = '/mgmt/shared/authn/login'
		body = {
			'username': connection_info['username'],
			'password': connection_info['password'],
			'loginProviderName': 'SSO Password',
		}
		response = self.post(path, j=body)
		if not response['success']:
			print(f'[E] failed logging into {self.config}')
			return response
		
		# time stuff
		from datetime import datetime
		expiration_timestamp = response['result']['token']['exp']
		expiration_timestamp_pretty = datetime.fromtimestamp(expiration_timestamp).strftime('%c')
		
		token = response['result']['token']['token']
		print(f'[I] Token {token} expires on {expiration_timestamp_pretty}')
		headers = {
			'X-F5-Auth-Token': token,
		}
		self.session.headers.update(headers)
		return response
	
	def post(self, path, j={}, body={}, params={}):
		url = f'{self.base_url}{path}'
		
		_params = {}
		for param_key in params:
			_params[param_key] = params[param_key]
		
		if j:
			response_raw = self.session.post(
				url,
				params=_params,
				json=j,
				verify=False,
			)
		elif body:
			response_raw = self.session.post(
				url,
				params=_params,
				data=body,
				verify=False,
			)
		output = {
			'success': False,
			'result': '',
			'response': response_raw,
		}
		if response_raw.status_code in [200,202]:
			output['success'] = True
			try:
				response_json = json.loads(response_raw.text)
				output['result'] = response_json
			except:
				print('[E] Could not load JSON')
			
		elif response_raw.status_code == 401:
			self.login()
			#
			# assume success
			#
			response_raw = self.session.post(
				url,
				params=_params,
				json=body,
				verify=False,
			)
			output['success'] = True
			try:
				response_json = json.loads(response_raw.text)
				output['result'] = response_json
			except:
				print('[E] Could not load JSON')
		else:
			pass
		return output
	
	def get(self, path, params={}):
		url = f'{self.base_url}{path}'
		
		_params = {}
		for param_key in params:
			_params[param_key] = params[param_key]
		
		response_raw = self.session.get(
			url,
			params=_params,
			verify=False,
		)
		output = {
			'success': False,
			'result': '',
			'response': response_raw,
		}
		if response_raw.status_code == 200:
			output['success'] = True
			try:
				response_json = json.loads(response_raw.text)
				output['result'] = response_json
			except:
				print('[E] Could not load JSON')
			
		elif response_raw.status_code == 401:
			self.login()
			response_raw = self.session.get(
				url,
				params=_params,
				verify=False,
			)
			#
			# assume success
			#
			output['success'] = True
			try:
				response_json = json.loads(response_raw.text)
				output['result'] = response_json
			except:
				print('[E] Could not load JSON')
		else:
			pass
		return output
	
	def delete(self, path, params={}):
		url = f'{self.base_url}{path}'
		
		_params = {}
		for param_key in params:
			_params[param_key] = params[param_key]
		
		response_raw = self.session.delete(
			url,
			params=_params,
			verify=False,
		)
		output = {
			'success': False,
			'result': '',
			'response': response_raw,
		}
		if response_raw.status_code == 200:
			output['success'] = True
			try:
				response_json = json.loads(response_raw.text)
				output['result'] = response_json
			except:
				print('[E] Could not load JSON')
			
		elif response_raw.status_code == 401:
			self.login()
			response_raw = self.session.delete(
				url,
				params=_params,
				verify=False,
			)
			#
			# assume success
			#
			output['success'] = True
			try:
				response_json = json.loads(response_raw.text)
				output['result'] = response_json
			except:
				print('[E] Could not load JSON')
		else:
			pass
		return output
	
	# CM or TM Specific
	
	def get_tm(self, feature='', params={}):
		path = f'/mgmt/tm/{feature}'
		output = self.get(path, params=params)
		return output
	
	def get_cm(self, feature='', params={}):
		path = f'/mgmt/cm/{feature}'
		output = self.get(path, params=params)
		return output
	
	def set_tm(self, feature='', j={}, body={}, params={}):
		path = f'/mgmt/tm/{feature}'
		output = self.post(path, j=j, body=body, params=params)
		return output
	
	def set_cm(self, feature='', j={}, body={}, params={}):
		path = f'/mgmt/cm/{feature}'
		output = self.post(path, j=j, body=body, params=params)
		return output
	
	def get_cm_config(self, module, config='current', feature='', params={}):
		# current, working, template
		path = f'/mgmt/cm/{module}/{config}-config/{feature}'
		output = self.get(path, params=params)
		return output
	
	def set_cm_config(self, module, config='working', feature='', j={}, body={}, params={}):
		path = f'/mgmt/cm/{module}/working-config/{feature}'
		output = self.post(path, j=j, body=body, params=params)
		return output
		
	def get_cm_report(self, module, feature='', params={}):
		path = f'/mgmt/cm/{module}/reports/{feature}'
		output = self.get(path, params=params)
		return output
	
	def get_cm_alert_config(self, f=''):
		path = f'/mgmt/cm/shared/event/alert-config'
		params = {
			'$filter': '(displayName eq \'Certificate expiration\')' if not f else f,
		}
		output = self.get(path, params=params)
		return output
	
	# LTM or ADC Specific
	
	def get_ltm_device_group(self, uid=''):
		path = f'/mgmt/shared/resolver/device-groups/{uid}'
		output = self.get(path)
		return output
	
	def get_ltm_feature(self, feature=''):
		path = f'ltm/{feature}'
		output = self.get_cm_config('adc-core', config='working', feature=path)
		return output
	
	def get_adc_device(self, uid=''):
		path = f'/mgmt/shared/resolver/device-groups/cm-adccore-allDevices/devices/{uid}'
		output = self.get(path)
		return output
	
	def _get(self):
		path = 'sys/'
		output = self.get_cm_working_config('adc-core', feature=path)
		return output
	
	def _set(self):
		path = 'sys/'
		output = self.set_cm_working_config('adc-core', feature=path)
		return output
	
	def set_pool_member_status(self, pool_member_link, status='enable'):
		# enable, disable, force-offline
		path = 'adc-core/tasks/self-service'
		body = {
			'name': f'LTMaaS - {pool_member_link}',
			'resourceReference': {
				'link': pool_member_link,
			},
			'operation': status,
		}
		output = self.set_cm(path, j=body)
		return output
	
	def get_adc_ssl_object(self, uid=''):
		path = f'/mgmt/cm/adc-core/tasks/certificate-management/{uid}'
		output = self.get(path)
		return output
	
	def get_adc_ssl_certificate(self, uid=''):
		path = f'sys/file/ssl-cert/{uid}'
		output = self.get_cm_config('adc-core', config='working', feature=path)
		return output
	
	def get_adc_ssl_key(self, uid=''):
		path = f'sys/file/ssl-key/{uid}'
		output = self.get_cm_config('adc-core', config='working', feature=path)
		return output
	
	def get_adc_profile_clientssl(self, uid=''):
		path = f'ltm/profile/client-ssl/{uid}'
		output = self.get_cm_config('adc-core', config='working', feature=path)
		return output
		
	def get_adc_profile_serverssl(self, uid=''):
		path = f'ltm/profile/server-ssl/{uid}'
		output = self.get_cm_config('adc-core', config='working', feature=path)
		return output
	
	def get_shared_config(self, f=''):
		# allContent eq '10.145.195.168*' and kind eq 'cm:adc-core:working-config:ltm:virtual:adcvirtualstate
		path = '/mgmt/shared/index/config'
		params = {
			'$filter': f,
		}
		output = self.get(path, params=params)
		return output
	
	def create_file(self, filename, data):
		path = f'/mgmt/shared/file-transfer/uploads/{filename}'
		payload = {
			'payload': {
				'content': data,
			},
		}
		headers_pre = {
			'Content-Range': f'bytes 0-{len(data)-1}/{len(data)}',
		}
		headers_post = {
			'Content-Range': '',
		}
		self.session.headers.update(headers_pre)
		output = self.post(path, body=data)
		self.session.headers.update(headers_post)
		return output
	
	def create_key(self, filename):
		path = f'/mgmt/cm/adc-core/tasks/certificate-management'
		payload = {
			'filePath': f'/var/config/rest/downloads/{filename}',
			'itemName': filename,
			'itemPartition': 'Common',
			'command': 'ADD_KEY',
		}
		output = self.post(path, j=payload)
		return output
	
	def create_cert(self, filename):
		path = f'/mgmt/cm/adc-core/tasks/certificate-management'
		payload = {
			'filePath': f'/var/config/rest/downloads/{filename}',
			'itemName': filename,
			'itemPartition': 'Common',
			'command': 'ADD_CERT',
		}
		output = self.post(path, j=payload)
		return output
	
	def get_file(self, filename):
		path = f'/mgmt/shared/file-transfer/downloads/{filename}'
		output = self.get(path)
		return output
	
	def delete_file(self, filename):
		path = f'/mgmt/shared/file-transfer/uploads/{filename}'
		output = self.delete(path)
		return output
	
	def _(self):
		return

if __name__ == '__main__':
	b = BigIQ('bigiq')
	r = b.login()
	
	d = b.get_adc_device()
	
	'''
	info = 'smloginmap'
	_params = {
		'$filter': f'allContent eq \'{info}*\' '
	}
	r = b.get_cm_working_config(
		'adc-core',
		feature=f'ltm/virtual',
		params=_params
	)
	'''
	
	print('[I] End')