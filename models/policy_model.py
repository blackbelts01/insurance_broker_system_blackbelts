import random
import string
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class PolicyBroker(models.Model):
    _name = "policy.broker"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.multi
    def show_claim(self):
        return {
            'name': ('Claim'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'insurance.claim',  # model name ?yes true ok
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {'default_policy_number': self.id},
            'domain': [('policy_number', '=', self.id)]
        }



    @api.model
    def default_get(self, fields):
            res = super(PolicyBroker, self).default_get(fields)
            if self._context.get('active_model') != 'crm.lead':
                return res
            lead = self.env['crm.lead'].browse(self._context.get('active_id'))

            recordrisks = self.env['new.risks'].search([('id', 'in', lead.objectrisks.ids)])
            print(recordrisks)
            records_risks = []
            for rec in recordrisks:
                records_risks.append(rec.id)

            recordproposal = self.env['proposal.opp.bb'].search([('id', '=', lead.selected_coverage.id)])
            print(recordproposal.id)
            recordcovers = self.env['coverage.line'].search([('proposal_id', '=', recordproposal.id)])

            records_covers = []
            for rec in recordcovers:
                coversline = (
                    0, 0,
                    {'riskk': rec.risk_id_covers.id ,'insurerd': rec.insurer.id,
                     'prod_product': rec.product.id, 'name1': rec.covers.id, 'sum_insure': rec.sum_insured,
                     'deductible' : rec.deductible, 'limitone' :rec.limitone ,'limittotal': rec.limittotal ,
                     'net_perimum': rec.net_premium, 'rate': rec.rate})
                print(coversline)
                records_covers.append(coversline)
                print(records_covers)

            # print(records_covers)

            res['new_risk_ids'] = [(6, 0, records_risks)]
            res['insurance_type'] = lead.insurance_type
            res['line_of_bussines'] = lead.LOB.id
            res['ins_type'] = lead.ins_type
            # res['propoasl_ids'] = records_proposal
            res['customer'] = lead.partner_id.id
            res['salesperson'] = lead.user_id.partner_id.id
            res['std_id'] = lead.policy_number
            res['name_cover_rel_ids'] = records_covers
            # res['checho'] = True
            res['company'] = lead.selected_coverage.Company.id
            res['product_policy'] = lead.selected_coverage.product_pol.id

            return res

    @api.multi
    def send_mail_template_policy(self):
        # Find the e-mail template
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = self.env.ref('insurance_broker_system_blackbelts.policy_email_template')
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'policy.broker',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id.id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            # 'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }





    @api.onchange("t_permimum","term", "number")
    def _cmpute_date_and_amount(self):
        if self.term == "onetime":
            self.rella_installment_id = [(0, 0, {
                "date": self.start_date,
                "amount": self.t_permimum,

            })]
        elif self.term == "year":
            start = fields.Datetime.from_string(self.start_date)
            duration = timedelta(days=365)

            phone_numbers = []
            for i in range(int(self.number)):
                x = (0, 0, {
                    "date": start + duration,
                    "amount": self.t_permimum / 1

                })
                phone_numbers.append(x)
                duration = duration + timedelta(days=365)
            self.rella_installment_id = phone_numbers
        elif self.term == "quarter":
            start = fields.Datetime.from_string(self.start_date)
            duration = timedelta(days=90)
            phone_numbers = []
            for i in range(4):
                x = (0, 0, {
                    "date": start + duration,
                    "amount": self.t_permimum / 4

                })
                phone_numbers.append(x)
                duration = duration + timedelta(days=90)
            self.rella_installment_id = phone_numbers
        elif self.term == "month":
            start = fields.Datetime.from_string(self.start_date)
            duration = timedelta(days=30)
            phone_numbers = []
            for i in range(12):
                x = (0, 0, {
                    "date": start + duration,
                    "amount": self.t_permimum / 12

                })
                phone_numbers.append(x)
                duration = duration + timedelta(days=30)
            self.rella_installment_id = phone_numbers


    @api.onchange('line_of_bussines')
    def _compute_comment_policy(self):
        for record in self:
            record.check_item = record.line_of_bussines.object

    @api.multi
    def print_policy(self):
        return self.env.ref('insurance_broker_system_blackbelts.policy_report').report_action(self)

    @api.model
    def compute_date(self):
        if (datetime.today().strftime('%Y-%m-%d')):
            if (datetime.today().strftime('%Y-%m-%d')) >= self.end_date:
                self.renewal_state=True


    bool = fields.Boolean()
    edit_number = fields.Integer(string="Endorsement Number")
    edit_decr = fields.Text('Endorsement Description', readonly=True)




    policy_number = fields.Char(string="Renewal Policy Number")
    renwal_check = fields.Boolean(string="Renewal")
    holding_cam = fields.Char(string="Holding Campany")

    std_id = fields.Char(string="Policy Number" ,required=True)
    issue_date = fields.Date(string="Issue Date")
    start_date = fields.Date(string="Effective From")
    end_date = fields.Date(string="Effective To")



    term = fields.Selection(
        [("onetime", "One Time"), ("year", "yearly"), ("quarter", "Quarterly"), ("month", "Monthly")],
        string="Payment Frequency")
    number = fields.Integer(string="No. Years", default=1)


    gross_perimum = fields.Float(string="Gross Perimum")
    t_permimum = fields.Float(string="Net Permium", compute="_compute_t_premium")


    salesperson = fields.Many2one('res.partner', string='Salesperson' ,domain="[('agent','=',1)]")

    commission_per = fields.Float(string="Commission",compute="_compute_commission_per")
    share_commission=fields.One2many('insurance.share.commission','policy_id',string='Share Commissions')

    @api.multi
    def _compute_commission_per(self):
        self.commission_per=(self.product_policy.commission_per/100)*self.t_permimum


    @api.onchange("t_permimum","term")
    def onchange_share_commission(self):
        if self.salesperson:
            self.share_commission =[(0, 0, {
                                        'agent': self.salesperson.id,
                                        'commission_per':100,})]



    rella_installment_id = fields.One2many("installment.installment", "installment_rel_id")

    customer = fields.Many2one('res.partner', 'Customer')

    insurance_type = fields.Selection([('Life', 'Life'),
                                       ('P&C', 'P&C'),
                                       ('Health', 'Health'), ],
                                      'Insurance Type', track_visibility='onchange')
    ins_type = fields.Selection([('Individual', 'Individual'),
                                 ('Group', 'Group'), ],
                                'I&G', track_visibility='onchange')
    line_of_bussines = fields.Many2one('insurance.line.business', string='Line of business',
                                       domain="[('insurance_type','=',insurance_type)]")

    check_item = fields.Char()
    group = fields.Boolean()



    commision = fields.Float(string="Basic Brokerage", compute="_compute_brokerage")
    com_commision = fields.Float(string="Complementary  Brokerage", compute="_compute_brokerage")
    fixed_commision = fields.Float(string="Fixed Brokerage", compute="_compute_brokerage")
    earl_commision = fields.Float(string="Early Collection" , compute="_compute_brokerage")
    total_commision = fields.Float(string="total Brokerage", compute="_compute_brokerage")
    new_risk_ids = fields.One2many("new.risks", 'policy_risk_id', string='Risk')
    company = fields.Many2one('res.partner', domain="[('insurer_type','=',1)]", string="Insurer")
    product_policy = fields.Many2one('insurance.product',domain="[('insurer','=',company),('line_of_bus','=',line_of_bussines)]", string="Product")
    hamda = fields.Many2one("new.risks")

    name_cover_rel_ids = fields.One2many("covers.lines","policy_rel_id",string="Covers Details" )
    currency_id = fields.Many2one("res.currency","Currency Code")
    benefit =fields.Char("Beneficiary")

    checho = fields.Boolean()
    count_claim = fields.Integer(compute="compute_true")

    @api.onchange('company')
    def _onchange_branch(self):
      if self.company:
           return {'domain': {'branch': [('setup_id.setup_key','=','branch'),('setup_id.setup_id','=',self.company.name)]}}

    branch = fields.Many2one('insurance.setup.item',string="Branch",domain="[('setup_id.setup_key','=','branch'),('setup_id.setup_id','=',company)]")





    @api.multi
    def compute_true(self):
        # self.count_claim = 0
        ids = self.env['insurance.claim'].search([('policy_number', '=', self.std_id)])
        for id in ids:
            self.count_claim +=1

    @api.one
    @api.depends("name_cover_rel_ids")
    def _compute_t_premium(self):
        total = 0.0
        for rec in self:
            for line in rec.name_cover_rel_ids:
                total += line.net_perimum
        rec.t_permimum = total


    @api.multi
    @api.depends("product_policy")
    def _compute_brokerage(self):
        for rec in self:
            rec.commision = (rec.product_policy.brokerage.basic_commission * rec.t_permimum) / 100
            rec.com_commision = (rec.product_policy.brokerage.complementary_commission * rec.t_permimum) / 100
            rec.earl_commision = (rec.product_policy.brokerage.early_collection * rec.t_permimum) / 100
            rec.fixed_commision = (rec.product_policy.brokerage.fixed_commission * rec.t_permimum) / 100
            rec.total_commision = rec.commision + rec.com_commision + rec.fixed_commision + rec.earl_commision










    @api.multi
    def generate_covers(self):
        self.checho = True
        return True

    # nohamed saber code

    policy_status = fields.Selection([('pending', 'Pending'),
                                      ('approved', 'Approved'), ],
                                     'Status', required=True, default='pending')
    hide_inv_button = fields.Boolean(copy=False)
    invoice_ids = fields.One2many('account.invoice', 'insurance_id', string='Invoices', readonly=True)
    renewal_state=fields.Boolean(copy=False,compute='compute_date')




    _sql_constraints = [
        ('std_id_unique', 'unique(std_id,policy_number)', 'Policy Number  already exists!')]


    @api.multi
    def create_renewal(self):
        view = self.env.ref('insurance_broker_system_blackbelts.my_view_for_policy_form_kmlo1')

        risk = self.env["new.risks"].search([('id', 'in', self.new_risk_ids.ids)])
        records_risk = []
        for rec in risk:
            object = (0, 0,
                      {'risk_description': rec.risk_description,
                       'car_tybe':rec.car_tybe.id, 'motor_cc':rec.motor_cc, 'year_of_made':rec.year_of_made, 'model':rec.model.id, 'Man':rec.Man.id,
                       'name':rec.name, 'DOB':rec.DOB, 'job':rec.job.id,
                       'From':rec.From, 'To':rec.To, 'cargo_type':rec.cargo_type, 'weight':rec.weight,
                       'address':rec.address , 'type':rec.type,
                       'group_name': rec.group_name, 'count': rec.count, 'file': rec.file,
                       })
            records_risk.append(object)

        share_commission = self.env["insurance.share.commission"].search([('id', 'in', self.share_commission.ids)])
        records_commission = []
        for rec in share_commission:
            comm = (0, 0,
                    {'agent': rec.agent.id,
                     'commission_per': rec.commission_per,
                       })
            records_commission.append(comm)

        installments = self.env["installment.installment"].search([('id', 'in', self.rella_installment_id.ids)])
        records_installments = []
        for rec in installments:
            install = (0, 0,
                       {'date': rec.date,
                        'amount': rec.amount,
                        'state': rec.state,
                       })
            records_installments.append(install)

        coverlines = self.env["covers.lines"].search([('id', 'in', self.name_cover_rel_ids.ids)])
        print(coverlines)
        records_cover = []
        for rec in coverlines:
            print(rec)
            covers=(
                0,0,{'riskk':rec.riskk.id,
                     'name1':rec.name1.id,
                     'check':rec.check,
                     'sum_insure':rec.sum_insure,
                     'deductible':rec.deductible,
                     'limitone': rec.limitone,
                     'limittotal': rec.limittotal,
                     'rate':rec.rate,
                     'net_perimum':rec.net_perimum,

                     }
            )
            records_cover.append(covers)

        return {
            'name': ('Policy'),
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'res_model': 'policy.broker',
            'target': 'current',
            'type': 'ir.actions.act_window',
            # 'flags': {'form': {'options': {'mode': 'view'}}},
            'context': {
                'default_renwal_check': True,
                'default_checho': True,
                'default_policy_number': self.std_id,
                'default_company': self.company.id,
                'default_ins_type': self.ins_type,
                'default_line_of_bussines': self.line_of_bussines.id,
                'default_product_policy': self.product_policy.id,
                'default_insurance_type': self.insurance_type,
                'default_customer': self.customer.id,
                'default_issue_date': self.issue_date,
                'default_start_date': self.start_date,
                'default_end_date': self.end_date,
                'default_branch': self.branch.id,
                'default_salesperson': self.salesperson.id,
                'default_currency_id': self.currency_id.id,
                'default_benefit': self.benefit,
                'default_gross_perimum': self.gross_perimum,
                'default_commision': self.commision,
                'default_com_commision': self.com_commision,
                'default_earl_commision': self.earl_commision,
                'default_fixed_commision': self.fixed_commision,
                'default_total_commision': self.total_commision,

                'default_new_risk_ids': records_risk,
                'default_share_commission': records_commission,
                'default_rella_installment_id': records_installments,
                'default_name_cover_rel_ids': records_cover,
            }
        }






    @api.multi
    def name_get(self):
        result = []
        for s in self:
            name = s.std_id + ' , ' +str(s.edit_number)
            result.append((s.id, name))
        return result

    @api.multi
    def confirm_policy(self):
        if self.term and self.customer and self.line_of_bussines and self.company:
            self.policy_status = 'approved'
            self.hide_inv_button = True
        else:
            raise UserError(_("Customer ,Line of Bussines , Company or Payment Frequency  should be Selected"))

    @api.multi
    def create_invoices(self):
        for record in self.rella_installment_id:
            if record.amount !=0:
                cust_invoice=self.env['account.invoice'].create({
                    'type': 'out_invoice',
                    'partner_id': self.customer.id,
                    'insured_invoice': 'customer_invoice',
                    'name': 'Customer Invoice of ' +str(self.customer.name),
                    'user_id': self.env.user.id,
                    'insurance_id': self.id,
                    'origin': self.policy_number,
                    'insured_type':self.insurance_type,
                    'insured_lOB': self.line_of_bussines.id,
                    'insured_insurer': self.company.id,
                    'insured_product': self.product_policy.id,
                    'date_due':record.date,
                    'invoice_line_ids': [(0, 0, {
                        'name': str(self.line_of_bussines.line_of_business),
                        'quantity': 1,
                        'price_unit': record.amount,
                        'account_id': self.line_of_bussines.income_account.id,
                    })],
                })
                cust_invoice.action_invoice_open()

                ins_bill=self.env['account.invoice'].create({
                    'type': 'in_invoice',
                    'partner_id': self.company.id,
                    'insured_invoice': 'insurer_bill',
                    'name': 'Insurer Bill  of ' +str(self.company.name),
                    'user_id': self.env.user.id,
                    'insurance_id': self.id,
                    'origin': self.policy_number,
                    'insured_type':self.insurance_type,
                    'insured_lOB': self.line_of_bussines.id,
                    'insured_insurer': self.company.id,
                    'insured_product': self.product_policy.id,
                    'date_due': record.date,
                    'invoice_line_ids': [(0, 0, {
                        'name': str(self.line_of_bussines.line_of_business),
                        'quantity': 1,
                        'price_unit': record.amount,
                        'account_id': self.line_of_bussines.expense_account.id,
                    })],
                })
                ins_bill.action_invoice_open()

        if self.total_commision !=0:
            brok_invoice = self.env['account.invoice'].create({
                'type': 'out_invoice',
                'partner_id': self.company.id,
                'insured_invoice':'brokerage',
                'name':'Brokerage  of ' +str(self.company.name),
                'user_id': self.env.user.id,
                'insurance_id': self.id,
                'origin': self.policy_number,
                'insured_type':self.insurance_type,
                'insured_lOB':self.line_of_bussines.id,
                'insured_insurer':self.company.id,
                'insured_product':self.product_policy.id,
                'invoice_line_ids': [(0, 0, {
                    'name': str(self.line_of_bussines.line_of_business),
                    'quantity': 1,
                    'price_unit': self.total_commision,
                    'account_id': self.line_of_bussines.income_account.id,
                })],
            })
            brok_invoice.action_invoice_open()

        for record in self.share_commission:
            com_bill = self.env['account.invoice'].create({
                'type': 'in_invoice',
                'partner_id':record.agent.id,
                'insured_invoice':'commission',
                'name':'Commission  of ' +str(record.agent.name),
                'user_id': self.env.user.id,
                'insurance_id': self.id,
                'origin': self.policy_number,
                'insured_type':self.insurance_type,
                'insured_lOB':self.line_of_bussines.id,
                'insured_insurer':self.company.id,
                'insured_product':self.product_policy.id,
                'invoice_line_ids': [(0, 0, {
                    'name': str(self.line_of_bussines.line_of_business),
                    'quantity': 1,
                    'price_unit': record.amount,
                    'account_id': self.line_of_bussines.expense_account.id,
                })],
            })
            com_bill.action_invoice_open()

        self.hide_inv_button = False

class AccountInvoiceRelate(models.Model):
    _inherit = 'account.invoice'

    insurance_id = fields.Many2one('policy.broker', string='Insurance')
    insured_type =fields.Char(string='Type')
    insured_lOB = fields.Many2one('insurance.line.business',string='LOB')
    insured_insurer = fields.Many2one('res.partner',string='Insurer')
    insured_product = fields.Many2one('insurance.product',string='Product')
    insured_invoice=fields.Char(string='insured invoice')


class Extra_Covers(models.Model):
    _name = "covers.lines"
    riskk = fields.Many2one("new.risks", "Risk")
    # risk_description = fields.Text(string="Risk Description")
    #
    insurerd = fields.Many2one(related="policy_rel_id.company")
    prod_product = fields.Many2one(related="policy_rel_id.product_policy",domain="[('insurer','=',insurerd)]")

    name1 = fields.Many2one("insurance.product.coverage",string="Cover", domain="[('product_id', '=' , prod_product)]")
    check = fields.Boolean(related="name1.readonly")

    sum_insure = fields.Float(string="SI")
    deductible = fields.Integer('Deductible')
    limitone=fields.Integer('Limit in One')
    limittotal=fields.Integer('Limit in Total')
    rate = fields.Float(string="Rate")
    net_perimum = fields.Float(string="Net Perimum")
    policy_rel_id = fields.Many2one("policy.broker")


    _sql_constraints = [
        ('cover_unique', 'unique(policy_rel_id,riskk,name1)', 'Cover already exists!')]


    @api.multi
    def name_get(self):
        result = []
        for s in self:
            name = str(s.name1.Name) + ' , ' +str(s.riskk.risk_description)
            result.append((s.id, name))
        return result


    @api.onchange("check")
    def _nameget(self):
        if self.check == True:
            self.net_perimum = self.sum_insure


    @api.onchange('policy_rel_id')
    def onchange_field_id(self):
        if self.policy_rel_id:
           return {'domain': {"riskk": [('id', 'in', self.policy_rel_id.new_risk_ids.ids)]}}

    # @api.onchange('policy_rel_id')
    # def _change_domain(self):
    #     if self.policy_rel_id:
    #         ids = self.env["policy.broker"].search([])
    #         return {
    #             "domain":{
    #                 "riskk":[('risk','in',[ids.new_risk_ids.ids])]
    #             }
    #         }

    @api.onchange('name1')
    def onchange_covers(self):
        if self.name1:
            self.sum_insure = self.name1.defaultvalue
            self.deductible = self.name1.deductible
            self.limitone = self.name1.limitone
            self.limittotal = self.name1.limittotal

    @api.onchange('rate','sum_insure')
    def compute_premium(self):
        if self.name1:
            self.net_perimum = (self.sum_insure * self.rate) / 100

    @api.onchange('riskk')
    def onchange_risc_desc(self):
        if self.riskk:
            self.risk_description = self.riskk.risk_description

class ShareCommition(models.Model):
    _name = "insurance.share.commission"


    agent = fields.Many2one("res.partner", string="Agent")
    commission_per = fields.Float(string="Percentage")
    amount = fields.Float(string="Amount",compute='_compute_amount')
    policy_id = fields.Many2one("policy.broker")

    @api.one
    @api.depends('commission_per')
    def _compute_amount(self):
        self.amount=self.policy_id.commission_per*(self.commission_per/100)







class InstallmentClass(models.Model):
    _name= "installment.installment"
    _rec_name = "date"

    date = fields.Date(string="Date")
    # enddate = fields.Date(string="End of premium")
    amount = fields.Float(string="Amount")
    state = fields.Selection([('open', 'Open'),
                             ('paid', 'Paid')],
                           'State',defualt='open')
    installment_rel_id = fields.Many2one("policy.broker")

