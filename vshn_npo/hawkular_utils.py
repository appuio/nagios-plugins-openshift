
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
