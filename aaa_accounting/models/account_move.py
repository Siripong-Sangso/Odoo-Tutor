# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class AccountMove(models.Model):
    _inherit = "account.move"

    project_name = fields.Char(string='Project', readonly=True, states={'draft': [('readonly', False)]})
    billing_number = fields.Char(string="Billing", default='', copy=False)
    billing_id = fields.Many2one('customer.billing', string="Billing Number", copy=False)
    tax_invoice_reference = fields.Char(string="Tax Invoice Reference",
                                        help="Reference to the original tax invoice related to this Credit Note.",
                                        readonly=True)

    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        if move.move_type == 'out_refund' and move.reversed_entry_id:  # เช็คว่าเป็น Credit Note
            move.tax_invoice_reference = move.reversed_entry_id.name  # กำหนดเลขอ้างอิงจากใบกำกับภาษีเดิม
        return move

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

    @api.depends('line_ids.price_unit', 'line_ids.quantity')
    def _compute_total_before_discount_and_tax(self):
        """
        คำนวณราคารวมก่อนหักส่วนลดและภาษีใน Invoice
        """
        for invoice in self:
            total = sum(line.price_unit * line.quantity for line in invoice.line_ids)
            invoice.total_before_discount_and_tax = total

    @api.depends('line_ids.discount_fixed', 'line_ids.discount', 'line_ids.price_unit', 'line_ids.quantity')
    def _compute_total_discount(self):
        """
        คำนวณส่วนลดรวมทั้งหมด (Fixed และ Percent) ใน Invoice
        """
        for invoice in self:
            total_discount = sum(
                line.discount_fixed or (line.price_unit * line.quantity * line.discount / 100) for line in
                invoice.line_ids)
            invoice.total_discount = total_discount

    @api.depends('total_before_discount_and_tax', 'total_discount')
    def _compute_total_after_discount(self):
        """
        คำนวณยอดรวมหลังหักส่วนลดใน Invoice
        """
        for invoice in self:
            invoice.total_after_discount = invoice.total_before_discount_and_tax - invoice.total_discount

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = 'debit desc'

    invoice_date = fields.Date(string='Invoice/Bill Date', related='move_id.invoice_date')

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits="Product Price",
        help="Fixed amount discount.",
    )

    disc_flag = fields.Boolean(default=False)

    @api.onchange('discount_fixed', 'price_unit', 'quantity')
    def _onchange_discount_fixed(self):
        """
        คำนวณส่วนลดแบบเปอร์เซ็นต์จากส่วนลดแบบจำนวนเงิน (Fixed Amount)
        """
        if not self.disc_flag and self.discount_fixed:
            total_price = self.price_unit * self.quantity
            if total_price != 0:
                self.discount = (self.discount_fixed / total_price) * 100
            self.disc_flag = True

    @api.onchange('discount', 'price_unit', 'quantity')
    def _onchange_discount(self):
        """
        คำนวณส่วนลดแบบจำนวนเงินจากส่วนลดแบบเปอร์เซ็นต์
        """
        if not self.disc_flag and self.discount:
            total_price = self.price_unit * self.quantity
            self.discount_fixed = (self.discount / 100) * total_price
        self.disc_flag = True

    @api.onchange('discount_fixed', 'discount')
    def _reset_flags(self):
        """
        Reset the discount flag after changes to prevent recursion
        """
        self.disc_flag = False

    @api.depends('discount_fixed', 'discount', 'price_unit', 'quantity', 'tax_ids')
    def _compute_amount(self):
        """
        คำนวณราคาหลังหักส่วนลด (ทั้งแบบ Fixed และ Percent) และภาษี
        """
        for line in self:
            total_price = line.price_unit * line.quantity
            discount_amount = line.discount_fixed or (total_price * line.discount / 100)
            price_after_discount = total_price - discount_amount
            taxes = line.tax_ids.compute_all(price_after_discount, line.move_id.currency_id, line.quantity,
                                             product=line.product_id, partner=line.move_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


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