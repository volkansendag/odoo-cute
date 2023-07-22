# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging

_logger = logging.getLogger(__name__)


class QualityDocs(models.Model):
    _name = "quality.docs"
    _inherit = ['base', 'mail.thread', 'mail.activity.mixin']
    _description = "Kalite Belgeleri"
    _order = "id desc"

    name = fields.Char(string='Belge Adı', required=True, tracking=True)
    reference = fields.Char(string='Belge No', required=True, tracking=True)
    institution_id = fields.Many2one('quality.institution', string="Belgeyi Veren Kurum", required=True, tracking=True)
    issue_date = fields.Date(string='Veriliş Tarihi', required=True, tracking=True)
    next_issue_date = fields.Date(string='Sonraki Denetleme Tarihi', tracking=True)
    validity_date = fields.Date(string='Geçerlilik Tarihi', tracking=True)
    duration = fields.Integer(string="Süresi (yıl)", tracking=True)
    note = fields.Text(string='Açıklama')

