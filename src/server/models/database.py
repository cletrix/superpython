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
import sys

if "AUTH_DOMAIN" in os.environ.keys():
    from google.appengine.ext import ndb
else:
    from lib.minimock import Mock
    sys.modules['google.appengine.ext'] = Mock('google.appengine.ext')
    ndb = Mock('google.appengine.ext')

NDB = ndb