# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE - Sadjidine
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp.tools.translate import _
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class CustomProximasDashboard(models.Model):
    _name = "custom.proximas.dashboard"

    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")

