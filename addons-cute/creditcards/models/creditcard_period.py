# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CreditCardPeriod(models.Model):
    _name = "creditcard.period"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Kredi Kartı Dönemleri"
    _rec_name = 'name'
    _order = "due_date desc"

    name = fields.Char(string='Dönem Adı', tracking=True)
    note = fields.Text(string='Açıklama', tracking=True)
    active = fields.Boolean(string="Active", default=True)
    creditcard_id = fields.Many2one('creditcard', string='Kredi Kartı')
    belotom_id = fields.Integer(string="Belotom No")
    period_begin = fields.Date(string="Dönem Başı", tracking=True)
    period_end = fields.Date(string="Dönem Sonu", tracking=True)
    due_date = fields.Date(string="Son Ödeme Tarihi", tracking=True)
    limit = fields.Float(string='Kart Limiti', digits='Kart Limiti', tracking=True)














