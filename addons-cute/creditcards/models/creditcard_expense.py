# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging

_logger = logging.getLogger(__name__)

class CreditCardExpense(models.Model):
    _name = "creditcard.expense"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Kredi Kartı Harcamaları"
    _rec_name = 'name'
    _order = "used_date desc"

    name = fields.Char(string='Kategori', tracking=True)
    period = fields.Text(string='Dönem Adı', tracking=True)
    creditcard_id = fields.Many2one('creditcard', string='Kredi Kartı')
    period_id = fields.Many2one('creditcard.period', string='Kredi Kartı Periodu')
    card_no2 = fields.Char(string='Son 4 Hane')
    limit = fields.Float(string='Kart Limiti', digits='Kart Limiti')
    used_date = fields.Date(string="Kullanım Tarihi")
    pay_date = fields.Date(string="Ödeme Tarihi")
    amount = fields.Float(string='Tutar', digits='Tutar')
    note = fields.Text(string='Açıklama')
    belotom_recid = fields.Char(string="Belotom Kodu")
    belotom_update_date = fields.Datetime(string="Belotom Güncelleme Tarihi")
    belotom_donem_id = fields.Integer(string="Belotom Dönem Id")
    belotom_personel_id = fields.Integer(string="Belotom Personel Id")
    belotom_personel_adi = fields.Char(string="Personel Adı")
    belotom_personel_soyadi = fields.Char(string="Personel Soyadı")
    belotom_personel_adi_soyadi = fields.Char(string="Personel Adı Soyadı", compute='_compute_cart_name_surname',
                                              store=True)

    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id

    employee_id = fields.Many2one('hr.employee', string="Personel (Odoo)",
                                  store=True, readonly=False, tracking=True,
                                  states={'approved': [('readonly', True)], 'done': [('readonly', True)]},
                                  default=_default_employee_id)
    @api.depends('belotom_personel_adi', 'belotom_personel_soyadi')
    def _compute_cart_name_surname(self):
        for cart in self:
            if cart.belotom_personel_adi and cart.belotom_personel_soyadi:
                cart.belotom_personel_adi_soyadi = cart.belotom_personel_adi + " " + cart.belotom_personel_soyadi

    def update_belotom_card_expense(self, conn, limit):

        expense = self.env['creditcard.expense']

        last_belotom_update_date = expense.search([('belotom_recid', '!=', False)],
                                        order='belotom_update_date desc', limit=1).belotom_update_date
        system = platform.system()

        if not last_belotom_update_date:
            last_date = '2001-01-01'
        elif system == 'Linux':
            last_date = last_belotom_update_date.strftime('%Y-%m-%d %H:%M')
        else:
            last_date = last_belotom_update_date.strftime('%Y-%d-%m %H:%M')

        sql = f"SELECT TOP {limit} * FROM hrcKrdKartHarcamaView where sonGuncellemeTarih>='{last_date}' order by sonGuncellemeTarih"
        cursor = conn.cursor()

        cursor.execute(sql)

        updated = 0

        for i in cursor:
            if updated > 1000:
                self.env.cr.commit()
                updated = 0

            has_val = expense.search([('belotom_recid', '=', i.recid)])

            lmt = i.lmt
            ttr = i.ttr

            if system != 'Linux':
                lmt = i.lmt / 10000  # mssql db den decimal hatali geliyor.
                ttr = i.ttr / 10000  # mssql db den decimal hatali geliyor.

            if not has_val:
                creditcard_id = 0
                period_id = 0
                creditcard_ids = self.env['creditcard'].search([('belotom_id', '=', i.kodkrt)])
                period_ids = self.env['creditcard.period'].search([('belotom_id', '=', i.donem_recid)])

                if creditcard_ids:
                    creditcard_id = creditcard_ids[0].id

                if period_ids:
                    period_id = period_ids[0].id

                expense.create({
                    'name': i.ad,
                    'period': i.donem_adi,
                    'creditcard_id': creditcard_id,
                    'period_id': period_id,
                    'card_no2': i.no4,
                    'limit': lmt,
                    'used_date': i.kultar,
                    'pay_date': i.tar,
                    'amount': ttr,
                    'note': i.ack,
                    'belotom_recid': i.recid,
                    'belotom_update_date': i.sonGuncellemeTarih,
                    'belotom_donem_id': i.donem_recid,
                    'belotom_personel_id': i.kodprs,
                    'belotom_personel_adi': i.prsad,
                    'belotom_personel_soyadi': i.prssoyad,
                })
                updated = updated + 1
            elif i.sonGuncellemeTarih > has_val.belotom_update_date:
                creditcard_id = 0
                period_id = 0
                creditcard_ids = self.env['creditcard'].search([('belotom_id', '=', i.kodkrt)])
                period_ids = self.env['creditcard.period'].search([('belotom_id', '=', i.donem_recid)])

                if creditcard_ids:
                    creditcard_id = creditcard_ids[0].id

                if period_ids:
                    period_id = period_ids[0].id

                has_val.name = i.ad
                has_val.period = i.donem_adi
                has_val.creditcard_id = creditcard_id
                has_val.period_id = period_id
                has_val.card_no2 = i.no4
                has_val.limit = lmt
                has_val.used_date = i.kultar
                has_val.pay_date = i.tar
                has_val.amount = ttr
                has_val.note = i.ack
                has_val.belotom_update_date = i.sonGuncellemeTarih
                has_val.belotom_donem_id = i.donem_recid
                has_val.belotom_personel_id = i.kodprs
                has_val.belotom_personel_adi = i.prsad
                has_val.belotom_personel_soyadi = i.prssoyad

                expense.update(has_val)

                updated = updated + 1

        if updated > 0:
            self.env.cr.commit()

    @api.model
    def get_creditcard_expense_from_belotom(self, limit=1000):
        configs = self.env['ir.config_parameter'].sudo()
        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = configs.get_param('belsis_settings.belotom_server')
        belotom_db = configs.get_param('belsis_settings.belotom_db')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1433;"
            conn = pyodbc.connect(connStr)
            self.update_belotom_card_expense(conn, limit)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")












