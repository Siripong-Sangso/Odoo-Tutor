# -*- coding: utf-8 -*-
{
    'name': 'Hospital Management System',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'author': 'Tutor minkyung',
    'summary': """Hospital""",
    'description': "Module Hospital Management",
    'website': 'https://rbs.co.th/',
    'summary': 'Odoo16 Development',
    'depends': ['mail', 'base'],
    'installable': True,
    'application': True,
    'demo': [
    ],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/Patients.xml',
        'views/doctor.xml',
        'reports/report.xml',
        'reports/patient_card.xml',
        'reports/report_doctor.xml',
        'reports/doctor_card.xml',
    ]
}
