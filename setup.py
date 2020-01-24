from setuptools import setup

setup(
    name='addext',
    version='2.0.1',
    url='https://github.com/tw4l/addext',
    author='Tim Walsh',
    author_email='timothyryanwalsh@gmail.com',
    packages=['addext'],
    py_modules=['addext'],
    scripts=['addext/addext.py'],
    install_requires=['inquirer'],
    description='Adds file extensions based on PRONOM ID',
    keywords='extensions identification',
    platforms=['POSIX', 'Windows'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities'
    ],
)
