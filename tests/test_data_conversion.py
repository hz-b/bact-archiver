from bact_archiver.utils import convert_data_time
import numpy as np


def test_convert_date_time():
    import datetime
    import pytz

    now = datetime.datetime(2023, 9, 12, 9, 42, 45)
    a_day = datetime.timedelta(seconds=24 * 60 * 60)

    start = now - 2 * a_day
    # every 10 minutes
    step = a_day / 24 / 6
    points = [start + step * i for i in range(10)]
    year_start = datetime.datetime(start.year, month=1, day=1)

    seconds = [int((p - year_start).total_seconds()) for p in points]
    nsecs = [v * 10 + 100 for v in range(len(seconds))]
    print(points)
    dt = convert_data_time([start.year] * len(seconds), seconds, nsecs)

    # need to add points their TimeZone: UTC
    time_deltas = [t_p - p.replace(tzinfo=pytz.utc) for p, t_p in zip(points, dt)]

    for dt, t_nsec in zip(time_deltas, nsecs):
        assert dt == np.timedelta64(t_nsec, "ns")
