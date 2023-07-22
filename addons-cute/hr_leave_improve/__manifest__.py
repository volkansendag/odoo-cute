# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'İzin Modülü Ek Özellikler',
    'version': '1.5',
    'category': 'Human Resources/İzin Modülü Ek Özellikler',
    'sequence': 10,
    'summary': 'Izin modulu icin yeni gelistirmeler',
    'website': 'https://volkansendag.com',
    'description': """
Izin modulu icin yeni gelistirmeler.
=====================================

Yapilacak calismalar
* Izin onayini mail olarak gondermek.

""",
    'depends': ['hr', 'resource'],
    'data': [
        'views/hr_leave_improve_reports.xml',
        'views/hr_leave_improve_mail.xml',
        'views/hr_employee_improve_view.xml',
        'views/hr_leave_type_improve_view.xml',
        'views/hr_leave_improve_view.xml',
        'security/hr_leave_improve_security.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
