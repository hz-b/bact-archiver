from typing import Sequence

import dateutil
import pandas as pd

def convert_data_time(years: Sequence, secs: Sequence, nsecs: Sequence) -> pd.DatetimeIndex:
    """convert time given in years, secs and nsecs to DatetimeIndex
    Todo:
        use the function in the archiver
    """
    df = pd.DataFrame(
        {"year": years, "month": 1, "day": 1, "second": secs, "ns": nsecs}
    )
    dt = pd.to_datetime(df, utc=True)
    dt = pd.DatetimeIndex(dt, name="datetime").tz_convert(dateutil.tz.tzlocal())
    return dt
