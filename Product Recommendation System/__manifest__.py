# -*- coding: utf-8 -*-
{
    'name': 'product recommendation',
    'autor': 'Tutor',
    'website': 'https://rbs.co.th/',
    'summary': 'Odoo 16 Development',
    'sequence': 1,
    'category': 'Tools',
    'version': '16.0.1.0.0',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'sale.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
