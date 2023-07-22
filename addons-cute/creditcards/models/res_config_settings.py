# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    db_driver_name = fields.Selection([('SQL Server', 'SQL Server'), ('FreeTDS', 'FreeTDS')], default='SQL Server', string='Veritabanı ODBC Driver', required=True)
    belotom_server = fields.Char("Veritabanı Sunucu Adresi")
    belotom_db = fields.Char("Veritabanı Adı")
    belotom_uid = fields.Char("Kullanıcı Adı")
    belotom_pwd = fields.Char("Parola")

    def set_values(self):
        """employee setting field values"""
        res = super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].set_param('belsis_settings.belotom_server', self.belotom_server)
        self.env['ir.config_parameter'].set_param('belsis_settings.belotom_db', self.belotom_db)
        self.env['ir.config_parameter'].set_param('belsis_settings.belotom_uid', self.belotom_uid)
        self.env['ir.config_parameter'].set_param('belsis_settings.belotom_pwd', self.belotom_pwd)
        self.env['ir.config_parameter'].set_param('belsis_settings.db_driver_name', self.db_driver_name)
        return res

    def get_values(self):
        """employee limit getting field values"""
        res = super(ResConfigSettings, self).get_values()

        _belotom_server = self.env['ir.config_parameter'].sudo().get_param('belsis_settings.belotom_server')
        _belotom_db = self.env['ir.config_parameter'].sudo().get_param('belsis_settings.belotom_db')
        _belotom_uid = self.env['ir.config_parameter'].sudo().get_param('belsis_settings.belotom_uid')
        _belotom_pwd = self.env['ir.config_parameter'].sudo().get_param('belsis_settings.belotom_pwd')
        _db_driver_name = self.env['ir.config_parameter'].sudo().get_param('belsis_settings.db_driver_name')

        res.update(
            db_driver_name=_db_driver_name,
            belotom_server=_belotom_server,
            belotom_db=_belotom_db,
            belotom_uid=_belotom_uid,
            belotom_pwd=_belotom_pwd,
        )
        return res
