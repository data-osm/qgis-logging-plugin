############################################################################
#    QGIS Server Plugin Filters: Add Output Formats to GetFeature request
#
#    Copyright            : (C) 2016-2019 by 3Liz
#    Email                : info at 3liz dot com
#                                                                         
#   This program is free software; you can redistribute it and/or modify  
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
############################################################################

from qgis.core import Qgis, QgsMessageLog
from qgis.server import QgsServerFilter

import traceback

from pathlib import Path
from time import time

FLUSH_INTERVAL = 3600 * 24


def dlog( message, severity=Qgis.Info ):
    QgsMessageLog.logMessage(message, 'qgis-logger', severity)

# Check every 3.0s
CHECK_INTERVAL=3.0
      

class FlushFilter(QgsServerFilter):
    """ Qgis filter implementation
    """
    def __init__(self, iface):
        super(FlushFilter, self).__init__(iface)
        self._cached = {}
        self._flush = time()

    def get_cached_entry(self, projectpath):
        return self._cached.get(projectpath)

    def clean_up(self, now):
        """
        """
        if now - self._flush > FLUSH_INTERVAL/2:
            # List candidates to deletion before deleting them
            paths = [p for p,(tm,_) in self._cached.items() if now - tm > FLUSH_INTERVAL]
            for p in paths:
                del self._cached[p]
        self._flush = now

    def requestReady(self):
        """ Called when request is ready 
        """
        projectpath = self.serverInterface().configFilePath()
        if not projectpath:
            # Fallback to 'MAP' because of
            # https://github.com/qgis/QGIS/pull/9773
            req = self.serverInterface().requestHandler()
            params = req.parameterMap()
            if params:
                projectpath = params.get('MAP')
            
        if not projectpath:
            # No path, no cache...
            return

        now  = time()
        path = Path(projectpath)
        if projectpath in self._cached:
            tm, timestamp = self._cached[projectpath] 
            if now-tm > CHECK_INTERVAL:
                new_timestamp = path.stat().st_mtime
                if new_timestamp > timestamp:
                    dlog('Updating cache for %s' % projectpath)
                    self.serverInterface().removeConfigCacheEntry(projectpath)
                    self._cached[projectpath] = (now, new_timestamp)
                self.clean_up(now)
        elif path.is_file():
            dlog('Adding %s to cache' % projectpath)
            self._cached[projectpath] = (now, path.stat().st_mtime)

    def responseComplete(self):
        """ Called when response is ready
        """

