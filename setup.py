#!/usr/bin/python
"""Upload videos to Youtube with automatic split."""

from youtube_upload import VERSION
from distutils.core import setup
import platform

setup_kwargs = dict(
    name="youtube-upload",
    version=VERSION,
    description="Upload videos to Youtube with automatic split",
    author="Arnau Sanchez",
    author_email="tokland@gmail.com",
    url="http://code.google.com/p/youtube-upload/",
    packages=[  
        "youtube_upload/",
    ],
    scripts=[
      "bin/youtube-upload",
	  ],
    license="GNU Public License v3.0",
    long_description=" ".join(__doc__.strip().splitlines()),
#    data_files=[
#        ('share/pysheng',
#            ('pysheng/main.glade',)),
#    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)

setup(**setup_kwargs)
