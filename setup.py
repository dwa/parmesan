from setuptools import setup

requirements = ['pandas', 'click']

setup(
    name='parmesan',
    version='0.0.1',
    description="Reads Qlik QVD files (using qvdreader) into Pandas DataFrames",
    author="David Wallin",
    author_email='parmesan@datawrangler.ninja',
    url='https://github.com/dwa/parmesan',
    packages=['parmesan'],
    # entry_points={
    #     'console_scripts': [
    #         'script-name=parmesan:cli'
    #     ]
    # },
    include_package_data=True,
    install_requires=requirements,
    keywords='parmesan',
#    classifiers=[
#        'Programming Language :: Python :: 3.7',
#    ]
)

## Local Variables: ***
## mode:python ***
## coding: utf-8 ***
## End: ***
