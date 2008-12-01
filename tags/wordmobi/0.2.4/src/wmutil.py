import re

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def decode_html(line):
    "http://mail.python.org/pipermail/python-list/2006-April/378536.html"
    pat = re.compile(r'&#(\d+);')
    def sub(mo):
        return unichr(int(mo.group(1)))
    return pat.sub(sub, unicode(line))

def parse_iso8601(val):
    "Returns a tupple with (yyyy, mm, dd, hh, mm, ss). Argument is provided by xmlrpc DateTime.value"
    dt,tm= val.split('T')
    tm = tm.split(':')
    return (int(dt[:4]),int(dt[4:6]),int(dt[6:8]),int(tm[0]),int(tm[1]),int(tm[2]))

def utf8_to_unicode(s):
    return unicode(s,'utf-8',errors='ignore')
