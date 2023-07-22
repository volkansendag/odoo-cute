# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import pyodbc
import logging

_logger = logging.getLogger(__name__)

class BelotomResPartner(models.Model):
    _inherit = "product.template"

    belotom_recid = fields.Integer(string="Belotom Recid")
    belotom_table_name = fields.Char(string="Belotom Tablo Adı")

    def _add_product_categories(self, name):
        category = self.env['product.category']

        id = category.search([('name', '=', name)], limit=1).id

        if(id == False):
            id = category.create({
                'name': name,
                'parent_id': 1
            }).id

        return id

    def _update_products_from_belotom_modul2(self, conn, limit):

        products = self.env['product.template']

        sql = f"select * from modul2"

        cursor = conn.cursor()

        cursor.execute(sql)
        updated = 0

        for i in cursor:

            if updated > 100:
                self.env.cr.commit()
                updated = 0

            hasval = products.search([('belotom_recid', '=', i.recid), ('belotom_table_name', '=', 'modul2')])

            categ_id = 1

            if(i.kategori == 1):
                categ_id = self._add_product_categories('Teknik')

            if(i.kategori == 2):
                categ_id = self._add_product_categories('Yazılım')

            if(i.kategori == 3):
                categ_id = self._add_product_categories('Grafik')

            if(i.kategori == 4):
                categ_id = self._add_product_categories('Eğitim')

            if(i.kategori == 5):
                categ_id = self._add_product_categories('Proje')

            if not hasval:
                products.create({
                    'name': i.ad,
                    'belotom_recid': i.recid,
                    'default_code': i.kod,
                    'belotom_table_name': 'modul2',
                    'detailed_type': 'service',
                    'type': 'service',
                    'list_price': 0,
                    'purchase_ok': False,
                    'categ_id': categ_id
                })
                updated = updated + 1
            else:
                hasval.name = i.ad
                hasval.belotom_recid = i.recid
                hasval.default_code = i.kod
                hasval.categ_id = categ_id

                products.update(hasval)

                updated = updated + 1

        if updated > 0:
            self.env.cr.commit()

    @api.model
    def update_products_from_belotom(self, limit=1000):
        configs = self.env['ir.config_parameter'].sudo()

        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = configs.get_param('belsis_settings.belotom_server')
        belotom_db = configs.get_param('belsis_settings.belotom_db')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1433;"
            conn = pyodbc.connect(connStr)
            self._update_products_from_belotom_modul2(conn, limit)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")









