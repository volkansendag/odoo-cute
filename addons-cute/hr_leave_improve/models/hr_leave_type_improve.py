# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrLeaveTypeImprove(models.Model):
    _inherit = "hr.leave.type"

    leave_reason = fields.Selection([('yillik', 'Yıllık İzin'), ('mazeret', 'Mazeret İzni')], string='İzin Sebebi', default='yillik')
    paid_leave = fields.Boolean(string='İzin Şekli (Ücretli)', default=True)


