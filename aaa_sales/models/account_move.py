# -*- coding: utf-8 -*-
from datetime import datetime, date
from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError, UserError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    discount = fields.Monetary(string=_('Discount'), default=0.0, store=True, readonly=True, compute='_compute_discount')
    amount_without_discount_tax = fields.Monetary(string=_('Amount without discount and tax'), default=0.0, store=True, readonly=True, compute='_compute_amount_without_discount_tax')

    @api.depends('line_ids.discount_amount')
    def _compute_discount(self):
        """
        คำนวณส่วนลดทั้งหมดจากบรรทัดใบแจ้งหนี้ (account.move.line)
        """
        for rec in self:
            total_discount = sum(line.discount_amount for line in rec.line_ids)
            rec.discount = total_discount

    @api.depends('line_ids.price_unit', 'line_ids.quantity', 'line_ids.discount_amount')
    def _compute_amount_without_discount_tax(self):
        """
        คำนวณยอดรวมก่อนหักส่วนลดและภาษี
        """
        for rec in self:
            total_amount_without_discount = sum(line.price_unit * line.quantity for line in rec.line_ids)
            rec.amount_without_discount_tax = total_amount_without_discount


class AccountInvoiceLineInherit(models.Model):
    _inherit = 'account.move.line'

    discount_amount = fields.Float(string=_('Discount amount'), default=0.0, digits=(10, 2))
    discount = fields.Float(string=_('Discount (%)'), digits=(2, 6), default=0.0)
    discount_show = fields.Float(string=_('Discount (%)'), digits=(2, 2), default=0.0)
    disc_flag = fields.Boolean(default=False)

    @api.onchange('discount', 'quantity', 'price_unit')
    def _onchange_discount(self):
        """
        คำนวณ discount_amount จากส่วนลดเปอร์เซ็นต์
        """
        if not self.disc_flag:
            self.discount_amount = ((self.price_unit * self.quantity) / 100) * self.discount
        self.disc_flag = True

    @api.onchange('discount_amount')
    def _onchange_discount_amount(self):
        """
        คำนวณ discount และ discount_show จาก discount_amount
        """
        if not self.disc_flag:
            total_price = self.price_unit * self.quantity
            if total_price != 0:
                self.discount = (self.discount_amount / total_price) * 100
            self.discount_show = self.discount
        self.disc_flag = True

    @api.onchange('discount_show')
    def _onchange_discount_show(self):
        """
        คำนวณ discount_amount จาก discount_show
        """
        if not self.disc_flag:
            self.discount_amount = ((self.price_unit * self.quantity) / 100) * self.discount_show
            self.discount = self.discount_show
        self.disc_flag = True