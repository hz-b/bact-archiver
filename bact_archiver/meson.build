py_sources = run_command('/bin/sh',
['glob.sh'],
  check : true
).stdout().strip().split('\n')

py.install_sources(
  py_sources,
  'archiver.cfg',
  pure: false,
  subdir: 'bact_archiver'
)
