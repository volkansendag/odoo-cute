# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CreditCardBank(models.Model):
    _name = "creditcard.type"
    _description = "Kart Tipi"
    _rec_name = 'title'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    title = fields.Char(string='Adı', required=True, tracking=True)
    note = fields.Text(string='Açıklama')
    active = fields.Boolean(string="Aktif", default=True)
    creditcard_count = fields.Integer(string='Kart Sayısı', compute='_compute_creditcard_count')
    belotom_id = fields.Integer(string="Belotom No")

    def _compute_creditcard_count(self):
        for rec in self:
            creditcard_count = self.env['creditcard'].search_count([('type_id', '=', rec.id)])
            rec.creditcard_count = creditcard_count












