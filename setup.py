# -*- coding: utf-8 -*-
from setuptools import setup

# NOTE(sjperkins)
# python poetry overwrites this, this exists
# so that people can easily hack away with
# development installs

packages = \
['packratt', 'packratt.tests']

package_data = \
{'': ['*'], 'packratt': ['conf/*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'pyyaml>=5.3.1,<6.0.0',
 'requests>=2.23.0,<3.0.0']

extras_require = \
{'testing': ['pytest[testing]>=5.4.2,<6.0.0',
             'pytest-flake8[testing]>=1.0.6,<2.0.0']}

entry_points = \
{'console_scripts': ['packratt = packratt.application:run']}

setup_kwargs = {
    'name': 'packratt',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Simon Perkins',
    'author_email': 'simon.perkins@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
