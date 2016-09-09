import nagiosplugin


class FullSummary(nagiosplugin.Summary):
  """Format check summary with all results.

  The base class only uses the most significant result as determined by result
  status.

  """
  @staticmethod
  def _format(results):
    return ", ".join(sorted(str(i) for i in results))

  def ok(self, results):
    return self._format(results)

  def problem(self, results):
    return self._format(results.most_significant)


# vim: set sw=2 sts=2 et :
