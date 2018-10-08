import random
import string
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class PolicyBroker(models.Model):
    _name = "policy.broker"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # @api.multi
    # def show_claim(self):
    #     form_view = self.env.ref('insurance_broker_system_blackbelts.tree_insurance_claim')
    #     form_view3 =self.env.ref('insurance_broker_system_blackbelts.form_insurance_claim')
    #     return {
    #         'name': ('tree insurance claim'),
    #         'view_type': 'form',
    #         'view_mode': 'tree, form',
    #         'views': [(form_view.id, 'form'),(form_view3.id, 'tree')],
    #         'res_model': 'insurance.claim',
    #         'target': 'current',
    #         'type': 'ir.actions.act_window',
    #         'context': {
    # #                     "default_policy_number":self.id
    #
    #         }
    # #     }
    #
    #
    #

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
            print(recordproposal.proposal_id)
            recordcovers = self.env['coverage.line'].search([('proposal_id', '=', recordproposal.proposal_id)])

            records_covers = []
            for rec in recordcovers:
                coversline = (
                    0, 0,
                    {'riskk': rec.risk_id_covers.id, 'risk_description': rec.risk_desc, 'insurerd': rec.insurer.id,
                     'prod_product': rec.product.id, 'name1': rec.covers.id, 'sum_insure': rec.sum_insured,
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
            res['salesperson'] = lead.user_id.id
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

    # def proposalselected(self):
    #     ids = self.env['proposal.bb'].search([('id', '=', self.prop_id)]).ids
    #     self.selected_proposal = [(6, 0, ids)]

    @api.onchange('line_of_bussines')
    def _compute_comment(self):
        for record in self:
            record.check_item = record.line_of_bussines.object

    @api.multi
    def print_policy(self):
        return self.env.ref('insurance_broker_system_blackbelts.policy_report').report_action(self)


    @api.multi
    @api.constrains('share_policy_rel_ids')
    @api.onchange("share_commition")
    def _check_something(self):
        total = 0.0
        for rec in self.share_policy_rel_ids:
            total += rec.share_commition

        if total > 100:
            raise ValidationError("Your share percentage must be under percentage")

    # @api.multi
    # @api.onchange('bool')
    # def setcovers_veh(self):
    #     ids = self.env['insurance.product.coverage'].search(
    #         [('product_id', '=', self.product_policy.id)])
    #     print(ids)
    #     if self.bool:
    #         print('xxx')
    #         for record in self.new_risk_ids:
    #              for rec in ids:
    #                  print('i enter')
    #                  record.name_cover_risk_ids =(0, 0, {
    #                      "name": rec.Name,
    #                      "sum_insure": rec.defaultvalue,
    #                      "check": rec.readonly,
    #                      # "rate": rec.product_id.name_cover_ids.covers_rel_ids.rate,
    #                      "net_perimum": rec.readonly and rec.defaultvalue
    #                  })


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
        string="payment frequency")
    number = fields.Integer(string="No Of Years", default=1)


    gross_perimum = fields.Float(string="Gross Perimum")
    t_permimum = fields.Float(string="Net Permium", compute="_compute_t_premium")

    salesperson = fields.Many2one('res.users', string='Salesperson', index=True, default=lambda self: self.env.user)
    onlayer = fields.Selection(related="salesperson.layer", string="Sales Layer")
    personcom = fields.Integer(string="commission",compute="_compute_personcom")
    rel_com_detail_id = fields.One2many("layers.layer", "policy_rel_do_id")
    rella_installment_id = fields.One2many("installment.installment", "installment_rel_id")
    share_policy_rel_ids = fields.One2many("share.commition", "share_commition_rel_id")

    customer = fields.Many2one('res.partner', 'Customer')

    insurance_type = fields.Selection([('life', 'Life'),
                                       ('p&c', 'P&C'),
                                       ('health', 'Health'), ],
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
    benefit =fields.Char("Beneifciary")

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


    # @api.multi
    # @api.depends("product_policy")
    # def _compute_com_commision(self):
    #     for rec in self:
    #         rec.com_commision = (rec.product_policy.brokerage.complementary_commission * rec.t_permimum) / 100
    #
    # @api.multi
    # @api.depends("product_policy")
    # def _compute_earl_commision(self):
    #     for rec in self:
    #             rec.earl_commision = (rec.product_policy.brokerage.early_collection * rec.t_permimum) / 100
    #
    #
    # @api.multi
    # @api.depends("product_policy")
    # def _compute_fixed_commision(self):
    #     for rec in self:
    #             rec.fixed_commision = (rec.product_policy.brokerage.fixed_commission * rec.t_permimum) / 100
    #
    # @api.multi
    # def _compute_sum(self):
    #     for rec in self:
    #         rec.total_commision = rec.commision + rec.com_commision + rec.fixed_commision

    @api.multi
    @api.depends("salesperson","onlayer","t_permimum")
    def _compute_personcom(self):
        if self.onlayer == "l1":
            self.personcom = (self.product_policy.commision_id.layer1 * self.t_permimum) / 100
        elif self.onlayer == "l2":
            self.personcom = (self.product_policy.commision_id.layer2 * self.t_permimum) / 100
        elif self.onlayer == "l3":
            self.personcom = (self.product_policy.commision_id.layer3 * self.t_permimum) / 100
        elif self.onlayer == "l4":
            self.personcom = (self.product_policy.commision_id.layer4 * self.t_permimum) / 100
        elif self.onlayer == "l5":
            self.personcom = (self.product_policy.commision_id.layer5 * self.t_permimum) / 100


    @api.multi
    @api.onchange("salesperson")
    def onchange_objectx(self):
        for rec in self:
            self.rel_com_detail_id = [
                (0, 0, {
                    "agent": rec.salesperson,
                    "l1": rec.salesperson.layer,
                    "allocation_layer1": rec.rel_com_detail_id.allocation_layer1,
                    "portion1": rec.rel_com_detail_id.portion1
                })]

    @api.multi
    @api.onchange("salesperson")
    def onchange_num_objectx(self):
        for rec in self:
            self.share_policy_rel_ids = [
                (0, 0, {
                    "agent": rec.salesperson,
                    "share_commition": rec.share_policy_rel_ids.share_commition,
                    "amount": rec.share_policy_rel_ids.amount
                })]



    @api.multi
    def generate_covers(self):
        self.checho = True
        return True

    # nohamed saber code

    policy_status = fields.Selection([('pending', 'Pending'),
                                      ('approve', 'Approve'), ],
                                     'Status', required=True, default='pending')
    hide_inv_button = fields.Boolean(copy=False)
    invoice_ids = fields.One2many('account.invoice', 'insurance_id', string='Invoices', readonly=True)

    _sql_constraints = [
        ('std_id_unique', 'unique(std_id,edit_number)', 'Policy Number  already exists!')]


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
            self.policy_status = 'approve'
            self.hide_inv_button = True
        else:
            raise UserError(_("Customer ,Line of Bussines or Company  should be Selected"))

    @api.multi
    def create_invoices(self):
        for record in self.rella_installment_id:
            if record.amount !=0:
                cust_invoice=self.env['account.invoice'].create({
                    'type': 'out_invoice',
                    'partner_id': self.customer.id,
                    'user_id': self.env.user.id,
                    'insurance_id': self.id,
                    'origin': self.policy_number,
                    'invoice_line_ids': [(0, 0, {
                        'name': 'Invoice For Insurance',
                        'quantity': 1,
                        'price_unit': record.amount,
                        'account_id': self.line_of_bussines.income_account.id,
                    })],
                })
                cust_invoice.action_invoice_open()

                ins_bill=self.env['account.invoice'].create({
                    'type': 'in_invoice',
                    'partner_id': self.company.id,
                    'user_id': self.env.user.id,
                    'insurance_id': self.id,
                    'origin': self.policy_number,
                    'invoice_line_ids': [(0, 0, {
                        'name': 'Bill For Insurance',
                        'quantity': 1,
                        'price_unit': record.amount,
                        'account_id': self.line_of_bussines.expense_account.id,
                    })],
                })
                ins_bill.action_invoice_open()

        for record in self.share_policy_rel_ids:
            if record.amount !=0:
                comm_bill = self.env['account.invoice'].create({
                    'type': 'in_invoice',
                    'partner_id': record.agent.id,
                    'user_id': self.env.user.id,
                    'insurance_id': self.id,
                    'origin': self.policy_number,
                    'invoice_line_ids': [(0, 0, {
                        'name': 'Commission Insurance',
                        'quantity': 1,
                        'price_unit': record.amount,
                        'account_id': self.line_of_bussines.expense_account.id,
                    })],
                })
                comm_bill.action_invoice_open()

        if self.total_commision !=0:
            brok_invoice = self.env['account.invoice'].create({
                'type': 'out_invoice',
                'partner_id': 1,
                'user_id': self.env.user.id,
                'insurance_id': self.id,
                'origin': self.policy_number,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Brokerage Insurance',
                    'quantity': 1,
                    'price_unit': self.total_commision,
                    'account_id': self.line_of_bussines.expense_account.id,
                })],
            })
            brok_invoice.action_invoice_open()

        self.hide_inv_button = False

class AccountInvoiceRelate(models.Model):
    _inherit = 'account.invoice'

    insurance_id = fields.Many2one('policy.broker', string='Insurance')

class Extra_Covers(models.Model):
    _name = "covers.lines"




    riskk = fields.Many2one("new.risks", "Risk ID")
    risk_description = fields.Text(string="Risk Description")
    #
    insurerd = fields.Many2one(related="policy_rel_id.company")
    prod_product = fields.Many2one(related="policy_rel_id.product_policy",domain="[('insurer','=',insurerd)]")

    name1 = fields.Many2one("insurance.product.coverage",string="Cover", domain="[('product_id', '=' , prod_product)]")
    check = fields.Boolean(related="name1.readonly")

    sum_insure = fields.Float(string="SI")
    rate = fields.Float(string="Rate")
    net_perimum = fields.Float(string="Net Perimum")
    policy_rel_id = fields.Many2one("policy.broker")


    _sql_constraints = [
        ('cover_unique', 'unique(policy_rel_id,riskk,name1)', 'Cover already exists!')]


    @api.multi
    def name_get(self):
        result = []
        for s in self:
            name = str(s.name1.Name) + ' , ' +str(s.riskk.risk)
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

    @api.onchange('rate')
    def compute_premium(self):
        if self.name1:
            self.net_perimum = (self.sum_insure * self.rate) / 100

    @api.onchange('riskk')
    def onchange_risc_desc(self):
        if self.riskk:
            self.risk_description = self.riskk.risk_description

    #     res = {}
    #     self.riskk = False
    #     if self.policy_rel_id.new_risk_ids:
    #         print("khaled")
    #         ids = self.env["policy.broker"].browse([self.policy_rel_id.new_risk_ids])
    #         print(ids)
    #         # ids = self.policy_rel_id.new_risk_ids.mapped('id')
    #         # print(ids)
    #         # for rec in ids:
    #         #     self.riskk = rec.risk
    #     #     res['domain'] = {'riskk': [('risk', 'in', ids)]}
    #     #     print(res)
    #     # return res

    # @api.multi
    # def _compute_risk(self):
    #     bns = self.env["new.risks"].search([('risk', '=', self.policy_rel_id.new_risk_ids.id)])
    #     print(bns.ids)
    #     for rec in bns.ids:
    #         self.riskk = rec.risk


    # @api.multi
    # def _compute_coverage(self):
    #     obj = self.env['insurance.product.coverage'].search([('product_id','=',self.policy_rel_id.product_policy.id)])
    #     print(obj.ids)
    #     for rec in obj.ids:
    #         self.name = rec.Name
    #         self.check = rec.readonly
    #         self.sum_insure = rec.defaultvalue






class ShareCommition(models.Model):
    _name = "share.commition"

    agent = fields.Many2one("res.users", string="Agent")
    share_commition = fields.Float(string="Share")
    amount = fields.Float(string="Amount")
    share_commition_rel_id = fields.Many2one("policy.broker")

    @api.multi
    @api.onchange("share_commition")
    def _compute_amount(self):
        self.amount = (self.share_commition_rel_id.personcom * self.share_commition) / 100


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

class Layers(models.Model):
    _name = "layers.layer"
    _rec_name = "agent"

    agent = fields.Many2one("res.users", string="Agent")
    l1 = fields.Char(string="Layer")
    allocation_layer1 = fields.Float(string="allocation", compute="_com_sum_one_name")

    portion1 = fields.Float(string="portion", compute="_com_sum_two_name")
    com_rel_ids = fields.Many2one("commision.setup")

    policy_rel_do_id = fields.Many2one("policy.broker")

    @api.multi
    @api.onchange("agent")
    def _compute_lay(self):
        for rec in self:
            rec.l1 = rec.agent.layer

    @api.multi
    def _com_sum_one_name(self):
        for record in self:
            if record.l1 == 'l1':
                record.allocation_layer1 = record.policy_rel_do_id.propoasl_ids.product_pol.commision_id.layer1
            elif record.l1 == 'l2':

                record.allocation_layer1 = record.policy_rel_do_id.propoasl_ids.product_pol.commision_id.layer2
            elif record.l1 == 'l3':

                record.allocation_layer1 = record.policy_rel_do_id.propoasl_ids.product_pol.commision_id.layer3
            elif record.l1 == 'l4':

                record.allocation_layer1 = record.policy_rel_do_id.propoasl_ids.product_pol.commision_id.layer4
            elif record.l1 == 'l5':

                record.allocation_layer1 = record.policy_rel_do_id.propoasl_ids.product_pol.commision_id.layer5

    @api.multi
    def _com_sum_two_name(self):
        for record in self:
            if record.l1 == 'l1':
                record.portion1 = (record.allocation_layer1 * record.policy_rel_do_id.commision) / 100
            elif record.l1 == 'l2':
                record.portion1 = (record.allocation_layer1 * record.policy_rel_do_id.commision) / 100
            elif record.l1 == 'l3':
                record.portion1 = (record.allocation_layer1 * record.policy_rel_do_id.commision) / 100
            elif record.l1 == 'l4':
                record.portion1 = (record.allocation_layer1 * record.policy_rel_do_id.commision) / 100
            elif record.l1 == 'l5':
                record.portion1 = (record.allocation_layer1 * record.policy_rel_do_id.commision) / 100


class CommisionSetup(models.Model):
    _name = "commision.setup"
    _rec_name = "date_from"

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    policy_relation_id = fields.Many2one("insurance.product")
    layer1 = fields.Float(string="L1 ")
    layer2 = fields.Float(string="L2 ")
    layer3 = fields.Float(string="L3 ")
    layer4 = fields.Float(string="L4 ")
    layer5 = fields.Float(string="L5 ")


class InheritUsers(models.Model):
    _inherit = "res.users"

    layer = fields.Selection(
        [("l1", "Layer 1"), ("l2", "Layer 2"), ("l3", "Layer 3"), ("l4", "Layer 4"), ("l5", "Layer 5"),
         ("l6", "Layer 6"), ("l7", "Layer 7"), ("l8", "Layer 8")], string="Layer", required=True)


class InheritSale(models.Model):
    _inherit = "crm.lead"


