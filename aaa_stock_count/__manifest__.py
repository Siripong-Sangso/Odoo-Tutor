{
    'name': 'Stock Count',
    'version': '1.1',
    'category': 'Inventory',
    'summary': 'Module for counting stock and updating inventory in Odoo',
    'description': 'This module allows users to count stock, scan barcodes,'
                   'scan lot/serial numbers, and update inventory records accordingly.'
                   'It is fully compatible with the Smart Stock application.',
    'website': 'https://www.anyworkanywhereanytime.com',
    'author': 'AAA',
    'maintainer': 'AAA',
    'sequence': 1,
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/stock_count_sequence.xml',
        'views/stock_count_menu.xml',
        'views/barcode_wizard_view.xml',
        'views/stock_count_view.xml',
        'reports/stock_count_report_template.xml',
        'reports/stock_count_report.xml',
    ],
    'installable': True,
    'application': True,
}
