# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging

_logger = logging.getLogger(__name__)


class CreditCard(models.Model):
    _name = "creditcard"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Kredi Kartları"
    _rec_name = 'card_no'
    _order = "id desc"

    name = fields.Char(string='Kart Adı', required=True, tracking=True)
    card_no = fields.Char(string='Kart No', compute='_compute_cart_no', readonly=False, store=True)
    card_no1 = fields.Char(string='İlk 4 Hane', required=True, tracking=True, size=4)
    card_no2 = fields.Char(string='Son 4 Hane', required=True, tracking=True, size=4)

    card_cvv = fields.Char(string='Güvenlik Kodu', tracking=True, size=3)

    limit = fields.Float(string='Kart Limiti', required=True, digits='Kart Limiti')
    current_limit = fields.Float(string='Güncel Kart Limiti', compute='_compute_cart_current_limit', digits='Güncel Kart Limiti', readonly="True", store=True)
    expense_count = fields.Integer(string='Toplam Alışveriş Sayısı', compute='_compute_cart_expense_count',
                                   readonly="True", store=True)

    priority = fields.Selection([('0', 'Çok düşük'), ('1', 'Düşük'), ('2', 'Normal'), ('3', 'Yüksek')], string='Öncelik')

    note = fields.Text(string='Açıklama')
    state = fields.Selection([('draft', 'Taslak'), ('confirm', 'Onaylı'), ('cancel', 'İptal')], default='draft',
                             string="Durumu", tracking=True)

    card_owner_type = fields.Selection([('company', 'Şirket'), ('private', 'Özel'), ('cancel', 'İptal')], default='company',
                             string="Sahip Türü", tracking=True)

    bank_id = fields.Many2one('creditcard.bank', string='Banka')
    type_id = fields.Many2one('creditcard.type', string='Kart Tipi')

    period_ids = fields.One2many('creditcard.period', 'creditcard_id', "Kart Dönemleri")

    expense_ids = fields.One2many('creditcard.expense', 'creditcard_id', "Kart Harcamaları")
    last_expense_date = fields.Date('Son Alışveriş Tarihi', compute='_compute_last_expense_date', store=True)

    image = fields.Binary(string="Kredi Kartı Resmi")

    belotom_id = fields.Integer(string="Belotom No")

    belotom_personel_id = fields.Integer(string="Belotom Personel Id")
    belotom_personel_adi = fields.Char(string="Personel Adı")
    belotom_personel_soyadi = fields.Char(string="Personel Soyadı")
    belotom_personel_adi_soyadi = fields.Char(string="Personel Adı Soyadı", compute='_compute_cart_name_surname', store=True)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_get_attachment_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Kredi Kartı Harcamaları',
            'res_model': 'creditcard.expense',
            'domain': [('creditcard_id', '=', self.id)],
            'context': {'creditcard_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_open_banks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Kredi Kartı Harcamaları',
            'res_model': 'creditcard.bank',
            'domain': [('bank_id', '=', self.id)],
            'context': {'bank_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current',
        }

    @api.depends('expense_ids')
    def _compute_cart_expense_count(self):
        for cart in self:
            if cart.expense_ids:
                cart.expense_count = cart.expense_ids.search_count([
                    ('creditcard_id', '=', cart.id)
                ])

    @api.depends('expense_ids.used_date', 'expense_ids')
    def _compute_last_expense_date(self):
        for cart in self:
            if self.expense_ids:
                last = self.expense_ids.search([('creditcard_id', '=', cart.id)], order='used_date desc', limit=1)
                cart.last_expense_date = last.used_date

    @api.depends('card_no1', 'card_no2')
    def _compute_cart_no(self):
        for cart in self:
            if self.card_no1 and self.card_no2:
                cart.card_no = cart.card_no1 + "-0000-0000-" + cart.card_no2

    @api.depends('belotom_personel_adi', 'belotom_personel_soyadi')
    def _compute_cart_name_surname(self):
        for cart in self:
            if cart.belotom_personel_adi and cart.belotom_personel_soyadi:
                cart.belotom_personel_adi_soyadi = cart.belotom_personel_adi + " " + cart.belotom_personel_soyadi

    @api.depends('expense_ids.amount','period_ids.period_begin', 'limit')
    def _compute_cart_current_limit(self):
        for cart in self:
            if not isinstance(cart.id, models.NewId) and self.expense_ids:
                period = self.period_ids.search(
                    [('creditcard_id', '=', cart.id), ('period_begin', '<', 'now()'), ('period_end', '>', 'now()')], limit=1)
                period_begin = period.period_begin

                expenses = self.expense_ids.search([('creditcard_id', '=', cart.id), ('used_date', '>', period_begin)])

                total_amount = sum(expenses.mapped('amount'))
                cart.current_limit = cart.limit - total_amount

    def update_belotom_bank(self, conn):
        cursor = conn.cursor()
        cursor.execute('SELECT *  FROM hrcBanka')

        for i in cursor:
            bank = self.env['creditcard.bank']
            hasval = bank.search([('belotom_id', '=', i.recid)])
            if not hasval:
                id = bank.create({
                    'title': i.ad,
                    'belotom_id': i.recid
                })
                self.env.cr.commit()

    def update_belotom_card_types(self, conn):
        cursor = conn.cursor()
        cursor.execute('SELECT *  FROM hrcKrtTur')

        for i in cursor:
            bank = self.env['creditcard.type']
            hasval = bank.search([('belotom_id', '=', i.recid)])
            if not hasval:
                id = bank.create({
                    'title': i.ad,
                    'belotom_id': i.recid
                })
                self.env.cr.commit()

    def update_belotom_card_periods(self, conn):
        period = self.env['creditcard.period']
        system = platform.system()

        last_belotom_id = period.search([('belotom_id', '>', 0)],
                                        order='belotom_id desc', limit=1).belotom_id

        last_write_date = period.search([('belotom_id', '!=', False)],
                                        order='write_date desc', limit=1).write_date

        if not last_belotom_id:
            last_belotom_id = 0

        if not last_belotom_id:
            last_date = '2001-01-01'
        elif system == 'Linux':
            last_date = last_write_date.strftime('%Y-%m-%d %H:%M')
        else:
            last_date = last_write_date.strftime('%Y-%d-%m %H:%M:%S')

        cursor = conn.cursor()
        cursor.execute(f"select * from hrcKrtDnm where recid > {last_belotom_id} or sonGuncellemeTarih>'{last_date}' order by sonGuncellemeTarih, recid")

        updated = 0

        for i in cursor:
            hasval = period.search([('belotom_id', '=', i.recid)])

            lmt = i.lmtd

            if system != 'Linux':
                lmt = i.lmtd/10000 #mssql db den decimal hatali geliyor.
            if not hasval:
                creditcard_id = 0
                creditcard_ids = self.env['creditcard'].search([('belotom_id', '=', i.kodkrt)])
                if creditcard_ids:
                    creditcard_id = creditcard_ids[0].id
                else:
                    print("null card id")

                period.create({
                    'name': i.ad,
                    'belotom_id': i.recid,
                    'note': i.aciklama,
                    'period_begin': i.tar1,
                    'period_end': i.tar2,
                    'due_date': i.tarsonodm,
                    'creditcard_id': creditcard_id,
                    'limit': lmt
                })
                updated = updated + 1
            elif i.sonGuncellemeTarih > hasval.write_date:
                creditcard_id = self.env['creditcard'].search([('belotom_id', '=', i.kodkrt)])[0].id
                hasval.name = i.ad
                hasval.creditcard_id = creditcard_id
                hasval.note = i.aciklama
                hasval.period_begin = i.tar1
                hasval.period_end = i.tar2
                hasval.due_date = i.tarsonodm
                hasval.limit = lmt
                hasval.write_date = i.sonGuncellemeTarih

                period.update(hasval)

                updated = updated + 1

        if updated > 0:
            self.env.cr.commit()

    def update_belotom_cards(self, conn):
        cursor = conn.cursor()
        cursor.execute(f'SELECT  k.recid,	k.kodbnk,	k.kodtur,	k.no1,	k.no2,	k.no3,	k.no4,	k.cvv,	k.lmt,	'
                       f'k.ack,	k.durum,	p.recid pid,	p.ad,	p.soyad  '
                       f'FROM hrcKrdKart k  '
                       f'left join personel p on p.recid=k.kodprs')

        system = platform.system()

        for i in cursor:
            card = self.env['creditcard']
            hasval = card.search([('belotom_id', '=', i.recid)])
            if not hasval:
                _bank = self.env['creditcard.bank'].search([('belotom_id', '=', i.kodbnk)])
                _type = self.env['creditcard.type'].search([('belotom_id', '=', i.kodtur)])
                lmt = i.lmt

                if system != 'Linux':
                    lmt = i.lmt / 10000  # mssql db den decimal hatali geliyor.

                id = card.create({
                    'name': i.no4,
                    'card_no1': i.no1,
                    'card_no2': i.no4,
                    'card_cvv': i.cvv,
                    'limit': lmt,
                    'note': i.ack,
                    'bank_id': _bank.id,
                    'type_id': _type.id,
                    'belotom_personel_id': i.pid,
                    'belotom_personel_adi': i.ad,
                    'belotom_personel_soyadi': i.soyad,
                    'belotom_id': i.recid
                })
                self.env.cr.commit()

    @api.model
    def get_creditcard_move_from_belotom(self):
        configs = self.env['ir.config_parameter'].sudo()
        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = configs.get_param('belsis_settings.belotom_server')
        belotom_db = configs.get_param('belsis_settings.belotom_db')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1433;"
            conn = pyodbc.connect(connStr)
            self.update_belotom_bank(conn)
            self.update_belotom_card_types(conn)
            self.update_belotom_cards(conn)
            self.update_belotom_card_periods(conn)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")

