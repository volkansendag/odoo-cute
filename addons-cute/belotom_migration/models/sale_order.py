# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_order_lines_from_belotom_modul3(self, ref_no, kodbld):
        conn = self._get_conn()
        sql = f"select" \
              f"		modul3.recid as recid," \
              f"		null as parentID," \
              f"		personel.recid personel_id," \
              f"		modul3.kodbld," \
              f"		modul3.kodmodul modulRecid," \
              f"		(select ad from modul2 where modul2.recid=modul3.kodmodul) as nodeText, " \
              f"		surum, " \
              f"		isNull(kodsatis,'') as lisansSayisi," \
              f"		isNull(lisansNo,'') as lisansNo," \
              f"		isNull(satisRefNo,'') as satisReferansNo," \
              f"		tarsatis as satisTarihi," \
              f"		isNull(personel.ad+' '+personel.soyad,'') as satisPersonel," \
              f"		bankaAdi," \
              f"		modul3.aktif " \
              f"	from modul3 " \
              f"		left join personel on personel.kod=modul3.kodsatici " \
              f"		left join bankalar on bankalar.ID=modul3.bankaID " \
              f"		where tarsatis is not null and satisRefNo='{ref_no}' and modul3.kodbld like '{kodbld}'" \
              f"		order by kodbld, tarsatis;"

        cursor = conn.cursor()

        cursor.execute(sql)

        return cursor

    def _get_orders_from_belotom_modul3(self):
        conn = self._get_conn()
        sql = f"select " \
              f"		personel.recid personel_id," \
              f"		kodbld," \
              f"		isNull(satisRefNo,'') as satisReferansNo," \
              f"		max(tarsatis) as satisTarihi" \
              f"	from modul3" \
              f"		left join personel on personel.kod=modul3.kodsatici" \
              f"		where tarsatis is not null" \
              f"		group by" \
              f"			satisRefNo," \
              f"			kodbld," \
              f"			personel.recid," \
              f"			kodbld" \
              f"		order by max(tarsatis) desc"

        cursor = conn.cursor()

        cursor.execute(sql)

        return cursor

    def update_orders_from_belotom_modul3(self, delete_all=False):

        if delete_all:
            self.env.cr.execute(f"delete from sale_order where reference is not null")

        orders = self.with_context(tracking_disable=True).env['sale.order']
        order_lines = self.with_context(tracking_disable=True).env['sale.order.line']
        products = self.with_context(tracking_disable=True).env['product.template']

        belotom_orders = self._get_orders_from_belotom_modul3()

        updated = 0

        for belotom_order in belotom_orders:

            has_val = orders.search([('reference', '=', belotom_order.satisReferansNo)])

            user_id = False
            partner_id = False

            if belotom_order.personel_id:
                user_id = self.env['res.users'].search([('belotom_personel_recid', '=', belotom_order.personel_id)]).id

            if belotom_order.kodbld:
                partner_id = self.env['res.partner'].search([('belotom_kod', '=', belotom_order.kodbld.strip())]).id

            if not partner_id:
                continue

            if belotom_order.satisTarihi:
                belotom_order.satisTarihi = belotom_order.satisTarihi + timedelta(hours=-3)

            if not has_val:
                ent_order = orders.create({
                    'name': f'{belotom_order.satisReferansNo}',
                    'reference': belotom_order.satisReferansNo,
                    'date_order': belotom_order.satisTarihi,
                    'create_date': belotom_order.satisTarihi,
                    'state': 'sale',
                    'invoice_status': 'invoiced',
                    'user_id': user_id,
                    'partner_id': partner_id,
                })

                belotom_order_lines = self._get_order_lines_from_belotom_modul3(belotom_order.satisReferansNo,
                                                                                belotom_order.kodbld)

                for belotom_order_line in belotom_order_lines:

                    has_order_line = order_lines.search([('belotom_recid', '=', belotom_order_line.recid)])

                    product = products.search(
                        [('belotom_recid', '=', belotom_order_line.modulRecid), ('belotom_table_name', '=', 'modul2')])

                    if product and not has_order_line:
                        order_lines.create({
                            'name': f'{belotom_order_line.nodeText}',
                            'order_id': ent_order.id,
                            'belotom_recid': belotom_order_line.recid,
                            'state': 'sale',
                            'invoice_status': 'invoiced',
                            'product_uom_qty': belotom_order_line.lisansSayisi,
                            'qty_delivered': belotom_order_line.lisansSayisi,
                            'qty_invoiced': belotom_order_line.lisansSayisi,
                            'product_id': product.id,
                        })

                    updated = updated + 1

                self.env.cr.commit()
                self.env.cr.execute(f"update sale_order set invoice_status ='invoiced' where id = {ent_order.id} ")
                self.env.cr.execute(f"update sale_order_line set invoice_status = 'invoiced' "
                                    f"where order_id = {ent_order.id}")

    def _get_conn(self):
        configs = self.env['ir.config_parameter'].sudo()

        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = configs.get_param('belsis_settings.belotom_server')
        belotom_db = configs.get_param('belsis_settings.belotom_db')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1433;"
            conn = pyodbc.connect(connStr)
            return conn
        else:
            _logger.info("there are no belsis_settings")
