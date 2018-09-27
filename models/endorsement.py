from odoo import api, fields, models

class Endorsement_edit(models.Model):
    _name="endorsement.edit"
    _rec_name="number_policy"


    number_policy=fields.Many2one("policy.broker", string="Edit policy number")
    number_edit = fields.Integer(string="Endorsement Number")
    reasonedit = fields.Text(string="Endorsement Reason")
    issue_date = fields.Date(string="Issue Date")
    start_date = fields.Date(string="Effective From")
    end_date = fields.Date(string="Effective To")


    @api.multi
    def create_endorsement(self):
        form_view = self.env.ref('insurance_broker_system_blackbelts.my_view_for_policy_form_kmlo1')

        riskrecordd = self.env["new.risks"].search([('id', 'in', self.number_policy.new_risk_ids.ids)])
        records_cargo = []
        for rec in riskrecordd:
            objectcargo = (
                    0, 0, {'risk': rec.risk, 'risk_description': rec.risk_description,

                           'car_tybe':rec.car_tybe, 'motor_cc':rec.motor_cc, 'year_of_made':rec.year_of_made, 'model':rec.model, 'Man':rec.Man,

                           'name':rec.name, 'DOB':rec.DOB, 'job':rec.job,

                           'From':rec.From, 'To':rec.To, 'cargo_type':rec.cargo_type, 'weight':rec.weight,

                           'group_name': rec.group_name, 'count': rec.count, 'file': rec.file,

                           })
            records_cargo.append(objectcargo)

        coverlines = self.env["covers.lines"].search([('id', 'in', self.number_policy.name_cover_rel_ids.ids)])
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
                    'default_customer': self.number_policy.customer.id,
                    'default_checho':True,

                    'default_company':self.number_policy.company.id,

                    'default_product_policy':self.number_policy.product_policy.id,
                    'default_edit_decr': self.reasonedit,

                    'default_std_id': self.number_policy.std_id,

                    'default_issue_date':self.number_policy.issue_date,
                    'default_start_date':self.number_policy.start_date,
                    'default_end_date':self.number_policy.end_date,
                    'default_barnche':self.number_policy.barnche.id,

                    'default_salesperson':self.number_policy.salesperson.id,
                    'default_onlayer':self.number_policy.onlayer,

                    'default_currency_id':self.number_policy.currency_id.id,
                    'default_benefit':self.number_policy.benefit,
                    'default_edit_number':self.number_edit ,
                    'default_insurance_type': self.number_policy.insurance_type,
                    'default_term':self.number_policy.term,

                    'default_line_of_bussines':self.number_policy.line_of_bussines.id ,
                    'default_ins_type': self.number_policy.ins_type,
                    'default_new_risk_ids':records_cargo,
                    'default_name_cover_rel_ids':value,


                            }
            }
