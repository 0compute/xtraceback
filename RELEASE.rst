Release Procedure
=================

Using git flow::

    VERSION=<new version>
    git flow release start $VERSION
    vi xtraceback/__init__.py
    git commit -m "version bump" xtraceback/__init__.py
    git flow release finish $VERSION
    git push --all

Then wait for the ci build on master and::

    git push --tags
    tox -e docs
    ./setup.py sdist register upload upload_sphinx
