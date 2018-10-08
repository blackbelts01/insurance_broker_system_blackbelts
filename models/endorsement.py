from odoo import api, fields, models

class Endorsement_edit(models.Model):
    _name="endorsement.edit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name="number_policy"


    number_policy=fields.Many2one("policy.broker", string="Edit policy number",domain="[('edit_number','=',0)]")
    number_edit = fields.Integer(string="Endorsement Number")
    last_policy=fields.Many2one('policy.broker' )
    reasonedit = fields.Text(string="Endorsement Reason")
    issue_date = fields.Date(string="Issue Date")
    start_date = fields.Date(string="Effective From")
    end_date = fields.Date(string="Effective To")

    @api.onchange('number_policy')
    def onchange_risk_id_pol(self):
        last_confirmed_edit = self.env['policy.broker'].search(
            [('std_id', '=', self.number_policy.std_id)],
            order='edit_number desc',
            limit=1
        )
        self.last_policy=last_confirmed_edit.id
        self.number_edit=(last_confirmed_edit.edit_number)+1



    #     if self.covers_crm:
    #         return {'domain': {'risk_id_covers': [('id', 'in', self.covers_crm.objectrisks.ids)]}}
    #
    # record_ids = self.search([('meter_no', '=', self.meter_no.id)], order='id desc', limit=1)
    # last_id = record_ids.id
    @api.multi
    def create_endorsement(self):
        form_view = self.env.ref('insurance_broker_system_blackbelts.my_view_for_policy_form_kmlo1')

        riskrecordd = self.env["new.risks"].search([('id', 'in', self.last_policy.new_risk_ids.ids)])
        records_cargo = []
        for rec in riskrecordd:
            objectcargo = (
                0, 0, {'risk': rec.risk, 'risk_description': rec.risk_description,

                       'car_tybe':rec.car_tybe.id, 'motor_cc':rec.motor_cc, 'year_of_made':rec.year_of_made, 'model':rec.model.id, 'Man':rec.Man,

                       'name':rec.name, 'DOB':rec.DOB, 'job':rec.job,

                       'From':rec.From, 'To':rec.To, 'cargo_type':rec.cargo_type, 'weight':rec.weight,

                       'group_name': rec.group_name, 'count': rec.count, 'file': rec.file,

                       })
            records_cargo.append(objectcargo)

            sharecommition = self.env["share.commition"].search([('id', 'in', self.last_policy.share_policy_rel_ids.ids)])
            records_sharecommition = []
            for rec in sharecommition:
                comm = (
                    0, 0, {'agent': rec.agent.id, 'share_commition': rec.share_commition,
                           'amount': rec.amount,
                           })
                records_sharecommition.append(comm)

            installments = self.env["installment.installment"].search([('id', 'in', self.last_policy.rella_installment_id.ids)])
            records_installments = []
            for rec in installments:
                install = (
                    0, 0, {'date': rec.date, 'amount': rec.amount,
                           'state': rec.state,
                           })
                records_installments.append(install)

        coverlines = self.env["covers.lines"].search([('id', 'in', self.last_policy.name_cover_rel_ids.ids)])
        print(coverlines)
        value = []
        for rec in coverlines:
            print(rec)
            covers=(
                0,0,{'riskk':rec.riskk.id,
                     'risk_description':rec.risk_description,
                     'name1':rec.name1.id,
                     'check':rec.check,
                     'sum_insure':rec.sum_insure,
                     'rate':rec.rate,
                     'net_perimum':rec.net_perimum,

                     }
            )
            value.append(covers)



        if self.number_edit:
            return {
                'name': ('Policy'),
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(form_view.id, 'form')],
                'res_model': 'policy.broker',
                'target': 'current',
                # 'store': False,
                # 'create': False,
                # 'edit': False ,
                'type': 'ir.actions.act_window',
                'context': {
                    'default_customer': self.last_policy.customer.id,
                    'default_checho':True,

                    'default_company':self.last_policy.company.id,

                    'default_product_policy':self.last_policy.product_policy.id,
                    'default_edit_decr': self.reasonedit,

                    'default_std_id': self.last_policy.std_id,

                    'default_issue_date':self.last_policy.issue_date,
                    'default_start_date':self.last_policy.start_date,
                    'default_end_date':self.last_policy.end_date,
                    'default_branch':self.last_policy.branch.id,

                    'default_salesperson':self.last_policy.salesperson.id,
                    'default_onlayer':self.last_policy.onlayer,

                    'default_currency_id':self.last_policy.currency_id.id,
                    'default_benefit':self.last_policy.benefit,
                    'default_benefit': self.last_policy.gross_perimum,
                    'default_edit_number':self.number_edit ,
                    'default_insurance_type': self.last_policy.insurance_type,
                    'default_commision':self.last_policy.commision,
                    'default_com_commision': self.last_policy.com_commision,
                    'default_earl_commision': self.last_policy.earl_commision,
                    'default_fixed_commision': self.last_policy.fixed_commision,
                    'default_total_commision': self.last_policy.total_commision,

                    'default_line_of_bussines':self.last_policy.line_of_bussines.id ,
                    'default_ins_type': self.last_policy.ins_type,
                    'default_new_risk_ids':records_cargo,
                    'default_share_policy_rel_ids': records_sharecommition,
                    'default_rella_installment_id': records_installments,

                    'default_name_cover_rel_ids':value,


                }
            }
