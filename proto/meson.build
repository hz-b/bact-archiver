# protoc: created required files
protoc = find_program('protoc', required : true)
protobuf = dependency('protobuf', required : true)

cpp_gen = generator(protoc,
  output    : ['@BASENAME@.pb.cc', '@BASENAME@.pb.h'],
  arguments : ['--proto_path=@CURRENT_SOURCE_DIR@', '--cpp_out=@BUILD_DIR@', '@INPUT@']
  )
cpp_generated = cpp_gen.process('epics_event.proto')

# Got generator not to do the job
py_gen2 = custom_target('epics_event_build_py',
    output: ['epics_event_pb2.py'],
    input: 'epics_event.proto',
    command: [
        protoc, '--proto_path=@CURRENT_SOURCE_DIR@', '--python_out=@OUTDIR@', '@INPUT@'
    ],
    install: true,
    install_dir: py.get_install_dir() / 'bact_archiver',  # need to instalall epics_event_pb2.py
    install_tag: 'python-runtime',
)

# cython extension
incdir_numpy = run_command(py,
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()
inc_dir = include_directories(incdir_numpy)

py.extension_module(
  'epics_event',
  'epics_event.pyx',
  cpp_generated,
  install: true,
  include_directories : inc_dir,
  subdir: 'bact_archiver',
  override_options : ['cython_language=cpp'],
  dependencies : protobuf
 )
