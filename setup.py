from setuptools import setup, find_packages

setup(
    name='beliveat',
    version='0.0',
    description = 'Open source platform for citizen journalists.',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Pylons',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    author='James Arthur',
    author_email='username: thruflo, domain: gmail.com',
    url = 'http://github.com/Actualise/belive.at',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires = [
        'alembic',
        'assetgen', 
        'coverage',
        'fabric',
        'formencode', 
        'gunicorn',
        'mock',
        'nose',
        'psycopg2', 
        'pyDNS', 
        'pyramid', 
        'pyramid_assetgen', 
        'pyramid_basemodel', 
        'pyramid_beaker', 
        'pyramid_debugtoolbar', 
        'pyramid_simpleauth', 
        'pyramid_simpleform', 
        'pyramid_twitterauth',
        'pyramid_tm', 
        'pyramid_weblayer', 
        'python-dateutil', 
        'python-postmark', 
        'setuptools-git', 
        'transaction', 
        'waitress', 
        'zope.sqlalchemy',
        'SQLAlchemy',
        'WebTest'
    ],
    entry_points = """\
        [setuptools.file_finders]
        ls = setuptools_git:gitlsfiles
        [paste.app_factory]
        main = beliveat:main
    """
)
