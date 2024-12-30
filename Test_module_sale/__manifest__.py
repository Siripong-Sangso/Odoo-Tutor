# -*- coding: utf-8 -*-
{
    'name': 'Test module sale',
    'autor': 'Tutor',
    'website': 'https://rbs.co.th/',
    'summary': 'Odoo 16 Development',
    'sequence': 1,
    'category': 'Tools',
    'version': '16.0.1.0.0',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/company.xml',
        'views/sale.xml',
        'reports/report.xml',
        'reports/sale_report_template.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
