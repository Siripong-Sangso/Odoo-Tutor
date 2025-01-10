#-*- coding: utf-8 -*-

from odoo import fields, models, api, _

def isodd(x):
    return bool(x % 2)

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

class account_asset_category(models.Model):
    _inherit = "account.asset.category"

    profit_loss_disposal_account_id = fields.Many2one('account.account',string='Disposal Account')
    salvage_value = fields.Float(string='Default Salvage Value')

class ResCompany(models.Model):
    _inherit = 'res.company'

    asset_depreciation_year = fields.Boolean(string='พิจารณาค่าเสื่อมทุกปีเท่ากัน')

class account_asset_asset(models.Model):
    _inherit = "account.asset.asset"

    barcode = fields.Char(string='Barcode',copy=False,readonly=True, states={'draft': [('readonly', False)]})
    employees_id = fields.Many2one('hr.employee', string='ชื่อพนักงาน',readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', related='employees_id.department_id', string='ชื่อแผนก', store=True,readonly=True, states={'draft': [('readonly', False)]})
    serial_number = fields.Char(string='Serial Number',readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text(string='Note')
    purchase_date = fields.Date(string='Purchase Date',readonly=True, states={'draft': [('readonly', False)]})
    asset_purchase_price = fields.Float(string='Purchase Value',readonly=True, states={'draft': [('readonly', False)]})
    depreciated_amount = fields.Float(string='ค่าเสื่อมราคาสะสม',readonly=True,compute='get_depreciated_amount')
    asset_disposal_date = fields.Date(string='Disposal Date', readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]})
    # End


    @api.depends('value_residual')
    def get_depreciated_amount(self):
        for asset in self:
            asset.depreciated_amount = asset.asset_purchase_price - asset.salvage_value - asset.value_residual


# class AccountAssetDepreciationLine(models.Model):
#     _inherit = 'account.asset.depreciation.line'
#
#     @api.multi
#     def create_move(self, post_move=True):
#         created_moves = self.env['account.move']
#         prec = self.env['decimal.precision'].precision_get('Account')
#         if post_move:
#             for line in self:
#                 category_id = line.asset_id.category_id
#                 depreciation_date = self.env.context.get(
#                     'depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
#                 company_currency = line.asset_id.company_id.currency_id
#                 current_currency = line.asset_id.currency_id
#                 amount = current_currency.compute(line.amount, company_currency)
#                 sign = (category_id.journal_id.type == 'purchase' or category_id.journal_id.type == 'sale' and 1) or -1
#                 asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
#                 prec = self.env['decimal.precision'].precision_get('Account')
#                 move_line_1 = {
#                     'name': asset_name,
#                     'account_id': category_id.account_depreciation_id.id,
#                     'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#                     'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
#                     'journal_id': category_id.journal_id.id,
#                     'partner_id': line.asset_id.partner_id.id,
#                     'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
#                     'currency_id': company_currency != current_currency and current_currency.id or False,
#                     'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
#                 }
#                 move_line_2 = {
#                     'name': asset_name,
#                     'account_id': category_id.account_depreciation_expense_id.id,
#                     'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#                     'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
#                     'journal_id': category_id.journal_id.id,
#                     'partner_id': line.asset_id.partner_id.id,
#                     'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
#                     'currency_id': company_currency != current_currency and current_currency.id or False,
#                     'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
#                 }
#                 move_vals = {
#                     'ref': line.asset_id.code,
#                     'date': depreciation_date or False,
#                     'journal_id': category_id.journal_id.id,
#                     'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
#                 }
#                 move = self.env['account.move'].create(move_vals)
#                 line.write({'move_id': move.id, 'move_check': True})
#                 created_moves |= move
#
#         #this is for sell or disposal
#         else:
#             for line in self:
#                 depreciation_date = self.env.context.get(
#                     'depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
#
#                 date = fields.Date.context_today(self)
#                 # print "depreciation_date"
#                 # print depreciation_date
#                 company_currency = line.asset_id.company_id.currency_id
#                 current_currency = line.asset_id.currency_id
#                 amount = current_currency.compute(line.amount, company_currency)
#                 sign = (
#                        line.asset_id.category_id.journal_id.type == 'purchase' or line.asset_id.category_id.journal_id.type == 'sale' and 1) or -1
#                 asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids)) + '- Disposal'
#                 reference = line.asset_id.code
#                 journal_id = line.asset_id.category_id.journal_id.id
#                 partner_id = line.asset_id.partner_id.id
#                 categ_type = line.asset_id.category_id.type
#
#                 #original
#                 # debit_account = line.asset_id.category_id.account_income_recognition_id.id or line.asset_id.category_id.account_asset_id.id
#                 # credit_account = line.asset_id.category_id.account_depreciation_id.id
#
#                 # new
#                 debit_account = line.asset_id.category_id.account_depreciation_id.id
#                 credit_account = line.asset_id.category_id.account_asset_id.id
#                 gain_loss_account = line.asset_id.category_id.profit_loss_disposal_account_id.id
#
#
#                 prec = self.env['decimal.precision'].precision_get('Account')
#                 move_line_1 = {
#                     'name': asset_name,
#                     'account_id': credit_account,
#                     'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#                     'credit': line.asset_id.value if float_compare(line.asset_id.value, 0.0, precision_digits=prec) > 0 else 0.0,
#                     'journal_id': journal_id,
#                     'partner_id': partner_id,
#                     'currency_id': company_currency != current_currency and current_currency.id or False,
#                     'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
#                     'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'sale' else False,
#                     'date': date,
#                 }
#
#                 move_line_2 = {
#                     'name': asset_name,
#                     'account_id': gain_loss_account,
#                     'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#                     'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
#                     'journal_id': journal_id,
#                     'partner_id': partner_id,
#                     'currency_id': company_currency != current_currency and current_currency.id or False,
#                     'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
#                     'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'purchase' else False,
#                     'date': date,
#                 }
#                 move_line_3 = {
#                     'name': asset_name,
#                     'account_id': debit_account,
#                     'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#                     'debit': (line.asset_id.value - amount) if float_compare((line.asset_id.value - amount), 0.0, precision_digits=prec) > 0 else 0.0,
#                     'journal_id': journal_id,
#                     'partner_id': partner_id,
#                     'currency_id': company_currency != current_currency and current_currency.id or False,
#                     'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
#                     'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'purchase' else False,
#                     'date': date,
#                 }
#                 move_vals = {
#                     'ref': reference,
#                     'date': depreciation_date or False,
#                     'journal_id': line.asset_id.category_id.journal_id.id,
#                     'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2),(0, 0, move_line_3)],
#                     'asset_id': line.asset_id.id,
#                 }
#
#                 move = self.env['account.move'].create(move_vals)
#                 line.write({'move_id': move.id, 'move_check': True})
#                 created_moves |= move
#
#
#         if post_move and created_moves:
#             created_moves.filtered(lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
#         return [x.id for x in created_moves]
#
# class AccountInvoiceLine(models.Model):
#     _inherit = 'account.invoice.line'
#
#     @api.one
#     def asset_create(self):
#         if self.asset_category_id:
#             vals = {
#                 'name': self.name,
#                 'code': self.invoice_id.number or False,
#                 'category_id': self.asset_category_id.id,
#                 'value': self.price_subtotal_signed,
#                 'salvage_value': self.asset_category_id.salvage_value,
#                 'partner_id': self.invoice_id.partner_id.id,
#                 'company_id': self.invoice_id.company_id.id,
#                 'currency_id': self.invoice_id.company_currency_id.id,
#                 'date': self.invoice_id.date_invoice,
#                 'invoice_id': self.invoice_id.id,
#             }
#             changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
#             vals.update(changed_vals['value'])
#             asset = self.env['account.asset.asset'].create(vals)
#             if self.asset_category_id.open_asset:
#                 asset.validate()
#         return True
#
# class AccountAssetDepreciationLine(models.Model):
#     _inherit = 'account.asset.depreciation.line'
#
#     category_id = fields.Many2one('account.asset.category',related='asset_id.category_id', string='Category ID',store=True)