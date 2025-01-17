# -*- coding: utf-8 -*-
{
    'name': 'Test module sale',
    'author': 'Tutor',
    'website': 'https://rbs.co.th/',
    'summary': 'Odoo 16 Development',
    'sequence': 1,
    'category': 'Tools',
    'version': '16.0.1.0.0',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale.xml',
        'views/account.xml',
        'reports/report.xml',
        'reports/report_cn.xml',
        'reports/sale_report_template.xml',
        'reports/invoice_report_infp_H.xml',
        'reports/delivery_report_infp_H.xml',
        'reports/receipt_report_infp_H.xml',
        'reports/Test3.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
