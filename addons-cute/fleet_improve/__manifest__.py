# -*- coding: utf-8 -*-
{
    'name': 'Araç Takip Modülü İyileştirmeleri',
    'version': '1.0.0',
    'summary': 'Araç Takip modülü üzerinde iyileştirmeler yapılmıştır.',
    'sequence': -100,
    'description': """Araç Takip İyileştirmeleri""",
    'category': 'Human Resources/Fleet',
    'author': 'Volkan Şendağ',
    'maintainer': 'Volkan Şendağ',
    'website': 'https://belsis.com.tr',
    'license': 'AGPL-3',
    'depends': [
        'mail', 'fleet',
    ],
    'data': [
        'views/fleet_vehicle_odometer_views.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
}
