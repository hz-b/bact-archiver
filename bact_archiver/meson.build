py_sources = run_command('/bin/sh',
['glob.sh'],
  check : true
).stdout().strip().split('\n')

py.install_sources(
  py_sources,
<<<<<<< HEAD
  # 'epics_event_pb2.py',
=======
  'epics_event_pb2.py',
>>>>>>> cc30f5d ([FIX] included created python file)
  'archiver.cfg',
  pure: false,
  subdir: 'bact_archiver'
)
subdir('proto')
