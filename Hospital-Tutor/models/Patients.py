from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = "mail.thread"
    _description = "Patient Records"

    name = fields.Char(string='Name', required=True, tracking=True)
    age = fields.Integer(string="Age", tracking=True)
    is_child = fields.Boolean(string="Is Child ?", tracking=True)
    notes = fields.Text(string="Notes")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others','Others')],
                              string="Gender", tracking=True)
    blood_type = fields.Selection([('a', 'A'), ('b', 'B'), ('ab', 'AB'), ('o', 'O')],
                                  string="Blood Type", tracking=True)
    capitalized_name = fields.Char(string='Capitalized Name', compute='_compute_capitalized_name',
                                   store=True)
    ref = fields.Char(string="Reference", default=lambda self: _('New'))
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    tag_id = fields.Many2many('res.partner.category', 'hospital_patient_tag_rel',
                              'patient_id', 'tag_id', string="Tags")
    image = fields.Binary(string='Image')
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company,
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string="Assigned User",
        help="The user responsible for this patient record"
    )

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hospital.patient'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hospital.patient',
            'docs': docs,
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).create(vals_list)


    @api.constrains('is_child', 'age')
    def _check_child_age(self):
        for rec in self:
            if rec.is_child and rec.age == 0:
                raise ValidationError(_("Age has to be recorded !"))

    @api.depends('name')
    def _compute_capitalized_name(self):
        for rec in self:
            if rec.name:
                rec.capitalized_name = rec.name.upper()
            else:
                rec.capitalized_name = ''

    @api.onchange('age')
    def _onchange_age(self):
        if self.age <= 10:
            self.is_child = True
        else:
            self.is_child = False