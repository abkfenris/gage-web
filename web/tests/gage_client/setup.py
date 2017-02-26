from setuptools import setup

setup(name='gage-client',
      version='0.1',
      description='API client to send data to gage-web',
      author='Alex Kerney',
      author_email='abkfenris@gmail.com',
      license='MIT',
      packages=['gage_client'],
      install_requires=[
        'requests',
        'itsdangerous',
      ],
      zip_save=False)
