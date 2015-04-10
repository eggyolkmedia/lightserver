import utils.format
import utils.logger
import xml.etree.ElementTree as ET

class Sequencer :

  consts = {}
  commands = {}
  sequences = {}
  command_classes = {}

  active = True # for multithreaded implementations

  def __init__(self, filename, logger=None) :
    self._parse_definitions(filename)  
    self.logger = logger

  # stops the sequence execution in multithreaded scenarios
  def stop(self) :
    self.active = False

  def close(self) :     
    pass

  def run_sequence(self, sequence, args={}) :

    # check that sequence exists
    if sequence not in self.sequences.keys() :
      raise Exception('\'{seq}\': nonexisting sequence'.format(seq=sequence))

    # check that all args appear
    for arg in self.sequences[sequence]['args'] :
      if arg not in args :
        raise Exception('\'{seq}\': missing argument \'{arg}\''.format(seq=sequence, arg=arg))

    # iterate over actions
    response = None
    for action in self.sequences[sequence]['actions'] :

      # stop the execution if stop() was called (multithreaded implementations)
      if not self.active :
        break

      # parse action args
      arguments = {}
      for k,v in action['args'].iteritems() :
        arguments[k] = v.format(**args)

      # create command class
      command = self._get_command_class(action['command'])
      response = command.run(arguments, self.logger)

    return response

  def _parse_definitions(self, filename) :

    # parse XML
    try :
      xml = ET.parse(filename).getroot()
    except Exception as e :
      raise Exception('definitions xml is invalid: ' + str(e))

    # parse consts
    cs = xml.find('consts')
    if cs==None :
      raise Exception('consts node not found')

    for c in cs.findall('const') :
      self.consts[c.attrib['name']] = c.text

    # parse commands
    cs =  xml.find('commands')
    if cs==None:
      raise Exception('commands node not found')

    for c in cs.findall('command') :
      cmd = {
        'name'  : c.attrib['name'],
        'class' : c.attrib['class'], 
        'args'  : c.attrib['args'].split(',') if 'args' in c.keys() else []
      }
      cmd['params'] = {}
      for p in c.findall('param') :
        cmd['params'][p.attrib['name']] = self._eval(p.text)
      self.commands[cmd['name']] = cmd

    # parse sequences
    cs = xml.find('sequences')
    if cs==None :
      raise Exception('sequences node not found')

    for c in cs.findall('sequence') :
      seq = {
        'name'     : c.attrib['name'],
        'args'    : c.attrib['args'].split(',') if 'args' in c.keys() else [],
        'actions'  : []
      }
      for a in c.findall('action') :
        action = {'command' : a.attrib['command']}
        action['args'] = {}
        for aa in a.findall('arg') :
          action['args'][aa.attrib['name']] = self._eval(aa.text)
        seq['actions'].append(action)
      self.sequences[seq['name']] = seq

    # validation
    for seqname, sequence in self.sequences.iteritems() :
      for action in sequence['actions'] :
        # 1. verify that command exists
        if action['command'] not in self.commands.keys() :
          raise Exception('\'{seq}/{cmd}\': nonexisting command'.format(
            seq=seqname,
            cmd=action['command']
          ))

        # 2. verify that all command args available on the action node
        for arg in self.commands[action['command']]['args'] :
          if arg not in action['args'].keys() :
            raise Exception('\'{seq}/{cmd}\': missing argument \'{arg}\''.format(
              seq=seqname,
              cmd=action['command'],
              arg=arg
            ))

  def _eval(self, text) :
    try :
      return text.format(**self.consts)
    except KeyError as e : # fallback - if not found, return original string (for runtime arg values)
      return text

  def _get_command_class(self, command) :

    module = 'commands.' + self.commands[command]['class']
    classname = self.commands[command]['class'].replace('_', ' ').title().replace(' ', '') + 'Command'

    # class not in cache? create and store
    if command not in self.command_classes.keys() :
      classdef  = getattr(__import__(module, fromlist=[classname]), classname)
      self.command_classes[command] = classdef(self.commands[command]['params'])

    # return from cache
    return self.command_classes[command]
