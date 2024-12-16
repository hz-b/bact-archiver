project(
    'purelib-and-platlib',
    'cpp',
    'cython',
    default_options: [
    ],
)

py = import('python').find_installation(pure: false)



# need to build the proto generated files before
# I can build the cython extension
subdir('bact_archiver')
