from odoo import models, fields, api
from odoo.exceptions import ValidationError



class inhertHREmployee(models.Model):
    _inherit = 'hr.employee'

    assets=fields.One2many('account.asset.asset','employee_id',string='Assets')



class inhertAssets(models.Model):
    _inherit = 'account.asset.asset'

    employee_id=fields.Many2one('hr.employee',string='Employee')
