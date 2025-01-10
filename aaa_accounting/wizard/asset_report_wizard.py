# -*- coding: utf-8 -*-
import datetime
import time
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.tools.safe_eval import safe_eval

from odoo import fields, models, api, _

#this is for tax report section
class AssetReport(models.Model):
    _name = 'asset.report'
    _description = 'Asset report'

    today = date.today()
    first_day = today.replace(day=1)
    last_day = datetime.datetime(today.year, today.month, 1) + relativedelta(months=1, days=-1)
    date_from = fields.Date(string='From Date', required=True, default=last_day.strftime('%Y-01-01'))
    date_to = fields.Date(string='To Date', required=True, default=last_day.strftime('%Y-12-31'))
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('asset.report'))
    category_id = fields.Many2one('account.asset.category', string='Asset Types')

    first_date_from = fields.Date(string='First From Date', default=last_day.strftime('%Y-01-01'))
    last_date_from = fields.Date(string='Last From Date', default=last_day.strftime('%Y-01-31'))
    first_date_to = fields.Date(string='First To Date', default=last_day.strftime('%Y-12-01'))
    last_date_to = fields.Date(string='Last To Date', default=last_day.strftime('%Y-12-31'))

    @api.onchange('date_from')
    def _date_from(self):
        for rec in self:
            last_date_from = datetime.datetime(rec.date_from.year, rec.date_from.month, 1) + relativedelta(months=1, days=-1)
            rec.first_date_from = rec.date_from.strftime('%Y-%m-01')
            rec.last_date_from = last_date_from.strftime('%Y-%m-%d')

    @api.onchange('date_to')
    def _date_to(self):
        for rec in self:
            last_date_to = datetime.datetime(rec.date_to.year, rec.date_to.month, 1) + relativedelta(months=1, days=-1)
            rec.first_date_to = rec.date_to.strftime('%Y-%m-01')
            rec.last_date_to = last_date_to.strftime('%Y-%m-%d')

    def print_pdf(self):
        data = self.read()[0]
        domain = []
        # domain.append(('state', 'in', ['open']))
        # domain.append(('date', '>=', self.date_from))
        # domain.append(('date', '<=', self.date_to))
        if self.category_id:
            domain.append(('category_id', '=', self.category_id.id))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        tax_ids = self.env['account.asset.asset'].search(domain, order='date,id ASC').ids
        datas = {'ids': tax_ids}
        datas.update(model='account.asset.asset')
        datas.update({'form': data})
        return self.env.ref('aaa_accounting.action_asset_report_pdf').report_action(self, data=datas,
                                                                                 config=False)  # odoo 12
