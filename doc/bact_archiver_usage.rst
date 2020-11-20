Usage
=====

A typical usage scenario is given below

.. code:: python

    from <your-local-bact-archiver-package> import default as default_archiver
    import datetime

    t0 = datetime.datetime(2020, 11, 20, 7, 40)
    t1 = datetime.datetime(2020, 11, 20, 7, 50)

    pvname = 'TOPUPCC:rdCur'
    df = default_archiver.getData(pvname, t0=t0, t1=t1)


if help is required, please address it to the mailing list.
Examples are very welcomed!
