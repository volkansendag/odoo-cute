# -*- coding: utf-8 -*-
{
    'name': 'Kalite Belge Yönetimi',
    'version': '1.0.0',
    'summary': 'Kalite belgelerinin takip edildiği modüldür.',
    'sequence': -100,
    'description': """Kalite Belge Yönetimi""",
    'category': 'Productivity',
    'author': 'Volkan Şendağ',
    'maintainer': 'Volkan Şendağ',
    'website': 'https://belsis.com.tr',
    'license': 'AGPL-3',
    'depends': ['mail'],
    'data': [
        'data/data.xml',
        'security/quality_docs_security.xml',
        'security/ir.model.access.csv',
        'views/quality_docs_view.xml',
        'views/quality_institution_view.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
