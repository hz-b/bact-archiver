# bact-archiver: access to the archiver appliance

## Usage


Typically download bact-archiver-local.
Rename it and configure it as described in the configuration section of this
package documentation.

Then you can use it by

```python3

from <your-local-bact-archiver-package> import default as default_archiver
import datetime

t0 = datetime.datetime(2020, 11, 20, 7, 40)
t1 = datetime.datetime(2020, 11, 20, 7, 50)

pvname = 'TOPUPCC:rdCur'
df = default_archiver.getData(pvname, t0=t0, t1=t1)
```
