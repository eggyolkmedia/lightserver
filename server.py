import sequencer
import threading
import socket
import utils.logger
import xml.etree.ElementTree as ET

class SequencerServer (threading.Thread) :
  
  def __init__(self, port, filename, logfile=None) :
    threading.Thread.__init__(self, name='SERVER')    
    self.active = True    
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.port = port    
    
    self.socket.bind(('0.0.0.0', self.port))
    self.socket.listen(1)
    
    self.logger = utils.logger.Logger(filename=logfile, console=True if not logfile else False)
    self.filename = filename
    
  def run(self) :
    self.logger.log('server started')
    while self.active :
      socket = None
      try :
        self.logger.log('listening')
        socket, addr = self.socket.accept()
        self.logger.log('accepted connection')
        if not self.active :                    
          response = 'terminated'
          
        else :
          request = socket.recv(1024)
          response = self._handle_request(request)
          
        socket.sendall(response)        
        
      except Exception as e :
         self.logger.log(str(e), e)
      
      finally :
        try :
          socket.close()
        except :
          pass
    
    # todo wait for threads or kill them
    
    self.logger.log('server done')
         
  def remove(self, thread) :
    pass
  
  def stop(self) :
    self.active = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', self.port)) # should stop the self.socket.listen() loop - no message should be sent
    s.close()
    self.logger.log('server terminated')
    
    # todo attempt to stop running threads
    
  def _handle_request(self, request) :
    xml = ET.fromstring(request)
    
    if 'name' not in xml.attrib.keys() :
      return self._compose_response(0, 'missing \'name\' attribute')
    sequence = xml.attrib['name']
      
    if 'immediate' not in xml.attrib.keys() :
      return self._compose_response(0, 'missing \'immediate\' attribute')
    immediate = int(xml.attrib['immediate'])
      
    args = {}
    for a in xml.findall('arg') :
      args[a.attrib['name']] = a.text
      
    self.logger.log('calling sequence \'{}\' with {}'.format(sequence, str(args) if len(args) else 'no args'))
    
    # either run() or start(), depending on the immediate flag
    response = None
    try :
      if immediate :
        seq = sequencer.Sequencer(self.filename, self.logger)
        response = self._compose_response(1, seq.run_sequence(sequence, args))
        seq.close()
      
      else :
        seq = SequencerThread(self, sequence, args)
        seq.start()
        response = self._compose_response(1, 'started sequence \'{}\' with {}'.format(sequence, str(args) if len(args) else 'no args'))
      
    except Exception as e :
      self.logger.log(str(e), e)
      response = self._compose_response(0, str(e))
      
    return response
      
  
  def _compose_response(self, ok, message) :
    return '<response ok="{}">{}</response>'.format(ok, message if message else '')
  
  
  
class SequencerThread (threading.Thread):
  
  def __init__(self, server, sequence, args) :
    threading.Thread.__init__(self)
    self.sequencer = sequencer.Sequencer(server.filename, server.logger) # throws exception if definitions are not parsed correctly
    self.sequence = sequence
    self.server = server
    self.args = args
  
  def run(self) :
    try :
      self.sequencer.run_sequence(self.sequence, self.args) # might throw an exception, will be logged via the sequencer
    except Exception as e :
      self.server.logger.log('failed running sequence {}: {}'.format(self.sequence, str(e)), e)
    finally :
      try :
        self.sequencer.close()
      except Exception as e:
        self.server.logger.log('failed closing sequencer: ' + str(e), e)
    
    # remove from active threads (not implemented yet)
    self.server.remove(self)

  def stop(self) :
    self.sequencer.stop() # stops the running sequence - need to call self.join for a clean exit
    
    
