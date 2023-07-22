# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime
import pyodbc
import logging

_logger = logging.getLogger(__name__)


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    belotom_node_id = fields.Integer(string="Belotom Id")

    def _update_hr_leave_allocation_from_belotom(self, conn, holiday_status_id):

        leave = self.env["hr.leave.allocation"]

        sql = f"select * from isciIzinTahakkuk"
        cursor = conn.cursor()

        cursor.execute(sql)

        for i in cursor:

            user_id = False

            usr = self.env['res.users'].search([
                ('belotom_personel_recid', '=', i.kulid),
                ('active', '=', True)], limit=1)

            if usr:
                user_id = usr.id

            if usr and usr.employee_id and i.izin_sure > 0:
                hasval = leave.search([('belotom_node_id', '=', i.nodeID)])
                hakedis_tarihi = i.hakedis_tarihi

                if not hakedis_tarihi:
                    hakedis_tarihi = datetime.date(i.nodeText, 1, 1)

                if not hasval:

                    params = (True, f"{i.nodeText} - {i.izintur}", i.nodeID,
                              'validate', hakedis_tarihi, holiday_status_id, usr.employee_id.id,
                              usr.employee_id.company_id.id, i.izin_sure, 'employee', 'regular', 1, hakedis_tarihi)

                    insert_sql = f"INSERT INTO hr_leave_allocation(active,private_name,belotom_node_id," \
                                 f"state, date_from, holiday_status_id ,employee_id," \
                                 f"employee_company_id, number_of_days," \
                                 f"holiday_type,allocation_type, create_uid,create_date )" \
                                 f"VALUES(%s, %s, %s, " \
                                 f"%s, %s, %s, %s, " \
                                 f"%s, %s, %s, %s, %s, %s )"

                    self.env.cr.execute(insert_sql, params)

                else:
                    params = (f"{i.nodeText} - {i.izintur}", hakedis_tarihi,
                              usr.employee_id.id, i.izin_sure,
                              hasval.id)

                    insert_sql = f"UPDATE hr_leave_allocation SET private_name = %s, date_from = %s," \
                                 f"employee_id = %s ,number_of_days = %s ," \
                                 f"write_uid = 1,write_date = now() " \
                                 f"where id = %s"

                    self.env.cr.execute(insert_sql, params)

    @api.model
    def update_hr_leave_allocation_from_belotom(self, holiday_status_id=1):
        configs = self.env['ir.config_parameter'].sudo()

        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = configs.get_param('belsis_settings.belotom_server')
        belotom_db = configs.get_param('belsis_settings.belotom_db')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1433;"
            conn = pyodbc.connect(connStr)
            self._update_hr_leave_allocation_from_belotom(conn, holiday_status_id)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")
