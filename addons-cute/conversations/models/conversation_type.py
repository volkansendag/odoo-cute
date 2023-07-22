# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging

_logger = logging.getLogger(__name__)


class ConversationType(models.Model):
    _name = "conversation.type"
    _inherit = ['base', 'mail.thread']
    _description = "Görüşme Türü"
    _order = "id desc"

    name = fields.Char(string='Başlık', required=True, tracking=True)
    note = fields.Text(string='Açıklama')

    belotom_id = fields.Integer(string="Belotom Id")
    belsat_id = fields.Integer(string="Belsat Id")


