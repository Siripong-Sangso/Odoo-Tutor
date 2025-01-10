# -*- coding: utf-8 -*-
import datetime
import time
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.tools.safe_eval import safe_eval

from odoo import fields, models, api, _

#this is for tax report section
class TaxReport(models.Model):
    _name = 'tax.report'
    _description = "Input/Output Tax Report"

    today = date.today()
    first_day = today.replace(day=1)
    last_day = datetime.datetime(today.year, today.month, 1) + relativedelta(months=1, days=-1)
    date_from = fields.Date(string='From Date', required=True, default=first_day)
    date_to = fields.Date(string='To Date', required=True, default=last_day.strftime('%Y-%m-%d'))
    report_type = fields.Selection([('sale', 'Sale Tax Report'), ('purchase', 'Purchase Tax Report')], default='sale',
                                   string='Report Type', required=True)
    disable_excel_tax_report = fields.Boolean(string="Disable Tax Report in Excel Format")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('tax.report'))
    tax_id = fields.Many2one('account.tax', string='Type of VAT', required=True)

    @api.onchange('report_type')
    def onchange_report_type(self):
        result = {}
        if self.report_type == 'sale':
            self.tax_id = self.env['account.tax'].search(
                [('type_tax_use', '=', 'sale'), ('company_id', '=', self.company_id.id), ('tax_report', '=', True)],
                limit=1)
            result['domain'] = {'tax_id': [('type_tax_use', '=', 'sale'), ('wht', '=', False)]}
        if self.report_type == 'purchase':
            self.tax_id = self.env['account.tax'].search(
                [('type_tax_use', '=', 'purchase'), ('company_id', '=', self.company_id.id), ('tax_report', '=', True)],
                limit=1)
            result['domain'] = {'tax_id': [('type_tax_use', '=', 'purchase'), ('wht', '=', False)]}
        return result

    def print_pdf(self):
        data = self.read()[0]
        domain = []
        if self.report_type == 'sale':
            domain = [('account_id', '=', self.tax_id.invoice_repartition_line_ids.account_id.id)]
            domain.append(('company_id', '=', self.company_id.id))
            domain.append(('invoice_date', '>=', self.date_from))
            domain.append(('invoice_date', '<=', self.date_to))
            tax_ids = self.env['account.move.line'].search(domain, order='invoice_date,move_name ASC').ids
            datas = {'ids': tax_ids}
            datas.update(model='account.move.line')
            datas.update({'form': data})
            return self.env.ref('aaa_accounting.action_sale_tax_report_pdf').report_action(self, data=datas, config=False)
        else:
            domain = [('account_id', '=', self.tax_id.invoice_repartition_line_ids.account_id.id)]
            domain.append(('company_id', '=', self.company_id.id))
            domain.append(('invoice_date', '>=', self.date_from))
            domain.append(('invoice_date', '<=', self.date_to))
            tax_ids = self.env['account.move.line'].search(domain, order='invoice_date,move_name ASC').ids
            datas = {'ids': tax_ids}
            datas.update(model='account.move.line')
            datas.update({'form': data})
            return self.env.ref('aaa_accounting.action_purchase_tax_report_pdf').report_action(self, data=datas, config=False)

    def print_xls(self):
        data = self.read()[0]
        domain = []
        if self.report_type == 'sale':
            domain = [('account_id', '=', self.tax_id.invoice_repartition_line_ids.account_id.id)]
            domain.append(('invoice_date', '>=', self.date_from))
            domain.append(('invoice_date', '<=', self.date_to))
            tax_ids = self.env['account.move.line'].search(domain, order='invoice_date,move_name ASC').ids
            datas = {'ids': tax_ids}
            datas.update(model='account.move.line')
            datas.update({'form': data})
            return self.env.ref('aaa_accounting.action_sale_tax_report_xls').report_action(self, data=datas, config=False)
        else:
            domain = [('account_id', '=', self.tax_id.invoice_repartition_line_ids.account_id.id)]
            domain.append(('invoice_date', '>=', self.date_from))
            domain.append(('invoice_date', '<=', self.date_to))
            tax_ids = self.env['account.move.line'].search(domain, order='invoice_date,move_name ASC').ids
            datas = {'ids': tax_ids}
            datas.update(model='account.move.line')
            datas.update({'form': data})
            return self.env.ref('aaa_accounting.action_purchase_tax_report_xls').report_action(self, data=datas, config=False)