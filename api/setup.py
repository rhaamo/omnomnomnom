from setuptools import setup

setup(
    name="omnomnomnom",
    version="0.1",
    license="AGPL",
    python_requires=">=3.6",
    long_description=open("../README.md").read(),
    url="http://dev.sigpipe.me/dashie/omnomnomnom",
    author="Dashie",
    author_email="dashie@sigpipe.me",
    install_requires=[
        "Flask==1.1.2",
        "SQLAlchemy==1.3.18",
        "SQLAlchemy-Searchable==1.2.0",
        "SQLAlchemy-Utils==0.36.8",
        "Flask-Mail==0.9.1",
        "Flask-Migrate==2.5.3",
        "bcrypt==3.2.0",
        "psycopg2-binary==2.8.5",
        "unidecode==1.1.1",
        "Flask_Babelex==0.9.4",
        "texttable==1.6.1",
        "python-slugify==4.0.1",
        "redis==3.5.3",
        "celery==4.4.7",
        "flask-accept==0.0.6",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest==6.0.1", "pytest-cov==2.10.0"],
)
