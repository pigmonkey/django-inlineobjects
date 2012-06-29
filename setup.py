from setuptools import setup, find_packages

setup(
    name = 'django-inlines',
    version = '0.2',
    description = 'A reusable Django application used to insert content objects into other pieces of content.',
    long_description = open('README.md').read(),
    url = 'https://github.com/pigmonkey/django-inlines',
    author = 'Pig Monkey',
    author_email = 'pm@pig-monkey.com',

    packages = find_packages(),
    include_package_data = True,
    zip_safe=False,
)
