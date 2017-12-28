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
          'google-api-python-client==1.6.4',
          'python-dateutil==2.6.1',
          'google-auth==1.2.1',
          'google-auth-oauthlib==0.2.0',
          'google-auth-httplib2==0.0.3'
      ],
      test_suite='tests'
      )