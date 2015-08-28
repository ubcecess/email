__all__ = ['get_existing_forwarders']

from bs4 import BeautifulSoup


def _get_forwarder(tr):
    tds = list(tr.find_all("td"))
    try:
        if not all([
            tds[0]["class"] == ["truncate", "nobrd-left"],
            tds[2]["class"] == ["truncate"],
        ]):
            return None
    except (KeyError, IndexError):
        return None

    return tds[0].text, tds[2].text


def _get_forwarders(b):
    for tr in b.find_all("tr"):
        forwarder_entry = _get_forwarder(tr)
        if forwarder_entry:
            yield forwarder_entry


def get_existing_forwarders(fn):
    """Given path to HTML page with forwarders, scrape and return

    Backstory: CPanel auth is fucked and I don't want to deal with it
    You must log in and download the source of the expanded page
    i.e., "https://secure152.sgcpanel.com:2083/cpsess{your_session_token}/frontend/Crystal/mail/fwds.html?api2_paginate_start=1&page=1&skip=-1&api2_sort_column=&api2_sort_reverse=0&itemsperpage=500&searchregex=" and save it as forwarders.html

    :type fn: str
    """
    with open(fn) as f:
        source = f.read()
    b = BeautifulSoup(source, "html.parser")
    existing_forwarders = list(_get_forwarders(b))
    return existing_forwarders
