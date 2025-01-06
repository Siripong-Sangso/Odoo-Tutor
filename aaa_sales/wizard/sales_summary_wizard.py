# -*- coding: utf-8 -*-
import datetime
import time
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _


class SalesSummaryReport(models.Model):
    _name = 'sales.summary.report'
    _description = 'Sales Summary'

    today = date.today()
    first_day = today.replace(day=1)
    last_day = today + relativedelta(day=31)

    # Fields for dates
    date_from = fields.Date(string='From Date', required=True, default=first_day)
    date_to = fields.Date(string='To Date', required=True, default=last_day)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    sort_option = fields.Selection([('sort_date', 'Sort by date'), ('sort_customer', 'Sort by Customer'),
                                    ('sort_salesperson', 'Sort by Salesperson')],
                                   default='sort_date', required=True, string='Sort by')
    report_type = fields.Selection([('detailed', 'Detailed'), ('summary ', 'Summary ')],
                                   default='detailed', required=True, string='Report Format')
    customer_ids = fields.Many2many('res.partner', string="Customer")
    salesperson_ids = fields.Many2many('res.users', string="Salesperson")
    status = fields.Selection(
        [('all', 'All'), ('draft', 'Quotation'), ('sent', 'Quotation Sent'), ('waiting', 'Waiting Approval'), ('sale', 'Sale Order'), ('done', 'Locked')],
        string='Status', default='all', required=True)

    # Onchange methods
    @api.onchange('date_from')
    def _onchange_date_from(self):
        for rec in self:
            first_day = rec.date_from.replace(day=1)
            last_day = rec.date_from + relativedelta(day=31)
            rec.date_to = last_day

    def print_pdf(self):
        data = self.read()[0]
        domain = []
        domain.append(('date_order', '>=', self.date_from))
        domain.append(('date_order', '<=', self.date_to))

        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))

        if self.sort_option == 'sort_customer':
            if self.customer_ids:
                for i in self.customer_ids:
                    domain.append(('partner_id', 'in', [i.id]))
        elif self.sort_option == 'sort_salesperson':
            if self.salesperson_ids:
                for i in self.salesperson_ids:
                    domain.append(('user_id', 'in', [i.id]))

        if self.status == 'all':
            domain.append(('state', '!=', 'cancel'))
        elif self.status == 'draft':
            domain.append(('state', '==', 'draft'))
        elif self.status == 'sent':
            domain.append(('state', '==', 'sent'))
        elif self.status == 'waiting':
            domain.append(('state', '==', 'waiting'))
        elif self.status == 'sale':
            domain.append(('state', '==', 'sale'))
        elif self.status == 'done':
            domain.append(('state', '==', 'done'))

        sale_ids = self.env['sale.order'].search(domain, order='date_order,name ASC').ids
        datas = {'ids': sale_ids}
        datas.update(model='sale.order')
        datas.update({'form': data})
        if self.report_type == 'detailed':
            return self.env.ref('aaa_sales.action_sales_summary_detailed_pdf').report_action(self, data=datas,
                                                                                config=False)
        else:
            return self.env.ref('aaa_sales.action_sales_summary_pdf').report_action(self, data=datas,
                                                                                    config=False)