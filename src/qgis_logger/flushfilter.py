# -*- coding: utf-8 -*-
# 
from qgis.core import QgsMessageLog
from qgis.server import QgsServerFilter
import json
import os
import hashlib

from time import time


FLUSH_INTERVAL = 3600 * 24


def md5( path ):
  try:
    content = open(path).read()
    if isinstance(content, unicode):
        content = content.encode('utf-8')
    return hashlib.md5(content).hexdigest() 
  except Exception as e:
    QgsMessageLog.logMessage('ERROR: '+str(e), 'plugin', QgsMessageLog.ERROR)
    raise 
      

def dlog( message ):
    QgsMessageLog.logMessage(message, 'plugin', QgsMessageLog.WARNING)


class FlushFilter(QgsServerFilter):
    """ Qgis filter implementation
    """
    def __init__(self, iface):
        super(FlushFilter, self).__init__(iface)
        self._cached = {}
        self._flush = time()

    def clean_up(self, now):
        """
        """
        if now - self._flush > FLUSH_INTERVAL/2:
            for path in self._cached:
                tm, _ = self._cached[path]
                if now - tm > FLUSH_INTERVAL:
                    del self._cached[path]
        self._flush = now

    def requestReady(self):
        """ Called when request is ready 
        """
        req = self.serverInterface().requestHandler()
        params = req.parameterMap()
        if params:
            now  = time()
            path = params.get('MAP')
            if path and path in self._cached:
                tm, digest = self._cached[path] 
                if now-tm > 15.0:
                    new_digest = md5(path)
                    if new_digest != digest:
                        QgsMessageLog.logMessage('Flushing cache entry: {}'.format(path), 'plugin', QgsMessageLog.WARNING)
                        self.serverInterface().removeProjectCacheEntry(path)
                    self._cached[path] = (now, new_digest)
                    self.clean_up(now)
            elif os.path.exists(path):
                self._cached[path] = (now, md5(path))


    def responseComplete(self):
        """ Called when response is ready
        """

