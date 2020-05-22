# -*- coding: utf-8 -*-
{
    'name': "Proximaas - PaaS de Gestion Couverture Maladie",

    'summary': """
        Plateforme de Gestion de Proximité
        Médicale et Assistance à l'Accès aux Soins.
        """,

    'description': """
        Proximaas :
        Plateforme de Gestion de Proximité Médicale et Assistance à l'Accès aux Soins..
        """,

    'author': "SIGEM",
    'website': "http://www.sigemci.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Medical',
    'version': '0.1',
    "application": True,
    "installable": True,
    # any module necessary for this one to work correctly
    'depends': ['base','board','mail'],

    # always loaded
    'data': [
        'security/proximas_medical_security.xml',
        'views/proximas_reseau_soins.xml',
        'views/proximas_parametres.xml',
        'views/proximas_medical.xml',
        'views/proximas_police.xml',
        'views/proximas_assure.xml',
        'views/assure_view_template.xml',
        'views/twiml_template.xml',
        'views/prise_charge_workflow.xml',
        'views/remb_fm_workflow.xml',
        'reports/prise_en_charge_report.xml',
        'reports/prise_charge_report_print.xml',
        'reports/prise_charge_report_print_calibrage.xml',
        # 'reports/prise_charge_détails_report.xml',
        'views/proximas_prise_charge.xml',
        'views/facture_workflow.xml',
        'reports/proximas_facture_report.xml',
        'reports/facture_prestataire_report.xml',
        'views/proximas_facture.xml',
        'reports/remboursement_frais_medicaux_report.xml',
        'views/proximas_remboursement.xml',
        'views/accord_pec_mail_template.xml',
        'views/proximas_menu.xml',
        'security/ir.model.access.csv',
        'views/proximas_dashboard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}