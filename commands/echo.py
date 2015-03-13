import command

class EchoCommand (command.AbstractCommand) :

	def run(self, args, logger) :
		if logger :
			logger.log(args['message'])
		


