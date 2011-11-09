Release Procedure
=================

Using git flow::

    VERSION=<new version>
    git flow release start $VERSION
    vi xtraceback/__init__.py
    gc -m "version bump" xtraceback/__init__.py
    git flow release finish $VERSION
    gp --all --tags

Then wait for the ci build and::

    ant publish
