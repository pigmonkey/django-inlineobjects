from setuptools import setup, find_packages

setup(
    name='django-inlineobjects',
    packages=find_packages(),
    version='2.0.3',
    description='A reusable Django application used to insert content objects into other pieces of content.',
    author='Peter Hogg',
    author_email='peter@havenaut.net',
    url='https://github.com/pigmonkey/django-inlineobjects',
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    zip_safe=False,
    install_requires=['beautifulsoup4'],
)
