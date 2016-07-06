import itertools
import logging
import os
import random
import requests
import time

from . import utils


class TryAgain(Exception):
  """Retry an operation at a later time.

  """


class RetryTimeout(Exception):
  """A repeated operation failed to produce a successful result.

  """


def Retry(retries, fn):
  """Attempt to call a function a number of times.

  A function call is considered successful if and when it returns successfully.
  An exception of type :class:`TryAgain` can be thrown to retry again.

  :param retries: Number of attempts
  :param fn: Callback function; use :func:`functools.partial` to pass
    parameters
  :return: Return value of :param:`fn`
  :raises RetryTimeout: When function is not successful within the given number
    of attempts

  """
  for i in itertools.count(1):
    try:
      return fn()

    except TryAgain as err:
      if i >= retries:
        raise RetryTimeout("No result after {} attempts".format(i))

      logging.debug("Retry requested (attempt %s of %s): %s", i, retries, err)
      time.sleep(i)
      continue

  return None


class UrlWaitContext:
  def __init__(self):
    self._timeout = None

  @property
  def timeout(self):
    return self._timeout

  @timeout.setter
  def timeout(self, obj):
    self._timeout = obj

  def before_request(self):
    """Invoked before issuing a request for a URL.

    """

  def check_response(self, resp):
    """Check whether response is acceptible.

    :raises RetryTimeout: Attempt check again at a later time

    """
    try:
      resp.raise_for_status()
    except Exception as err:
      raise TryAgain(str(err))


def wait_for_url(url, timeout, ctx=None, min_delay=5, max_delay=30):
  """Wait for a URL to become available.

  A URL is considered available if :func:`UrlWaitContext.check_response` does
  not raise an exception.

  :param url: String with URL
  :param timeout: Maximum number of seconds for URL to become available
  :param ctx: Context object

  """
  if ctx is None:
    ctx = UrlWaitContext()

  logging.debug("Waiting up to %0.1f seconds for \"%s\" to become available",
      timeout, url)

  delay = max(timeout * 0.01, min_delay)

  ctx.timeout = utils.Timeout(timeout)

  while True:
    ctx.before_request()

    try:
      resp = requests.get(url)
    except Exception as err:
      logging.error("Request error: %s", err)
    else:
      try:
        ctx.check_response(resp)
      except TryAgain as err:
        logging.error("Response check failed at %0.0f elapsed seconds: %s",
            ctx.timeout.elapsed, err)
      else:
        return ctx.timeout.elapsed

    if ctx.timeout.expired:
      raise Exception("Not ready after {:0.0f} seconds".format(ctx.timeout.elapsed))

    delay = min(delay * 1.25, ctx.timeout.remaining, max_delay)

    # Add a small amount of jitter
    delay *= 0.9 + (0.2 * random.random())

    logging.debug("Sleeping %0.1f seconds", delay)
    time.sleep(delay)

# vim: set sw=2 sts=2 et :
