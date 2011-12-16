import time
import hashlib
import datetime as dt

from django.views.decorators.http import condition
from django.conf import settings
from django.http import HttpResponse

class MWT(object):
    """Memoize With Timeout"""
    _caches = {}
    _timeouts = {}

    def __init__(self,timeout=2):
        self.timeout = timeout

    def collect(self):
        """Clear cache of results which have timed out"""
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (time.time() - self._caches[func][key][1]) < self._timeouts[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache

    def __call__(self, f):
        self.cache = self._caches[f] = {}
        self._timeouts[f] = self.timeout

        def func(*args, **kwargs):
            kw = kwargs.items()
            kw.sort()
            key = (args, tuple(kw))
            try:
                v = self.cache[key]
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                v = self.cache[key] = f(*args,**kwargs),time.time()
            return v[0]
        func.func_name = f.func_name

        return func


def cache_and_validate(timeout, hashing=hashlib.md5):
    '''
       Decorator to add caching, with support for ETag and Last-modified
       validation.

       Just give it the time for caching.
    '''
    def transform(f):
        f.cache = dict()
        def get_content(request, *args, **kwargs):
            '''
               Content is kept as

                (last_generation_time, last_modified_time, etag, content)

               inside the f.cache dictionnary
            '''
            key=args+tuple(sorted(kwargs.items()))
            if request.method == 'PURGE' and request.environ.get('REMOTE_ADDR') \
                    in settings.INTERNAL_IPS:
                # purge the cache place
                f.cache.pop(key, None)
            now = dt.datetime.now()
            if key in f.cache:
                date, last_modified, etag, mime_type, old_content = f.cache[key]
                if now - date < dt.timedelta(seconds=timeout):
                    return date, last_modified, etag, mime_type, old_content
                else:
                    content = f(request, *args, **kwargs)
                    if old_content == content.content:
                        data = (now, last_modified, etag, old_content)
                        return data
            else:
                content = f(request, *args, **kwargs)
            if content.status_code == 200:
                content_type = content.get('Content-Type', None)
                data = now, now, hashing(content.content).hexdigest(), content_type, content.content
                f.cache[key] = data
            else:
                data = None, None, None, None, content
            return data
        def get_last_modified(request, *args, **kwargs):
            _, last_modified, _, _, _ = get_content(request, *args, **kwargs)
            return last_modified
        def get_etag(request, *args, **kwargs):
            _, _, etag, _, _ = get_content(request, *args, **kwargs)
            return etag
        @condition(etag_func=get_etag, last_modified_func=get_last_modified)
        def replacement(request, *args, **kwargs):
            _, _, _, content_type, content = get_content(request, *args, **kwargs)
            if isinstance(content, basestring):
                return HttpResponse(content, content_type=content_type)
            else:
                return content
        return replacement
    return transform
