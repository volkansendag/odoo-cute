# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging

_logger = logging.getLogger(__name__)

class BelotomResPartner(models.Model):
    _inherit = "res.users"

    belotom_personel_recid = fields.Char(string="Belotom Personel Id")

    def _update_users_from_belotom_personel(self, conn, limit):

        users = self.env['res.users']
        users_list = users.search([
            # ('belotom_personel_recid', '=', False),
            ('active', '=', True)])

        updated = 0

        for usr in users_list:
            adsoyad = usr.partner_id.name.replace(" ", "%")
            sql = f"select * from personel where ad + ' ' + soyad like '%{adsoyad}%' "
            cursor = conn.cursor()

            cursor.execute(sql)

            for i in cursor:
                usr.belotom_personel_recid = i.recid
                users.update(usr)

                updated = updated + 1

        if updated > 0:
            self.env.cr.commit()

    @api.model
    def update_users_from_belotom_personel(self, limit=1000):
        configs = self.env['ir.config_parameter'].sudo()

        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = configs.get_param('belsis_settings.belotom_server')
        belotom_db = configs.get_param('belsis_settings.belotom_db')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1433;"
            conn = pyodbc.connect(connStr)
            self._update_users_from_belotom_personel(conn, limit)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")









