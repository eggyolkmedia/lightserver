import command
import requests

class LifxControllerCommand (command.AbstractCommand) :

  # TODO NONBLOCKING HTTP REQ
  def run(self, args, logger=None) :
    group = args['group']
    state = args['state']
    fade = args['fade']

    token = self.params['auth_token']

    self._debug('setting {} {}'.format(group, state), logger)
  
    headers = {
      "Authorization": "Bearer %s" % token,  
    }

    payload = {
      "power": state,
      "duration": fade
    }

    response = requests.put('https://api.lifx.com/v1/lights/group:{}/state'.format(group), data=payload, headers=headers)
    self._debug(response.content, logger)
    

  def _debug(self, message, logger) :
    if logger :
      logger.log('[DEBUG] ' + message)
