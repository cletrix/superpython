#! /usr/bin/env python
# -*- coding: UTF8 -*-
# Este arquivo é parte do programa SuperPython
# Copyright 2013-2015 Carlo Oliveira <carlo@nce.ufrj.br>,
# `Labase <http://labase.selfip.org/>`__; `GPL <http://is.gd/3Udt>`__.
#
# SuperPython é um software livre; você pode redistribuí-lo e/ou
# modificá-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 2 da
# Licença.
#
# Este programa é distribuído na esperança de que possa ser útil,
# mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO
# a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, veja em <http://www.gnu.org/licenses/>


"""Google HDB storage.

.. moduleauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

"""
__author__ = 'carlo'
# Imports the NDB data modeling API
import os
from uuid import uuid1
import database as dbs

DEFAULT_PROJECTS = "DEFAULT_PROJECTS"
DEFAULT_PROJECT_NAMES = "JardimBotanico SuperPlataforma SuperPython MuseuGeo"
OLDNA = "granito basalto pomes calcario marmore arenito" \
        " calcita_laranja agua_marinha amazonita hematita quartzo_rosa turmalina" \
        " citrino pirita silex ametista cristal quartzo-verde" \
        " seixo dolomita fluorita aragonita calcita onix".split()
NAMES = "granito arenito" \
        " calcita_laranja agua_marinha amazonita quartzo_rosa turmalina" \
        " citrino pirita silex ametista cristal quartzo-verde" \
        " fluorita onix" \
        " feldspato jaspe agata sodalita alabastro".split()


class Program(dbs.NDB.Expando):
    """A main model for representing all projects."""
    name = dbs.NDB.StringProperty(indexed=True)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.put()
        return instance

    @classmethod
    def nget(cls, query):
        return query.fetch()[0] if query.fetch() else None


class Project(dbs.NDB.Expando):
    """Sub model for representing an project."""
    program = dbs.NDB.KeyProperty(kind=Program)
    name = dbs.NDB.StringProperty(indexed=True)
    persons = dbs.NDB.TextProperty(indexed=False)
    populated = dbs.NDB.BooleanProperty(default=False)
    sessions = dbs.NDB.JsonProperty(default={})

    def updatesession(self, person):
        # self.sessions = set(self.sessions).add(person)
        self.sessions[person] = True
        self.put()

    def removesession(self, person):
        # self.sessions = set(self.sessions).remove(person)
        self.sessions[person] = False
        print("removesession", person, self.sessions)
        self.put()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.put()
        return instance

    @classmethod
    def nget(cls, name):
        query = cls.query(cls.name == name).fetch()
        return query and query[0]

    def islogged(self, person):
        return person in self.sessions and self.sessions[person]


class Person(dbs.NDB.Expando):
    """Sub model for representing an author."""
    project = dbs.NDB.KeyProperty(kind=Project)
    name = dbs.NDB.StringProperty(indexed=True)
    lastsession = dbs.NDB.KeyProperty(indexed=False)
    lastcode = dbs.NDB.KeyProperty(indexed=False)

    def updatesession(self, session):
        self.lastsession = session
        self.put()

    def updatecode(self, code):
        self.lastcode = code
        self.put()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.put()
        return instance

    @classmethod
    def nget(cls, name):
        query = cls.query(cls.name == name).fetch()
        return query and query[0]

    @classmethod
    def obtain(cls, name):
        return Person.nget(name=name) or Person.create(name=name)


class Code(dbs.NDB.Model):
    """A sub model for representing an individual Question entry."""
    person = dbs.NDB.KeyProperty(kind=Person)
    name = dbs.NDB.StringProperty(indexed=True)
    text = dbs.NDB.TextProperty(indexed=False)

    def set_text(self, value):
        self.text = value
        self.put()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.put()
        return instance

    @classmethod
    def nget(cls, name):
        query = cls.query(cls.name == name).fetch()
        return query and query[0]

    @classmethod
    def obtain(cls, person, name, text):
        print("codeobtain", dict(person=person, name=name, text=text))
        person = Person.nget(person)
        print(dict(person=person.key, name=name, text=text))
        code = Code.nget(name=name)
        if code:
            code.set_text(text)
            code.put()
        else:
            code = Code.create(person=person.key, name=name, text=text)
        person.updatecode(code.key)
        return code


class Error(dbs.NDB.Model):
    """A main model for representing an individual Question entry."""
    code = dbs.NDB.KeyProperty(kind=Code)
    message = dbs.NDB.TextProperty(indexed=False)
    value = dbs.NDB.IntegerProperty(indexed=False)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.put()
        return instance


class Session(dbs.NDB.Expando):
    """A main model for representing a user interactive session."""
    _session = None
    project = dbs.NDB.KeyProperty(kind=Project)
    person = dbs.NDB.KeyProperty(kind=Person)
    code = dbs.NDB.KeyProperty(kind=Code)
    name = dbs.NDB.StringProperty(indexed=True)
    modified_date = dbs.NDB.DateTimeProperty(auto_now=True)

    @classmethod
    def nget(cls, name):
        query = cls.query(cls.name == name).fetch()
        return query and query[0]

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.put()
        return instance

    @classmethod
    def load(cls, name):
        path = name.split("/")
        if Person.nget(path[0]) and "__init__" in path[1]:
            return "#"
        code = Code.nget(name=name)
        return code.text

    @classmethod
    def save(cls, **kwargs):
        code = Code.obtain(**kwargs)
        return code

    @classmethod
    def getlogged(cls, project):
        return Project.nget(project).sessions

    @classmethod
    def islogged(cls, project, person):
        project = Project.nget(project)
        return project.islogged(person)

    @classmethod
    def logout(cls, project, person):
        project = Project.nget(project)
        project.removesession(person)

    @classmethod
    def login(cls, project, person):
        print("project, person", project, person)
        sessionname = uuid1().hex
        project = Project.nget(project)
        project.updatesession(person)
        person = Person.nget(person)
        print("project, person", project, person)
        cursession = cls.create(project=project.key, person=person.key, name=sessionname)
        lastsession = person.lastsession or cursession.key
        person.updatesession(cursession.key)
        return cursession, lastsession

    @classmethod
    def lastcode(cls, lastsession):
        session = lastsession.get()
        person = session.person.get()
        lastcode = person.lastcode
        if lastcode:
            code = lastcode.get()
            name = code.name if code else "nono"
            text = code.text if code else "# empty"
        else:
            name = "nono"
            text = "# empty"

        print("lastcode", person.name, person.lastsession, name, text)
        code = (name, text) if lastcode else ("%s/main.py" % session.person.get().name, "# main")
        return code

    @classmethod
    def _populate_codes(cls, session, persons):
        prj = session.project.get()  # Project.kget(key=session.project)
        if prj.populated:
            return prj.questions
        oquestions = [
            Code.create(name=key, text=value) for key, value in persons
            ]
        print(oquestions)
        prj.populated = True
        prj.questions = oquestions
        prj.put()
        return oquestions

    @classmethod
    def init_db_(cls, persons=NAMES):

        if "AUTH_DOMAIN" not in os.environ.keys():
            return

        prj = Project.nget(name="superpython")
        if not prj:
            prj = Project.create(name="superpython")
        # persons = ["projeto%d" % d for d in range(20)]
        ses = Session.create(name=uuid1().hex, project=prj.key)
        Session._populate_persons(prj, ses, persons)

    @classmethod
    def _populate_persons(cls, project, session, persons):
        prj = session.project.get()  # Project.kget(key=session.project)
        if prj.populated:
            return prj.persons
        new_persons = [
            # Person.create(project=project.key, name=key, lastsession=session.key) for key in persons
            Person.create(project=project.key, name=key, lastsession=None) for key in persons
            ]
        print(new_persons)
        prj.sessions = {person: False for person in persons}
        prj.populated = True
        #  prj.persons = new_persons
        prj.put()
        return new_persons

Session.init_db_()
DB = Session