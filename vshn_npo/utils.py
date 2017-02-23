import contextlib
import io
import time
import logging
import random
import re
import sys

from . import constants


def validate_fqdn(fqdn):
  if not re.match(r"^[-.a-zA-Z0-9]+\.[-a-zA-Z0-9]{2,}$", fqdn):
    raise Exception("Unacceptable FQDN \"{}\"".format(fqdn))


class Timeout:
  def __init__(self, duration):
    self._duration = duration
    self.reset()

  def reset(self):
    self._start = time.monotonic()

  @property
  def duration(self):
    return self._duration

  @property
  def elapsed(self):
    """Get number of seconds until now.

    """
    return time.monotonic() - self._start

  @property
  def remaining(self):
    """Get number of remaining seconds.

    """
    return self._duration - self.elapsed

  @property
  def expired(self):
    """Determine whether timeout has expired.

    """
    return self.remaining < 0


class Delayer:
  def __init__(self, initial, max_):
    self._delay = initial
    self._max = max_

  def sleep(self, remaining):
    delay = max(1, min(self._delay * 1.25, remaining, self._max))

    # Add a small amount of jitter
    delay *= 0.9 + (0.2 * random.random())

    self._delay = delay

    logging.debug("Sleeping %0.1f seconds (%0.1f seconds remaining)", delay, remaining)

    time.sleep(delay)


class _Reporter:
  def __init__(self):
    self._exit_code = constants.STATE_UNKNOWN
    self._output = None
    self._metrics = None

  @property
  def exit_code(self):
    return self._exit_code

  @property
  def exit_code_text(self):
    fallback = constants.STATE_TEXT[constants.STATE_UNKNOWN]

    return constants.STATE_TEXT.get(self._exit_code, fallback)

  @property
  def output(self):
    return self._output

  @property
  def metrics(self):
    return self._metrics

  def exit(self, code, output, metrics=None):
    self._exit_code = code
    self._output = output
    self._metrics = metrics

    sys.exit(self._exit_code)


def _iter_any(value):
  if isinstance(value, (list, tuple)):
    return list(value)
  else:
    return [value]


@contextlib.contextmanager
def NagiosOutputFile(nagios_output):
  logging.basicConfig(level=logging.NOTSET,
                      format="%(asctime)s %(message)s")

  if nagios_output is None:
    fh = sys.stdout
  else:
    fh = open(nagios_output, "w")

  ctx = _Reporter()

  try:
    try:
      yield ctx.exit
    except Exception as err:
      logging.exception("Exception caught")
      ctx.exit(constants.STATE_CRITICAL, str(err))
  finally:
    buf = io.StringIO()
    buf.write(ctx.exit_code_text)
    buf.write(" ")
    buf.write(", ".join(str(i) for i in _iter_any(ctx.output)))
    if ctx.metrics:
      buf.write(" | ")
      buf.write(" ".join(str(i) for i in _iter_any(ctx.metrics)))

    logging.info("%s", buf.getvalue())

    fh.write(buf.getvalue())
    fh.write("\n")
    fh.flush()


def add_verbose_argument(parser):
  parser.add_argument("-v", "--verbose", action="count", default=0,
                      help="Increase output verbosity")


def setup_basic_logging(verbose):
  if verbose > 1:
    level = logging.NOTSET
  elif verbose:
    level = logging.INFO
  else:
    level = logging.CRITICAL

  logging.basicConfig(level=level)


# vim: set sw=2 sts=2 et :
