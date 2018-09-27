from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError

class claimPolicy(models.Model):
    _name ="insurance.claim"

    name = fields.Char(string='Claim Number', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    intimation_date=fields.Date(string='Intimation Date')
    intimation_no=fields.Char(string='Intimation No')
    dateofloss=fields.Date(string='Date of Loss')
    causeofloss=fields.Many2one('insurance.setup.item',string='Cause of Loss',domain="[('setup_id.setup_key','=','closs')]")
    natureofloss=fields.Many2one('insurance.setup.item',string='Nature of Loss',domain="[('setup_id.setup_key','=','nloss')]")
    lossdesc=fields.Text(string='Loss Desc.')
    naturelossdesc = fields.Text(string='Nature of Loss Desc.')
    typeofgoods = fields.Many2one('insurance.setup.item', string='Type of Goods',domain="[('setup_id.setup_key','=','goods')]")
    remarks=fields.Char(string='Close/Open Remarks')
    totalloss=fields.Boolean(string='Total Loss')
    totalclaimexp=fields.Float(string='Total Claim Expected')
    totalsettled=fields.Float(string='Total Settled',compute='_onchange_totalsettled')
    totalunpaid = fields.Float(string='Total Unpaid',compute='_onchange_total_unpaid')

    claimstatus=fields.Many2one('insurance.setup.item',string='Claim Status',domain="[('setup_id.setup_key','=','state')]")
    policy_number = fields.Many2one('policy.broker',string='Policy Number',required=True,domain="[('edit_number','=',False)]")
    endorsement= fields.Many2one('policy.broker',string='Endorsement Number',domain="['&',('edit_number','!=',False),('std_id','=',related_policy)]")
    related_policy=fields.Char(related='policy_number.std_id',store=True,readonly=True)
    customer_policy=fields.Many2one('res.partner',string='Customer',store=True,readonly=True)
    insured=fields.Char(string='Insured',store=True)
    beneficiary = fields.Char(string='Beneficiary', store=True,readonly=True)
    currency = fields.Many2one('res.currency',string="Currency")
    lob = fields.Many2one('insurance.line.business', string='Line of Business', store=True,readonly=True)
    product = fields.Many2one('insurance.product', string='Product', store=True,readonly=True)
    insurer = fields.Many2one('res.partner', string='Insurer', store=True,readonly=True)
    insurer_branch= fields.Many2one('res.partner',related='insurer.insurer_branch', string='Insurer Branch', store=True,
                              readonly=True)
    insurer_contact= fields.Many2one('res.partner',string='Insurer Contact',domain="[('insurer_type','=',1)]")
    total_paid_amount=fields.Float(string='Total Paid Amount',compute='_onchange_payment_history')
    settlement_type=fields.Many2one('insurance.setup.item',string='Settlement Type',domain="[('setup_id.setup_key','=','setltype')]")
    settle_history=fields.One2many('settle.history','claimheader',string='Settle History')
    payment_history=fields.One2many('payment.history','header_payment',string='Payment History')
    claim_action=fields.One2many('product.claim.action','claim',related='product.claim_action')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.claim') or 'New'
        return super(claimPolicy, self).create(vals)

    @api.onchange('endorsement','policy_number')
    def _onchange_policy_details(self):
        if self.endorsement:
            self.customer_policy = self.endorsement.customer
            self.insured = self.endorsement.line_of_bussines.object
            self.lob = self.endorsement.line_of_bussines
            self.product = self.endorsement.product_policy
            self.insurer = self.endorsement.company
            self.beneficiary = self.endorsement.benefit
            self.currency = self.endorsement.currency_id.id

        else:
            self.customer_policy=self.policy_number.customer
            self.insured =self.policy_number.line_of_bussines.object
            self.lob=self.policy_number.line_of_bussines
            self.product=self.policy_number.product_policy
            self.insurer=self.policy_number.company
            self.beneficiary=self.policy_number.benefit
            self.currency = self.policy_number.currency_id.id

    @api.one
    @api.depends('payment_history')
    def _onchange_payment_history(self):
        total=0
        for record in self.payment_history:
            total+=record.paid_amount
        self.total_paid_amount=total

    @api.onchange('total_paid_amount','totalclaimexp')
    def _onchange_total_unpaid(self):
        self.totalunpaid=self.totalclaimexp - self.total_paid_amount

    @api.one
    @api.depends('settle_history')
    def _onchange_totalsettled(self):
        total=0
        for record in self.settle_history:
            total+=record.sum_insured
        self.totalsettled=total


class settleHistory(models.Model):
    _name ="settle.history"

    risk_type=fields.Char(related='claimheader.insured',string='Risk Type',readonly=True,store=True)
    risk_id=fields.Many2one('new.risks',string='Risk')
    #Vehicle details
    vcar_type = fields.Char(related='risk_id.car_tybe',string='Vehicle Type')
    vmotor_cc = fields.Char(related='risk_id.motor_cc',string="Motor cc")
    vyear_of_made = fields.Date(related='risk_id.year_of_made',string="Year of Made")
    vmodel = fields.Char(related='risk_id.model',string="Motor Model")
    vbrande = fields.Char(related='risk_id.Man',string='Vehicle Brande')
    #Person details
    pname = fields.Char(related='risk_id.name',string='Name')
    p_birthday = fields.Date(related='risk_id.DOB',string='Date Of Birth')
    pjob = fields.Char(related='risk_id.job',string='Job Tiltle')
    #Cargo details
    cfrom = fields.Char(related='risk_id.From',string='From')
    cto = fields.Char(related='risk_id.To',string='To')
    ctype = fields.Char(related='risk_id.cargo_type',string="Type Of Cargo")
    cweight = fields.Float(related='risk_id.weight',string='Weight')

    risk_details = fields.Char(related='risk_id.risk_description',string='Risk Description')
    coverage = fields.Many2one('covers.lines',string='Coverage')
    sum_insured=fields.Float(related='coverage.sum_insure',string='Sum Insured',store=True,readonly=True)
    settle_amount=fields.Float(string='Settle Amount',compute='_onchange_settle_amount')
    settle_date=fields.Date(string='Settle Date')
    status=fields.Many2one('insurance.setup.item',string='Status',domain="[('setup_id.setup_key','=','state')]")
    claimheader=fields.Many2one('insurance.claim')
    endorsement_related=fields.Many2one('policy.broker',store=True,readonly=True)
    claim_item=fields.One2many('insurance.claim.item','settle_history',string='Repair/Claim Items')

    @api.onchange('claimheader')
    def _onchange_endo(self):
      if self.claimheader.endorsement:
          self.endorsement_related=self.claimheader.endorsement.id
      else:
          self.endorsement_related = self.claimheader.policy_number.id


    @api.onchange('claimheader')
    def _onchange_risk_id(self):
      if self.endorsement_related:
           return {'domain': {'risk_id': [('policy_risk_id','=',self.endorsement_related.id if self.endorsement_related else False)]}}

    @api.onchange('risk_id')
    def _onchange_cover(self):
      if self.endorsement_related:
          return {'domain': {'coverage': [('policy_rel_id', '=', self.endorsement_related.id if self.endorsement_related else False),('riskk', '=', self.risk_id.id if self.risk_id else False)]}}

    @api.one
    @api.depends('claim_item')
    def _onchange_settle_amount(self):
        total=0
        for record in self.claim_item:
            total+=record.amount
        self.settle_amount=total


class paymentHistory(models.Model):
    _name ="payment.history"

    payment_date=fields.Date(string='Payment Date')
    paid_amount=fields.Float(string='Paid Amount')
    currency=fields.Many2one('res.currency', string="Currency")
    check_bank=fields.Char(string='Check Bank')
    check_number=fields.Char(string='Check Number')
    payee=fields.Char(string='Payee Name')
    header_payment=fields.Many2one('insurance.claim')

class claimItem(models.Model):
    _name ="insurance.claim.item"
    _rec_name = "claim_item"

    claim_item=fields.Many2one('insurance.setup.item',string='Items',domain="[('setup_id.setup_key','=','clmitem')]")
    amount=fields.Float(string='Cost')
    settle_history=fields.Many2one('settle.history')






