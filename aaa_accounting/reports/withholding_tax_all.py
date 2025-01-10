# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _

class ReportWithholdingTax(models.AbstractModel):
    _name = 'report.aaa_invoice_v12.withholding_tax_all'

    @api.model
    def _get_report_values(self, docids, data=None):
        tax_ids = data['ids']
        report = self.env['ir.actions.report']._get_report_from_name('aaa_invoice_v12.withholding_tax_all')
        # docargs = {
        return {  # odoo 11
            'doc_ids': tax_ids,
            'doc_model': 'withholding.tax',
            'docs': self.env['withholding.tax'].browse(tax_ids),
            'data': data,
        }
