# unicode_literals breaks gevent wsgi wrapper
#from __future__ import unicode_literals
#-*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from uuid import uuid5, NAMESPACE_OID

from sqlalchemy import Column, Integer, Boolean, String, DateTime, Text
from sqlalchemy.orm import synonym
from sqlalchemy.ext.declarative import declarative_base

PACKAGE_URL = 'https://www.archlinux.org/packages/{repo}/{arch}/{pkgname}/'
AUR_PKG_URL = "https://aur.archlinux.org/packages/{pkgname}/"

Base = declarative_base()

ARCH = ["unknown", "any", "x86_64", "i686"]
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
        if self.maintainers is None: # sometimes packages are without maintainers
            self.maintainers = "-"
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
        keys = []
        for col in self.__table__.columns.keys():
            if col != "id":
                keys.append((col, getattr(self, col)))
        return iter(keys)
    def atom_id(self):
        # TODO refactor me, when deprecating python2
        return uuid5(NAMESPACE_OID, "%s/%s/%s/%s" % (self.repo.encode("utf-8"),
            self.arch.encode("utf-8"),
            self.name.encode("utf-8"),
            self.version.encode("utf-8"))).urn
    def arch_url(self):
        if self.repo == "aur":
            return AUR_PKG_URL.format(pkgname=self.name)
        else:
            return PACKAGE_URL.format(repo=self.repo, arch=self.arch, pkgname=self.name)
