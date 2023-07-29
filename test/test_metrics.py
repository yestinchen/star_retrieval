from vsimsearch.metrics import Metrics


def test_metrics():
  metrics = Metrics()
  metrics.start_timer('test')

  for x in range(10):
    metrics.add_entry('table', x=x, y=x**2)

  metrics.end_timer('test')

  metrics.print()


if __name__ == '__main__':
  test_metrics()