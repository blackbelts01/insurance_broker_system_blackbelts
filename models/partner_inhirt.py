from odoo import models, fields, api
from odoo.exceptions import ValidationError



class inhertResPartner(models.Model):
    _inherit = 'res.partner'

    insurer_type=fields.Boolean('Insurer')
    agent=fields.Boolean('Agent')
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

    @api.one
    def _compute_policy_count(self):
        if self.customer == 1:
            for partner in self:
                operator = 'child_of' if partner.is_company else '='
                partner.policy_count = self.env['policy.broker'].search_count(
                    [('customer', operator, partner.id)])

        elif self.insurer_type == 1:
            for partner in self:
                operator = 'child_of' if partner.is_company else '='
                partner.policy_count = self.env['policy.broker'].search_count(
                    [('company', operator, partner.id)])
        elif self.agent == 1:
            for partner in self:
                operator = 'child_of' if partner.is_company else '='
                partner.policy_count = self.env['policy.broker'].search_count(
                    [('salesperson', operator, partner.id)])
    @api.multi
    def show_partner_policies(self):
        if self.customer == 1:
            return {
                'name': ('Policy'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'policy.broker',  # model name ?yes true ok
                'target': 'current',
                'type': 'ir.actions.act_window',
                'context': {'default_customer': self.id},
                'domain': [('customer', '=', self.id)]
            }
        elif self.insurer_type == 1:
            return {
                'name': ('Policy'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'policy.broker',  # model name ?yes true ok
                'target': 'current',
                'type': 'ir.actions.act_window',
                'context': {'default_company': self.id},
                'domain': [('company', '=', self.id)]
            }
        elif self.agent == 1:
            return {
                'name': ('Policy'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'policy.broker',  # model name ?yes true ok
                'target': 'current',
                'type': 'ir.actions.act_window',
                'context': {'default_salesperson': self.id},
                'domain': [('salesperson', '=', self.id)]
            }
    @api.one
    def _compute_claim_count(self):
        if self.customer == 1:
            for partner in self:
                operator = 'child_of' if partner.is_company else '='
                partner.claim_count = self.env['insurance.claim'].search_count(
                    [('customer_policy', operator, partner.id)])
        elif self.insurer_type == 1:
            for partner in self:
                operator = 'child_of' if partner.is_company else '='
                partner.claim_count = self.env['insurance.claim'].search_count(
                    [('insurer', operator, partner.id)])
        elif self.agent == 1:
            for partner in self:
                operator = 'child_of' if partner.is_company else '='
                policy = self.env['policy.broker'].search(
                    [('salesperson', operator, partner.id)]).ids
                partner.claim_count = self.env['insurance.claim'].search_count(
                    [('policy_number', operator, policy)])



    @api.multi
    def show_partner_claim(self):
        if self.customer == 1:
            return {
                'name': ('Claim'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'insurance.claim',  # model name ?yes true ok
                'target': 'current',
                'type': 'ir.actions.act_window',
                'context': {'default_customer_policy': self.id},
                'domain': [('customer_policy', '=', self.id)]
            }
        elif self.insurer_type == 1:
            return {
                'name': ('Claim'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'insurance.claim',  # model name ?yes true ok
                'target': 'current',
                'type': 'ir.actions.act_window',
                'context': {'default_insurer': self.id},
                'domain': [('insurer', '=', self.id)]
            }
        elif self.agent == 1:
            return {
                'name': ('Claim'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'insurance.claim',  # model name ?yes true ok
                'target': 'current',
                'type': 'ir.actions.act_window',
                # 'context': {'default_agent': self.id},
                'domain': [('policy_number.salesperson', '=', self.id)]
            }

    @api.multi
    def partner_report_opp(self):
        if self.insurer_type:
            proposal = self.env['proposal.opp.bb'].search([('Company', '=', self.id)]).ids
            opp = self.env['crm.lead'].search([('proposal_opp', 'in', proposal)])
            return opp
        elif self.customer:
            opp = self.env['crm.lead'].search([('partner_id', '=', self.id)])
            return opp
        elif self.agent:
            print("***************")
            opp = self.env['crm.lead'].search([('user_id.partner_id', '=', self.id)])
            return opp
    @api.multi
    def partner_report_policy(self):
        if self.insurer_type:
            # proposal = self.env['proposal.opp.bb'].search([('Company', '=', self.id)]).ids
            policy = self.env['policy.broker'].search([('company', '=', self.id)])
            return policy
        elif self.customer:
            # proposal = self.env['proposal.opp.bb'].search([('Company', '=', self.id)]).ids
            policy = self.env['policy.broker'].search([('customer', '=', self.id)])
            return policy
        elif self.agent:
            print("***************")
            policy = self.env['policy.broker'].search([('salesperson', '=', self.id)])
            return policy

    @api.multi
    def partner_report_claim(self):
        if self.insurer_type:
            # proposal = self.env['proposal.opp.bb'].search([('Company', '=', self.id)]).ids
            claim = self.env['insurance.claim'].search([('insurer', '=', self.id)])
            return claim
        elif self.customer:
            claim = self.env['insurance.claim'].search([('customer_policy', '=', self.id)])
            return claim
        elif self.agent:
            policy = self.env['policy.broker'].search([('salesperson', '=', self.id)]).ids
            claim = self.env['insurance.claim'].search([('policy_number', 'in', policy)])
            return claim





    # @api.multi
    # def partner_report_opp_agent(self):
    #     opp = self.env['crm.lead'].search([('user_id', '=', self.id)])
    #     return opp
    #
    # @api.multi
    # def partner_report_policy_agent(self):
    #     policy = self.env['policy.broker'].search([('salesperson', '=', self.id)])
    #     return policy
    #
    # @api.multi
    # def partner_report_claim_agent(self):
    #     policy = self.env['policy.broker'].search([('salesperson', '=', self.id)]).ids
    #     claim = self.env['insurance.claim'].search([('policy_number', 'in', policy)])
    #     return claim
