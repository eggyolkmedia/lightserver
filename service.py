import server
import sys

server = server.SequencerServer(int(sys.argv[1]), 'config/definitions.xml', sys.argv[2] if len(sys.argv)>2 else None)
server.start()
raw_input() # break when something is typed in the console
server.stop()
server.join()
