import commands

class AbstractCommand :
	
	def __init__(self, params) :
		self.params = params

	def run(self, args, logger=None) :
		raise Exception('abstract')