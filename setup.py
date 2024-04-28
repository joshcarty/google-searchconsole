# encoding: utf-8

from setuptools import find_packages, setup


setup(name='searchconsole',
      description='A wrapper for the Google Search Console API.',
      author='Josh Carty',
      author_email='carty.josh@gmail.com',
      version='0.0.3',
      license='MIT',
      packages=find_packages(),
      keywords='data analysis search console google api seo',
      install_requires=[
          'google-api-python-client>=1.7.3',
          'python-dateutil>=2.7.3',
          'google-auth>=1.5.0',
          'google-auth-oauthlib>=0.2.0'
      ],
      test_suite='tests'
      )
