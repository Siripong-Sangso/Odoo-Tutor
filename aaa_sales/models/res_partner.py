# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_group_id = fields.Many2one(
        'customer.group', string="Customer Group",
        help="Assign the customer to a specific group."
    )

    def create(self, vals):
        """
        Override create to update contact_ids in customer.group when a new res.partner is created.
        """
        # สร้างเรคคอร์ดใหม่
        partner = super(ResPartner, self).create(vals)

        # ตรวจสอบว่า customer_group_id ถูกตั้งค่าหรือไม่
        if 'customer_group_id' in vals and vals['customer_group_id']:
            group = self.env['customer.group'].browse(vals['customer_group_id'])
            if group:
                # เพิ่มลูกค้าใน contact_ids ของ Customer Group
                group.contact_ids = [(4, partner.id)]

        return partner

    def write(self, vals):
        """
        Override write to update contact_ids in customer.group when customer_group_id is changed in res.partner.
        """
        # เรียกใช้ write ของ superclass
        res = super(ResPartner, self).write(vals)

        # ตรวจสอบว่า customer_group_id มีการเปลี่ยนแปลงหรือไม่
        if 'customer_group_id' in vals:
            for partner in self:
                # เพิ่มลูกค้าใน contact_ids ของ Customer Group ที่เลือก
                if partner.customer_group_id:
                    partner.customer_group_id.contact_ids = [(4, partner.id)]

                # ลบลูกค้าออกจาก contact_ids ของ Customer Group อื่น (ถ้ามี)
                other_groups = self.env['customer.group'].search([('contact_ids', 'in', partner.id)])
                for group in other_groups:
                    if group.id != partner.customer_group_id.id:
                        group.contact_ids = [(3, partner.id)]

        return res