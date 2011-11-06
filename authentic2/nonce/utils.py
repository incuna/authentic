import os.path
import datetime as dt
from calendar import timegm
import tempfile
import glob
import errno

from django.conf import settings

import models

__all__ = ('accept_nonce', 'cleanup_nonces')

STORAGE_MODEL = 'model'
STORAGE_FILESYSTEM = 'fs:'

def compute_not_on_or_after(now, not_on_or_after):
    try: # first try integer semantic
        seconds = int(not_on_or_after)
        not_on_or_after = now + dt.timedelta(seconds=seconds)
    except ValueError:
        try: # try timedelta semantic
            not_on_or_after = now + not_on_or_after
        except TypeError: # datetime semantic
            pass
    return not_on_or_after

# For the nonce filesystem storage the policy is to catch any OSerror when
# errno == ENOENT and to handle this case gracefully as there can be many race
# condition errors.  But any other OSError is problematic and should be
# reported to the administrator by mail and so we let it unroll the stack

def unlink_if_exists(path):
    try:
        os.unlink(path)
    except OSError, e:
        if e.errno != errno.ENOENT:
            raise

def accept_nonce_file_storage(path, now, value, context=None,
        not_on_or_after=None):
    '''
       Use a directory as a storage for nonce-context values. The last
       modification time is used to store the expiration timestamp.
    '''
    now = dt.datetime.now()
    filename = '%s_%s' % (value.encode('base64'), context.encode('base64'))
    file_path = os.path.join(path, filename)
    # test if the file exists
    try:
        stat = os.stat(file_path)
    except OSError, e:
        # test if it doesnt exit or if another error happened
        if e.errno != errno.ENOENT:
            raise
    else:
        # if it exists, test if it is too old
        if stat.st_mtime < timegm(now.utctimetuple()):
            # if it is too old delete it
            unlink_if_exists(file_path)
        else:
            # not too old, the nonce is unacceptable
            return False

    temp_file = tempfile.NamedTemporaryFile(dir=path, delete=False)
    temp_file.close()

    if not_on_or_after:
        not_on_or_after = compute_not_on_or_after(now, not_on_or_after)
        mtime = timegm(not_on_or_after.utctimetuple())
    else:
        mtime = 0x7FFF
    try:
        os.utime(temp_file.name, (mtime, mtime))
    except OSError:
        unlink_if_exists(temp_file.name)
        raise
    try:
        os.link(temp_file.name, file_path)
    except OSError, e:
        if e.eerno == errno.EEXIST:
            unlink_if_exists(temp_file.name)
        return False
    return True

def accept_nonce_model(now, value, context=None, not_on_or_after=None):
    if not_on_or_after:
        not_on_or_after = compute_not_on_or_after(now, not_on_or_after)
    nonce, created = models.Nonce.objects.get_or_create(value=value,
            context=context)
    if created or (nonce.not_on_or_after and nonce.not_on_or_after < now):
        nonce.not_on_or_after = not_on_or_after
        nonce.save()
        return True
    else:
        return False

def cleanup_nonces_file_storage(dir_path, now):
    for nonce_path in glob.iglob(os.path.join(dir_path, '*')):
        now_time = timegm(now.utctimetuple())
        try:
            stat = os.stat(nonce_path)
        except OSError, e:
            if e.errno == errno.ENOENT:
                continue
            raise
        if stat.st_mtime < now_time:
            try:
                os.unlink(nonce_path)
            except OSError, e:
                if e.errno == errno.ENOENT:
                    continue
                raise

def cleanup_nonces(now=None):
    '''
       Cleanup stored nonce whose timestamp has expired, i.e.
       nonce.not_on_or_after < now.

       :param now:
           a datetime value to define what is the current time, if None is
           given, datetime.now() is used. It can be used for unit testing.
    '''
    now = now or dt.datetime.now()
    mode = getattr(settings, 'NONCE_STORAGE', STORAGE_MODEL)
    # the model always exists, so we always clean it
    models.Nonce.objects.cleanup(now)
    if mode == STORAGE_MODEL:
        pass
    if mode.startswith(STORAGE_FILESYSTEM):
        dir_path = mode[len(STORAGE_FILESYSTEM):]
        return cleanup_nonces_file_storage(dir_path, now)
    else:
        raise ValueError('Invalid NONCE_STORAGE setting: %r' % mode)

def accept_nonce(value, context=None, not_on_or_after=None, now=None):
    '''
       Verify that the given nonce value has not already been seen in the
       context. If not, remember it for ever or until not_on_or_after if is
       not None.

       Depending on the backend storage used there can be limitation on the
       acceptable length for the value and the context. For example the model
       storage backend limits the length of those strings to 256 bytes.

       :param value:
           a string representing a nonce value.
       :param context:
           a string giving context to the nonce value
       :param not_on_or_after:
           an integer, a datetime.timedelta or datetime.datetime value. If not
           none it is used to compute the expiration time for remembering this
           nonce value.  If an integer is given it is interpreted as relative
           number of seconds since now, if a timedelta object is given it is
           used as an offset from now, and if a datetime is given it is used
           as an absolute value for the expiration time.
       :param now:
           a datetime value to define what is the current time, if None is
           given, datetime.now() is used. It can be used for unit testing.
       :returns:
           a boolean, if True the nonce has never been seen before, or it
           expired since the last time seen, otherwise the nonce has already
           been seen and is invalid.
    '''
    now = now or dt.datetime.now()
    mode = getattr(settings, 'NONCE_STORAGE', STORAGE_MODEL)
    if mode == STORAGE_MODEL:
        return accept_nonce_model(now, value, context=context,
                not_on_or_after=not_on_or_after)
    elif mode.startswith(STORAGE_FILESYSTEM):
        dir_path = mode[len(STORAGE_FILESYSTEM):]
        return accept_nonce_file_storage(dir_path, now, value,
                context=context, not_on_or_after=not_on_or_after)
    else:
        raise ValueError('Invalid NONCE_STORAGE setting: %r' % mode)
