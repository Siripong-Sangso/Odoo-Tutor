# -*- coding: utf-8 -*-

from datetime import datetime, date
from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError, UserError
from collections import defaultdict
from datetime import timedelta, datetime, date
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round
from bahttext import bahttext
from num2words import num2words


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    contact_person = fields.Many2one('res.partner', string="Contact Person", readonly=True,
                                     states={'draft': [('readonly', False)]})

    project_name = fields.Char(string='Project', readonly=True, states={'draft': [('readonly', False)]})

    validity_days = fields.Integer(string="Validity (Days)", default=30, readonly=True, states={'draft': [('readonly', False)]},
                                   help="Number of days the quotation is valid for.")
    expiration_date = fields.Date(string="Expiration Date", compute="_compute_expiration_date", store=True)

    @api.depends('date_order', 'validity_days')
    def _compute_expiration_date(self):
        for order in self:
            if order.date_order:
                order.expiration_date = order.date_order + timedelta(days=order.validity_days)
            else:
                order.expiration_date = False

    total_before_discount_and_tax = fields.Monetary(
        string='Total Before Discount and Tax',
        store=True,
        readonly=True,
        compute='_compute_total_before_discount_and_tax',
        help='ราคารวมก่อนหักส่วนลดและภาษี'
    )

    total_discount = fields.Monetary(
        string='Total Discount',
        store=True,
        readonly=True,
        compute='_compute_total_discount',
        help='ยอดรวมของส่วนลดทั้งหมด (Fixed และ Percent)'
    )

    total_after_discount = fields.Monetary(
        string='Total After Discount',
        store=True,
        readonly=True,
        compute='_compute_total_after_discount',
        help='ยอดรวมหลังหักส่วนลด'
    )

    # def action_confirm(self):
    #     """Override action_confirm to block stock picking creation."""
    #     res = super(SaleOrderInherit, self).action_confirm()
    #     # ยกเลิก Stock Picking ที่สร้างขึ้น (ถ้ามี)
    #     for order in self:
    #         order.picking_ids.filtered(lambda p: p.state == 'draft').unlink()
    #     return res

    def _create_delivery(self):
        """Block creation of stock picking."""
        return False  # ไม่สร้าง Stock Picking

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderInherit, self)._prepare_invoice()
        # ดึงค่า project_name จาก SO เพื่อส่งไปยัง invoice
        invoice_vals['project_name'] = self.project_name
        return invoice_vals

    @api.depends('order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_total_before_discount_and_tax(self):
        """
        คำนวณราคารวมก่อนหักส่วนลดและภาษี
        """
        for order in self:
            total = sum(line.price_unit * line.product_uom_qty for line in order.order_line)
            order.total_before_discount_and_tax = total

    @api.depends('order_line.discount_fixed', 'order_line.discount', 'order_line.price_unit',
                 'order_line.product_uom_qty')
    def _compute_total_discount(self):
        """
        คำนวณส่วนลดรวมทั้งหมด (Fixed และ Percent)
        """
        for order in self:
            total_discount = sum(
                line.discount_fixed or (line.price_unit * line.product_uom_qty * line.discount / 100) for line in
                order.order_line)
            order.total_discount = total_discount

    @api.depends('total_before_discount_and_tax', 'total_discount')
    def _compute_total_after_discount(self):
        """
        คำนวณยอดรวมหลังหักส่วนลด
        """
        for order in self:
            order.total_after_discount = order.total_before_discount_and_tax - order.total_discount

    def baht_text(self, amount_total):
        return bahttext(amount_total)

    @api.depends('amount_total')
    def amount_num2words_text(self):
        for record in self:
            amount_num2words_text = num2words(record.amount_total)
            record.amount_total_num2words_text = amount_num2words_text

    def num2_words(self, amount_total):
        before_point = ""
        amount_total_str = str(amount_total)
        for i in range(0, len(amount_total_str)):
            if amount_total_str[i] != ".":
                before_point += amount_total_str[i]
            else:
                break

        after_point = float(amount_total) - float(before_point)
        after_point = locale.format("%.2f", float(after_point), grouping=True)
        after_point = float(after_point)
        before_point = float(before_point)

        # print before_point
        # print after_point
        before_point_str = num2words(before_point)
        after_point_str = num2words(after_point)
        if after_point_str == 'zero':
            before_point_str += ' Only'
        else:
            for i in range(4, len(after_point_str)):
                before_point_str += after_point_str[i]

        n2w_origianl = before_point_str
        # print n2w_origianl
        # n2w_origianl = num2words(float(amount_total))
        n2w_new = ""
        for i in range(len(n2w_origianl)):
            if i == 0:
                n2w_new += n2w_origianl[i].upper()
            else:
                if n2w_origianl[i] != ",":
                    if n2w_origianl[i - 1] == " ":
                        n2w_new += n2w_origianl[i].upper()
                    else:
                        n2w_new += n2w_origianl[i]

        # print n2w_origianl
        # print n2w_new
        return n2w_new


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits="Product Price",
        help="Fixed amount discount.",
    )

    disc_flag = fields.Boolean(default=False)

    @api.onchange('discount_fixed', 'price_unit', 'product_uom_qty')
    def _onchange_discount_fixed(self):
        """
        คำนวณส่วนลดแบบเปอร์เซ็นต์จากส่วนลดแบบจำนวนเงิน (Fixed Amount)
        และส่งผลไปยังฟิลด์ `discount` ซึ่งเป็นฟิลด์เปอร์เซ็นต์ดั้งเดิมของ Odoo
        """
        if not self.disc_flag and self.discount_fixed:
            total_price = self.price_unit * self.product_uom_qty
            if total_price > 0:
                self.discount = (self.discount_fixed / total_price) * 100
            self.disc_flag = True

    @api.onchange('discount', 'price_unit', 'product_uom_qty')
    def _onchange_discount(self):
        """
        คำนวณส่วนลดแบบจำนวนเงินจากส่วนลดแบบเปอร์เซ็นต์
        """
        if not self.disc_flag and self.discount:
            total_price = self.price_unit * self.product_uom_qty
            self.discount_fixed = (self.discount / 100) * total_price
        self.disc_flag = True

    @api.onchange('discount_fixed', 'discount')
    def _reset_flags(self):
        """
        รีเซ็ต flag เพื่อป้องกันการคำนวณซ้ำ
        """
        self.disc_flag = False

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the invoice line values by sending the discount data (fixed and percentage)
        """
        res = super(SaleOrderLineInherit, self)._prepare_invoice_line(**optional_values)
        # ส่งข้อมูลส่วนลดทั้งแบบ Fixed และ Percentage ไปยังใบแจ้งหนี้
        res.update({
            'discount': self.discount,  # ส่งเปอร์เซ็นต์ส่วนลด
            'discount_fixed': self.discount_fixed,  # ส่งส่วนลดแบบจำนวนเงิน (Fixed Amount)
        })
        return res

    def calculate_line_count(self, text, max_width_px=300, font_size_px=18, avg_char_width_px=6):
        """
        คำนวณจำนวนบรรทัดจากความยาวของข้อความ และตรวจสอบการขึ้นบรรทัดใหม่ด้วยการกด Enter
        """
        # คำนวณจำนวนตัวอักษรที่พอดีใน 1 บรรทัดตามความกว้างที่กำหนด
        max_chars_per_line = max_width_px // avg_char_width_px

        english_count = 0
        thai_count = 0

        # แยกข้อความตามบรรทัดที่ผู้ใช้กด Enter เพื่อดูว่ามีกี่บรรทัด
        lines = text.split('\n')  # แยกตาม \n (Enter)

        total_lines = 0
        for line in lines:
            for char in line:
                # เช็คว่าตัวอักษรอยู่ในช่วงอักษรไทยหรือไม่
                if 'ก' <= char <= 'ฮ' or 'เ' <= char <= '์':  # ช่วงของอักษรไทย
                    thai_count += 1.5  # ให้ค่าเป็น 1.5 หน่วยสำหรับภาษาไทย
                else:
                    english_count += 1  # ให้ภาษาอังกฤษเป็น 1 หน่วย

            # คำนวณความยาวทั้งหมดของแต่ละบรรทัด
            total_length = english_count + thai_count
            # คำนวณจำนวนบรรทัดที่ต้องใช้สำหรับบรรทัดปัจจุบัน
            total_lines += (total_length // max_chars_per_line) + (1 if total_length % max_chars_per_line else 0)

            # รีเซ็ตค่า count หลังจากจบบรรทัดหนึ่ง
            english_count = 0
            thai_count = 0

        return total_lines

    def get_line_count(self):
        # เรียกใช้ฟังก์ชัน calculate_line_count เพื่อคำนวณจำนวนบรรทัดของฟิลด์ 'name'
        return self.calculate_line_count(self.name)

    # amount_total_invoice_text = fields.Char(string='Total(Text)', store=True, readonly=True,
    #                                         compute='amount_invoice_move_text',
    #                                         track_visibility='always')
    #
    # @api.depends('amount_total')
    # def amount_invoice_move_text(self):
    #     for record in self:
    #         amount_invoice_text = bahttext(record.amount_total)
    #         record.amount_total_invoice_text = amount_invoice_text

