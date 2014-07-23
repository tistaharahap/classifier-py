from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='textclassifier',
      version='0.1.0',
      description='A classifier for texts and documents',
      long_description=readme(),
      keywords='text document bayes classifier redis machine learning',
      url='https://github.com/tistaharahap/text-classifier',
      author='Batista Harahap',
      author_email='batista@bango29.com',
      license='MIT',
      packages='textclassifier',
      setup_requires=['redis>=2.7.0', 'hiredis>=0.1.0', 'textblob'],
      zip_safe=False)