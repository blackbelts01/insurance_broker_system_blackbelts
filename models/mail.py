from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError

# class mailMessages(models.Model):
#     _inherit = 'mail.message'
#
#     userId = fields.Many2one(related='uid.partner_id')
#
#     @api.onchange('author_id')
#     def onchage(self):
#         print (self.userId)