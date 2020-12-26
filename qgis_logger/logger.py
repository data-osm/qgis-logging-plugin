__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'

import json
import os
import syslog

from time import time
from urllib.parse import unquote

from qgis.core import Qgis, QgsMessageLog
from qgis.server import QgsServerFilter

from .flushfilter import FlushFilter

TAG_PREFIX = 'QGIS_LOGGING_TAG_'


class SyslogFilter(QgsServerFilter):
    """ Qgis syslog filter implementation
    """
    def __init__(self, iface):
        syslog.openlog("qgis_mapserver", logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL7)
        super(SyslogFilter, self).__init__(iface)

        # Get global tags
        tags = ((e.partition(TAG_PREFIX)[2], os.environ[e]) for e in os.environ if e.startswith(TAG_PREFIX))
        self._tags = {t: v for (t, v) in tags if t}

    def requestReady(self):
        """ Called when request is ready
        """
        self.t_start = time()

    def responseComplete(self):
        """ Called when response is complete
        """
        req = self.serverInterface().requestHandler()
        params = req.parameterMap()
        # If we are called with no params
        # There is nothing to log so just return
        if not params:
            return
        # Params are URL encoded
        params = {k: unquote(v) for (k, v) in params.items()}
        # Send all params throught syslog
        ms = int((time() - self.t_start) * 1000.0)
        if req.exceptionRaised():
            pri = syslog.LOG_ERR
            status = "error"
        else:
            pri = syslog.LOG_NOTICE
            status = "ok"
        params.update(
            self._tags,
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
