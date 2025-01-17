# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2021. All rights reserved.

from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _compute_group_payment(self):
        res = super(AccountPaymentRegister, self)._compute_group_payment()
        for wizard in self:
            if wizard.can_edit_wizard:
                batches = wizard._get_batches()
                if len(batches[0]['lines'].move_id) >= 1 and 'cust_billing' in self.env.context:
                    wizard.group_payment = True
        return res





