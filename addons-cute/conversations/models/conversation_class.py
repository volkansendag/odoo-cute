# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging

_logger = logging.getLogger(__name__)


class ConversationClass(models.Model):
    _name = "conversation.class"
    _inherit = ['base','mail.thread']
    _description = "Görüşme Sınıfı"
    _order = "id desc"

    name = fields.Char(string='Başlık', required=True, tracking=True)
    note = fields.Text(string='Açıklama')

    belotom_id = fields.Integer(string="Belotom Id")
    belsat_id = fields.Integer(string="Belsat Id")


