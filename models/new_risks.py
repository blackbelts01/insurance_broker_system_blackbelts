from odoo import models, fields, api
from odoo.exceptions import ValidationError


class New_Risks(models.Model):
    _name="new.risks"
    _rec_name="risk"


    @api.one

    @api.depends('policy_risk_id', 'risks_crm')
    def _compute_risk_descriptionn(self):
        if self.risks_crm or self.policy_risk_id:
            if self.test == "person" or self.type_risk == 'person':
                self.risk_description = (str(self.name) if self.name else " " + "_") + "  " + (
                    str(self.DOB) if self.DOB else " " + "_") + "  " + (str(self.job) if self.job else " " + "_")

            if self.test == "vehicle" or self.type_risk == 'vehicle':
                self.risk_description = (str(self.car_tybe) if self.car_tybe else " " + "_") + "  " + (
                    str(self.motor_cc) if self.motor_cc else " " + "_") + "  " + (
                                           str(self.year_of_made) if self.year_of_made else " " + "_") + "  " + (
                                           str(self.model) if self.model else " " + "_") + "  " + (
                                           str(self.Man) if self.Man else " " + "_")
            #
            if self.test == "cargo" or self.type_risk == 'cargo':
                self.risk_description = (str(self.From) if self.From else " " + "_") + "  " + (
                    str(self.To) if self.To else " " + "_") + "  " + (
                                           str(self.cargo_type) if self.cargo_type else " " + "_") + "  " + (
                                           str(self.weight) if self.weight else " " + "_")
            # if rec.test == "location":
            #     rec.risk_description = (str(rec.group_name) if rec.group_name else " " + "_") + "  " + (
            #         str(rec.count) if rec.count else " " + "_")

    policy_risk_id = fields.Many2one("policy.broker")
    risks_crm = fields.Many2one("crm.lead", string='Risks')
    type_risk = fields.Char(related='risks_crm.test')

    risk = fields.Char("Risk ID" ,required=True)
    risk_description = fields.Char("Risk Description", compute="_compute_risk_descriptionn", store=True)

    test = fields.Char(related="policy_risk_id.check_item")



    #group car
    car_tybe = fields.Char(string="Vehicle Type")
    motor_cc = fields.Char("Motor cc")
    year_of_made = fields.Date("Year of Made")
    model = fields.Char("Motor Model")
    Man = fields.Char(string='Vehicle Brande')



    #group person
    name = fields.Char('Name')
    DOB = fields.Date('Date Of Birth')
    job = fields.Char('Job Tiltle')




    #group cargo
    From = fields.Char('From')
    To = fields.Char('To')
    cargo_type = fields.Char("Type Of Cargo")
    weight = fields.Float('Weight')


    #gropu group
    group_name=fields.Char('Name')

    count=fields.Char('Group Count')

    file = fields.Binary(string='Group Details File')


    # @api.model
    # def create(self,vals):
    #     self.env["policy.broker"].create({"new_risk_ids.risk":self.risk,"new_risk_ids.risk_description":self.risk_description})
    #
    #
    #     return super(New_Risks, self).create(vals)

