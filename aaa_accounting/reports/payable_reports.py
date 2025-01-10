# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _

class ReportPayable(models.AbstractModel):
    _name = 'report.aaa_accounting.account_payable_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        tax_ids = data['ids']
        report = self.env['ir.actions.report']._get_report_from_name('aaa_accounting.account_payable_report')
        # docargs = {
        return {  # odoo 11
            'doc_ids': tax_ids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].browse(tax_ids),
            'data': data,
        }