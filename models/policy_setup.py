from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Policy_Info(models.Model):
    _name ="insurance.line.business"
    _rec_name = 'line_of_business'

    insurance_type = fields.Selection([('life', 'Life'),
                          ('p&c', 'P&C'),
                          ('health', 'Health'), ],
                         'Insured Type', track_visibility='onchange', required=True)
    line_of_business = fields.Char(string='Line of Business', required=True)
    object= fields.Selection([('person', 'Person'),
                          ('vehicle', 'Vehicle'),
                          ('cargo', 'Cargo'),
                          ('location', 'Location'),],
                         'Insured Object', track_visibility='onchange', required=True)
    desc = fields.Char(string='Description')
    income_account=fields.Many2one('account.account','Income Account')
    expense_account = fields.Many2one('account.account','Expense Account')


class Product(models.Model):
    _name='insurance.product'
    _rec_name = 'product_name'

    product_name=fields.Char('Product Name',required=True)
    insurer=fields.Many2one('res.partner', string="Insurer",domain="[('insurer_type','=',1)]")
    line_of_bus=fields.Many2one('insurance.line.business','Line of Business')
    coverage=fields.One2many('insurance.product.coverage','product_id',string='Coverage')
    brokerage=fields.One2many('insurance.product.brokerage','product_id',string='Brokerage')
    commision_id = fields.One2many("commision.setup","policy_relation_id")
    claim_action=fields.One2many('product.claim.action','product')
    name_cover_id = fields.Many2one("name.cover")

class claimAction(models.Model):
    _name='product.claim.action'

    action=fields.Char('Claim Action')
    completed=fields.Boolean(string='Completed')
    comments=fields.Text(string='Comments')
    product=fields.Many2one('insurance.product')
    claim=fields.Many2one('insurance.claim')




class coverage(models.Model):
    _name='insurance.product.coverage'
    _rec_name= "Name"

    Name=fields.Char('Cover Name')
    defaultvalue=fields.Float('Default Sum Insured')
    required=fields.Boolean('Required')
    deductible = fields.Integer('Deductible')
    limitone=fields.Integer('Limit in One')
    limittotal=fields.Integer('Limit in Total')
    readonly=fields.Boolean('Read Only')
    product_id=fields.Many2one('insurance.product')
    lop_id=fields.Many2one('insurance.line.business',string='Line of Business')


class Brokerage(models.Model):
    _name='insurance.product.brokerage'

    datefrom=fields.Date('Date from')
    dateto=fields.Date('Date to')
    basic_commission = fields.Float('Basic Commission')
    complementary_commission = fields.Float('Complementary Commission')
    early_collection = fields.Float('Early Collection Commission')
    fixed_commission = fields.Monetary(default=0.0, currency_field='company_currency_id',string='Fixed Commission')
    company_currency_id = fields.Many2one('res.currency', related='product_id.insurer.currency_id', string="Company Currency", readonly=True,store=True)
    product_id = fields.Many2one('insurance.product')

    @api.constrains('datefrom')
    def _constrain_date(self):
        for record in self:
            if record.dateto < record.datefrom:
                raise ValidationError('Error! Date to Should be After Date from')




class insuranceSetup(models.Model):
    _name = 'insurance.setup'

    setup_key=fields.Selection([('closs', 'CLoss'),
                          ('nloss', 'NLoss'),
                          ('goods', 'Goods'),
                          ('setltype', 'SetlType'),
                          ('state', 'State'),
                          ('clmitem', 'CLMItem'),],
                         'KEY', track_visibility='onchange', required=True)
    setup_id=fields.Char(string='ID')
    setup_item=fields.One2many('insurance.setup.item','setup_id',string='List Items')

class insuranceSetupItem(models.Model):
    _name = 'insurance.setup.item'

    name=fields.Char('Item')
    setup_id=fields.Many2one('insurance.setup')




