{
    'name': 'Report_infp',
    'author': 'By Tutor',
    'website': 'https://rbs.co.th/',
    'summary': 'Odoo 16 Development',
    'sequence': 1,
    'category': 'Tools',
    'version': '16.0.1.0.0',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'reports/report.xml',
        'reports/quotation_report_infp.xml',
        'reports/billing_report_infp_H.xml',
        'reports/billing_report_infp.xml',
        'reports/credit_notes_report_infp.xml',
        'reports/credit_notes_report_infp_H.xml',
        'reports/delivery_report_infp_H.xml',
        'reports/receipt_report_infp_H.xml',
        'reports/kol_return_receipt.xml'
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
