# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import platform
import pyodbc
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)


class Conversation(models.Model):
    _name = "conversation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Görüşme Kayıtları"
    _order = "start_date desc"

    name = fields.Char(string='Konu', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Müşteri', tracking=True)
    partner_personal_name = fields.Char(string='Müşteri Personeli')
    user_id = fields.Many2one('res.users', string='Görüşme Yapan', tracking=True)

    start_date = fields.Datetime(string="Başlangıç Zamanı", help='Görüşmeye başlama zamanıdır.', required=True,
                                 default=fields.Datetime.now)
    end_date = fields.Datetime(string="Bitiş Zamanı", help='Görüşmenin bitiş zamanıdır.')
    duration = fields.Integer(string="Görüşme Süresi (dk)", compute='_calculate_date_diff_minute', store=True)

    priority = fields.Selection([('0', 'Çok düşük'), ('1', 'Düşük'), ('2', 'Normal'), ('3', 'Yüksek')],
                                string='Öncelik', default='0')

    note = fields.Html(string='Görüşme Notu')
    state = fields.Selection([('draft', 'Devam Ediyor'), ('done', 'Çözüldü'), ('cancel', 'Yapılmayacak')],
                             default='draft', string="Durumu", tracking=True)

    platform_id = fields.Many2one('conversation.platform', string="Görüşme Şekli")
    class_id = fields.Many2one('conversation.class', string="Görüşme Sınıfı")
    type_id = fields.Many2one('conversation.type', string="Görüşme Türü")
    partner_section_id = fields.Many2one('conversation.partner.section', string="Bölüm")

    belotom_id = fields.Integer(string="Belotom Id", index=True)
    belotom_update_time = fields.Datetime(string="Belotom Güncelleme Tarihi")
    belsat_id = fields.Integer(string="Belsat Id", index=True)

    source_name = fields.Selection([('belsat', 'Belsat'), ('belotom', 'Belotom'), ('odoo', 'Odoo')], index=True,
                                   default='odoo', string='Kayıt kaynağı', compute='_calculate_source_name', store=True)

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.depends('start_date', 'end_date')
    def _calculate_date_diff_minute(self):
        for record in self:
            start_date = record.start_date
            end_date = record.end_date

            if start_date and end_date and start_date < end_date:
                self.duration = ((end_date - start_date).seconds / 60)
            else:
                self.duration = 0

    @api.depends('belsat_id', 'belotom_id', 'note')
    def _calculate_source_name(self):
        for record in self:
            belotom_id = record.belotom_id
            belsat_id = record.belsat_id

            if belotom_id:
                self.source_name = 'belotom'
            elif belsat_id:
                self.source_name = 'belsat'
            else:
                self.source_name = 'odoo'

    def write(self, values):
        if 'state' in values:
            if not self.end_date and values["state"] == 'done':
                values['end_date'] = fields.datetime.now()

        res = super(Conversation, self).write(values)

        return res

    def _get_conversations_from_belotom(self, conn, is_belsat, limit):

        conversation = self.with_context(tracking_disable=True).env['conversation']

        if is_belsat:
            last_update_time = conversation.search([('belotom_update_time', '!=', False), ('belsat_id', '!=', False)],
                                                   order='belotom_update_time desc', limit=1).belotom_update_time
        else:
            last_update_time = conversation.search([('belotom_update_time', '!=', False), ('belotom_id', '!=', False)],
                                                   order='belotom_update_time desc', limit=1).belotom_update_time

        system = platform.system()

        if not last_update_time:
            last_date = '2001-01-01'
            if is_belsat:
                last_date = '2009-07-07'
        elif system == 'Linux':
            last_date = last_update_time.strftime('%Y-%m-%d %H:%M')
        else:
            last_date = last_update_time.strftime('%Y-%d-%m %H:%M')

        cursor = conn.cursor()
        sql = f'SELECT TOP {limit} g.recid,' \
              f'g.tarbsl baslama_tarihi, ' \
              f'g.tarbts bitis_tarihi, ' \
              f'g.idgrmskl gorusme_sekli_id, ' \
              f'gs.ad gorusme_sekli_ad, ' \
              f'b.kod belediye_kod, ' \
              f'b.ad belediye_ad,  ' \
              f'g.idbldblm belediye_bolum_id, ' \
              f'blm.mudurlukadi belediye_bolum_ad, ' \
              f'g.bldprsad belediye_personel_ad, ' \
              f'g.bldprssoyad belediye_personel_soyad, ' \
              f'g.idgrmsnf gorusme_sinif_id, ' \
              f'gsnf.ad gorusme_sinif_ad, ' \
              f'g.idgrmtur gorusme_tur_id, ' \
              f'gtur.ad gorusme_tur_ad, ' \
              f'gd.idmdl modul_id, ' \
              f'm.ad modul_ad, ' \
              f'gd.idprs personel_id, ' \
              f'p.ad personel_ad, ' \
              f'p.soyad personel_soyad, ' \
              f'gd.idktg gorusme_kategori_id, ' \
              f'gktg.ad gorusme_kategori_ad, ' \
              f'gd.iddrm gorusme_durum_id, ' \
              f'gdrm.ad gorusme_durum_ad, ' \
              f'g.updateTime update_time,  ' \
              f'gd.srn sorun,  ' \
              f'gd.czm cozum ' \
              f'FROM grmGiris g ' \
              f'left join grmDetay gd on gd.idGiris = g.recid ' \
              f'and gd.recid = (select max(recid) from grmDetay where idGiris = g.recid) ' \
              f'left join grmGrmSkl gs on g.idgrmskl = gs.recid ' \
              f'left join belediye b on b.kod = g.idbld ' \
              f'left join bolum blm on blm.mudurlukno = g.idbldblm ' \
              f'left join grmGrmSnf gsnf on gsnf.recid = g.idgrmsnf ' \
              f'left join grmGrmTur gtur on gtur.recid = g.idgrmtur ' \
              f'left join modul2 m on m.recid = gd.idmdl ' \
              f'left join personel p on p.recid = gd.idprs ' \
              f'left join grmGrmKtg gktg on gktg.recid = gd.idktg ' \
              f'left join grmDurum gdrm on gdrm.recid = gd.iddrm ' \
              f'where g.tarbsl is not null and g.updateTime > \'{last_date}\' ' \
              f'order by g.updateTime'

        cursor.execute(sql)

        updated = 0

        for i in cursor:
            if updated >= 1000:
                self.env.cr.commit()
                updated = 0
            if is_belsat:
                has_val = conversation.search([('belsat_id', '=', i.recid)])
            else :
                has_val = conversation.search([('belotom_id', '=', i.recid)])

            if i.baslama_tarihi:
                i.baslama_tarihi = i.baslama_tarihi + timedelta(hours=-3)

            if i.bitis_tarihi:
                i.bitis_tarihi = i.bitis_tarihi + timedelta(hours=-3)

            if i.baslama_tarihi and not has_val:
                belediye_bolum_id, gorusme_sekli_id, gorusme_sinif_id, gorusme_tur_id, note, partner_id, \
                    state, user_id = self._get_conversation_data(i)

                ent = {
                    'name': i.sorun or f'{i.recid} nolu görüşme',
                    'note': note,
                    'start_date': i.baslama_tarihi,
                    'end_date': i.bitis_tarihi,
                    'platform_id': gorusme_sekli_id,
                    'partner_section_id': belediye_bolum_id,
                    'class_id': gorusme_sinif_id,
                    'partner_personal_name': f'{i.belediye_personel_ad} {i.belediye_personel_soyad}',
                    'type_id': gorusme_tur_id,
                    'partner_id': partner_id,
                    'user_id': user_id,
                    'state': state,
                    'belotom_update_time': i.update_time
                }

                if is_belsat:
                    ent['belsat_id'] = i.recid
                else:
                    ent['belotom_id'] = i.recid

                conversation.create(ent)
                updated = updated + 1

            elif not last_update_time or i.update_time > last_update_time:

                belediye_bolum_id, gorusme_sekli_id, gorusme_sinif_id, gorusme_tur_id, note, partner_id, \
                    state, user_id = self._get_conversation_data(i)

                has_val.partner_section_id = belediye_bolum_id
                has_val.platform_id = gorusme_sekli_id
                has_val.class_id = gorusme_sinif_id
                has_val.type_id = gorusme_tur_id

                has_val.note = note

                if has_val.partner_id != partner_id:
                    has_val.partner_id = partner_id

                if has_val.state != state:
                    has_val.state = state

                if has_val.user_id != user_id:
                    has_val.user_id = user_id

                has_val.name = i.sorun or f'{i.recid} nolu görüşme'
                has_val.start_date = i.baslama_tarihi
                has_val.end_date = i.bitis_tarihi
                has_val.partner_personal_name = f'{i.belediye_personel_ad} {i.belediye_personel_soyad}'
                has_val.belotom_update_time = i.update_time

                conversation.update(has_val)

                updated = updated + 1

        if updated > 0:
            self.env.cr.commit()

    def _get_conversation_data(self, i):
        gorusme_sekli_id = False
        belediye_bolum_id = False
        gorusme_sinif_id = False
        gorusme_tur_id = False
        partner_id = False
        user_id = False
        state = 'draft'
        if i.gorusme_durum_id == 1:
            state = 'done'
        if i.gorusme_durum_id == 3:
            state = 'cancel'
        if i.belediye_kod:
            partner_id = self.env['res.partner'].search([('belotom_kod', '=', i.belediye_kod.strip())]).id
        if i.gorusme_sekli_ad:
            gorusme_sekli_id = self.env['conversation.platform'].search([('name', '=', i.gorusme_sekli_ad)]).id
            if not gorusme_sekli_id:
                gorusme_sekli_id = self.env['conversation.platform'].create({
                    'name': i.gorusme_sekli_ad,
                    'belotom_id': i.gorusme_sekli_id
                }).id
        if i.belediye_bolum_ad:
            belediye_bolum_id = self.env['conversation.partner.section'].search(
                [('name', '=', i.belediye_bolum_ad)]).id
            if not belediye_bolum_id:
                belediye_bolum_id = self.env['conversation.partner.section'].create({
                    'name': i.belediye_bolum_ad,
                    'belotom_id': i.belediye_bolum_id
                }).id
        if i.gorusme_sinif_ad:
            gorusme_sinif_id = self.env['conversation.class'].search(
                [('name', '=', i.gorusme_sinif_ad)]).id
            if not gorusme_sinif_id:
                gorusme_sinif_id = self.env['conversation.class'].create({
                    'name': i.gorusme_sinif_ad,
                    'belotom_id': i.gorusme_sinif_id
                }).id
        if i.gorusme_tur_ad:
            gorusme_tur_id = self.env['conversation.type'].search(
                [('name', '=', i.gorusme_tur_ad)]).id
            if not gorusme_tur_id:
                gorusme_tur_id = self.env['conversation.type'].create({
                    'name': i.gorusme_tur_ad,
                    'belotom_id': i.gorusme_tur_id
                }).id
        note = i.cozum
        if i.personel_id:
            user_id = self.env['res.users'].search([('belotom_personel_recid', '=', i.personel_id)]).id
        if not user_id:
            note = f'{i.personel_ad} {i.personel_soyad} notu: <br /> {i.cozum}'

        return belediye_bolum_id, gorusme_sekli_id, gorusme_sinif_id, gorusme_tur_id, note, partner_id, state, user_id

    @api.model
    def get_conversations_from_belotom(self, limit=1000):
        configs = self.env['ir.config_parameter'].sudo()
        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_server = configs.get_param('belsis_settings.belotom_server')
        belotom_db = configs.get_param('belsis_settings.belotom_db')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1433;"
            conn = pyodbc.connect(connStr)
            self._get_conversations_from_belotom(conn, False, limit)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")

    @api.model
    def get_conversations_from_belsat(self, limit=1000):
        configs = self.env['ir.config_parameter'].sudo()

        db_driver_name = configs.get_param('belsis_settings.db_driver_name')
        belotom_uid = configs.get_param('belsis_settings.belotom_uid')
        belotom_pwd = configs.get_param('belsis_settings.belotom_pwd')

        belotom_server = "beldb6\\belotom"
        belotom_db = "belsat"

        if belotom_server and belotom_db and belotom_uid and belotom_pwd:
            connStr = f"DRIVER={db_driver_name}; Server={belotom_server}; UID={belotom_uid};PWD={belotom_pwd};DataBase={belotom_db};Port=1447;"
            conn = pyodbc.connect(connStr)
            self._get_conversations_from_belotom(conn, True, limit)
            _logger.info("belotom sync success")
        else:
            _logger.info("there are no belsis_settings")
