import os, sys, re
from urllib.parse import urljoin, quote
from datetime import datetime, timedelta
from uuid import uuid5, NAMESPACE_OID

import bottle
from bottle.ext import sqlalchemy
from bottle import template, request

from sqlalchemy import create_engine, Column, Integer, Boolean, String, DateTime, Text, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import synonym

import feedparser
import requests

__author__ = 'Jörg Thalheim'
__version__ = '0.1'
__license__ = 'MIT'

PACKAGE_FEED="https://www.archlinux.org/feeds/packages/"
AUR_FEED = "https://aur.archlinux.org/rss/"
AUR_PKG_URL = "https://aur.archlinux.org/packages/{pkgname}/"
AUR_RPC_URL = "https://aur.archlinux.org/rpc.php?type=multiinfo"
PACKAGE_URL = 'https://www.archlinux.org/packages/{repo}/{arch}/{pkgname}/'
PACKAGE_API_URL = 'https://www.archlinux.org/packages/{repo}/{arch}/{pkgname}/json'

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

app = bottle.Bottle()

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)

plugin = sqlalchemy.Plugin(engine,
                           Base.metadata,
                           keyword='db',
                           create=True,
                           commit=True,
                           use_kwargs=False
                           )
app.install(plugin)

ARCH = ["unknown", "any", "x86_64", "i686"]
REPOSITORIES = ["core", "testing", "extra", "community", "community-testing", "aur"]
CATEGORIES = ["unknown", "daemons", "devel", "editors", "emulators", "games", "gnome", "i18n",
              "kde", "lib", "modules", "multimedia", "network", "office", "science",
              "system", "x11", "xfce", "kernels"]

# <option value="2">daemons</option>
# <option value="3">devel</option>
# <option value="4">editors</option>
# <option value="5">emulators</option>
# <option value="6">games</option>
# <option value="7">gnome</option>
# <option value="8">i18n</option>
# <option value="9">kde</option>
# <option value="10">lib</option>
# <option value="11">modules</option>
# <option value="12">multimedia</option>
# <option value="13">network</option>
# <option value="14">office</option>
# <option value="15">science</option>
# <option value="16">system</option>
# <option value="17">x11</option>
# <option value="18">xfce</option>
# <option value="19">kernels</option>

def parse_time(dt_str):
    dt,  _,  us= dt_str.partition(".")
    dt= datetime.strptime(dt,  "%Y-%m-%dT%H:%M:%S")
    us= int(us.rstrip("Z"), 10)
    return dt + timedelta(microseconds=us)

def formate_file_size(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num,  x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def humanize(word):
    return word.replace("_"," ").capitalize()

class Package(Base):
    __tablename__ = 'packages'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    version = Column(String, nullable=False)
    _arch = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    license = Column(String, nullable=False)
    depends = Column(String)
    conflicts = Column(String)
    maintainers = Column(String, nullable=False)
    last_update = Column(DateTime, index=True)
    repo = Column(String, nullable=False)

    # Respository specific
    installed_size = Column(Integer)
    compressed_size = Column(Integer)

    # AUR specific
    votes = Column(Integer)
    _category = Column(Integer)
    out_of_date = Column(Boolean)

    @property
    def arch(self):
        return ARCH[self._arch];
    @arch.setter
    def arch(self, value):
        self._arch = ARCH.index(value)
    arch = synonym('_arch',  descriptor=arch)

    @property
    def category(self):
        return categories[self._category - 1];
    @category.setter
    def category(self, value):
        value = int(value)
        if (value >= 2 and value <= CATEGORIES.count):
            self._category = value
        else:
            self._category = 1
    category = synonym('_category', descriptor=category)
    def apply_aur_package_info(self, data):
        self.arch = "unknown"
        self.name = data["Name"]
        self.description = data["Description"]
        self._category = data["CategoryID"]
        self.url = data["URL"]
        self.license = data["License"]
        self.version = data["Version"]
        self.last_update = datetime.utcfromtimestamp(data["LastModified"])
        self.maintainers = data["Maintainer"]
        self.votes = data["NumVotes"]
        self.out_of_date = data["OutOfDate"] == "1"
        self.repo = "aur"
    def apply_arch_package_info(self, data):
        self.arch = data['arch']
        self.compressed_size = data['compressed_size']
        self.conflicts = ", ".join(data['conflicts'])
        self.depends = ", ".join(data['depends'])
        self.description = data['pkgdesc']
        self.installed_size = data['installed_size']
        self.name = data['pkgname']
        self.last_update = parse_time(data['last_update'])
        self.license = ", ".join(data['licenses'])
        self.maintainers = ", ".join(data['maintainers'])
        self.repo = data['repo']
        self.url = data['url']
        self.version = data['pkgver']
    def to_feed_item(self, includes):
        item = []
        for include in includes:
            if include in self.__dict__:
                value = getattr(self, include)
                if value is None:
                    continue
                if include == "compressed_size" or include == "installed_size":
                    value = formate_file_size(value)
                if include == "Last update":
                    value = value.strftime("%y-%m-%d %H:%M UTC")
                item.append((humanize(include), value))
            if include == "arch_url":
                item.append(("Package Url", self.arch_url()))
        return item
    def __iter__(self):
        return iter([(col, getattr(self, col)) for col in self.__table__.columns.keys()])
    def atom_id(self):
        return uuid5(NAMESPACE_OID,"%s/%s/%s/%s" % (self.repo, self.arch, self.name, self.version)).urn
    def arch_url(self):
        if self.repo == "aur":
            return AUR_PKG_URL.format(pkgname=self.name)
        else:
            return PACKAGE_URL.format(repo=self.repo, arch=self.arch, pkgname=self.name)

@app.get('/')
def index(db):
    return template('index.tpl')

AVAIBLE_INCLUDES = [
    "name", "version", "description", "license"
    "arch", "category", "repo",
    "arch_url", "url", "last_update",
    "compressed_size", "installed_size",
    "depends", "conflicts", "maintainers"
    ]

@app.get('/update')
def update(db):
    update_arch_repositories(db)
    update_aur(db)
    return "ok"

@app.get('/feed')
def feed(db):
    # Input validation
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
    for include in AVAIBLE_INCLUDES:
        if include in user_includes:
            includes.append(include)

    entries = db.query(Package).order_by(Package.last_update.desc()).\
            filter(Package.repo.in_(repos)).\
            filter(Package.arch.in_(archs)).\
            limit(50)
    url = request.url
    description = {
      "title": "Archlinux Packages",
      "subtitle":"",
      "site_url": app.get_url("/"),
      "feed_url": urljoin(url, '/feed'),
      "date_updated": "",
    }
    return template('feed.tpl', d=description, title="", entries=entries, includes=includes)

def update_aur(db):
    feed = feedparser.parse(AUR_FEED)
    latest_packages = []
    for item in feed['items']:
        latest_packages.append((item['title'], item['published_parsed']))
    conditions = []
    for (name, _) in latest_packages:
        conditions.append(Package.name == name)
    cached_packages = db.query(Package).\
        filter(or_(*conditions)).\
        filter(Package.repo == "aur").all()

    new_rows = []
    pkgs_to_update = []

    for (name, last_update) in latest_packages:
        pkg = None
        for p in cached_packages:
            if p.name == name and p.last_update == last_update:
                cached_packages.remove(p)
                pkg = p
                break
        if pkg is None or pkg.last_update != last_update:
            pkgs_to_update.append(name)

    queries = "&".join("arg[]=%s" % quote(pkg, safe="+") for pkg in pkgs_to_update)
    try:
        results = requests.get(AUR_RPC_URL + "&" + queries).json()["results"]
        for json in results:
            pkg = Package()
            pkg.apply_aur_package_info(json)
            new_rows.append(dict(pkg))
    except requests.exceptions.RequestException as e:
        print("failed to get information for package '%s': %s" % (name, e))
    if len(new_rows) > 0:
        db.execute(Package.__table__.insert(), new_rows)

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
    app.run(server='gunicorn', host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", 3000)))