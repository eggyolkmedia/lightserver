import time as t
import traceback

def time() :
	return t.strftime('%Y-%m-%d %H:%M:%S')
	
def logmessage(message, exception=None) :
	ts = '[' + time() + '] '
	logmsg = ts + message
	if exception : # append exception with indentation
		tb = traceback.format_exc()
		logmsg = logmsg + '\n' + '\n'.join(map(lambda s: ' '*len(ts) + s, tb.split('\n')))
	return logmsg