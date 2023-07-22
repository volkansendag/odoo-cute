# -*- coding: utf-8 -*-
{
    'name': 'Kredi Kartları Modülü',
    'version': '1.0.0',
    'summary': 'Kredi kartlarının yönetimi için oluşturulmuştur.',
    'sequence': -100,
    'description': """Kredi Kartları Modülü""",
    'category': 'Invoicing',
    'author': 'Volkan Şendağ',
    'maintainer': 'Volkan Şendağ',
    'website': 'https://belsis.com.tr',
    'license': 'AGPL-3',
    'depends': [
        'mail', 'hr',
    ],
    'data': [
        'security/creditcard_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/creditcard_view.xml',
        'views/creditcard_type_view.xml',
        'views/bank_view.xml',
        'views/res_config_settings_view.xml',
        'views/creditcard_period_view.xml',
        'views/creditcard_expense_view.xml'
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
