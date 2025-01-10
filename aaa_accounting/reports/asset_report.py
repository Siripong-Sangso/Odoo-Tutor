# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, _

class ReportAsset(models.AbstractModel):
    _name = 'report.aaa_accounting.report_asset_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        asset_ids = data['ids']
        report = self.env['ir.actions.report']._get_report_from_name('aaa_accounting.report_asset_report')
        # docargs = {
        return {  # odoo 11
            'doc_ids': asset_ids,
            'doc_model': 'account.asset.asset',
            'docs': self.env['account.asset.asset'].browse(asset_ids),
            'data': data,
        }