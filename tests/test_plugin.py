import logging

import lxml.etree


def test_load_plugins(client):

    client.load_plugins()
    plugin = client.getplugin('qgis_logger')
    assert plugin is not None


def test_cache_filter(client):

    from qgis_logger.flushfilter import FlushFilter

    iface = client.server_interface

    _filter = FlushFilter(iface)
    iface.registerFilter( _filter,  10 )

    # Issue a request
    qs = "?MAP=france_parts.qgs&SERVICE=WMS&REQUEST=GetCapabilities"
    rv = client.get(qs, 'france_parts.qgs')

    if rv.status_code != 200:
        logging.error(lxml.etree.tostring(rv.xml, pretty_print=True))

    assert rv.status_code == 200

    # Test that the project is in cache
    projectpath = client.getprojectpath('france_parts.qgs')
    entry = _filter.get_cached_entry(projectpath)
    assert entry is not None
