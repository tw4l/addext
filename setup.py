from setuptools import setup

setup(
    name = 'addext',
    version = '1.0.0',
    url = 'https://github.com/timothyryanwalsh/addext',
    author = 'Tim Walsh',
    author_email = 'timothyryanwalsh@gmail.com',
    packages=['addext'],
    package_data={
        'addext': ['pronom.db']
    },
    include_package_data=True,
    py_modules = ['addext'],
    scripts = ['addext/addext.py'],
    install_requires = ['inquirer'],
    description = 'Adds file extensions to files based on their PRONOM identifiers (PUIDs).',
    keywords = 'extensions identification',
    platforms = ['POSIX', 'Windows'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Natural Language :: English', 
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities'
    ],
)