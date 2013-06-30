# unicode_literals breaks gevent wsgi wrapper
#from __future__ import unicode_literals
#-*- coding: UTF-8 -*-

from gevent import monkey; monkey.patch_all()

import os, sys, re
from requests.compat import urljoin, quote

from datetime import datetime

import bottle
from bottle.ext import sqlalchemy
from bottle import template, request, response

from sqlalchemy import create_engine, or_
from gzip_middleware import GzipMiddleware

import feedparser
import requests

from model import Package, Base, ARCH

__author__ = 'Joerg Thalheim'
__version__ = '0.1'
__license__ = 'MIT'

PACKAGE_FEED="https://www.archlinux.org/feeds/packages/"
AUR_FEED = "https://aur.archlinux.org/rss/"
AUR_RPC_URL = "https://aur.archlinux.org/rpc.php?type=multiinfo"
PACKAGE_API_URL = 'https://www.archlinux.org/packages/{repo}/{arch}/{pkgname}/json'

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

app = bottle.Bottle()
engine = create_engine(DATABASE_URL, echo=True)

plugin = sqlalchemy.Plugin(engine,
                           Base.metadata,
                           keyword='db',
                           create=True,
                           commit=True,
                           use_kwargs=False)
app.install(plugin)

@app.get('/')
def index(db):
    return template('index.tpl')

AVAILABLE_INCLUDES = [
    "name", "version", "description", "license"
    "arch", "category", "repo",
    "arch_url", "url", "last_update",
    "compressed_size", "installed_size",
    "depends", "conflicts", "maintainers"
]
REPOSITORIES = ["core", "testing", "extra", "community", "community-testing", "aur"]

@app.get('/update')
def update(db):
    update_arch_repositories(db)
    update_aur(db)
    return "ok"

@app.get('/feed')
def feed(db):
    # Input sanitation
    feed_link = request.query.get("feed_link", 'project_url')
    if not feed_link in ['project_url', 'package_url']:
        feed_link = 'project_url'
    entry_size = int(request.query.get("entry_size"))
    if not entry_size in [10, 20, 50]:
        entry_size = 5 # punish "hackers"!

    repos = set(request.query.getall("repos")) & set(REPOSITORIES)
    archs = []

    # aur doesn't expose ARCH
    if "aur" in repos:
        archs.append(ARCH.index("unknown"))

    for arch in set(request.query.getall("arch")):
        if arch in ARCH:
            archs.append(ARCH.index(arch))
    user_includes = set(request.query.getall("includes"))
    includes = []
    for include in AVAILABLE_INCLUDES:
        if include in user_includes:
            includes.append(include)

    entries = db.query(Package).order_by(Package.last_update.desc()).\
            filter(Package.repo.in_(repos)).\
            filter(Package.arch.in_(archs)).\
            limit(entry_size).all()
    url = request.url
    description = {
      "title": "Archlinux Packages",
      "subtitle":"",
      "site_url": app.get_url("/"),
      "feed_url": urljoin(url, '/feed'),
      "date_updated": "",
    }
    response.set_header("Content-Type", "application/atom+xml")
    return template('feed.tpl',
            d=description,
            title="",
            entries=entries,
            includes=includes,
            feed_link=feed_link)

@app.route('/static/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root='./static')

def update_aur(db):
    feed = feedparser.parse(AUR_FEED)
    latest_packages = []
    for item in feed['items']:
        (year, mon, mday, hour, m, sec) = item['published_parsed'][:6]
        # time is one hour off on the server
        published = datetime(year, mon, mday, hour + 1 , m, sec)
        latest_packages.append((item['title'], published))
    conditions = []
    for (name, _) in latest_packages:
        conditions.append(Package.name == name)
    cached_packages = db.query(Package).\
        filter(or_(*conditions)).\
        filter(Package.repo == "aur").all()

    pkgs_to_fetch = {}

    for (name, last_update) in latest_packages:
        pkg = None
        for p in cached_packages:
            if p.name == name:
                cached_packages.remove(p)
                pkg = p
                break
        if pkg is None:
            pkg = Package()
            db.add(pkg)
            pkgs_to_fetch[name] = pkg
        # FIXME relying on last_update doesn't work for all packages
        elif pkg.last_update != last_update:
            pkgs_to_fetch[name] = pkg

    if len(pkgs_to_fetch) == 0:
        return

    queries = "&".join("arg[]=%s" % quote(pkg, safe="+") for pkg in pkgs_to_fetch.keys())
    try:
        results = requests.get(AUR_RPC_URL + "&" + queries).json()["results"]
        for json in results:
            pkg = pkgs_to_fetch[json["Name"]]
            pkg.apply_aur_package_info(json)
    except requests.exceptions.RequestException as e:
        print("failed to get information for package '%s': %s" % (name, e))

def update_arch_repositories(db):
    feed = feedparser.parse(PACKAGE_FEED)
    latest_packages = []
    for item in feed['items']:
        (name, version, arch) = item['title'].split()
        repo = item['category'].lower()
        latest_packages.append((name, version, arch, repo))

    conditions = []
    for (name, _, arch, repo) in latest_packages:
        condition = (Package.name == name) & \
                (Package.repo == repo) & \
                (Package.arch == ARCH.index(arch))
        conditions.append(condition)
    cached_packages = db.query(Package).filter(or_(*conditions)).all()

    new_rows = []
    for (name, version, arch, repo) in latest_packages:
        pkg = None
        for p in cached_packages:
            if p.name == name and p.arch == arch and p.repo == repo:
                cached_packages.remove(p)
                pkg = p
        if pkg is None:
            url = PACKAGE_API_URL.format(repo=repo, arch=arch, pkgname=name)
            try:
                json = requests.get(url).json()
                pkg = Package()
                pkg.apply_arch_package_info(json)
                pkg.version = version
                new_rows.append(dict(pkg))
            except requests.exceptions.RequestException as e:
                print("failed to get information for package '%s': %s" % (name, e))
                continue
        elif pkg.version != version:
            url = PACKAGE_API_URL.format(repo=repo, arch=arch, pkgname=name)
            try:
                json = requests.get(url).json()
                pkg.apply_arch_package_info(json)
                pkg.version = version
            except requests.exceptions.RequestException as e:
                print("failed to get information for package '%s': %s" % (name, e))
                continue
    if len(new_rows) > 0:
        db.execute(Package.__table__.insert(), new_rows)

if __name__ == "__main__":
    gzip_app = GzipMiddleware(app, compresslevel=5)
    bottle.run(app=gzip_app,
               server='gevent',
               host=os.environ.get("HOST", "0.0.0.0"),
               port=int(os.environ.get("PORT", 3000)))
