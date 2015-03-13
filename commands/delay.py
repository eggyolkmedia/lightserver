import time
import command

class DelayCommand (command.AbstractCommand) :

	def run(self, args, logger) :		
		time.sleep(int(args['value'])/1000)


