__all__ = [
  "expires", "lastmodified", 
  "prefixurl", "modified", 
  "changequery", "url",
  "profiler",
]

import sys, os, threading, urllib, urlparse
try: import datetime
except ImportError: pass
import rbweb.net, rbweb.utils
import rbweb.webapi as web

def prefixurl(base=''):
    cctx=web.ctx
    url = cctx.path.lstrip('/')
    for i in xrange(url.count('/')): 
        base += '../'
    if not base: 
        base = './'
    return base

def expires(delta):
    if isinstance(delta, (int, long)):
        delta = datetime.timedelta(seconds=delta)
    date_obj = datetime.datetime.utcnow() + delta
    web.header('Expires', rbweb.net.httpdate(date_obj))

def lastmodified(date_obj):
    web.header('Last-Modified', rbweb.net.httpdate(date_obj))

def modified(date=None, etag=None):    
    try:
        from __builtin__ import set
    except ImportError:
        # for python 2.3
        from sets import Set as set
        
    env=web.ctx.env

    n = set([x.strip('" ') for x in env.get('HTTP_IF_NONE_MATCH', '').split(',')])
    m = rbweb.net.parsehttpdate(env.get('HTTP_IF_MODIFIED_SINCE', '').split(';')[0])
    validate = False
    if etag:
        if '*' in n or etag in n:
            validate = True
    if date and m:
        if date-datetime.timedelta(seconds=1) <= m:
            validate = True
    
    if date: lastmodified(date)
    if etag: web.header('ETag', '"' + etag + '"')
    if validate:
        raise web.notmodified()
    else:
        return True

def urlencode(query, doseq=0):
    def convert(value, doseq=False):
        if doseq and isinstance(value, list):
            return [convert(v) for v in value]
        else:
            return rbweb.utils.safestr(value)
        
    query = dict([(k, convert(v, doseq)) for k, v in query.items()])
    return urllib.urlencode(query, doseq=doseq)

def changequery(query=None, **kw):
    if query is None:
        query = web.rawinput(method='get')
    for k, v in kw.iteritems():
        if v is None:
            query.pop(k, None)
        else:
            query[k] = v
    out = web.ctx.path
    if query:
        out += '?' + urlencode(query, doseq=True)
    return out

def url(path=None, doseq=False, **kw):
    if path is None:
        path = web.ctx.path
    if path.startswith("/"):
        out = web.ctx.homepath + path
    else:
        out = path

    if kw:
        out += '?' + urlencode(kw, doseq=doseq)
    
    return out

def profiler(app):
    from utils import profile
    def profile_internal(e, o):
        out, result = profile(app)(e, o)
        return list(out) + ['<pre>' + rbweb.net.websafe(result) + '</pre>']
    return profile_internal

if __name__ == "__main__":
    import doctest
    doctest.testmod()
