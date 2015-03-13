import command
import serial
import threading

class BoxControllerCommand (command.AbstractCommand) :

	_semaphore = threading.BoundedSemaphore(value=1)
	
	def run(self, args, logger=None) :
	
		s = None
		response = None
		
		try :			
			# get a lock
			self._debug('acquiring lock', logger)
			BoxControllerCommand._semaphore.acquire()
			self._debug('opening serial port', logger)
			s = serial.Serial(self.params['port'], 9600)
			s.setDTR(True)
		
			if self.params['mode'] == 'set_analog' :
				for addr in args['addr'].split(',') :		
					command = 'SET {0} {1} {2}'.format(addr, args['value'], args['fade'])		
					response = self._call(s, command, logger)
					if logger :
						logger.log('{0} ==> {1}'.format(command, response))
			elif self.params['mode'] == 'get_status' :
				response = self._call(s, 'STATUS', logger)
			
		except Exception as e :			
			if logger :
				logger.log(str(e))
				
			raise e
			
		finally :
			if s :
				try :
					self._debug('closing serial port', logger)
					s.close()
					self._debug('serial port closed', logger)
				except :
					pass
			self._debug('releasing lock', logger)
			BoxControllerCommand._semaphore.release()
					
					
		return response
				
	def _call(self, socket, command, logger) :
		self._debug('sending to serial port: ' + command, logger)
		socket.write(command + '\n')
		self._debug('reading from serial port', logger)
		response = socket.readline().strip('\n')	
		self._debug('received from serial port: ' + response, logger)
		return response

	def _debug(self, message, logger) :
		if logger :
			logger.log('[DEBUG] ' + message)
			