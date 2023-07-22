# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    contact_permission = fields.Selection(
        [('new', 'İletişim İzni Kontrol'), ('allow', 'İletişim İzni Var'), ('disallow', 'İletişim İzni Yok')],
        string="İletişim İzni", required=True, default='new', tracking=True,
        help="Pazarlama amacıyla yapılan iletişimlerde izni olmadığını beyan eden kişiye pazarlama içeriği "
             "göndermenin suç olması sebebiyle; şirket veya şahıs kayıtlarında, iletişim bilgisi kaydedilen "
             "kişinin pazarlama iletişimini kabul edip etmediğine dair bilgi tutulmalıdır.")

    source_of_info = fields.Many2one('res.partner.sourceofinfo', string="Bilgi Kaynağı", tracking=True)

    sale_order_line_ids = fields.Many2many('sale.order.line', string="Sales Orders",
                                           compute='_compute_sale_order_line_ids',
                                           readonly=True)

    @api.depends('sale_order_ids')
    def _compute_sale_order_line_ids(self):
        sale_order_lines = self.env['sale.order.line'].search([('order_partner_id', 'in', self.ids)],
                                                              order="order_id DESC")
        for lot in self:
            lot.sale_order_line_ids = sale_order_lines
