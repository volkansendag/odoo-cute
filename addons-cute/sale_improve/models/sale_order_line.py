# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    date_order = fields.Date(string='Sipariş Tarihi', readonly=True, compute='_compute_sale_order_date', store=True)

    price_reduce_amount = fields.Float(string='İndirim Tutarı *', digits='Product Price')
    discount_type = fields.Boolean(default=True, store=False)

    @api.depends('order_id')
    def _compute_sale_order_date(self):
        for lot in self:
            lot.date_order = lot.order_id.date_order

    @api.onchange('price_reduce_amount')
    def _onchange_price_reduce_amount(self):
        for lot in self:
            if self.discount_type:
                self.discount_type = False
                lot.discount = round(lot.price_reduce_amount / (lot.price_unit * lot.product_uom_qty) * 100, 5)

    @api.onchange('discount')
    def _onchange_discount_manuel(self):
        for lot in self:
            if self.discount_type:
                self.discount_type = False
                lot.price_reduce_amount = lot.price_unit * (lot.discount / 100) * lot.product_uom_qty

    @api.depends('price_unit', 'discount', 'price_reduce_amount')
    def _compute_price_reduce(self):
        for line in self:
            line.price_reduce = (line.price_unit * line.product_uom_qty) - line.price_reduce_amount
