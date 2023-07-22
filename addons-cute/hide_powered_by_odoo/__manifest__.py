{
    'name': 'Hide Powered By Odoo',
    'version': '15.0.1.0.0',
    'sequence': 1,
    'summary': """
        Hide Powered By Odoo login screen
    """,
    'description': "Hide Powered By Odoo in login screen.",
    'author': 'Belsis Solutions',
    'maintainer': 'Belsis Solutions',
    'price': '0.0',
    'currency': 'TRY',
    'website': 'https://belsis.com.tr',
    'license': 'LGPL-3',
    'depends': [
        'web'
    ],
    'data': [
        'views/login_templates.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
