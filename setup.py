from distutils.core import setup

setup(
    name='webpy',
    version='0.1',
    description='Python Web Framework',
    author='Juan Pablo Caram',
    author_email='jpcaram@siliconcr.com',
    url='http://caram.cl',
    packages=['webpy'],
    requires=['tornado', 'jinja2', 'matplotlib', 'numpy']
)
