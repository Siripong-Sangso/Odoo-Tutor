# -*- coding: utf-8 -*-

{
    'name': 'AAA Accounting V16',
    'version': '1.0.0',
    'category': 'Accounting',
    'summary': 'Accounting Reports, Asset Management and Account Budget, Recurring Payments, '
               'Lock Dates, Fiscal Year For Odoo 16 Community Edition, Accounting Dashboard, Financial Reports, '
               'Customer Follow up Management, Bank Statement Import, Odoo Budget',
    'description': 'Odoo 16 Financial Reports, Asset Management and '
                   'Account Budget, Financial Reports, Recurring Payments, '
                   'Bank Statement Import, Customer Follow Up Management,'
                   'Account Lock Date, Accounting Dashboard',
    'sequence': '1',
    'website': 'https://www.anyworkanywhereanytime.com',
    'author': 'AAA',
    'maintainer': 'AAA',
    'license': 'LGPL-3',
    'support': 'info@rbs-center.info',
    'depends': ['base', 'account', 'sale'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'reports/report_reg.xml',
        'views/account_account_view.xml',
        'views/account_journal_view.xml',
        'views/account_move_view.xml',
        'views/account_tax_view.xml',
        'views/account_asset_asset_view.xml',
        'views/withholding_tax_view.xml',
        'wizard/tax_report_view.xml',
        'wizard/payable_report_view.xml',
        'wizard/asset_report_view.xml',
        'wizard/withholding_tax_view.xml',
        'reports/invoice_th_report.xml',
        'reports/invoice_eng_report.xml',
        'reports/invoice_th_eng_report.xml',
        'reports/credit_note_th_report.xml',
        'reports/credit_note_eng_report.xml',
        'reports/credit_note_th_eng_report.xml',
        'reports/purchase_tax_report.xml',
        'reports/sale_tax_report.xml',
        'reports/account_payable_report.xml',
        'reports/asset_report.xml',
        'reports/withholding_tax_report.xml',
        'reports/withholding_tax_all_report.xml',
        'reports/invoice_report_ill.xml',
        'reports/vendor_bill_report_ill.xml',
        'reports/credit_note_report_ill.xml',
        'reports/pre_invoice_report_ill.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}
