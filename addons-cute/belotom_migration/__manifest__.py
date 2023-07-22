# -*- coding: utf-8 -*-
{
    'name': 'Beletom Veri Taşıma Modülü',
    'version': '1.0.0',
    'summary': 'Belotom üzerinden veri aktarım modülüdür.',
    'sequence': -10,
    'description': """Beletom Veri Taşıma Modülü""",
    'category': 'Extra Tools',
    'author': 'Volkan Şendağ',
    'maintainer': 'Volkan Şendağ',
    'website': 'https://belsis.com.tr',
    'license': 'AGPL-3',
    'depends': [
        'mail', 'hr', 'sale', 'creditcards'
    ],
    'data': [
        # 'security/creditcard_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/res_partner_view.xml',
        'views/res_users_view.xml',
        'views/res_product_view.xml',
        'views/sale_order_view.xml',
        'views/hr_leave_view.xml',
        'views/hr_leave_allocation_view.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
