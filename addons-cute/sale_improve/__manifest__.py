# -*- coding: utf-8 -*-
{
    'name': 'Satış Modülü İyileştirmeleri',
    'version': '1.0.0',
    'summary': 'Satış modülleri üzerinde iyileştirmeler yapılmıştır.',
    'sequence': -100,
    'description': """Satış Modülü İyileştirmeleri""",
    'category': 'Sale',
    'author': 'Volkan Şendağ',
    'maintainer': 'Volkan Şendağ',
    'website': 'https://belsis.com.tr',
    'license': 'AGPL-3',
    'depends': [
        'mail', 'sale',
    ],
    'data': [
        'data/data.xml',
        'views/res_partner_view.xml',
        'views/res_partner_source_of_info.xml',
        'views/sale_order_views.xml',
        'views/sale_order_temp_views.xml',
        'security/res_partner_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
