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


## Installation

When using anaconda, make sure you have the google protocol buffer included

```bash
conda install protobuf
```

on native Linux/Debian installations use

```bash
sudo apt install g++ libprotobuf-dev protobuf-compiler python3-protobuf \
                 python3-setuptools python3-wheel cython3 \
                 python3-numpy
```


The standard build sequence is
```bash
python setup.py build_proto_c
python setup.py build
python setup.py install
```

In case the google protocol buffer include files are not found automatically, you can set the include path like
```
export CFLAGS="-I /opt/anaconda3/include"
```
