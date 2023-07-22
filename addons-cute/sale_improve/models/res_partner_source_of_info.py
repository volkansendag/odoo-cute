# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ConversationPlatform(models.Model):
    _name = "res.partner.sourceofinfo"
    _inherit = ['base', 'mail.thread']
    _description = "Bilgi Kaynağı"
    _order = "id desc"

    name = fields.Char(string='Başlık', required=True, tracking=True)
    note = fields.Text(string='Açıklama')


