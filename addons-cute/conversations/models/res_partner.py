# -*- coding: utf-8 -*-

from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    conversation_ids = fields.One2many('conversation', 'partner_id', string='Görüşmeler')
    conversation_count = fields.Integer("Görüşme", compute='_compute_conversation_count')

    def _compute_conversation_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        conversation_data = self.env['conversation'].with_context(active_test=False).read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )

        self.conversation_count = 0
        for group in conversation_data:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.conversation_count += group['partner_id_count']
                partner = partner.parent_id

    def action_view_conversation(self):
        '''
        Bu method kisilerin gorusmelerini gostermek icin kullanilir.
        '''
        action = self.env['ir.actions.act_window']._for_xml_id('conversations.action_conversation_views')
        action['context'] = {'active_test': False}
        if self.is_company:
            action['domain'] = [('partner_id.commercial_partner_id.id', '=', self.id)]
        else:
            action['domain'] = [('partner_id.id', '=', self.id)]
        return action
