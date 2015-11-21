# -*- coding: utf-8 -*-
# 
from qgis.core import QgsMessageLog
from qgis.server import QgsServerFilter
from time import time 
import json
import syslog

class SyslogFilter(QgsServerFilter):
    """ Qgis syslog filter implementation
    """
    def __init__(self, iface):
        syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL7)
        super(SyslogFilter, self).__init__(iface)
    
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
        # Send all params throught syslog
        ms = int((time() - self.t_start) * 1000.0)
        if req.exceptionRaised():
            pri = syslog.LOG_ERR
            status = "error"
        else:
            pri = syslog.LOG_NOTICE
            status = "ok"
        params.update(RESPONSE_TIME=ms, RESPONSE_STATUS=status)
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
        QgsMessageLog.logMessage("Initializing Syslog plugin", 'plugin', QgsMessageLog.WARNING)
        self.iface.registerFilter( SyslogFilter(iface), 1000 ) 
