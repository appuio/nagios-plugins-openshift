import argparse


class _SelectorArg:
  """Utility to parse label selector from command line arguments.

  """
  def __init__(self):
    self._sel = {}

  def __str__(self):
    return repr(self._sel)

  def append(self, value):
    parts = value.split("=", 1)

    if len(parts) != 2:
      raise argparse.ArgumentTypeError("Must use format KEY=VALUE")

    self._sel[parts[0]] = parts[1]

  def dict(self):
    """Retrieve desired labels and values.

    :return: Dictionary with labels

    """
    return self._sel


def add_label_filter_argument(parser):
  parser.add_argument("-l", "--selector", metavar="NAME=VALUE",
                      default=_SelectorArg(), action="append",
                      help="Selector (label query) to filter on")


class LabelFilter:
  def __init__(self, wanted):
    """Initialize instances of this class.

    :type wanted: iterable
    :param wanted: Iterable with tuples/lists with label name and value

    """
    self._wanted = \
        frozenset("{}:{}".format(key, value)
                  for (key, value) in wanted)

  def want_metric(self, metric):
    """Determine whether a given metric matches wanted labels.

    """
    if not self._wanted:
      return True

    try:
      labels = metric["tags"]["labels"]
    except KeyError:
      return False

    # TODO: Decode labels from metric into individual parts (including undoing
    # escape sequences). The current implementation assumes there being no
    # "special characters".
    return bool(frozenset(labels.split(",")) & self._wanted)

# vim: set sw=2 sts=2 et :
