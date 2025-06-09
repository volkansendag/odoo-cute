# -*- coding: utf-8 -*-
{
    'name': 'Satış Modülü Rapor Templates',
    'version': '1.0.1',
    'summary': 'Satış modülleri üzerinde iyileştirmeler yapılmıştır.',
    'sequence': -90,
    'description': """Satış Modülü Rapor Templates""",
    'category': 'Sale',
    'author': 'Volkan Şendağ',
    'maintainer': 'Volkan Şendağ',
    'website': 'https://vsendag.com',
    'license': 'AGPL-3',
    'depends': [
        'base', 'mail', 'sale', 'contacts'
    ],
    'data': [
        'views/sale_order_reports.xml'
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}