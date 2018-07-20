from setuptools import setup

setup(name='gtk_modules',
      version='0.1',
      description='GTK modules to use in other applications',
      url='',
      author='Henrik Egemose',
      author_email='hes1990@gmail.com',
      license='MIT',
      packages=['gtk_modules'],
      install_requires=[
          'numpy',
      ],
      zip_safe=False)
