# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging

_logger = logging.getLogger(__name__)


class BelotomResPartner(models.Model):
    _inherit = "res.partner"

    belsat_kod = fields.Char(string="Belsat Kod")
    belotom_kod = fields.Char(string="Belotom Kod")

    belotom_vergi_dairesi = fields.Char(string="Vergi Dairesi")
    belotom_kodbld = fields.Selection(
        [('1', 'Belediye'), ('2', 'Kod 2'), ('3', 'Kod 3'), ('4', 'Diğer')],
        string='Belotom KodBld',
        default='4')

    def _update_belotom_belediye(self, conn, limit='1,2,3', add_new=True):

        partner = self.env['res.partner']

        sql = f"select * from belediye b " \
              f"left join genil i on i.il_kodu = b.kodil " \
              f"left join genilce ic on ic.ilce_kodu = b.kodilce and ic.il_kodu = i.il_kodu " \
              f"where b.kodbld in ({limit})"

        cursor = conn.cursor()

        cursor.execute(sql)
        updated = 0

        for i in cursor:

            if updated > 1000:
                self.env.cr.commit()
                updated = 0

            trim_kod = i.kod.strip()

            user_id = False

            usr = self.env['res.users'].search([
                ('belotom_personel_recid', '=', i.musteriTemsilcisi),
                ('active', '=', True)], limit=1)

            if usr:
                user_id = usr.id

            has_val = partner.search([('belotom_kod', '=', trim_kod)])

            if i.il_kodu:
                state_id = self.env['res.country.state'] \
                    .search([('country_id', '=', self.env.user.company_id.country_id.id),
                             ('code', '=', f'{i.il_kodu:02d}')]).id

            if not has_val:
                if add_new:
                    partner.create({
                        'name': i.ad,
                        'belotom_kod': trim_kod,
                        'belotom_kodbld': str(i.kodbld),
                        'belotom_vergi_dairesi': i.vergidaire,
                        'is_company': True,
                        'lang': 'tr_TR',
                        'street': i.adres,
                        'street2': f"{i.adr1} - {i.adr2}",
                        'vat': i.vergino,
                        'phone': i.telefon,
                        'mobile': i.faks,
                        'email': i.email,
                        'website': i.www,
                        'country_id': 224,
                        'city': i.ilce_adi,
                        'state_id': state_id,
                        'user_id': user_id,
                        'team_id': 1,
                    })
                    updated = updated + 1
            else:
                # - güncelleme işlemini özel durumlarda yapacağız.
                # if user_id:
                #     has_val.user_id = user_id
                # has_val.name = i.ad
                # has_val.belotom_kodbld = str(i.kodbld)
                # if i.vergidaire:
                #     has_val.belotom_vergi_dairesi = i.vergidaire
                # if i.vergino:
                #     has_val.vat = i.vergino
                # if i.adres:
                #     has_val.street = i.adres
                # if i.adr1 or i.adr2:
                #     has_val.street2 = f"{i.adr1} - {i.adr2}"
                # if i.telefon:
                #     has_val.phone = i.telefon
                # if i.faks:
                #     has_val.mobile = i.faks
                # if i.email:
                #     has_val.email = i.email
                # if i.www:
                #     has_val.website = i.www
                if i.ilce_adi:
                    has_val.city = i.ilce_adi
                if state_id:
                    has_val.state_id = state_id

                partner.update(has_val)

                updated = updated + 1

        if updated > 0:
            self.env.cr.commit()

    @api.model
    def get_res_partner_from_belotom(self, limit, add_new=True):
        configs = self.env['ir.config_parameter'].sudo()

        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = configs.get_param('belsis_settings.belotom_server')
        belotom_db = configs.get_param('belsis_settings.belotom_db')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1433;"
            conn = pyodbc.connect(connStr)
            self._update_belotom_belediye(conn, limit, add_new)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")

    def _update_belsat_belediye(self, conn, limit='1,2,3', add_new=True):

        partner = self.env['res.partner']

        sql = f"select * from belediye b " \
              f"left join genil i on i.il_kodu = b.kodil " \
              f"left join genilce ic on ic.ilce_kodu = b.kodilce and ic.il_kodu = i.il_kodu " \
              f"where b.kodbld in ({limit})"

        cursor = conn.cursor()

        cursor.execute(sql)
        updated = 0

        for i in cursor:

            if updated > 1000:
                self.env.cr.commit()
                updated = 0

            trim_kod = i.kod.strip()

            hasvalBelotom = partner.search([('belotom_kod', '=', trim_kod)])
            hasvalBelsat = partner.search([('belsat_kod', '=', trim_kod)])

            if i.il_kodu:
                state_id = self.env['res.country.state'] \
                    .search([('country_id', '=', self.env.user.company_id.country_id.id),
                             ('code', '=', f'{i.il_kodu:02d}')]).id

            if not hasvalBelotom:
                if not hasvalBelsat:
                    if add_new:
                        partner.create({
                            'name': i.ad,
                            'belotom_kod': trim_kod,
                            'belsat_kod': trim_kod,
                            'belotom_kodbld': str(i.kodbld),
                            'belotom_vergi_dairesi': i.vergidaire,
                            'is_company': True,
                            'lang': 'tr_TR',
                            'street': i.adres,
                            'street2': f"{i.adr1} - {i.adr2}",
                            'vat': i.vergino,
                            'phone': i.telefon,
                            'mobile': i.faks,
                            'email': i.email,
                            'website': i.www,
                            'country_id': 224,
                            'city': i.il_adi,
                            'team_id': 1,
                        })
                        updated = updated + 1
                else:
                    # hasvalBelsat.name = i.ad
                    # hasvalBelsat.belotom_kodbld = str(i.kodbld)
                    # if i.vergidaire:
                    #     hasvalBelsat.belotom_vergi_dairesi = i.vergidaire
                    # if i.vergino:
                    #     hasvalBelsat.vat = i.vergino
                    # if i.adres:
                    #     hasvalBelsat.street = i.adres
                    # if i.adr1 or i.adr2:
                    #     hasvalBelsat.street2 = f"{i.adr1} - {i.adr2}"
                    # if i.telefon:
                    #     hasvalBelsat.phone = i.telefon
                    # if i.faks:
                    #     hasvalBelsat.mobile = i.faks
                    # if i.email:
                    #     hasvalBelsat.email = i.email
                    # if i.www:
                    #     hasvalBelsat.website = i.www

                    if i.ilce_adi:
                        hasvalBelsat.city = i.ilce_adi
                    if state_id:
                        hasvalBelsat.state_id = state_id

                    partner.update(hasvalBelsat)

                    updated = updated + 1

        if updated > 0:
            self.env.cr.commit()

    @api.model
    def get_res_partner_from_belsat(self, limit, add_new=True):
        configs = self.env['ir.config_parameter'].sudo()

        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = "beldb6\\belotom"
        belotom_db = "belsat"
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1447;"
            conn = pyodbc.connect(connStr)
            self._update_belsat_belediye(conn, limit, add_new)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")

    def name_get(self):
        res = []
        for record in self:
            display_name = record.name
            state = record.state_id.name or record.city
            if state:
                display_name = display_name + ' (' + state + ')'
            res.append((record.id, display_name))

        return res