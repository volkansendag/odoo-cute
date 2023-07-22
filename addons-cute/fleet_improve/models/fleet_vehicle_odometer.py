# -*- coding: utf-8 -*-
import pytz
from odoo import api, fields, models, _


class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    # override
    value = fields.Float(string='Bitiş Km', group_operator="max")
    # override
    driver_id = fields.Many2one(related="vehicle_id.driver_id", string="Sürücü (Zimmet)", readonly=True)

    used_driver_id = fields.Many2one('res.partner', required=True, string="Sürücü", domain=[('is_company', '=', False)])
    begin_value = fields.Float('Başlangıç Km', required=True, group_operator="min")
    used_value = fields.Float('Kullanım Km')
    begin_time = fields.Datetime('Başlangıç Zamanı', required=True, default=lambda self: fields.Datetime.now())
    end_time = fields.Datetime('Bitiş Zamanı', required=True, default=lambda self: fields.Datetime.now())
    description = fields.Char(string='Açıklama')
    customer_id = fields.Many2one('res.partner', string='İlgili Müşteri')
    private_usage = fields.Boolean(string="Özel Kullanım", default=False)
    private_usage_km = fields.Float(string="Özel Kullanım KM", default=0)

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            max_value = max(self.env['fleet.vehicle.odometer']
                            .search([('vehicle_id', '=', self.vehicle_id.id)])
                            .mapped('value'))
            self.begin_value = max_value
            self.value = max_value

    @api.onchange('private_usage', 'used_value')
    def _onchange_private_usage_km(self):
        for model in self:
            if model.private_usage:
                self.private_usage_km = model.used_value

    @api.onchange('value', 'begin_value')
    def _onchange_value_begin_value(self):
        for model in self:
            if model.value and model.begin_value:
                self.used_value = model.value - model.begin_value

    @api.onchange('begin_time')
    def _compute_begin_time(self):
        for model in self:
            if model.begin_time:
                local_tz = pytz.timezone(self.env.user.tz or 'UTC')
                local_datetime = pytz.utc.localize(model.begin_time).astimezone(local_tz)
                user_date = local_datetime.date()
                self.date = user_date
