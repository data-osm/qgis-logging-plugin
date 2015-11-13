# -*- coding: utf-8 -*-

def serverClassFactory(serverIface):
    from .syslogd import SyslogClient
    return SyslogClient(serverIface)
