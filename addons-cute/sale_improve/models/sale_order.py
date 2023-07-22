# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # sale_crm/models/sale_order.py
    opportunity_id = fields.Many2one(
        'crm.lead', string='Opportunity', check_company=True,
        domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('waiting', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('sent', 'Müşteriye Gönderildi'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('reject', 'Reddedildi'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    is_order_line_readonly = fields.Boolean(string='Is Readonly', compute='_compute_is_order_line_readonly')

    @api.depends('state')
    def _compute_is_order_line_readonly(self):
        for line in self:
            if self.env.user.has_group('sales_team.group_sale_manager'):
                line.is_order_line_readonly = line.state not in ['draft', 'waiting', 'approved']
            else:
                line.is_order_line_readonly = line.state not in ['draft', 'waiting']

    @api.model
    def write(self, vals):
        record = super(SaleOrder, self).write(vals)

        for follower in self.message_follower_ids:
            if follower.partner_id.id == self.partner_id.id:
                follower.unlink()

        return record

    def action_draft(self):
        orders = self.filtered(lambda s: s.state not in ['sale', 'done'])
        return orders.write({
            'state': 'draft',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })

    def action_waiting(self):
        orders = self.filtered(lambda s: s.state in ['draft', 'sent'])
        return orders.write({'state': 'waiting'})

    def action_reject(self):
        orders = self.filtered(lambda s: s.state in ['draft', 'waiting'])
        return orders.write({'state': 'reject'})

    def action_approved(self):
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            raise exceptions.UserError("Sadece satış yöneticisi siparişi onaylayabilir.")

        orders = self.filtered(lambda s: s.state in ['waiting'])
        return orders.write({'state': 'approved'})

    def action_sent(self):
        orders = self.filtered(lambda s: s.state in ['approved'])
        return orders.write({'state': 'sent'})

    def action_quotation_sent(self):
        if self.filtered(lambda so: so.state != 'approved'):
            raise UserError(_('Only draft orders can be marked as sent directly.'))
        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)
        self.write({'state': 'sent'})
