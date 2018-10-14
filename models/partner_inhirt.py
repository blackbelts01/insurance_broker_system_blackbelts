from odoo import models, fields, api
from odoo.exceptions import ValidationError



class inhertResPartner(models.Model):
    _inherit = 'res.partner'

    insurer_type=fields.Boolean('Insurer')
    insurer_branch=fields.Many2one("res.partner",string="Insurer Branch")
    holding_type=fields.Boolean("Holding")
    holding_company=fields.Many2one("res.partner",string="Holding Company")
    numberofchildren=fields.Integer('Number of Children')
    policy_count=fields.Integer(compute='_compute_policy_count')
    claim_count=fields.Integer(compute='_compute_claim_count')

    C_industry=fields.Many2one('insurance.setup.item',string='Industry',domain="[('setup_id.setup_key','=','industry')]")
    DOB=fields.Date('Date of Birth')
    martiual_status = fields.Selection([('Single', 'Single'),
                                        ('Married', 'Married'),],
                                       'Marital Status', track_visibility='onchange')
    last_time_insure = fields.Date('Last Time Insure')

    @api.multi
    def _compute_policy_count(self):
        for partner in self:
            operator = 'child_of' if partner.is_company else '='
            partner.policy_count = self.env['policy.broker'].search_count(
                [('customer', operator, partner.id)])
    @api.multi
    def show_partner_policies(self):
        return {
            'name': ('Policy'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'policy.broker',#model name ?yes true ok
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {'default_customer':self.id},
            'domain': [('customer','=',self.id)]
        }
    @api.multi
    def _compute_claim_count(self):
        for partner in self:
            operator = 'child_of' if partner.is_company else '='
            partner.claim_count = self.env['insurance.claim'].search_count(
                [('customer_policy', operator, partner.id)])
    @api.multi
    def show_partner_claim(self):
        return {
            'name': ('Claim'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'insurance.claim',#model name ?yes true ok
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {'default_customer_policy':self.id},
            'domain': [('customer_policy','=',self.id)]
        }

    # @api.multi
    # def _compute_policy_dis(self):
    #     self.policy_display = str(self.policy_count) + "Policies"
    #
    #
    # @api.multi
    # def _compute_claim_dis(self):
    #     self.claim_display = str(self.claim_count) + "Claims"



