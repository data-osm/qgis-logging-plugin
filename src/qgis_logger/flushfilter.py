# -*- coding: utf-8 -*-
# 
from qgis.core import QgsMessageLog
from qgis.server import QgsServerFilter
import json


def dprint( *args ):
   import sys
   sys.stderr.write( ' '.join(str(a) for a in args)+'\n')
   sys.stderr.flush() 


class FlushFilter(QgsServerFilter):
    """ Qgis filter implementation
    """
    def __init__(self, iface):
        super(FlushFilter, self).__init__(iface)
    
    def requestReady(self):
        """ Called when request is ready 
        """
        pass

    def responseComplete(self):
        """ Called when response is ready
        """
        req = self.serverInterface().requestHandler()
        params = req.parameterMap()
        # If we are called with no params
        # There is nothing to log so just return
        if not params:
            return

        if params.get('SERVICE', '').upper() == 'FLUSH':
            path = params.get('PATH')
            req.clearHeaders()
            req.clearBody()
            req.setHeader('Content-type', 'application/json')
            if path is not None:
                self.serverInterface().removeConfigCacheEntry(path)
                req.appendBody('{ "command":"FLUSH", "path":"%s" }' % path)
            else:
                req.appendBody('{ "command":"FLUSH", "error": "path_missing" }')


