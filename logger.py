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
from time import time 
from urllib.parse import unquote
import os
import json
import syslog

from .flushfilter import FlushFilter

TAG_PREFIX = 'QGIS_LOGGING_TAG_'

class SyslogFilter(QgsServerFilter):
    """ Qgis syslog filter implementation
    """
    def __init__(self, iface):
        syslog.openlog("qgis_mapserver", logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL7)
        super(SyslogFilter, self).__init__(iface)

        # Get global tags
        tags = ((e.partition(TAG_PREFIX)[2],os.environ[e]) for e in os.environ if e.startswith(TAG_PREFIX))
        self._tags = { t:v for (t,v) in tags if t }

    def requestReady(self):
        """ Called when request is ready 
        """
        self.t_start = time()

    def responseComplete(self):
        """ Called when response is ready
        """
        req = self.serverInterface().requestHandler()
        params = req.parameterMap()
        # If we are called with no params
        # There is nothing to log so just return
        if not params:
            return
        # Params are URL encoded 
        params = { k:unquote(v) for (k,v) in params.items() }
        # Send all params throught syslog
        ms = int((time() - self.t_start) * 1000.0)
        if req.exceptionRaised():
            pri = syslog.LOG_ERR
            status = "error"
        else:
            pri = syslog.LOG_NOTICE
            status = "ok"
        params.update(self._tags, 
                RESPONSE_TIME=ms, 
                RESPONSE_STATUS=status)
        log_msg = json.dumps(params)
        syslog.syslog(pri, log_msg)
        


class SyslogClient:

    def __init__(self, iface):
        """ Note that we use a very low priority
            because we want all processing done 
            before going returning syslog infos
        """
        # save reference to the QGIS interface
        self.iface = iface
        QgsMessageLog.logMessage("Initializing Syslog/Flush plugin", 'plugin', Qgis.Info)
        self.iface.registerFilter( SyslogFilter(iface), 1000 ) 
        self.iface.registerFilter( FlushFilter(iface),  10 )

