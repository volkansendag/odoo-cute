# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import pyodbc
import logging

_logger = logging.getLogger(__name__)


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    belotom_node_id = fields.Integer(string="Belotom Id")

    def _update_hr_leave_from_belotom(self, conn, holiday_status_id):

        leave = self.env["hr.leave"]

        sql = f"select * from isciIzinKullanim"
        cursor = conn.cursor()

        cursor.execute(sql)

        for i in cursor:

            user_id = False

            usr = self.env['res.users'].search([
                ('belotom_personel_recid', '=', i.kulid),
                ('active', '=', True)], limit=1)

            if usr:
                user_id = usr.id

            if usr and usr.employee_id:
                hasval = leave.search([('belotom_node_id', '=', i.nodeID)])

                if not hasval:
                    params = (i.izin_aciklama, i.nodeID, user_id, usr.employee_id.id, holiday_status_id,
                              i.izin_bas_tar, i.izin_bit_tar, usr.employee_id.company_id.id,
                              usr.employee_id.department_id.id, i.kullan,
                              i.izin_bas_tar, i.izin_bit_tar, i.islem_tarihi)

                    insert_sql = f"INSERT INTO hr_leave(private_name,belotom_node_id,user_id,employee_id," \
                                 f"holiday_status_id,holiday_type,state,date_from,date_to,employee_company_id," \
                                 f"department_id,number_of_days,duration_display,request_date_from,request_date_to," \
                                 f"request_date_from_period,request_unit_half,request_unit_hours,request_unit_custom," \
                                 f"create_uid,create_date) " \
                                 f"VALUES(%s, %s, %s, %s, %s,'employee','validate',%s, %s, %s, %s, %s,'{i.kullan} gün'," \
                                 f"%s, %s, 'am', False, False, False, 1, %s)"

                    self.env.cr.execute(insert_sql, params)

                else:
                    params = (i.izin_aciklama, user_id, usr.employee_id.id, i.izin_bas_tar, i.izin_bit_tar,
                              i.kullan, i.izin_bas_tar, i.izin_bit_tar, hasval.id)

                    insert_sql = f"UPDATE hr_leave SET private_name = %s, user_id = %s, employee_id = %s," \
                                 f"date_from = %s ,date_to = %s ," \
                                 f"number_of_days = %s, duration_display = '{i.kullan} gün'," \
                                 f"request_date_from = %s,request_date_to = %s," \
                                 f"write_uid = 1,write_date = now() " \
                                 f"where id = %s"

                    self.env.cr.execute(insert_sql, params)

    @api.model
    def update_hr_leave_from_belotom(self, holiday_status_id=1):
        configs = self.env['ir.config_parameter'].sudo()

        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = configs.get_param('belsis_settings.belotom_server')
        belotom_db = configs.get_param('belsis_settings.belotom_db')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1433;"
            conn = pyodbc.connect(connStr)
            self._update_hr_leave_from_belotom(conn, holiday_status_id)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")
