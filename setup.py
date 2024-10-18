from setuptools import setup

setup(name='sensei',
      version='0.1',
      description='The funniest joke in the world',
      url='https://github.com/senseirobotics/sensei-api',
      author='Sensei Robotics',
      author_email='info@senseirobotics.com',
      license='MIT',
      packages=['sensei'],
      install_requires=[
          'requests',
          'tqdm',
      ],
      scripts=['bin/sensei'],
      zip_safe=False)