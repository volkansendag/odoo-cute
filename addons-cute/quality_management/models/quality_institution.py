# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging

_logger = logging.getLogger(__name__)


class QualityInstitution(models.Model):
    _name = "quality.institution"
    _inherit = ['base', 'mail.thread', 'mail.activity.mixin']
    _description = "Kalite Kuruluşu"
    _order = "name desc"

    name = fields.Char(string='Kurum Adı', required=True, tracking=True)
    note = fields.Text(string='Açıklama')


