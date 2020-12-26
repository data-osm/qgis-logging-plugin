
def serverClassFactory(serverIface):
    from .logger import SyslogClient
    return SyslogClient(serverIface)
