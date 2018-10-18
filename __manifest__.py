# -*- coding: utf-8 -*-
{
    'name': "Insurance Broker",

    'summary': """Insurance Broker System""",

    'description': """
         for managing:
            - Leads
            - Policy
            - Installments
            - Commissions 
            - Invoices
            - Journal Entries
    """,

    'author': "Black Belts",
    'website': "http://www.blackbelts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale','crm','sale_crm','hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'reports/report_crm.xml',
        'reports/crm_report_template.xml',
        'reports/claim_report.xml',
        'reports/report_opp_partner.xml',
        'reports/report_agent.xml',
        'data/mail_template_data.xml',
        'views/policy_setup_view.xml',
        'views/endorsement.xml',
        'views/renewal_view.xml',
        'views/claimform_view.xml',
        'views/proposals.xml',
        "views/users_views.xml",
        "views/insurer_partner.xml",
        "views/installments_view.xml",
        "views/views.xml",
        "views/view.xml",
        'views/insured_cargo.xml',
        'views/insured_object.xml',
        'views/insured_vehicle.xml',
        'views/settlements.xml',
        'views/asset_emp.xml',
        'views/invoices_view.xml',
        "views/application_menu.xml",

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
