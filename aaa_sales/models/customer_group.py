# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CustomerGroup(models.Model):
    _name = 'customer.group'
    _description = 'Customer Group'

    name = fields.Char(string="Group Name", required=True)
    description = fields.Text(string="Description")
    contact_ids = fields.Many2many('res.partner', string='Contacts',
                                   help='Add contacts to the customer group')
    pricelist_id = fields.Many2one(
        'product.pricelist', string="Pricelist", required=True,
        help="Select the pricelist that will apply to this group."
    )
    sales_team_id = fields.Many2one(
        'crm.team', string="Sales Team",
        help="Select the Sales Team responsible for this customer group."
    )
    approval = fields.Boolean(string="Approved", help="Approval from the manager is required before creating a Sales Order.")

    def write(self, vals):
        """
        Override write to update res.partner when contact_ids are changed in customer.group.
        """
        res = super(CustomerGroup, self).write(vals)

        if 'contact_ids' in vals:
            # อัปเดต customer_group_id และ Pricelist สำหรับ contacts ที่ถูกเพิ่ม
            for group in self:
                for contact in group.contact_ids:
                    if contact.customer_group_id != group:
                        contact.write({
                            'customer_group_id': group.id,
                            'property_product_pricelist': group.pricelist_id.id if group.pricelist_id else False
                        })

                # ลบ customer_group_id และ Pricelist สำหรับ contacts ที่ถูกลบออกจากกลุ่ม
                all_partners = self.env['res.partner'].search([('customer_group_id', '=', group.id)])
                for partner in all_partners:
                    if partner not in group.contact_ids:
                        partner.write({
                            'customer_group_id': False,
                            'property_product_pricelist': False
                        })

        return res

    @api.model
    def create(self, vals):
        """
        Override create to update res.partner when a new customer.group is created.
        """
        group = super(CustomerGroup, self).create(vals)

        # อัปเดต customer_group_id และ Pricelist สำหรับ contacts ที่ถูกเพิ่ม
        if 'contact_ids' in vals:
            for contact in group.contact_ids:
                contact.write({
                    'customer_group_id': group.id,
                    'property_product_pricelist': group.pricelist_id.id if group.pricelist_id else False
                })

        return group