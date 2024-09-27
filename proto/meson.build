# protoc: created required files
protoc = find_program('protoc', required : true)
protobuf = dependency('protobuf', required : true)

cpp_gen = generator(protoc,
  output    : ['@BASENAME@.pb.cc', '@BASENAME@.pb.h'],
  arguments : ['--proto_path=@CURRENT_SOURCE_DIR@', '--cpp_out=@BUILD_DIR@', '@INPUT@']
  )
py_gen = generator(protoc,
  output    : ['@BASENAME@_pb2.py'],
  arguments : ['--proto_path=@CURRENT_SOURCE_DIR@', '--python_out=@BUILD_DIR@', '@INPUT@']
  )
cpp_generated = cpp_gen.process('epics_event.proto')
py_generated = py_gen.process('epics_event.proto')

py_proc = custom_target('py_proto',
                        command: [ 'cp', '@INPUT@', '@OUTPUT@' ],
                        input : py_generated,
                        output : 'epics_event_pb2.py',
                        build_by_default : true)

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
