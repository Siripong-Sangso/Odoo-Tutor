# -*- coding: utf-8 -*-
import datetime
import time
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.tools.safe_eval import safe_eval

from odoo import fields, models, api, _


# this is for tax report section
class PayableReport(models.Model):
    _name = 'payable.report'
    _description = "Account Payable Report"

    today = date.today()
    first_day = today.replace(day=1)
    last_day = datetime.datetime(today.year, today.month, 1) + relativedelta(months=1, days=-1)
    date_from = fields.Date(string='From Date', required=True, default=first_day)
    date_to = fields.Date(string='To Date', required=True, default=last_day.strftime('%Y-%m-%d'))
    report_type = fields.Selection([('detail', 'แบบแจกแจง'), ('summary', 'แบบสรุป')], default='detail',
                                   string='Report Type', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('payable.report'))

    def print_pdf(self):
        data = self.read()[0]
        domain = []
        if self.report_type == 'detail':
            domain = [('journal_id.type', '=', 'purchase')]
            domain.append(('company_id', '=', self.company_id.id))
            domain.append(('move_type', 'in', ['in_invoice', 'in_refund']))
            domain.append(('invoice_date', '>=', self.date_from))
            domain.append(('invoice_date', '<=', self.date_to))
            tax_ids = self.env['account.move'].search(domain, order='invoice_date,name ASC').ids
            datas = {'ids': tax_ids}
            datas.update(model='account.move')
            datas.update({'form': data})
            return self.env.ref('aaa_accounting.action_payable_detail_report_pdf').report_action(self, data=datas,
                                                                                           config=False)
        else:
            domain = [('journal_id.type', '=', 'purchase')]
            domain.append(('company_id', '=', self.company_id.id))
            domain.append(('move_type', 'in', ['in_invoice', 'in_refund']))
            domain.append(('invoice_date', '>=', self.date_from))
            domain.append(('invoice_date', '<=', self.date_to))
            tax_ids = self.env['account.move'].search(domain, order='invoice_date,name ASC').ids
            datas = {'ids': tax_ids}
            datas.update(model='account.move')
            datas.update({'form': data})
            return self.env.ref('aaa_accounting.action_payable_summary_report_pdf').report_action(self, data=datas,
                                                                                           config=False)
