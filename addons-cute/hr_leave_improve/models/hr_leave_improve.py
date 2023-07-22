# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from pytz import timezone, UTC
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _
import base64


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    request_hour_from = fields.Selection(selection='_get_request_hour_from', string='Hour from')
    request_hour_to = fields.Selection(selection='_get_request_hour_to', string='Hour to')

    @api.model
    def _get_request_hour_to(self):

        selection = [
            ('8.83', '8:50 AM'), ('9', '9:00 AM'),
            ('9.17', '9:10 AM'), ('9.5', '9:30 AM'),
            ('10', '10:00 AM'), ('10.5', '10:30 AM'),
            ('11', '11:00 AM'), ('11.5', '11:30 AM'),
            ('12', '12:00 PM'), ('12.5', '12:30 PM'),
            ('13', '1:00 PM'), ('13.5', '1:30 PM'),
            ('14', '2:00 PM'), ('14.5', '2:30 PM'),
            ('15', '3:00 PM'), ('15.5', '3:30 PM'),
            ('16', '4:00 PM'), ('16.5', '4:30 PM'),
            ('17', '5:00 PM'), ('17.5', '5:30 PM'),
            ('18', '6:00 PM'), ('18.5', '6:30 PM')]

        return selection

    @api.depends('number_of_hours_display')
    def _compute_number_of_hours_text(self):
        # YTI Note: All this because a readonly field takes all the width on edit mode...
        for leave in self:
            leave.number_of_hours_text = '%s%g %s%s' % (
                '' if leave.request_unit_half or leave.request_unit_hours else '(',
                float_round(leave.number_of_hours_display, precision_digits=2),
                _('Hours'),
                '' if leave.request_unit_half or leave.request_unit_hours else ')')

    @api.model
    def _get_request_hour_from(self):

        selection = [
            ('8.5', '8:30 AM'),
            ('9', '9:00 AM'), ('9.5', '9:30 AM'),
            ('10', '10:00 AM'), ('10.5', '10:30 AM'),
            ('11', '11:00 AM'), ('11.5', '11:30 AM'),
            ('12', '12:00 PM'), ('12.5', '12:30 PM'),
            ('13', '1:00 PM'), ('13.5', '1:30 PM'),
            ('14', '2:00 PM'), ('14.5', '2:30 PM'),
            ('15', '3:00 PM'), ('15.5', '3:30 PM'),
            ('16', '4:00 PM'), ('16.5', '4:30 PM'),
            ('17', '5:00 PM'), ('17.5', '5:30 PM'),
            ('18', '6:00 PM')]
        return selection

    def action_approve(self):
        res = super(HolidaysRequest, self)
        res.action_approve()

        self.action_send_email()

    def action_send_email(self):
        if self.holiday_status_id.info_mail:
            self.send_email_with_pdf_attach()

            return True

    def send_email_with_pdf_attach(self):
        repdata = self.env.ref('hr_leave_improve.hr_leave_improve_report')

        report = repdata._render_qweb_pdf([self.id], data={'report_type': 'pdf'})

        data_record = base64.b64encode(report[0])

        ir_values = {
            'name': 'Izin Formu',
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'hr.leave',
        }

        report_attachment = self.env['ir.attachment'].create(ir_values)

        email_template = self.env.ref('hr_leave_improve.hr_leave_improve_belsis_mail_template')

        email_template.attachment_ids = [report_attachment.id]

        email_template.send_mail(self.id)

        email_template.attachment_ids = []
