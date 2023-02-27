# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class HrEmployeImprove(models.Model):
    _inherit = "hr.employee"

    register_no = fields.Char(string='Sicil No')
