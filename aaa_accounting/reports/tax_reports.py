# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _

class ReportSaleTax(models.AbstractModel):
    _name = 'report.aaa_accounting.sale_tax_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        tax_ids = data['ids']
        report = self.env['ir.actions.report']._get_report_from_name('aaa_accounting.sale_tax_report')
        # docargs = {
        return {  # odoo 11
            'doc_ids': tax_ids,
            'doc_model': 'account.move.line',
            'docs': self.env['account.move.line'].browse(tax_ids),
            'data': data,
        }

class ReportPurchaseTax(models.AbstractModel):
    _name = 'report.aaa_accounting.purchase_tax_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        tax_ids = data['ids']
        report = self.env['ir.actions.report']._get_report_from_name('aaa_accounting.purchase_tax_report')
        # docargs = {
        return {  # odoo 11
            'doc_ids': tax_ids,
            'doc_model': 'account.move.line',
            'docs': self.env['account.move.line'].browse(tax_ids),
            'data': data,
        }