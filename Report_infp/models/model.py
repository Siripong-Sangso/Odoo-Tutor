from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CustomerBillingInherit(models.Model):
    _inherit = 'customer.billing'

    amount_total_text_th = fields.Char(
        string="Amount Total Text (TH)",
        compute="_compute_amount_total_text_th",
        store=True
    )

    @api.model
    def get_line_count(self):
        return len(self.name.splitlines())

    @api.depends('amount_total')
    def _compute_amount_total_text_th(self):
        for order in self:
            order.amount_total_text_th = self._number_to_thai_text(order.amount_total)

    def _number_to_thai_text(self, number):
        thai_num = ["", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
        thai_unit = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
        result = ""
        number_str = str(int(number))
        number_len = len(number_str)

        for i in range(number_len):
            digit = int(number_str[i])
            unit_index = number_len - i - 1

            if digit != 0:
                if unit_index == 1 and digit == 1:
                    result += "สิบ"
                elif unit_index == 1 and digit == 2:
                    result += "ยี่สิบ"
                elif unit_index == 0 and digit == 1 and number_len > 1:
                    result += "เอ็ด"
                else:
                    result += thai_num[digit] + thai_unit[unit_index]
        return result


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    def get_line_count(self):
        """
        นับจำนวนบรรทัดในฟิลด์ name
        """
        self.ensure_one()  # ตรวจสอบให้แน่ใจว่าใช้กับเรคคอร์ดเดียว
        return len(self.name.splitlines()) if self.name else 0

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    amount_total_text_th = fields.Char(
        string="Amount Total Text (TH)",
        compute="_compute_amount_total_text_th",
        store=True
    )

    @api.depends('move_ids_without_package.price_unit', 'move_ids_without_package.quantity_done')
    def _compute_amount_total_text_th(self):
        for picking in self:
            total_amount = sum(line.price_unit * line.quantity_done for line in picking.move_ids_without_package)
            picking.amount_total_text_th = self._number_to_thai_text(total_amount)

    def _number_to_thai_text(self, number):
        thai_num = ["", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
        thai_unit = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
        result = ""
        number_str = str(int(number))
        number_len = len(number_str)

        for i in range(number_len):
            digit = int(number_str[i])
            unit_index = number_len - i - 1

            if digit != 0:
                if unit_index == 1 and digit == 1:
                    result += "สิบ"
                elif unit_index == 1 and digit == 2:
                    result += "ยี่สิบ"
                elif unit_index == 0 and digit == 1 and number_len > 1:
                    result += "เอ็ด"
                else:
                    result += thai_num[digit] + thai_unit[unit_index]
        return result

    def _get_report_values(self, docids, data=None):
        """
        เตรียมข้อมูลสำหรับ QWeb Template
        """
        docs = self.env['stock.picking'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': docs,
        }


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    project_name = fields.Char(string="Project Name")
    amount_total_text_th = fields.Char(
        string="Amount Total Text (TH)",
        compute="_compute_amount_total_text_th",
        store=True
    )

    @api.model
    def get_line_count(self):
        return len(self.name.splitlines())

    @api.depends('amount_total')
    def _compute_amount_total_text_th(self):
        for order in self:
            order.amount_total_text_th = self._number_to_thai_text(order.amount_total)

    def _number_to_thai_text(self, number):
        thai_num = ["", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
        thai_unit = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
        result = ""
        number_str = str(int(number))
        number_len = len(number_str)

        for i in range(number_len):
            digit = int(number_str[i])
            unit_index = number_len - i - 1

            if digit != 0:
                if unit_index == 1 and digit == 1:
                    result += "สิบ"
                elif unit_index == 1 and digit == 2:
                    result += "ยี่สิบ"
                elif unit_index == 0 and digit == 1 and number_len > 1:
                    result += "เอ็ด"
                else:
                    result += thai_num[digit] + thai_unit[unit_index]
        return result

    def _get_report_values(self, docids, data=None):
        """
        เตรียมข้อมูลสำหรับ QWeb Template
        """
        docs = self.env['account.move'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
        }


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    @api.constrains('company_name_th')
    def _check_company_name_th(self):
        for record in self:
            if record.company_name_th and any(char.isdigit() for char in record.company_name_th):
                raise ValidationError("The Thai company name should not contain any digits.")


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    amount_total_text_th = fields.Char(
        string="Amount Total Text (TH)",
        compute="_compute_amount_total_text_th",
        store=True
    )

    @api.depends('amount_total')
    def _compute_amount_total_text_th(self):
        for order in self:
            order.amount_total_text_th = self._number_to_thai_text(order.amount_total)

    def _number_to_thai_text(self, number):
        thai_num = ["", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
        thai_unit = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
        result = ""
        number_str = str(int(number))
        number_len = len(number_str)

        for i in range(number_len):
            digit = int(number_str[i])
            unit_index = number_len - i - 1

            if digit != 0:
                if unit_index == 1 and digit == 1:
                    result += "สิบ"
                elif unit_index == 1 and digit == 2:
                    result += "ยี่สิบ"
                elif unit_index == 0 and digit == 1 and number_len > 1:
                    result += "เอ็ด"
                else:
                    result += thai_num[digit] + thai_unit[unit_index]
        return result

    @api.constrains('partner_mobile')
    def _check_partner_mobile(self):
        for record in self:
            if record.partner_mobile and not record.partner_mobile.isdigit():
                raise ValidationError("The mobile number should contain only digits.")


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    def get_line_count(self):
        """
        นับจำนวนบรรทัดในฟิลด์ name
        """
        self.ensure_one()  # ตรวจสอบให้แน่ใจว่าใช้กับเรคคอร์ดเดียว
        return len(self.name.splitlines()) if self.name else 0


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    def get_line_count(self):
        """
        นับจำนวนบรรทัดในฟิลด์ name
        """
        self.ensure_one()  # ตรวจสอบให้แน่ใจว่าใช้กับเรคคอร์ดเดียว
        return len(self.name.splitlines()) if self.name else 0
