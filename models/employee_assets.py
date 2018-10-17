from odoo import models, fields, api
from odoo.exceptions import ValidationError



class inhertHREmployee(models.Model):
    _inherit = 'hr.employee'

    assets=fields.One2many('account.asset.asset','employee_id',string='Assets')

    @api.multi
    def partner_report_opp_agent(self):
        opp = self.env['crm.lead'].search([('user_id', '=', self.user_id.id)])
        return opp

    @api.multi
    def partner_report_policy_agent(self):
        policy = self.env['policy.broker'].search([('salesperson', '=', self.user_id.id)])
        return policy

    @api.multi
    def partner_report_claim_agent(self):
        policy = self.env['policy.broker'].search([('salesperson', '=', self.user_id.id)]).ids
        claim = self.env['insurance.claim'].search([('policy_number', 'in', policy)])
        return claim



class inhertAssets(models.Model):
    _inherit = 'account.asset.asset'

    employee_id=fields.Many2one('hr.employee',string='Employee')
