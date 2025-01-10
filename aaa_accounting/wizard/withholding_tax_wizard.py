# -*- coding: utf-8 -*-
import datetime
import time
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.tools.safe_eval import safe_eval

from odoo import fields, models, api, _

#this is for tax report section
class WithholdingTaxReport(models.Model):
    _name = 'withholding.tax.all'

    today = date.today()
    first_day = today.replace(day=1)
    last_day = datetime.datetime(today.year, today.month, 1) + relativedelta(months=1, days=-1)
    date_from = fields.Date(string='From Date', required=True, default=first_day)
    date_to = fields.Date(string='To Date', required=True, default=last_day.strftime('%Y-%m-%d'))
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('withholding.tax.report'))

    def print_pdf(self):
        data = self.read()[0]
        domain = []
        # domain.append(('state', 'in', ['done']))
        # domain.append(('order_date', '>=', self.date_from))
        # domain.append(('order_date', '<=', self.date_to))
        tax_ids = self.env['withholding.tax'].search(domain, order='order_date,name ASC').ids
        datas = {'ids': tax_ids}
        datas.update(model='withholding.tax')
        datas.update({'form': data})
        return self.env.ref('aaa_accounting.withholding_tax_all_report').report_action(self, data=datas,
                                                                             config=False)  # odoo 12