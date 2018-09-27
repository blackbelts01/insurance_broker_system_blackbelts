from odoo import api, fields, models

class Renewal_Again(models.Model):
    _name = "renewal.again"
    _rec_name="old_number"

    old_number = fields.Many2one("policy.broker", string="Old Policy Number")
    new_number = fields.Char(string="New Policy Number")
    issue_date = fields.Date(string="Issue Date")
    start_date = fields.Date(string="Effective From")
    end_date = fields.Date(string="Effective To")

    @api.multi
    def create_renewal(self):
        form_view = self.env.ref('insurance_broker_system_blackbelts.my_view_for_policy_form_kmlo1')


        riskrecordd = self.env["new.risks"].search([('id', 'in', self.old_number.new_risk_ids.ids)])
        records_cargo = []
        for rec in riskrecordd:
            objectcargo = (
                    0, 0, {'risk': rec.risk, 'risk_description': rec.risk_description,

                           'car_tybe': rec.car_tybe, 'motor_cc': rec.motor_cc, 'year_of_made': rec.year_of_made, 'model': rec.model, 'Man': rec.Man,

                           'name': rec.name, 'DOB': rec.DOB, 'job': rec.job,

                           'From': rec.From, 'To': rec.To, 'cargo_type': rec.cargo_type, 'weight': rec.weight,

                           'group_name': rec.group_name, 'count': rec.count, 'file': rec.file,

                           })
            records_cargo.append(objectcargo)

        coverlines = self.env["covers.lines"].search([('id', 'in', self.old_number.name_cover_rel_ids.ids)])
        print(coverlines)
        value = []
        for rec in coverlines:
            print(rec)
            covers = (
                0, 0, {'riskk': rec.riskk.id,
                       'risk_description': rec.risk_description,
                       'name1': rec.name1.id,
                       'check': rec.check,
                       'sum_insure': rec.sum_insure,
                       'rate': rec.rate,
                       'net_perimum': rec.net_perimum,

                       }
            )
            value.append(covers)


        if self.new_number:
            return {
                'name': ('Policy'),
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(form_view.id, 'form')],
                'res_model': 'policy.broker',
                'target': 'current',
                'type': 'ir.actions.act_window',
                # 'flags': {'form': {'options': {'mode': 'view'}}},
                'context': {
                            'default_renwal_check': True,
                    'default_checho': True,
                    'default_company': self.old_number.company.id,

                    'default_product_policy': self.old_number.product_policy.id,

                    'default_policy_number':self.new_number,

                    'default_std_id': self.old_number.std_id,

                    'default_customer': self.old_number.customer.id,

                    'default_issue_date': self.issue_date,

                    'default_start_date': self.start_date,

                    'default_end_date': self.end_date,

                    'default_barnche': self.old_number.barnche.id,

                    'default_salesperson': self.old_number.salesperson.id,

                    'default_onlayer': self.old_number.onlayer,

                    'default_currency_id': self.old_number.currency_id.id,

                    'default_benefit': self.old_number.benefit,

                    'default_insurance_type': self.old_number.insurance_type,

                    'default_line_of_bussines': self.old_number.line_of_bussines.id,

                    'default_ins_type': self.old_number.ins_type,

                    'default_new_risk_ids': records_cargo,

                    'default_name_cover_rel_ids': value,
                            }
            }