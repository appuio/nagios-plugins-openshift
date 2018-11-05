import itertools
import logging
import requests
import time
import urllib.parse
import collections
from email.utils import parsedate_tz, mktime_tz

from . import utils


# Retry request if one of these status codes was received
_RETRY_STATUS_CODES = frozenset([
  requests.codes.internal_server_error,
  requests.codes.bad_gateway,
  requests.codes.service_unavailable,
  requests.codes.gateway_timeout,
  requests.codes.insufficient_storage,
  requests.codes.bandwidth_limit_exceeded,
  ])


def idquote(text):
  return urllib.parse.quote(text, "")


def _format_tags(tags):
  return ','.join("{}:{}".format(key, val) for (key, val) in tags.items())



class Response(collections.namedtuple("Response", [
  "data",
  "server_time",
  ])):
  @classmethod
  def from_request(cls, req):
    if req.status_code == requests.codes.no_content:
      data = None
    else:
      data = req.json()

    raw_date = req.headers.get("Date", None)

    if raw_date:
      # See https://stackoverflow.com/a/26435566
      timestamp = mktime_tz(parsedate_tz(raw_date))
    else:
      timestamp = None

    return cls(data=data, server_time=timestamp)


class HawkularClient(object):
  """A simplistic client for the REST API provided by Hawkular.

  """
  def __init__(self, endpoint=None, tenant=None):
    self._endpoint = endpoint
    self._tenant = tenant
    self._token = None
    self._timeout = None
    self._retries = 1
    self._session = requests.Session()

  @property
  def endpoint(self):
    return self._endpoint

  @endpoint.setter
  def endpoint(self, value):
    self._endpoint = value

  @property
  def tenant(self):
    return self._tenant

  @tenant.setter
  def tenant(self, value):
    self._tenant = value

  @property
  def token(self):
    return self._token

  @token.setter
  def token(self, value):
    self._token = value

  @property
  def timeout(self):
    return self._timeout

  @timeout.setter
  def timeout(self, value):
    self._timeout = value

  @property
  def retries(self):
    return self._retries

  @retries.setter
  def retries(self, value):
    self._retries = value

  def get(self, path, params=None, tags=None):
    """Retrieve data behind given path.

    :param path: string relative to API endpoint
    :param params: None or dict with request parameters
    :param tags: None or dict with request tags

    """
    if self._tenant is None:
      raise Exception("Tenant was not set")

    url = "{}/{}".format(self._endpoint.rstrip("/"), path.lstrip("/"))

    headers = {
        "Hawkular-Tenant": self._tenant,
        }

    if self._token:
      headers["Authorization"] = "Bearer {}".format(self._token)

    if params is None:
      params = {}

    if tags:
      params["tags"] = _format_tags(tags)

    for attempt in itertools.count(1):
      if attempt > 1:
        delay = (attempt - 1) ** 1.1
        logging.debug("Sleeping %0.1f seconds before trying again", delay)
        time.sleep(delay)

      try:
        req = self._session.get(url, headers=headers, params=params, timeout=self._timeout)
      except requests.exceptions.Timeout as err:
        if attempt < self._retries:
          logging.debug("Connection timed out: %s", err)
          continue
        raise

      # Important: Only certain verbs are idempotent in HTTP, one of them being
      # GET. That must be taken into consideration should this code ever be
      # extended for other verbs.
      if req.status_code in _RETRY_STATUS_CODES and attempt < self._retries:
        logging.debug("Request failed with status code %s", req.status_code)
        continue

      # All other issues are fatal
      req.raise_for_status()

      return Response.from_request(req)

    # This should never be reached
    raise Exception("Request failed after %s attempts", self._retries)


def setup_argument_parser(parser):
  """Add common arguments to an argument parser.

  :param parser: An instance of :class:`argparse.ArgumentParser`

  """
  utils.add_token_arguments(parser)

  group = parser.add_argument_group(title="API client")
  group.add_argument("--endpoint", required=True, metavar="URL",
                     help="API endpoint")
  group.add_argument("--tenant", default="_system", metavar="NAME",
                     help="Hawkular tenant")
  group.add_argument("--timeout", type=int, default=10, metavar="SEC",
                     help="Request timeout in seconds")
  group.add_argument("--query-retries", type=int, default=3, metavar="N",
                     help="Number of retries for GET queries")


def make_client(args):
  """Instantiate Hawkular client based on parsed arguments.

  :param args: An instance of :class:`argparse.Namespace` as returned by
    :func:`argparse.ArgumentParser.parse_args` and related functions

  """
  client = HawkularClient(args.endpoint, args.tenant)
  client.token = utils.extract_token_argument(args)
  client.timeout = args.timeout
  client.retries = args.query_retries
  return client

# vim: set sw=2 sts=2 et :
