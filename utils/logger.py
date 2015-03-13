import utils.format


class Logger :
	console = False
	file = None
	
	def __init__(self, filename=None, console=False) :
		self.console = console
		if filename :
			self.file = open(filename, 'a', 1)
	
	def log(self, message, exception=None) :		
		logmsg = utils.format.logmessage(message, exception)
		
		# output to console
		if self.console :
			print logmsg
			
		# output to file
		if self.file :
			try :
				self.file.write(logmsg + '\n')
			except :
				pass
				
	def close(self) :
		if file :
			try :
				file.close()
			except :
				pass