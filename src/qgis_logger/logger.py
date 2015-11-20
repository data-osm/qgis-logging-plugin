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
        # Send all params throught syslog
        ms = int((time() - self.t_start) * 1000.0)
        params.update(RESPONSE_TIME=ms)
        log_msg = json.dumps(params)
        pri = syslog.LOG_ERR if req.exceptionRaised() else syslog.LOG_NOTICE
        syslog.syslog(pri, log_msg)


class SyslogClient:

    def __init__(self, iface):
        """ Note that we use a very low priority
            because we want all processing done 
            before going returning syslog infos
        """
        # save reference to the QGIS interface
        self.iface = iface
        QgsMessageLog.logMessage("Initializing Syslog plugin", 'plugin', QgsMessageLog.INFO)
        self.iface.registerFilter( SyslogFilter(iface), 1000 ) 
