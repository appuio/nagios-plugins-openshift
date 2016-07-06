import base64
import contextlib
import functools
import json
import logging
import subprocess
import tempfile
import time
import uuid

from . import retry


class ProjectNamer:
  def __init__(self, prefix):
    if not prefix:
      raise ValueError("Prefix must be set")

    if "-" in prefix:
      raise ValueError("Prefix may not contain dashes (\"-\")")

    self._prefix = prefix

  @property
  def prefix(self):
    return self._prefix

  def make_name(self):
    """Generate a new, usually unique name.

    """
    # UUIDs are for all intents and purposes guaranteed to be unique
    suffix = (base64.b32encode(uuid.uuid4().bytes).decode("UTF-8").
        rstrip("=").lower())

    return "{}-{}-{}".format(self._prefix, int(time.time()), suffix)

  @staticmethod
  def parse(name):
    """Split a generated name into its parts.

    :returns: None if name has invalid format or a tuple with the name prefix
      and timestamp

    """
    parts = name.split("-", 2)

    if len(parts) > 1:
      try:
        return (parts[0], int(parts[1]))
      except (TypeError, ValueError):
        pass

    return None


@contextlib.contextmanager
def TemporaryConfig(cfgfile):
  """Write a temporary copy of the input configuration.

  The oc binary will write to the configuration when creating projects. It's
  better to direct those writes to a temporary copy as to not affect other
  users of the same input configuration file.

  """
  # Use a directory so that we can close the config file again
  with tempfile.TemporaryDirectory(prefix="os-e2e-") as tmpdir:
    path = tempfile.mktemp(dir=tmpdir, prefix="cfg", suffix="")

    with open(path, "w") as fh:
      content = open(cfgfile, "r").read()
      fh.write(content)
      logging.info("Configuration:\n%s", content)

    yield path


class Client:
  def __init__(self, binary, cfgfile):
    """Initialize an instance of this class.

    :param binary: Path to "oc" binary
    :param cfgfile: Path to configuration file; file will be modified

    """
    self._binary = binary
    self._cfgfile = cfgfile
    self._ns = "default"

  @property
  def namespace(self):
    return self._ns

  @namespace.setter
  def namespace(self, value):
    logging.info("Using namespace \"%s\"", value)
    self._ns = value

  def _make_base_cmd(self):
    return [
        self._binary,
        "--config={}".format(self._cfgfile),
        "--namespace={}".format(self._ns),
        ]

  def run(self, args):
    cmd = self._make_base_cmd()
    cmd.extend(args)
    logging.debug("%r", cmd)
    subprocess.check_call(cmd)

  def capture_output(self, args):
    cmd = self._make_base_cmd()
    cmd.extend(args)
    logging.debug("%r", cmd)
    return subprocess.check_output(cmd)

  def capture_json(self, args):
    return json.loads(self.capture_output(args).decode("UTF-8"))


def create_project(client, namer):
  """Create a project with a random name.

  :param client: An instance of :class:`Client`
  :param namer: An instance of :class:`ProjectNamer`

  """
  def inner(client, namer):
    project_name = namer.make_name()

    try:
      client.run(["new-project",
        "--display-name=End-to-end {}".format(time.ctime()),
        project_name,
        ])
    except subprocess.CalledProcessError as err:
      raise retry.TryAgain(str(err))

    return project_name

  # Retry a couple of times in case the name is already taken
  return retry.Retry(3, functools.partial(inner, client, namer))


def delete_project(client, name):
  """Delete a project.

  """
  client.run(["delete",
    # Remove everything
    "--cascade=true",

    # In case someone else is faster
    "--ignore-not-found=true",

    "project",
    name,
    ])


def cleanup_projects(client, namer, named_max_age, max_age):
  """Remove old projects.

  :param namer: An instance of :class:`ProjectNamer`
  :param named_max_age: Remove projects older than this amount of seconds
    if their name matches the prefix of :param:`namer`.
  :param max_age: Remove any project older than this amount of seconds.

  """
  logging.debug(("Removing any project older than %0.0f seconds or"
                 " %0.0f seconds if the name prefix is \"%s\""),
                max_age, named_max_age, namer.prefix)

  data = client.capture_json(["get", "--output=json", "projects"])

  now = time.time()

  for i in data["items"]:
    name = i["metadata"]["name"]

    parts = namer.parse(name)

    if parts is None:
      # Unrecognized prefix or invalid timestamp
      prefix = None
      ts = 0
    else:
      (prefix, ts) = parts

    if ts < (now - (named_max_age if prefix == namer.prefix else max_age)):
      logging.info("Cleaning up project \"%s\" from %s", name, time.ctime(ts))
      delete_project(client, name)

# vim: set sw=2 sts=2 et :
