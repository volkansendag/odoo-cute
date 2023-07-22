# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderTemp(models.Model):
    _name = "sale.order.temp"
    _inherit = ['base']
    _description = "Eski Satış Kayıtları"

    name = fields.Char(string='Sipariş Numarası', required=True)
    order_date = fields.Date(string="Sipariş Tarihi", help='Sipariş tarihidir.', required=True,
                             default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string='Müşteri', required=True)
    user_id = fields.Many2one('res.users', string='Satış Temsilcisi')

    musteri_ili = fields.Char(string='Müşteri İli', readonly=True)
    musteri_adi = fields.Char(string='Müşteri Adı', readonly=True)
    temsilci_soyadi = fields.Char(string='Temsilci Soyadı', readonly=True)

    amount_untaxed = fields.Monetary(string='Vergisiz Tutar', currency_field='company_currency')
    amount_tax = fields.Monetary(string='Vergi Toplamı', currency_field='company_currency')
    amount_total = fields.Monetary(string='Toplam Tutar', currency_field='company_currency')
    currency_rate = fields.Float(string="Döviz Kuru", digits=(12, 6), group_operator='avg')
    amount_total_usd = fields.Monetary(string='Toplam Tutar USD', currency_field='usd_currency',
                                       compute='_compute_amount_total_usd', store=True, readonly=True)

    company_currency = fields.Many2one("res.currency", string='Currency', compute="_compute_company_currency",
                                       readonly=True)
    usd_currency = fields.Many2one("res.currency", string='USD Currency', compute="_compute_usd_currency",
                                   readonly=True)

    def _compute_company_currency(self):
        for lead in self:
            lead.company_currency = self.env.company.currency_id

    def _compute_usd_currency(self):
        for lead in self:
            lead.usd_currency = self.env['res.currency'].search([('name', '=', 'USD')])

    @api.depends('amount_total', 'currency_rate')
    def _compute_amount_total_usd(self):
        for sale in self:
            sale.amount_total_usd = sale.amount_total / sale.currency_rate

