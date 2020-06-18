# -*- coding:utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE - Sadjidine
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp.tools.translate import _
from openerp import api, fields, models
from openerp.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta
# from random import randint
from openerp.tools import amount_to_text_fr
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class ReportSinistreRecapWizard(models.TransientModel):
    _name = 'proximas.sinistre.report.wizard'
    _description = 'Details PEC Report Wizard'

    date_debut = fields.Date(
        string="Date Début",
        required=True,
    )
    date_fin = fields.Date(
        string="Date Fin",
        default=fields.Date.today,
        required=True,
    )
    report_kpi = fields.Selection(
        string="Indicateur",
        selection=[
            ('contrat', 'Famille (Contrat)'),
            ('assure', 'Assuré (Bénéficiare)'),
            ('prestataire', 'Prestataire Soins médicaux'),
            ('medecin', 'Médecin Traitant'),
            ('groupe', 'Groupe (Organe)'),
            ('localite', 'Localité'),
            # ('zone', 'Zone adminsitrative'),
            ('rubrique', 'Rubrique médicale'),
        ],
        default='contrat',
        required=True,
    )
    report_type = fields.Selection(
        string="Type Rapport",
        selection=[
            ('detail', 'Détaillé'),
            ('groupe', 'Synthèse'),
        ],
        default='groupe',
        required=True,
    )
    report_data = fields.Selection(
        string="Type données",
        selection=[
            ('rubrique', 'Rubrique Médicale'),
            ('prestation', 'Prestation Médicale'),
            ('assure', 'Assuré (Bénéficiaire)'),
        ],
    )
    contrat_limit = fields.Boolean(
        string="20 plus gros contrats sinistrés",
    )
    assure_limit = fields.Boolean(
        string="20 plus gros bénéficiaires sinistrés",
    )
    police_filter = fields.Boolean(
        string="Filtre/Police",
    )
    police_id = fields.Many2one (
        comodel_name="proximas.police",
        string="Police Couverture",
        required=False,
    )
    contrat_id = fields.Many2one(
        comodel_name="proximas.contrat",
        string="Contrat Adhérent",
        required=False,
    )
    assure_id = fields.Many2one(
        comodel_name="proximas.assure",
        string="Assuré (Bénéficiaire)",
        required=False,
    )
    prestataire_id = fields.Many2one (
        comodel_name="res.partner",
        string="Prestataire de soins",
        domain=[('is_prestataire', '=', True)],
        required=False,
    )
    medecin_id = fields.Many2one (
        comodel_name="proximas.medecin",
        string="Médecin Traitant",
        required=False,
    )
    rubrique_id = fields.Many2one (
        comodel_name="proximas.rubrique.medicale",
        string="Rubrique Médicale",
        required=False,
    )
    groupe_id = fields.Many2one (
        comodel_name="proximas.groupe",
        string="Groupe",
        required=False,
    )
    localite_id = fields.Many2one (
        comodel_name="proximas.localite",
        string="Localité",
        required=False,
    )
    # zone_id = fields.Many2one (
    #     comodel_name="proximas.zone",
    #     string="Zone Géographique",
    #     required=False,
    # )

    @api.multi
    def get_report(self):
        """"
            Methode à appeler au clic sur le bouton "Valider" du formulaire Wuzard
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_debut': self.date_debut,
                'date_fin': self.date_fin,
                'report_kpi': self.report_kpi,
                'report_type': self.report_type,
                'report_data': self.report_data,
                'police_filter': self.police_filter,
                'police_id': self.police_id.id,
                'contrat_id': self.contrat_id.id,
                'assure_id': self.assure_id.id,
                'rubrique_id': self.rubrique_id.id,
                'prestataire_id': self.prestataire_id.id,
                'medecin_id': self.medecin_id.id,
                'groupe_id': self.groupe_id.id,
                'localite_id': self.localite_id.id,
                'contrat_limit': self.contrat_limit,
                'assure_limit': self.assure_limit,
                # 'zone_id': self.zone_id.id,
            },
        }

        return self.env['report'].get_action(self, 'proximas_medical.report_suivi_sinistres_view', data=data)

    # CONTRAINTES
    _sql_constraints = [
        ('check_dates',
         'CHECK (date_debut <= date_fin)',
         '''
         Erreurs sur les date début et date fin!
         La date début doit obligatoirement être inférieure (antérieure) à la date de fin...
         Vérifiez s'il n'y pas d'erreur de saisies sur les dates ou contactez l'administrateur.
         '''
         )
    ]

class ReportPecDetailsRecap(models.AbstractModel):
    """
        Abstract Model for report template.
        for '_name' model, please use 'report.' as prefix then add 'module_name.report_name'.
    """
    _name = 'report.proximas_medical.report_suivi_sinistres_view'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        # print'>>>>>>>>>>>>>>>>>......', report_obj
        report = report_obj._get_report_from_name('proximas_medical.report_suivi_sinistres_view')
        # print'>>>>>>>>>>>>>>>>>......', report
        date_debut = data['form']['date_debut']
        date_fin = data['form']['date_fin']
        report_kpi = data['form']['report_kpi']
        report_type = data['form']['report_type']
        report_data = data['form']['report_data']
        police_filter = data['form']['police_filter']
        date_debut_obj = datetime.strptime(date_debut, DATE_FORMAT)
        date_fin_obj = datetime.strptime(date_fin, DATE_FORMAT)
        date_diff = (date_fin_obj - date_debut_obj).days + 1
        police_id = data['form']['police_id']
        contrat_id = data['form']['contrat_id']
        assure_id = data['form']['assure_id']
        rubrique_id = data['form']['rubrique_id']
        prestataire_id = data['form']['prestataire_id']
        medecin_id = data['form']['medecin_id']
        groupe_id = data['form']['groupe_id']
        localite_id = data['form']['localite_id']
        contrat_limit = data['form']['contrat_limit']
        assure_limit = data['form']['assure_limit']
        # zone_id = data['form']['zone_id']

        docs = []
        docargs = {}
        police = self.env['proximas.police'].search([
            ('id', '=', police_id)
        ], order='name asc')
        # 1.1. RAPPORT SINISTRALITE DETAILLE PAR CONTRAT (FAMILLE)
        if report_kpi == 'contrat' and report_type == 'detail':
            contrat = self.env['proximas.contrat'].search([('id', '=', contrat_id)])
            # PRESENTATION PAR RUBRIQUE
            if report_data == 'rubrique':
                rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')
                for rubrique in rubriques:
                    if bool(contrat_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif bool(contrat_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Suivi Evolution Sinistres: \n\
                            Après recherche, aucun contrat ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % rubrique.name
                        )
                    if bool(details_pec):
                        rubrique_id = rubrique.id
                        rubrique_medicale = rubrique.name
                        nbre_actes = len(details_pec) or 0
                        cout_total = sum(item.cout_total for item in details_pec) or 0
                        total_pc = sum(item.total_pc for item in details_pec) or 0
                        total_npc = sum(item.total_npc for item in details_pec) or 0
                        total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int(net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int(net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'rubrique_id': rubrique_id,
                            'rubrique_medicale': rubrique_medicale,
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'contrat_id': contrat_id,
                        'num_contrat': contrat.num_contrat,
                        'date_activation': datetime.strptime(contrat.date_activation, DATE_FORMAT).strftime('%d/%m/%Y'),
                        'effectif_contrat': contrat.effectif_contrat,
                        'code_id_externe': contrat.code_id_externe,
                        'matricule': contrat.matricule,
                        'groupe_id': contrat.groupe_id,
                        'photo': contrat.adherent_id.image,
                        'adherent': contrat.adherent_id.name,
                        'code_id': contrat.adherent_id.code_id,
                        'city': contrat.adherent_id.city,
                        'phone': contrat.adherent_id.phone,
                        'mobile': contrat.adherent_id.mobile,
                        'note': contrat.adherent_id.note,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PRESTATION
            elif report_data == 'prestation':
                prestations = self.env['proximas.code.prestation'].search([], order='name asc')
                for prestation in prestations:
                    if bool(contrat_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('prestation_id', '=', prestation.id),
                        ])
                    elif bool (contrat_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('prestation_id', '=', prestation.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % prestation.name
                                         )
                    if bool (details_pec):
                        prestation_id = prestation.id
                        prestation_medicale = prestation.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'prestation_id': prestation_id,
                            'prestation_medicale': prestation_medicale,
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted (docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime(date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime(date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'contrat_id': contrat_id,
                        'num_contrat': contrat.num_contrat,
                        'matricule': contrat.matricule,
                        'groupe_id': contrat.groupe_id,
                        'photo': contrat.adherent_id.image,
                        'adherent': contrat.adherent_id.name,
                        'code_id': contrat.adherent_id.code_id,
                        'city': contrat.adherent_id.city,
                        'phone': contrat.adherent_id.phone,
                        'mobile': contrat.adherent_id.mobile,
                        'note': contrat.adherent_id.note,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PATIENT (ASSURE)
            elif report_data == 'assure':
                assures = self.env['proximas.assure'].search([
                    ('contrat_id', '=', contrat_id),
                ])
                for assure in assures:
                    assure_pec = self.env['proximas.prise.charge'].search([
                        ('assure_id', '=', assure.id),
                    ])
                    if bool(contrat_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('assure_id', '=', assure.id),
                        ])
                    elif bool(contrat_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('assure_id', '=', assure.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour le contrat. \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        )
                                         )
                    if bool(details_pec):
                        assure_id = assure.id
                        assure_name = assure.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append ({
                            'assure_id': assure_id,
                            'code_id': assure.code_id,
                            'assure_name': assure_name,
                            'statut_familial': assure.statut_familial,
                            'age': assure.age,
                            'genre': assure.genre,
                            'nbre_pec': len(assure_pec),
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted (docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'contrat_id': contrat_id,
                        'num_contrat': contrat.num_contrat,
                        'matricule': contrat.matricule,
                        'groupe_id': contrat.groupe_id,
                        'photo': contrat.adherent_id.image,
                        'adherent': contrat.adherent_id.name,
                        'code_id': contrat.adherent_id.code_id,
                        'city': contrat.adherent_id.city,
                        'phone': contrat.adherent_id.phone,
                        'mobile': contrat.adherent_id.mobile,
                        'note': contrat.adherent_id.note,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 1.2. RAPPORT SYNTHESE SINISTRALITE PAR CONTRAT (FAMILLE)
        elif report_kpi == 'contrat' and report_type == 'groupe':
            contrats = self.env['proximas.contrat'].search([])
            if police_filter:
                contrats = self.env['proximas.contrat'].search([
                    ('police_id', '=', police_id),
                ], order='id asc')
            for contrat in contrats:
                # DETAILS PEC TRAITES ET LIES A UN CONTRAT
                details_pec = self.env['proximas.details.pec'].search ([
                    ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                    ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                    ('prestataire', '!=', None),
                    ('contrat_id', '=', contrat.id),
                ])
                if bool(details_pec):
                    name_length = len(contrat.adherent_id.name)
                    if int(name_length) > 60:
                        adherent = contrat.adherent_id.name[:40] + '...'
                    else:
                        adherent = contrat.adherent_id.name
                    code_id = contrat.adherent_id.code_id
                    code_id_externe = contrat.adherent_id.code_id_externe
                    date_activation = contrat.adherent_id.date_activation
                    num_contrat = contrat.adherent_id.num_contrat
                    matricule = contrat.adherent_id.matricule
                    groupe_name = contrat.groupe_id.name
                    nbre_actes = len(details_pec) or 0
                    cout_total = sum(item.cout_total for item in details_pec) or 0
                    total_pc = sum(item.total_pc for item in details_pec) or 0
                    total_npc = sum(item.total_npc for item in details_pec) or 0
                    total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                    net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                    net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                    # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                    net_a_payer = 0
                    if net_prestataire:
                        net_a_payer = int (net_prestataire)
                    elif net_remboursement:
                        net_a_payer = int (net_remboursement)
                    else:
                        net_a_payer = 0

                    docs.append({
                        'adherent': adherent,
                        'code_id': code_id,
                        'code_id_externe': code_id_externe,
                        'num_contrat': num_contrat,
                        'matricule': matricule,
                        'groupe_name': groupe_name,
                        'date_activation': datetime.strptime(date_activation, DATE_FORMAT).strftime('%d/%m/%Y'),
                        'nbre_actes': int(nbre_actes),
                        'cout_total': int(cout_total),
                        'total_pc': int(total_pc),
                        'total_npc': int(total_npc),
                        'total_exclusion': int(total_exclusion),
                        'ticket_moderateur': int(ticket_moderateur),
                        'net_tiers_payeur': int(net_tiers_payeur),
                        'net_prestataire': int(net_prestataire),
                        'net_remboursement': int(net_remboursement),
                        'net_a_payer': int(net_a_payer),
                    })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'police_filter': police_filter,
                        'contrat_limit': contrat_limit,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs[0:20] if contrat_limit else docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))

        # 2.1. RAPPORT SINISTRALITE DETAILLE PAR BENEFICIAIRE (ASSURE)
        if report_kpi == 'assure' and report_type == 'detail':
            assure = self.env['proximas.assure'].search([('id', '=', assure_id)])
            # PRESENTATION PAR RUBRIQUE
            if report_data == 'rubrique':
                rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')
                for rubrique in rubriques:
                    if bool(assure_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('assure_id', '=', assure.id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif bool(assure_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('assure_id', '=', assure.id),
                            ('prestataire', '!=', None),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    else:
                        raise UserError(_(
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun contrat ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % rubrique.name
                                         )
                    if bool(details_pec):
                        rubrique_id = rubrique.id
                        rubrique_medicale = rubrique.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'rubrique_id': rubrique_id,
                            'rubrique_medicale': rubrique_medicale,
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'assure_id': assure_id,
                        'code_id': assure.code_id,
                        'date_activation': datetime.strptime(assure.date_activation, DATE_FORMAT).strftime(
                            '%d/%m/%Y'),
                        'code_id_externe': assure.code_id_externe,
                        'contrat_id': assure.contrat_id,
                        'num_contrat': assure.contrat_id.num_contrat,
                        'adherent': assure.contrat_id.adherent_id.name,
                        'groupe_id': assure.groupe_id,
                        'photo': assure.image,
                        'assure': assure.name,
                        'date_naissance': datetime.strptime(assure.date_naissance, DATE_FORMAT).strftime(
                            '%d/%m/%Y'),
                        'age': assure.age,
                        'statut_familial': assure.statut_familial,
                        'genre': assure.genre,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PRESTATION
            elif report_data == 'prestation':
                prestations = self.env['proximas.code.prestation'].search([], order='name asc')
                for prestation in prestations:
                    if bool(assure_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('assure_id', '=', assure.id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('prestation_id', '=', prestation.id),
                        ])
                    elif bool(assure_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('assure_id', '=', assure.id),
                            ('prestataire', '!=', None),
                            ('prestation_id', '=', prestation.id),
                        ])
                    else:
                        raise UserError(_(
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % prestation.name
                                         )
                    if bool (details_pec):
                        prestation_id = prestation.id
                        prestation_medicale = prestation.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append ({
                            'prestation_id': prestation_id,
                            'prestation_medicale': prestation_medicale,
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'assure_id': assure_id,
                        'code_id': assure.code_id,
                        'date_activation': datetime.strptime (assure.date_activation, DATE_FORMAT).strftime (
                            '%d/%m/%Y'),
                        'code_id_externe': assure.code_id_externe,
                        'contrat_id': assure.contrat_id,
                        'num_contrat': assure.contrat_id.num_contrat,
                        'adherent': assure.contrat_id.adherent_id.name,
                        'groupe_id': assure.groupe_id,
                        'photo': assure.image,
                        'assure': assure.name,
                        'date_naissance': datetime.strptime(assure.date_naissance, DATE_FORMAT).strftime(
                            '%d/%m/%Y'),
                        'age': assure.age,
                        'statut_familial': assure.statut_familial,
                        'genre': assure.genre,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PATIENT (ASSURE)
            elif report_data == 'assure':
                assure_pec = self.env['proximas.prise.charge'].search([
                    ('assure_id', '=', assure_id),
                ])
                if bool(assure_id) and police_filter:
                    # ETAILS PEC TRAITES ET LIES A l'ASSURE ET LA POLICE
                    details_pec = self.env['proximas.details.pec'].search([
                        ('date_execution', '!=', None),
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('assure_id', '=', assure_id),
                        ('prestataire', '!=', None),
                        ('police_id', '=', police_id),
                    ])
                elif bool(assure_id) and not police_filter:
                    # ETAILS PEC TRAITES ET LIES AU CONTRAT
                    details_pec = self.env['proximas.details.pec'].search([
                        ('date_execution', '!=', None),
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('assure_id', '=', assure_id),
                        ('prestataire', '!=', None),
                    ])
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée pour l'assuré indiqué. \
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    )
                    )
                if bool(details_pec):
                    # details_pec_assure = details_pec
                    assure_pec = len(assure_pec)
                    assure_id = assure.id
                    assure_name = assure.name
                    nbre_actes = len (details_pec) or 0
                    cout_total = sum (item.cout_total for item in details_pec) or 0
                    total_pc = sum (item.total_pc for item in details_pec) or 0
                    total_npc = sum (item.total_npc for item in details_pec) or 0
                    total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                    net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                    net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                    net_a_payer = 0
                    if net_prestataire:
                        net_a_payer = int (net_prestataire)
                    elif net_remboursement:
                        net_a_payer = int (net_remboursement)
                    else:
                        net_a_payer = 0

                    docs.append({
                        'assure_id': assure_id,
                        'code_id': assure.code_id,
                        'assure_name': assure_name,
                        'statut_familial': assure.statut_familial,
                        'age': assure.age,
                        'genre': assure.genre,
                        'nbre_pec': assure_pec,
                        'nbre_actes': int (nbre_actes),
                        'cout_total': int (cout_total),
                        'total_pc': int (total_pc),
                        'total_npc': int (total_npc),
                        'total_exclusion': int (total_exclusion),
                        'ticket_moderateur': int (ticket_moderateur),
                        'net_tiers_payeur': int (net_tiers_payeur),
                        'net_prestataire': int (net_prestataire),
                        'net_remboursement': int (net_remboursement),
                        'net_a_payer': int (net_a_payer),
                    })
                if bool(docs):
                    details_pec = sorted(details_pec, key=lambda x: x['date_execution'], reverse=True)
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'assure_id': assure_id,
                        'code_id': assure.code_id,
                        'date_activation': datetime.strptime (assure.date_activation, DATE_FORMAT).strftime(
                            '%d/%m/%Y'),
                        'code_id_externe': assure.code_id_externe,
                        'contrat_id': assure.contrat_id,
                        'num_contrat': assure.contrat_id.num_contrat,
                        'adherent': assure.contrat_id.adherent_id.name,
                        'groupe_id': assure.groupe_id,
                        'photo': assure.image,
                        'assure': assure.name,
                        'date_naissance': datetime.strptime(assure.date_naissance, DATE_FORMAT).strftime(
                            '%d/%m/%Y'),
                        'age': assure.age,
                        'statut_familial': assure.statut_familial,
                        'genre': assure.genre,
                        'details_pec_assure': details_pec,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 2.2. RAPPORT SYNTHESE SINISTRALITE PAR BENEFICIAIRE (ASSURE)
        elif report_kpi == 'assure' and report_type == 'groupe':
            assures = self.env['proximas.assure'].search([])
            if police_filter:
                assures = self.env['proximas.assures'].search([
                    ('police_id', '=', police_id),
                ], order='id asc')
            for assure in assures:
                # DETAILS PEC TRAITES ET LIES A UN CONTRAT
                details_pec = self.env['proximas.details.pec'].search ([
                    ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                    ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                    ('prestataire', '!=', None),
                    ('assure_id', '=', assure.id),
                ])
                if bool(details_pec):
                    name_length = len(assure.name)
                    if int(name_length) > 60:
                        beneficiaire = assure.name[:40] + '...'
                    else:
                        beneficiaire = assure.name
                    code_id = assure.code_id
                    code_id_externe = assure.code_id_externe
                    date_naissance = assure.date_naissance
                    statut_familial = assure.statut_familial
                    genre = assure.genre
                    date_activation = assure.date_activation
                    num_contrat = assure.contrat_id.num_contrat
                    adherent = assure.contrat_id.adherent_id.name
                    matricule = assure.contrat_id.matricule
                    groupe_name = assure.groupe_id.name
                    nbre_actes = len (details_pec) or 0
                    cout_total = sum (item.cout_total for item in details_pec) or 0
                    total_pc = sum (item.total_pc for item in details_pec) or 0
                    total_npc = sum (item.total_npc for item in details_pec) or 0
                    total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                    net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                    net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                    # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                    net_a_payer = 0
                    if net_prestataire:
                        net_a_payer = int (net_prestataire)
                    elif net_remboursement:
                        net_a_payer = int (net_remboursement)
                    else:
                        net_a_payer = 0

                    docs.append({
                        'adherent': adherent,
                        'code_id': code_id,
                        'beneficiaire': beneficiaire,
                        'code_id_externe': code_id_externe,
                        'date_naissance': datetime.strptime(assure.date_naissance, DATE_FORMAT).strftime(
                            '%d/%m/%Y'),
                        'statut_familial': statut_familial,
                        'genre': genre,
                        'num_contrat': num_contrat,
                        'matricule': matricule,
                        'groupe_name': groupe_name,
                        'date_activation': datetime.strptime (date_activation, DATE_FORMAT).strftime (
                            '%d/%m/%Y'),
                        'nbre_actes': int (nbre_actes),
                        'cout_total': int (cout_total),
                        'total_pc': int (total_pc),
                        'total_npc': int (total_npc),
                        'total_exclusion': int (total_exclusion),
                        'ticket_moderateur': int (ticket_moderateur),
                        'net_tiers_payeur': int (net_tiers_payeur),
                        'net_prestataire': int (net_prestataire),
                        'net_remboursement': int (net_remboursement),
                        'net_a_payer': int (net_a_payer),
                    })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'police_filter': police_filter,
                        'assure_limit': assure_limit,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs[0:20] if assure_limit else docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 3.1. RAPPORT SINISTRALITE DETAILLE PAR PRESTATAIRE DE SOINS
        if report_kpi == 'prestataire' and report_type == 'detail':
            prestataire = self.env['res.partner'].search([
                ('id', '=', prestataire_id),
            ])
            # PRESENTATION PAR RUBRIQUE
            if report_data == 'rubrique':
                rubriques = self.env['proximas.rubrique.medicale'].search ([], order='name asc')
                for rubrique in rubriques:
                    if bool(prestataire_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('prestataire', '=', prestataire.id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif bool(prestataire_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('prestataire', '=', prestataire.id),
                            ('prestataire', '!=', None),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun contrat ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % rubrique.name
                                         )
                    if bool(details_pec):
                        rubrique_id = rubrique.id
                        rubrique_medicale = rubrique.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'rubrique_id': rubrique_id,
                            'rubrique_medicale': rubrique_medicale,
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'prestataire_id': prestataire_id,
                        'prestataire': prestataire.name,
                        'categorie': prestataire.categorie_id.name,
                        'city': prestataire.city,
                        'phone': prestataire.phone,
                        'mobile': prestataire.mobile,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PRESTATION
            elif report_data == 'prestation':
                prestations = self.env['proximas.code.prestation'].search ([], order='name asc')
                for prestation in prestations:
                    if bool(prestataire_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('prestataire', '=', prestataire.id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('prestation_id', '=', prestation.id),
                        ])
                    elif bool(prestataire_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('prestataire', '=', prestataire.id),
                            ('prestataire', '!=', None),
                            ('prestation_id', '=', prestation.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % prestation.name
                                         )
                    if bool(details_pec):
                        prestation_id = prestation.id
                        prestation_medicale = prestation.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'prestation_id': prestation_id,
                            'prestation_medicale': prestation_medicale,
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted (docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'prestataire_id': prestataire_id,
                        'prestataire': prestataire.name,
                        'categorie': prestataire.categorie_id.name,
                        'city': prestataire.city,
                        'phone': prestataire.phone,
                        'mobile': prestataire.mobile,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PATIENT (ASSURE)
            elif report_data == 'assure':
                assures = self.env['proximas.assure'].search([])
                for assure in assures:
                    assure_pec = self.env['proximas.prise.charge'].search ([
                        ('assure_id', '=', assure.id),
                    ])
                    if bool(prestataire_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            # ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('prestataire', '=', prestataire.id),
                        ])
                    elif bool(prestataire_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            # ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('prestataire', '=', prestataire.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour le prestataire\
                             indiqué. Par conséquent, le système ne peut vous fournir un rapport dont le contenu est \
                             vide. Veuillez contacter les administrateurs pour plus détails..."
                        )
                        )
                    if bool(details_pec):
                        assure_id = assure.id
                        assure_name = assure.name
                        nbre_actes = len(details_pec) or 0
                        cout_total = sum(item.cout_total for item in details_pec) or 0
                        total_pc = sum(item.total_pc for item in details_pec) or 0
                        total_npc = sum(item.total_npc for item in details_pec) or 0
                        total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int(net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int(net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append ({
                            'assure_id': assure_id,
                            'code_id': assure.code_id,
                            'assure_name': assure_name,
                            'statut_familial': assure.statut_familial,
                            'age': assure.age,
                            'genre': assure.genre,
                            'nbre_pec': len(assure_pec),
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime(date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime(date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'prestataire_id': prestataire_id,
                        'prestataire': prestataire.name,
                        'categorie': prestataire.categorie_id.name,
                        'city': prestataire.city,
                        'phone': prestataire.phone,
                        'mobile': prestataire.mobile,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 3.2. RAPPORT SYNTHESE SINISTRALITE PAR PRESTATAIRE DE SOINS
        elif report_kpi == 'prestataire' and report_type == 'groupe':
            prestataires = self.env['res.partner'].search([
                ('is_prestataire', '=', True),
            ], order='id asc')
            for prestataire in prestataires:
                # DETAILS PEC TRAITES ET LIES A UN CONTRAT
                if police_id:
                    details_pec = self.env['proximas.details.pec'].search ([
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('prestataire', '!=', None),
                        ('prestataire', '=', prestataire.id),
                        ('police_id', '=', police_id),
                    ])
                else:
                    details_pec = self.env['proximas.details.pec'].search ([
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('prestataire', '!=', None),
                        ('prestataire', '=', prestataire.id),
                    ])
                if bool(details_pec):
                    name_length = len(prestataire.name)
                    if int(name_length) > 60:
                        prestataire_name = prestataire.name[:40] + '...'
                    else:
                        prestataire_name = prestataire.name
                    categorie = prestataire.categorie_id.name
                    city = prestataire.city
                    phone = prestataire.phone
                    mobile = prestataire.mobile
                    nbre_actes = len(details_pec) or 0
                    cout_total = sum(item.cout_total for item in details_pec) or 0
                    total_pc = sum(item.total_pc for item in details_pec) or 0
                    total_npc = sum(item.total_npc for item in details_pec) or 0
                    total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                    net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                    net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                    # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                    net_a_payer = 0
                    if net_prestataire:
                        net_a_payer = int(net_prestataire)
                    elif net_remboursement:
                        net_a_payer = int(net_remboursement)
                    else:
                        net_a_payer = 0

                    docs.append({
                        'prestataire': prestataire_name,
                        'categorie': categorie,
                        'city': city,
                        'phone': phone,
                        'mobile': mobile,
                        'nbre_actes': int(nbre_actes),
                        'cout_total': int(cout_total),
                        'total_pc': int(total_pc),
                        'total_npc': int(total_npc),
                        'total_exclusion': int(total_exclusion),
                        'ticket_moderateur': int(ticket_moderateur),
                        'net_tiers_payeur': int(net_tiers_payeur),
                        'net_prestataire': int(net_prestataire),
                        'net_remboursement': int(net_remboursement),
                        'net_a_payer': int(net_a_payer),
                    })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime(date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime(date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 4.1. RAPPORT SINISTRALITE DETAILLE PAR MEDECIN
        if report_kpi == 'medecin' and report_type == 'detail':
            medecin = self.env['proximas.medecin'].search([
                ('id', '=', medecin_id),
            ])
            # PRESENTATION PAR RUBRIQUE
            if report_data == 'rubrique':
                rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')
                for rubrique in rubriques:
                    if bool(medecin_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('medecin_id', '=', medecin.id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif bool(medecin_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('medecin_id', '=', medecin.id),
                            ('prestataire', '!=', None),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun contrat ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % rubrique.name
                                         )
                    if bool(details_pec):
                        rubrique_id = rubrique.id
                        rubrique_medicale = rubrique.name
                        nbre_actes = len(details_pec) or 0
                        cout_total = sum(item.cout_total for item in details_pec) or 0
                        total_pc = sum(item.total_pc for item in details_pec) or 0
                        total_npc = sum(item.total_npc for item in details_pec) or 0
                        total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int(net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int(net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'rubrique_id': rubrique_id,
                            'rubrique_medicale': rubrique_medicale,
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'medecin_id': medecin_id,
                        'medecin': medecin.name,
                        'grade': medecin.grade_id.name,
                        'city': medecin.city,
                        'phone': medecin.phone,
                        'mobile': medecin.mobile,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PRESTATION
            elif report_data == 'prestation':
                prestations = self.env['proximas.code.prestation'].search([], order='name asc')
                for prestation in prestations:
                    if bool(medecin_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('medecin_id', '=', medecin.id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('code_prestation_id', '=', prestation.id),
                        ])
                    elif bool(medecin_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('medecin_id', '=', medecin.id),
                            ('prestataire', '!=', None),
                            ('code_prestation_id', '=', prestation.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % prestation.name
                                         )
                    if bool(details_pec):
                        prestation_id = prestation.id
                        prestation_medicale = prestation.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append ({
                            'prestation_id': prestation_id,
                            'prestation_medicale': prestation_medicale,
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'medecin_id': medecin_id,
                        'medecin': medecin.name,
                        'grade': medecin.grade_id.name,
                        'city': medecin.city,
                        'phone': medecin.phone,
                        'mobile': medecin.mobile,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PATIENT (ASSURE)
            elif report_data == 'assure':
                assures = self.env['proximas.assure'].search([])
                for assure in assures:
                    assure_pec = self.env['proximas.prise.charge'].search([
                        ('assure_id', '=', assure.id),
                    ])
                    if bool(medecin_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            # ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('medecin_id', '=', medecin.id),
                        ])
                    elif bool(medecin_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            # ('contrat_id', '=', contrat_id),
                            ('prestataire', '!=', None),
                            ('medecin_id', '=', medecin.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour le prestataire\
                             indiqué. Par conséquent, le système ne peut vous fournir un rapport dont le contenu est \
                             vide. Veuillez contacter les administrateurs pour plus détails..."
                        )
                        )
                    if bool(details_pec):
                        assure_id = assure.id
                        assure_name = assure.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'assure_id': assure_id,
                            'code_id': assure.code_id,
                            'assure_name': assure_name,
                            'statut_familial': assure.statut_familial,
                            'age': assure.age,
                            'genre': assure.genre,
                            'nbre_pec': len (assure_pec),
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted (docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime(date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime(date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'medecin_id': medecin_id,
                        'medecin': medecin.name,
                        'grade': medecin.grade_id.name,
                        'city': medecin.city,
                        'phone': medecin.phone,
                        'mobile': medecin.mobile,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 4.2. RAPPORT SYNTHESE SINISTRALITE PAR MEDECIN
        elif report_kpi == 'medecin' and report_type == 'groupe':
            medecins = self.env['proximas.medecin'].search([])
            for medecin in medecins:
                # DETAILS PEC TRAITES ET LIES A UN CONTRAT
                details_pec = self.env['proximas.details.pec'].search ([
                    ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                    ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                    ('prestataire', '!=', None),
                    ('medecin_id', '=', medecin.id),
                ])
                if bool(details_pec):
                    name_length = len(medecin.name)
                    if int(name_length) > 60:
                        medecin_name = medecin.name[:40] + '...'
                    else:
                        medecin_name = medecin.name
                    grade = medecin.grade_id.name
                    city = medecin.city
                    phone = medecin.phone
                    mobile = medecin.mobile
                    nbre_actes = len (details_pec) or 0
                    cout_total = sum (item.cout_total for item in details_pec) or 0
                    total_pc = sum (item.total_pc for item in details_pec) or 0
                    total_npc = sum (item.total_npc for item in details_pec) or 0
                    total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                    net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                    net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                    # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                    net_a_payer = 0
                    if net_prestataire:
                        net_a_payer = int (net_prestataire)
                    elif net_remboursement:
                        net_a_payer = int(net_remboursement)
                    else:
                        net_a_payer = 0

                    docs.append({
                        'medecin': medecin_name,
                        'grade': grade,
                        'city': city,
                        'phone': phone,
                        'mobile': mobile,
                        'nbre_actes': int(nbre_actes),
                        'cout_total': int(cout_total),
                        'total_pc': int(total_pc),
                        'total_npc': int(total_npc),
                        'total_exclusion': int(total_exclusion),
                        'ticket_moderateur': int(ticket_moderateur),
                        'net_tiers_payeur': int(net_tiers_payeur),
                        'net_prestataire': int(net_prestataire),
                        'net_remboursement': int(net_remboursement),
                        'net_a_payer': int(net_a_payer),
                    })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))

        ################################################################################################################
        # 5.1. RAPPORT SINISTRALITE DETAILLE PAR GROUPE D'ADHERENTS
        if report_kpi == 'groupe' and report_type == 'detail':
            groupe = self.env['proximas.groupe'].search([
                ('id', '=', groupe_id),
            ])
            # PRESENTATION PAR RUBRIQUE
            if report_data == 'rubrique':
                rubriques = self.env['proximas.rubrique.medicale'].search ([], order='name asc')
                for rubrique in rubriques:
                    if bool(groupe_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('groupe_id', '=', groupe_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif bool(groupe_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('groupe_id', '=', groupe_id),
                            ('prestataire', '!=', None),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    else:
                        raise UserError(_(
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun contrat ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % rubrique.name
                                         )
                    if bool(details_pec):
                        rubrique_id = rubrique.id
                        rubrique_medicale = rubrique.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int(net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int(net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'rubrique_id': rubrique_id,
                            'rubrique_medicale': rubrique_medicale,
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'groupe_id': groupe_id,
                        'groupe': groupe.name,
                        'city': groupe.city,
                        'phone': groupe.phone,
                        'mobile': groupe.mobile,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PRESTATION
            elif report_data == 'prestation':
                prestations = self.env['proximas.code.prestation'].search([], order='name asc')
                for prestation in prestations:
                    if bool(groupe_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('groupe_id', '=', groupe_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('prestation_id', '=', prestation.id),
                        ])
                    elif bool(groupe_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('groupe_id', '=', groupe_id),
                            ('prestataire', '!=', None),
                            ('prestation_id', '=', prestation.id),
                        ])
                    else:
                        raise UserError(_(
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % prestation.name
                                         )
                    if bool(details_pec):
                        prestation_id = prestation.id
                        prestation_medicale = prestation.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'prestation_id': prestation_id,
                            'prestation_medicale': prestation_medicale,
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'groupe_id': groupe_id,
                        'groupe': groupe.name,
                        'city': groupe.city,
                        'phone': groupe.phone,
                        'mobile': groupe.mobile,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PATIENT (ASSURE)
            elif report_data == 'assure':
                assures = self.env['proximas.assure'].search([])
                for assure in assures:
                    assure_pec = self.env['proximas.prise.charge'].search([
                        ('assure_id', '=', assure.id),
                    ])
                    if bool(groupe_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('groupe_id', '=', groupe_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('assure_id', '=', assure.id),
                        ])
                    elif bool(groupe_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('groupe_id', '=', groupe_id),
                            ('prestataire', '!=', None),
                            ('assure_id', '=', assure.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour le groupe concerné. \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        )
                        )
                    if bool(details_pec):
                        assure_id = assure.id
                        assure_name = assure.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append ({
                            'assure_id': assure_id,
                            'code_id': assure.code_id,
                            'assure_name': assure_name,
                            'statut_familial': assure.statut_familial,
                            'age': assure.age,
                            'genre': assure.genre,
                            'nbre_pec': len (assure_pec),
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted (docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'groupe_id': groupe_id,
                        'groupe': groupe.name,
                        'city': groupe.city,
                        'phone': groupe.phone,
                        'mobile': groupe.mobile,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 5.2. RAPPORT SYNTHESE SINISTRALITE PAR GROUPE ADHERENTS
        elif report_kpi == 'groupe' and report_type == 'groupe':
            groupes = self.env['proximas.groupe'].search([])
            for groupe in groupes:
                # DETAILS PEC TRAITES ET LIES A UN CONTRAT
                if police_filter:
                    details_pec = self.env['proximas.details.pec'].search ([
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('prestataire', '!=', None),
                        ('groupe_id', '=', groupe.id),
                        ('police_id', '=', police_id)
                    ])
                else:
                    details_pec = self.env['proximas.details.pec'].search ([
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('prestataire', '!=', None),
                        ('groupe_id', '=', groupe.id),
                    ])
                if bool(details_pec):
                    groupe_id = groupe.id
                    groupe_name = groupe.name
                    nbre_actes = len (details_pec) or 0
                    cout_total = sum (item.cout_total for item in details_pec) or 0
                    total_pc = sum (item.total_pc for item in details_pec) or 0
                    total_npc = sum (item.total_npc for item in details_pec) or 0
                    total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                    net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                    net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                    # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                    net_a_payer = 0
                    if net_prestataire:
                        net_a_payer = int (net_prestataire)
                    elif net_remboursement:
                        net_a_payer = int (net_remboursement)
                    else:
                        net_a_payer = 0

                    docs.append({
                        'groupe_id': groupe_id,
                        'groupe_name': groupe_name,
                        'nbre_actes': int(nbre_actes),
                        'cout_total': int(cout_total),
                        'total_pc': int(total_pc),
                        'total_npc': int(total_npc),
                        'total_exclusion': int(total_exclusion),
                        'ticket_moderateur': int(ticket_moderateur),
                        'net_tiers_payeur': int(net_tiers_payeur),
                        'net_prestataire': int(net_prestataire),
                        'net_remboursement': int(net_remboursement),
                        'net_a_payer': int(net_a_payer),
                    })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime(date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime(date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 6.1. RAPPORT SINISTRALITE DETAILLE PAR LOCALITE
        if report_kpi == 'localite' and report_type == 'detail':
            localite = self.env['proximas.localite'].search([
                ('id', '=', localite_id),
            ])
            # PRESENTATION PAR RUBRIQUE
            if report_data == 'rubrique':
                rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')
                for rubrique in rubriques:
                    if bool(localite_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('localite_id', '=', localite_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif bool(localite_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('localite_id', '=', localite_id),
                            ('prestataire', '!=', None),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun contrat ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % rubrique.name
                                         )
                    if bool(details_pec):
                        rubrique_id = rubrique.id
                        rubrique_medicale = rubrique.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'rubrique_id': rubrique_id,
                            'rubrique_medicale': rubrique_medicale,
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'localite_id': localite_id,
                        'localite': localite.name,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PRESTATION
            elif report_data == 'prestation':
                prestations = self.env['proximas.code.prestation'].search ([], order='name asc')
                for prestation in prestations:
                    if bool(localite_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('localite_id', '=', localite_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('prestation_id', '=', prestation.id),
                        ])
                    elif bool(localite_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('localite_id', '=', localite_id),
                            ('prestataire', '!=', None),
                            ('prestation_id', '=', prestation.id),
                        ])
                    else:
                        raise UserError(_(
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % prestation.name
                                         )
                    if bool(details_pec):
                        prestation_id = prestation.id
                        prestation_medicale = prestation.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'prestation_id': prestation_id,
                            'prestation_medicale': prestation_medicale,
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'localite_id': localite_id,
                        'localite': localite.name,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PATIENT (ASSURE)
            elif report_data == 'assure':
                assures = self.env['proximas.assure'].search([])
                for assure in assures:
                    assure_pec = self.env['proximas.prise.charge'].search([
                        ('assure_id', '=', assure.id),
                    ])
                    if bool(localite_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('assure_id', '=', assure.id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('localite_id', '=', localite_id),
                        ])
                    elif bool(localite_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('assure_id', '=', assure.id),
                            ('prestataire', '!=', None),
                            ('localite_id', '=', localite_id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour la localité indiquée. \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        )
                        )
                    if bool(details_pec):
                        assure_id = assure.id
                        assure_name = assure.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'assure_id': assure_id,
                            'code_id': assure.code_id,
                            'assure_name': assure_name,
                            'statut_familial': assure.statut_familial,
                            'age': assure.age,
                            'genre': assure.genre,
                            'nbre_pec': len (assure_pec),
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted (docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'localite_id': localite_id,
                        'localite': localite.name,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 6.2. RAPPORT SYNTHESE SINISTRALITE PAR LOCALITE
        elif report_kpi == 'localite' and report_type == 'groupe':
            localites = self.env['proximas.localite'].search([])
            for localite in localites:
                # DETAILS PEC TRAITES ET LIES A UN CONTRAT
                if police_id:
                    details_pec = self.env['proximas.details.pec'].search ([
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('prestataire', '!=', None),
                        ('localite_id', '=', localite.id),
                        ('police_id', '=', police_id),
                    ])
                else:
                    details_pec = self.env['proximas.details.pec'].search ([
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('prestataire', '!=', None),
                        ('localite_id', '=', localite.id),
                    ])
                if bool(details_pec):
                    localite_name = localite.name
                    nbre_actes = len(details_pec) or 0
                    cout_total = sum(item.cout_total for item in details_pec) or 0
                    total_pc = sum(item.total_pc for item in details_pec) or 0
                    total_npc = sum(item.total_npc for item in details_pec) or 0
                    total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                    net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                    net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                    # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                    net_a_payer = 0
                    if net_prestataire:
                        net_a_payer = int (net_prestataire)
                    elif net_remboursement:
                        net_a_payer = int (net_remboursement)
                    else:
                        net_a_payer = 0

                    docs.append({
                        'localite_name': localite_name,
                        'nbre_actes': int (nbre_actes),
                        'cout_total': int (cout_total),
                        'total_pc': int (total_pc),
                        'total_npc': int (total_npc),
                        'total_exclusion': int (total_exclusion),
                        'ticket_moderateur': int (ticket_moderateur),
                        'net_tiers_payeur': int (net_tiers_payeur),
                        'net_prestataire': int (net_prestataire),
                        'net_remboursement': int (net_remboursement),
                        'net_a_payer': int (net_a_payer),
                    })
                if bool(docs):
                    docs = sorted (docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 7.1. RAPPORT SINISTRALITE DETAILLE PAR RUBRIQUE MEDICALE
        if report_kpi == 'rubrique' and report_type == 'detail':
            # rubrique_select = self.env['proximas.rubrique.medicale'].search([
            #     ('id', '=', rubrique_id),
            # ])
            # PRESENTATION PAR RUBRIQUE
            if report_data == 'rubrique':
                rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')
                for rubrique in rubriques:
                    if bool(rubrique_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('rubrique_id', '=', rubrique_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif bool(rubrique_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('rubrique_id', '=', rubrique_id),
                            ('prestataire', '!=', None),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun contrat ne correspond à la période indiquée pour la Rubrique médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % rubrique.name
                                         )
                    if bool(details_pec):
                        rubrique_id = rubrique_id
                        rubrique_medicale = rubrique.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'rubrique_id': rubrique_id,
                            'rubrique_medicale': rubrique_medicale,
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'rubrique_id': rubrique_id,
                        'rubriquee_name': rubrique_medicale,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PRESTATION
            elif report_data == 'prestation':
                prestations = self.env['proximas.code.prestation'].search([], order='name asc')
                for prestation in prestations:
                    if bool(rubrique_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('rubrique_id', '=', rubrique_id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('prestation_id', '=', prestation.id),
                        ])
                    elif bool(rubrique_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('rubrique_id', '=', rubrique_id),
                            ('prestataire', '!=', None),
                            ('prestation_id', '=', prestation.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour la prestation médicale : %s.  \
                            Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                            Veuillez contacter les administrateurs pour plus détails..."
                        ) % prestation.name
                                         )
                    if bool(details_pec):
                        prestation_id = prestation.id
                        prestation_medicale = prestation.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'prestation_id': prestation_id,
                            'prestation_medicale': prestation_medicale,
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'rubrique_id': rubrique_id,
                        'rubrique_medicale': rubrique_medicale,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # PRESENTATION PAR PATIENT (ASSURE)
            elif report_data == 'assure':
                assures = self.env['proximas.assure'].search([])
                for assure in assures:
                    assure_pec = self.env['proximas.prise.charge'].search ([
                        ('assure_id', '=', assure.id),
                    ])
                    if bool(rubrique_id) and police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT ET LA POLICE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('assure_id', '=', assure.id),
                            ('prestataire', '!=', None),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique_id),
                        ])
                    elif bool(rubrique_id) and not police_filter:
                        # ETAILS PEC TRAITES ET LIES AU CONTRAT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('assure_id', '=', assure.id),
                            ('prestataire', '!=', None),
                            ('rubrique_id', '=', rubrique_id),
                        ])
                    else:
                        raise UserError(_(
                            "Proximaas : Rapport - Evolution Niveau Sinistres: \n\
                            Après recherche, aucun sinistre ne correspond à la période indiquée pour la rubrique médicale.\
                             indiqué. Par conséquent, le système ne peut vous fournir un rapport dont le contenu est \
                             vide. Veuillez contacter les administrateurs pour plus détails..."
                        )
                        )
                    if bool(details_pec):
                        assure_id = assure.id
                        assure_name = assure.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append ({
                            'assure_id': assure_id,
                            'code_id': assure.code_id,
                            'assure_name': assure_name,
                            'statut_familial': assure.statut_familial,
                            'age': assure.age,
                            'genre': assure.genre,
                            'nbre_pec': len (assure_pec),
                            'nbre_actes': int (nbre_actes),
                            'cout_total': int (cout_total),
                            'total_pc': int (total_pc),
                            'total_npc': int (total_npc),
                            'total_exclusion': int (total_exclusion),
                            'ticket_moderateur': int (ticket_moderateur),
                            'net_tiers_payeur': int (net_tiers_payeur),
                            'net_prestataire': int (net_prestataire),
                            'net_remboursement': int (net_remboursement),
                            'net_a_payer': int (net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'report_data': report_data,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'rubrique_id': rubrique_id,
                        'rubrique_medicale': rubrique_medicale,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        # 7.2. RAPPORT SYNTHESE SINISTRALITE PAR RUBRIQUE MEDICALE
        elif report_kpi == 'rubrique' and report_type == 'groupe':
            rubriques = self.env['proximas.rubrique.medicale'].search([])
            for rubrique in rubriques:
                # DETAILS PEC TRAITES ET LIES A UN CONTRAT
                if police_id:
                    details_pec = self.env['proximas.details.pec'].search ([
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('prestataire', '!=', None),
                        ('rubrique_id', '=', rubrique.id),
                        ('police_id', '=', police_id),
                    ])
                else:
                    details_pec = self.env['proximas.details.pec'].search ([
                        ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ('prestataire', '!=', None),
                        ('rubrique_id', '=', rubrique.id),
                    ])
                if bool(details_pec):
                    rubrique_medicale = rubrique.name
                    nbre_actes = len (details_pec) or 0
                    cout_total = sum (item.cout_total for item in details_pec) or 0
                    total_pc = sum (item.total_pc for item in details_pec) or 0
                    total_npc = sum (item.total_npc for item in details_pec) or 0
                    total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                    net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                    net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                    # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                    net_a_payer = 0
                    if net_prestataire:
                        net_a_payer = int (net_prestataire)
                    elif net_remboursement:
                        net_a_payer = int (net_remboursement)
                    else:
                        net_a_payer = 0

                    docs.append({
                        'rubrique_id': rubrique_id,
                        'rubrique_medicale': rubrique_medicale,
                        'nbre_actes': int (nbre_actes),
                        'cout_total': int (cout_total),
                        'total_pc': int (total_pc),
                        'total_npc': int (total_npc),
                        'total_exclusion': int (total_exclusion),
                        'ticket_moderateur': int (ticket_moderateur),
                        'net_tiers_payeur': int (net_tiers_payeur),
                        'net_prestataire': int (net_prestataire),
                        'net_remboursement': int (net_remboursement),
                        'net_a_payer': int (net_a_payer),
                    })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport Suivi Evolution Sinistres \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
        return report_obj.render('proximas_medical.report_suivi_sinistres_view', docargs)

    class ReglementSinistresReportWizard (models.TransientModel):
        _name = 'proximas.reglement.sinistres.report.wizard'
        _description = 'Reglements Sinistres Report Wizard'

        date_debut = fields.Date(
            string="Date Début",
            required=True,
        )
        date_fin = fields.Date(
            string="Date Fin",
            default=fields.Date.today,
            required=True,
        )
        report_kpi = fields.Selection (
            string="Indicateur de sinistralité",
            selection=[
                ('rubrique', 'Rubrique Médicale'),
                ('prestation', 'Prestation Médicale'),
                ('facture', 'Facture/Remboursement'),
                # ('medecin', 'Médecin Traitant'),
            ],
            default='rubrique',
            required=True,
        )
        report_type = fields.Selection(
            string="Type d'Etat",
            selection=[
                ('groupe', 'Synthèse'),
                ('detail', 'Détails'),
            ],
            default='groupe',
            required=True,
        )
        filter_type = fields.Selection(
            string="Type de Filtre",
            selection=[
                ('pec', 'Facture (Prestataire)'),
                ('rfm', 'Reboursements (Adhérent)'),
            ],
            default='pec',
            required=True,
        )
        police_filter = fields.Boolean(
            string="Filtre/Police?",
            help="Cochez pour filtrer l'état par police de couverture...",
        )
        police_id = fields.Many2one(
            comodel_name="proximas.police",
            string="Police Couverture",
            required=False,
        )
        prestataire_id = fields.Many2one(
            comodel_name="res.partner",
            string="Prestataire de soins",
            domain=[('is_prestataire', '=', True)],
            required=False,
        )
        adherent_id = fields.Many2one(
            comodel_name="proximas.adherent",
            string="Adhérent Souccripteur",
            required=False,
        )
        rubrique_id = fields.Many2one(
            comodel_name="proximas.rubrique.medicale",
            string="Rubrique Médicale",
            required=False,
        )
        prestation_id = fields.Many2one(
            comodel_name="proximas.code.prestation",
            string="Prestation médicale",
            required=False,
        )
        facture_id = fields.Many2one(
            comodel_name="proximas.facture",
            string="Réf. Facture",
        )
        rfm_id = fields.Many2one(
            comodel_name="proximas.remboursement.pec",
            string="Réf. Remb. frais médicaux",
        )

        @api.multi
        def facture_filter_function(self, cr, uid, context=None):
            prestataire_id = self.prestataire_id.id
            date_debut_obj = datetime.strptime(self.date_debut, DATE_FORMAT)
            date_fin_obj = datetime.strptime(self.date_fin, DATE_FORMAT)
            view_id = self.env.ref('proximas_medical.proximas_report_reglement_sinistres_wizard_form')
            context = self.env.context
            action = {
                'name': 'Filtre facture par date émission',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'proximas.facture',
                'target': 'current',
                'domain': [
                    ('prestataire_id', '=', prestataire_id),
                    ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                    ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                ],
                'context': context,
                'views': [(view_id.id, 'form')],
                'view_id': view_id,
            }
            return action

        @api.multi
        def get_report(self):
            """"
                Methode à appeler au clic sur le bouton "Valider" du formulaire Wuzard
            """
            data = {
                'ids': self.ids,
                'model': self._name,
                'form': {
                    'date_debut': self.date_debut,
                    'date_fin': self.date_fin,
                    'report_kpi': self.report_kpi,
                    'report_type': self.report_type,
                    'filter_type': self.filter_type,
                    'police_filter': self.police_filter,
                    'police_id': self.police_id.id,
                    'prestataire_id': self.prestataire_id.id,
                    'rubrique_id': self.rubrique_id.id,
                    'adherent_id': self.adherent_id.id,
                    'prestation_id': self.prestation_id.id,
                    'facture_id': self.facture_id.id,
                    'rfm_id': self.rfm_id.id,
                },
            }

            return self.env['report'].get_action(self, 'proximas_medical.report_reglements_sinistres_view', data=data)

        # CONTRAINTES
        _sql_constraints = [
            ('check_dates',
             'CHECK (date_debut < date_fin)',
             '''
             Erreurs sur les date début et date fin!
             La date début doit obligatoirement être inférieure (antérieure) à la date de fin...
             Vérifiez s'il n'y pas d'erreur de saisies sur les dates ou contactez l'administrateur.
             '''
             )
        ]

    class ReglementSinistresReport(models.AbstractModel):
        """
            Abstract Model for report template.
            for '_name' model, please use 'report.' as prefix then add 'module_name.report_name'.
        """
        _name = 'report.proximas_medical.report_reglements_sinistres_view'

        @api.multi
        def render_html(self, data=None):
            report_obj = self.env['report']

            date_debut = data['form']['date_debut']
            date_fin = data['form']['date_fin']
            report_kpi = data['form']['report_kpi']
            report_type = data['form']['report_type']
            filter_type = data['form']['filter_type']
            date_debut_obj = datetime.strptime(date_debut, DATE_FORMAT)
            date_fin_obj = datetime.strptime (date_fin, DATE_FORMAT)
            date_diff = (date_fin_obj - date_debut_obj).days + 1
            police_filter = data['form']['police_filter']
            police_id = data['form']['police_id']
            prestataire_id = data['form']['prestataire_id']
            adherent_id = data['form']['adherent_id']
            rubrique_id = data['form']['rubrique_id']
            prestation_id = data['form']['prestation_id']
            facture_id = data['form']['facture_id']
            rfm_id = data['form']['rfm_id']

            docs = []
            docargs = {}
            details_pec = []
            # 1.1. ETAT DETAILLE PAR RUBRIQUE MEDICALE
            if report_kpi == 'rubrique' and report_type == 'detail':
                now = datetime.now().strftime('%d/%m/%Y')
                rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')
                police = self.env['proximas.police'].search([('id', '=', police_id)], order='name asc')
                facture = self.env['proximas.facture'].search([('id', '=', facture_id)])
                rfm = self.env['proximas.remboursement.pec'].search([('id', '=', rfm_id)])
                adherent = self.env['proximas.adherent'].search([('id', '=', adherent_id)])
                prestataire = self.env['res.partner'].search([
                    ('id', '=', prestataire_id), ('is_prestataire', '=', True)], order='name asc')
                date_emission = facture.date_emission
                date_reception = facture.date_reception
                montant_facture = facture.montant_en_text()
                date_saisie = rfm.date_saisie
                date_depot = rfm.date_depot
                montant_rfm = rfm.net_remb_texte
                if facture:
                    date_emission = datetime.strptime(facture.date_emission, DATE_FORMAT).strftime ('%d/%m/%Y')
                    date_reception = datetime.strptime(facture.date_reception, DATE_FORMAT).strftime (
                        '%d/%m/%Y')
                if rfm:
                    date_saisie = datetime.strptime (rfm.date_saisie, DATETIME_FORMAT).strftime ('%d/%m/%Y')
                    date_depot = datetime.strptime (rfm.date_depot, DATE_FORMAT).strftime ('%d/%m/%Y')

                for rubrique in rubriques:
                    if filter_type == 'pec' and bool(prestataire_id) and bool(facture_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('facture_id', '=', facture.id),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif filter_type == 'pec' and bool(prestataire_id) and bool(facture_id) and not police_filter :
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('facture_id', '=', facture.id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif filter_type == 'rfm' and bool(adherent_id) and bool(rfm_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('rubrique_id', '=', rubrique.id),
                            ('date_execution', '!=', None),
                            ('rfm_id', '!=', rfm.id),
                            ('police_id', '=', police_id),
                        ])

                    elif filter_type == 'rfm' and bool(adherent_id) and bool(rfm_id) and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('rfm_id', '=', rfm.id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Règlements Sinistres: \n\
                            Vous n'avez pas renseigné tous les champs concernés pour générer le rapport.\
                            Veuillez vérifier que les informations ont été fournies. Si c'est le cas, \
                            Veuillez contacter les administrateurs pour plus détails..."
                        )
                        )
                    if bool(details_pec):
                        rubrique_id = rubrique.id
                        rubrique_medicale = rubrique.name
                        nbre_actes = len(details_pec) or 0
                        cout_total = sum(item.cout_total for item in details_pec) or 0
                        total_pc = sum(item.total_pc for item in details_pec) or 0
                        total_npc = sum(item.total_npc for item in details_pec) or 0
                        total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int(net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int(net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'rubrique_id': rubrique_id,
                            'rubrique_medicale': rubrique_medicale,
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime(date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime(date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'filter_type': filter_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'prestataire': prestataire.name,
                        'adherent': adherent.name,
                        'code_id': adherent.code_id,
                        'groupe': adherent.groupe_id.name,
                        'ref_facture': facture.name,
                        'ref_interne': facture.ref_interne,
                        'num_facture': facture.num_facture,
                        'date_emission': date_emission,
                        'date_reception': date_reception,
                        'montant_facture': montant_facture,
                        'city': facture.city,
                        'phone': facture.phone,
                        'mobile': facture.mobile,
                        'note': facture.note,
                        'num_rfm': rfm.code_rfm,
                        'date_saisie': date_saisie,
                        'date_depot': date_depot,
                        'montant_rfm': montant_rfm,
                        'ref_fiche': rfm.num_fiche,
                        'code_saisi': rfm.code_saisi,
                        'contrat_id': rfm.contrat_id,
                        'num_contrat': rfm.num_contrat,
                        'matricule': rfm.matricule,
                        'photo': rfm.image,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport - Règlements Sinistres: \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # 1.2. ETAT SYNTHESE PAR RUBRIQUE MEDICALE
            elif report_kpi == 'rubrique' and report_type == 'groupe':
                # Récuperer la liste complète des rubriques médicales
                rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')
                police = self.env['proximas.police'].search([('id', '=', police_id)], order='name asc')
                factures = []
                remboursements = []
                if filter_type == 'pec':
                    factures = self.env['proximas.facture'].search([
                        ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                        ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                    ])
                elif filter_type == 'rfm':
                    remboursements = self.env['proximas.remboursement.pec'].search ([
                        ('date_saisie', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                        ('date_saisie', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                    ])
                for rubrique in rubriques:
                    if filter_type == 'pec' and police_filter:
                        if factures:
                            for facture in factures:
                                # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                                details_pec = self.env['proximas.details.pec'].search ([
                                    ('rubrique_id', '=', rubrique.id),
                                    ('date_execution', '!=', None),
                                    ('facture_id', '!=', facture.id),
                                    ('pec_id', '!=', None),
                                    ('police_id', '=', police_id),
                                ])
                        else:
                            raise UserError (_ (
                                "Proximaas : Rapport - Règlements Sinistres: \n\
                                Aucune facture n'a été enregistrée sur la période indiquée.\
                                Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                                Veuillez contacter les administrateurs pour plus détails..."
                            ))
                    elif filter_type == 'pec' and not police_filter:
                        if factures:
                            for facture in factures:
                                # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                                details_pec = self.env['proximas.details.pec'].search ([
                                    ('rubrique_id', '=', rubrique.id),
                                    ('date_execution', '!=', None),
                                    ('facture_id', '!=', facture.id),
                                    ('pec_id', '!=', None),
                                ])
                        else:
                            raise UserError (_ (
                                "Proximaas : Rapport - Règlements Sinistres: \n\
                                Aucune facture n'a été enregistrée sur la période indiquée.\
                                Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                                Veuillez contacter les administrateurs pour plus détails..."
                            ))
                    elif filter_type == 'rfm' and police_filter:
                        if remboursements:
                            for rfm in remboursements:
                                # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                                details_pec = self.env['proximas.details.pec'].search([
                                    ('rubrique_id', '=', rubrique.id),
                                    ('date_execution', '!=', None),
                                    ('rfm_id', '!=', rfm.id),
                                    ('police_id', '=', police_id),
                                ])
                        else:
                            raise UserError(_(
                                "Proximaas : Rapport - Règlements Sinistres: \n\
                                Aucun Remboursement n'a été enregistrée sur la période indiquée.\
                                Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                                Veuillez contacter les administrateurs pour plus détails..."
                            ))
                    elif filter_type == 'rfm' and not police_filter:
                        if remboursements:
                            for rfm in remboursements:
                                # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                                details_pec = self.env['proximas.details.pec'].search([
                                    ('rubrique_id', '=', rubrique.id),
                                    ('date_execution', '!=', None),
                                    ('rfm_id', '!=', rfm.id),
                                ])
                        else:
                            raise UserError(_(
                                "Proximaas : Rapport - Règlements Sinistres: \n\
                                Aucun Remboursement n'a été enregistrée sur la période indiquée.\
                                Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                                Veuillez contacter les administrateurs pour plus détails..."
                            ))
                    if bool(details_pec):
                        rubrique_id = rubrique.id
                        rubrique_medicale = rubrique.name
                        nbre_actes = len(details_pec) or 0
                        cout_total = sum(item.cout_total for item in details_pec) or 0
                        total_pc = sum(item.total_pc for item in details_pec) or 0
                        total_npc = sum(item.total_npc for item in details_pec) or 0
                        total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int(net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int(net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'rubrique_id': rubrique_id,
                            'rubrique_medicale': rubrique_medicale,
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'filter_type': filter_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport - Règlements Sinistres: \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    )
                    )
            # 2.1. ETAT DETAILLE PAR PRESTATION MEDICALE
            if report_kpi == 'prestation' and report_type == 'detail':
                now = datetime.now().strftime('%d/%m/%Y')
                prestations = self.env['proximas.code.prestation'].search([])
                police = self.env['proximas.police'].search([('id', '=', police_id)], order='name asc')
                facture = self.env['proximas.facture'].search([('id', '=', facture_id)])
                rfm = self.env['proximas.remboursement.pec'].search([('id', '=', rfm_id)])
                adherent = self.env['proximas.adherent'].search([('id', '=', adherent_id)])
                prestataire = self.env['res.partner'].search([
                    ('id', '=', prestataire_id), ('is_prestataire', '=', True)], order='name asc')
                date_emission = datetime.strptime(facture.date_emission, DATE_FORMAT).strftime('%d/%m/%Y') or now
                date_reception = datetime.strptime(facture.date_reception, DATE_FORMAT).strftime('%d/%m/%Y') or now
                montant_facture = facture.montant_en_text()
                date_saisie = datetime.strptime(rfm.date_saisie, DATETIME_FORMAT).strftime('%d/%m/%Y') or now
                date_depot = datetime.strptime(rfm.date_depot, DATE_FORMAT).strftime('%d/%m/%Y') or now
                montant_rfm = rfm.montant_en_text()

                for prestation in prestations:
                    if filter_type == 'pec' and bool(prestataire_id) and bool(facture_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        details_pec = self.env['proximas.details.pec'].search([
                            # ('date_execution', '!=', None),
                            # ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            # ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            # ('facture_id', '!=', None),
                            # ('pec_id', '!=', None),
                            ('facture_id', '=', facture_id),
                            ('prestataire_id', '=', prestataire_id),
                            ('police_id', '=', police_id),
                            ('code_prestation_id', '=', prestation.id),
                        ])
                    elif filter_type == 'pec' and bool (prestataire_id) and bool (
                            facture_id) and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            # ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            # ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            # ('facture_id', '!=', None),
                            # ('pec_id', '!=', None),
                            ('facture_id', '=', facture_id),
                            ('prestataire_id', '=', prestataire_id),
                            ('code_prestation_id', '=', prestation.id),
                        ])
                    elif filter_type == 'rfm' and bool(adherent_id) and bool (rfm_id) and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            # ('date_saisie_rfm', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            # ('date_saisie_rfm', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            # ('rfm_id', '!=', None),
                            # ('pec_id', '=', None),
                            ('rfm_id', '=', rfm_id),
                            ('adherent_id', '=', adherent_id),
                            ('police_id', '=', police_id),
                            ('code_prestation_id', '=', prestation.id),
                        ])
                    elif filter_type == 'rfm' and bool (adherent_id) and bool (rfm_id) and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            # ('date_saisie_rfm', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            # ('date_saisie_rfm', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            # ('rfm_id', '!=', None),
                            # ('pec_id', '=', None),
                            ('rfm_id', '=', rfm_id),
                            ('adherent_id', '=', adherent_id),
                            ('code_prestation_id', '=', prestation.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Rapport - Règlements Sinistres: \n\
                            Vous n'avez pas renseigné tous les champs concernés pour générer le rapport.\
                            Veuillez vérifier que les informations ont été fournies. Si c'est le cas, \
                            Veuillez contacter les administrateurs pour plus détails..."
                        )
                        )
                    if bool(details_pec):
                        prestation_id = prestation.id
                        name_length = len(prestation.name)
                        if int(name_length) > 60:
                            prestation_medicale = prestation.name[:60] + '...'
                        else:
                            prestation_medicale = prestation.name
                        nbre_actes = len(details_pec) or 0
                        cout_total = sum(item.cout_total for item in details_pec) or 0
                        total_pc = sum(item.total_pc for item in details_pec) or 0
                        total_npc = sum(item.total_npc for item in details_pec) or 0
                        total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int (net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int (net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'prestation_id': prestation_id,
                            'prestation_medicale': prestation_medicale,
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime (date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime (date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'filter_type': filter_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'prestataire': prestataire.name,
                        'adherent': adherent.name,
                        'code_id': adherent.code_id,
                        'groupe': adherent.groupe_id.name,
                        'ref_facture': facture.name,
                        'ref_interne': facture.ref_interne,
                        'num_facture': facture.num_facture,
                        'date_emission': date_emission,
                        'date_reception': date_reception,
                        'montant_facture': montant_facture,
                        'city': facture.city,
                        'phone': facture.phone,
                        'mobile': facture.mobile,
                        'note': facture.note,
                        'num_rfm': rfm.code_rfm,
                        'date_saisie': date_saisie,
                        'date_depot': date_depot,
                        'montant_rfm': montant_rfm,
                        'ref_fiche': rfm.num_fiche,
                        'code_saisi': rfm.code_saisi,
                        'contrat_id': rfm.contrat_id,
                        'num_contrat': rfm.num_contrat,
                        'matricule': rfm.matricule,
                        'photo': rfm.image,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport - Règlements Sinistres: \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # 2.2. ETAT SYNTHESE PAR RUBRIQUE MEDICALE
            if report_kpi == 'prestation' and report_type == 'groupe':
                # Récuperer la liste complète des prestations médicales
                prestations = self.env['proximas.code.prestation'].search([])
                police = self.env['proximas.police'].search([('id', '=', police_id)], order='name asc')
                # factures = []
                # remboursements = []
                for prestation in prestations:
                    if filter_type == 'pec':
                        factures = self.env['proximas.facture'].search ([
                            ('date_emission', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            ('date_emission', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                        ])
                        if factures and police_filter:
                            for facture in factures:
                                # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                                details_pec = self.env['proximas.details.pec'].search ([
                                    ('code_prestation_id', '=', prestation.id),
                                    ('facture_id', '!=', facture.id),
                                    ('police_id', '=', police_id),
                                ])
                        elif factures and not police_filter:
                            for facture in factures:
                                # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                                details_pec = self.env['proximas.details.pec'].search ([
                                    ('code_prestation_id', '=', prestation.id),
                                    ('facture_id', '!=', facture.id),
                                ])
                        else:
                            raise UserError (_ (
                                "Proximaas : Rapport - Règlements Sinistres: \n\
                                Aucune facture n'a été enregistrée sur la période indiquée.\
                                Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                                Veuillez contacter les administrateurs pour plus détails..."
                            ))
                    elif filter_type == 'rfm':
                        remboursements = self.env['proximas.remboursement.pec'].search ([
                            ('date_saisie', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_saisie', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                        ])
                        if remboursements and police_filter:
                            for rfm in remboursements:
                                # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                                details_pec = self.env['proximas.details.pec'].search ([
                                    ('code_prestation_id', '=', prestation.id),
                                    ('date_execution', '!=', None),
                                    ('rfm_id', '!=', rfm.id),
                                    ('police_id', '=', police_id),
                                ])

                        elif remboursements and not police_filter:
                            for rfm in remboursements:
                                # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                                details_pec = self.env['proximas.details.pec'].search ([
                                    ('code_prestation_id', '=', prestation.id),
                                    ('date_execution', '!=', None),
                                    ('rfm_id', '!=', rfm.id),
                                ])
                        else:
                            raise UserError (_ (
                                "Proximaas : Rapport - Règlements Sinistres: \n\
                                Aucun Remboursement n'a été enregistrée sur la période indiquée.\
                                Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                                Veuillez contacter les administrateurs pour plus détails..."
                            ))
                    if bool(details_pec):
                        prestation_id = prestation.id
                        name_length = len(prestation.name)
                        if int(name_length) > 60:
                            prestation_medicale = prestation.name[:60] + '...'
                        else:
                            prestation_medicale = prestation.name
                        nbre_actes = len (details_pec) or 0
                        cout_total = sum (item.cout_total for item in details_pec) or 0
                        total_pc = sum (item.total_pc for item in details_pec) or 0
                        total_npc = sum (item.total_npc for item in details_pec) or 0
                        total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                        ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                        net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                        net_prestataire = sum (item.net_prestataire for item in details_pec) or 0
                        net_remboursement = sum (item.mt_remboursement for item in details_pec) or 0
                        net_a_payer = 0
                        if net_prestataire:
                            net_a_payer = int(net_prestataire)
                        elif net_remboursement:
                            net_a_payer = int(net_remboursement)
                        else:
                            net_a_payer = 0

                        docs.append({
                            'prestation_id': prestation_id,
                            'prestation_medicale': prestation_medicale,
                            'nbre_actes': int(nbre_actes),
                            'cout_total': int(cout_total),
                            'total_pc': int(total_pc),
                            'total_npc': int(total_npc),
                            'total_exclusion': int(total_exclusion),
                            'ticket_moderateur': int(ticket_moderateur),
                            'net_tiers_payeur': int(net_tiers_payeur),
                            'net_prestataire': int(net_prestataire),
                            'net_remboursement': int(net_remboursement),
                            'net_a_payer': int(net_a_payer),
                        })
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime(date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime(date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'filter_type': filter_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport - Règlements Sinistres: \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    )
                    )
            # 3.1. ETAT DETAILLE PAR FACTURE/RFM MEDICALE
            if report_kpi == 'facture' and report_type == 'detail':
                prestataire = self.env['res.partner'].search([
                    ('id', '=', prestataire_id), ('is_prestataire', '=', True)], order='name asc')
                police = self.env['proximas.police'].search([('id', '=', police_id)], order='name asc')
                adherent = self.env['proximas.adherent'].search([('id', '=', adherent_id)])
                if filter_type == 'pec' and bool(prestataire):
                    factures = self.env['proximas.facture'].search([
                        ('prestataire_id', '=', prestataire_id),
                        ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                        ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                    ])
                    for facture in factures:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        date_emission = datetime.strptime(facture.date_emission, DATE_FORMAT).strftime('%d/%m/%Y')
                        date_reception = datetime.strptime(facture.date_reception, DATE_FORMAT).strftime('%d/%m/%Y')
                        if police_id:
                            details_pec = self.env['proximas.details.pec'].search([
                                ('facture_id', '=', facture.id),
                                # ('prestataire_id', '=', prestataire_id),
                                ('police_id', '=', police_id),
                            ])
                        elif not police_id:
                            details_pec = self.env['proximas.details.pec'].search([
                                ('facture_id', '=', facture.id),
                                # ('prestataire_id', '=', prestataire_id),
                            ])
                        if bool(details_pec):
                            facture_id = facture.id
                            ref_facture = facture.name
                            num_facture = facture.num_facture
                            nbre_actes = len(details_pec) or 0
                            cout_total = sum(item.cout_total for item in details_pec) or 0
                            total_pc = sum(item.total_pc for item in details_pec) or 0
                            total_npc = sum(item.total_npc for item in details_pec) or 0
                            total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                            ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                            net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                            net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                            net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                            #net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                            net_a_payer = 0
                            if net_prestataire:
                                net_a_payer = int (net_prestataire)
                            elif net_remboursement:
                                net_a_payer = int (net_remboursement)
                            else:
                                net_a_payer = 0

                            docs.append({
                                'facture_id': facture_id,
                                'ref_facture': ref_facture,
                                'num_facture': num_facture,
                                'date_emission': date_emission,
                                'date_reception': date_reception,
                                'nbre_actes': int(nbre_actes),
                                'cout_total': int (cout_total),
                                'total_pc': int (total_pc),
                                'total_npc': int (total_npc),
                                'total_exclusion': int (total_exclusion),
                                'ticket_moderateur': int (ticket_moderateur),
                                'net_tiers_payeur': int (net_tiers_payeur),
                                'net_prestataire': int (net_prestataire),
                                'net_remboursement': int (net_remboursement),
                                'net_a_payer': int (net_a_payer),
                            })
                elif filter_type == 'rfm' and bool(adherent):
                    rfms = self.env['proximas.remboursement.pec'].search([
                        ('adherent_id', '=', adherent.id),
                        ('date_saisie', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_saisie', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                    ])
                    for remboursement in rfms:
                        date_saisie = datetime.strptime(remboursement.date_saisie, DATETIME_FORMAT).strftime('%d/%m/%Y')
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        if police_id:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('rfm_id', '=', remboursement.id),
                                # ('adherent_id', '=', adherent_id),
                                ('police_id', '=', police_id),
                            ])
                        elif not police_id:
                            details_pec = self.env['proximas.details.pec'].search([
                                ('rfm_id', '=', remboursement.id),
                                # ('adherent_id', '=', adherent_id),
                            ])
                        if bool(details_pec):
                            rfm_id = remboursement.id
                            ref_fiche = remboursement.num_fiche
                            num_rfm = remboursement.code_rfm
                            nbre_actes = len(details_pec) or 0
                            cout_total = sum(item.cout_total for item in details_pec) or 0
                            total_pc = sum(item.total_pc for item in details_pec) or 0
                            total_npc = sum(item.total_npc for item in details_pec) or 0
                            total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                            ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                            net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                            net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                            net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                            # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                            net_a_payer = 0
                            if net_prestataire:
                                net_a_payer = int (net_prestataire)
                            elif net_remboursement:
                                net_a_payer = int (net_remboursement)
                            else:
                                net_a_payer = 0

                            docs.append({
                                'rfm_id': rfm_id,
                                'ref_fiche': ref_fiche,
                                'num_rfm': num_rfm,
                                'date_saisie': date_saisie,
                                'nbre_actes': int(nbre_actes),
                                'cout_total': int (cout_total),
                                'total_pc': int (total_pc),
                                'total_npc': int (total_npc),
                                'total_exclusion': int (total_exclusion),
                                'ticket_moderateur': int (ticket_moderateur),
                                'net_tiers_payeur': int (net_tiers_payeur),
                                'net_prestataire': int (net_prestataire),
                                'net_remboursement': int (net_remboursement),
                                'net_a_payer': int (net_a_payer),
                            })
                else:
                    raise UserError(_(
                        "Proximaas : Rapport - Règlements Sinistres: \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime(date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime(date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'filter_type': filter_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'prestataire': prestataire.name,
                        'adherent': adherent.name,
                        'code_id': adherent.code_id,
                        'city': prestataire.city,
                        'phone': prestataire.phone,
                        'mobile': prestataire.mobile,
                        'code_saisi': adherent.code_id,
                        'contrat_id': adherent.contrat_id,
                        'groupe': adherent.groupe_id.name,
                        'num_contrat': adherent.num_contrat,
                        'matricule': adherent.matricule,
                        'photo': adherent.image,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Rapport - Règlements Sinistres: \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # 3.2. ETAT SYNTHESE PAR FACTURE / REMBOURSEMENT
            if report_kpi == 'facture' and report_type == 'groupe':
                police = self.env['proximas.police'].search([
                    ('id', '=', police_id)
                ], order='name asc')
                if filter_type == 'pec':
                    factures = self.env['proximas.facture'].search([
                        ('date_emission', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_emission', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                    ])
                    for facture in factures:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        date_emission = datetime.strptime(facture.date_emission, DATE_FORMAT).strftime('%d/%m/%Y')
                        date_reception = datetime.strptime(facture.date_reception, DATE_FORMAT).strftime('%d/%m/%Y')
                        if police_id:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('facture_id', '=', facture.id),
                                ('police_id', '=', police_id),
                            ])
                        elif not police_id:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('facture_id', '=', facture.id),
                            ])
                        if bool(details_pec):
                            facture_id = facture.id
                            name_length = len(facture.prestataire_id.name)
                            if int(name_length) > 60:
                                facture_prestataire = facture.prestataire_id.name[:60] + '...'
                            else:
                                facture_prestataire = facture.prestataire_id.name
                            ref_facture = facture.name
                            num_facture = facture.num_facture
                            nbre_actes = len(details_pec) or 0
                            cout_total = sum(item.cout_total for item in details_pec) or 0
                            total_pc = sum(item.total_pc for item in details_pec) or 0
                            total_npc = sum(item.total_npc for item in details_pec) or 0
                            total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                            ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                            net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                            net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                            net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                            # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                            net_a_payer = 0
                            if net_prestataire:
                                net_a_payer = int (net_prestataire)
                            elif net_remboursement:
                                net_a_payer = int (net_remboursement)
                            else:
                                net_a_payer = 0

                            docs.append({
                                'facture_id': facture_id,
                                'facture_prestataire': facture_prestataire,
                                'ref_facture': ref_facture,
                                'num_facture': num_facture,
                                'date_emission': date_emission,
                                'date_reception': date_reception,
                                'nbre_actes': int(nbre_actes),
                                'cout_total': int (cout_total),
                                'total_pc': int (total_pc),
                                'total_npc': int (total_npc),
                                'total_exclusion': int(total_exclusion),
                                'ticket_moderateur': int(ticket_moderateur),
                                'net_tiers_payeur': int(net_tiers_payeur),
                                'net_prestataire': int(net_prestataire),
                                'net_remboursement': int(net_remboursement),
                                'net_a_payer': int(net_a_payer),
                            })
                elif filter_type == 'rfm':
                    rfms = self.env['proximas.remboursement.pec'].search([
                        ('date_saisie', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                        ('date_saisie', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                    ])
                    for remboursement in rfms:
                        # fields.Datetime.from_string(remboursement.date_saisie)
                        date_saisie = datetime.strptime(remboursement.date_saisie, DATETIME_FORMAT).strftime('%d/%m/%Y')
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        if police_id:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('rfm_id', '=', remboursement.id),
                                ('police_id', '=', police_id),
                            ])
                        elif not police_id:
                            details_pec = self.env['proximas.details.pec'].search([
                                ('rfm_id', '=', remboursement.id),
                            ])
                        if bool(details_pec):
                            rfm_id = remboursement.id
                            name_length = len(remboursement.adherent_id.name)
                            if int(name_length) > 60:
                                rfm_adherent = remboursement.adherent_id.name[:60]
                            else:
                                rfm_adherent = remboursement.adherent_id.name
                            ref_fiche = remboursement.num_fiche
                            num_rfm = remboursement.code_rfm
                            nbre_actes = len(details_pec) or 0
                            cout_total = sum(item.cout_total for item in details_pec) or 0
                            total_pc = sum(item.total_pc for item in details_pec) or 0
                            total_npc = sum(item.total_npc for item in details_pec) or 0
                            total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                            ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                            net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                            net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                            net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                            # net_a_payer = sum(item.net_a_payer for item in details_pec) or 0
                            net_a_payer = 0
                            if net_prestataire:
                                net_a_payer = int (net_prestataire)
                            elif net_remboursement:
                                net_a_payer = int (net_remboursement)
                            else:
                                net_a_payer = 0

                            docs.append({
                                'rfm_id': rfm_id,
                                'rfm_adherent': rfm_adherent,
                                'ref_fiche': ref_fiche,
                                'num_rfm': num_rfm,
                                'date_saisie': date_saisie,
                                'nbre_actes': int(nbre_actes),
                                'cout_total': int (cout_total),
                                'total_pc': int (total_pc),
                                'total_npc': int (total_npc),
                                'total_exclusion': int (total_exclusion),
                                'ticket_moderateur': int (ticket_moderateur),
                                'net_tiers_payeur': int (net_tiers_payeur),
                                'net_prestataire': int (net_prestataire),
                                'net_remboursement': int (net_remboursement),
                                'net_a_payer': int (net_a_payer),
                            })
                else:
                    raise UserError(_(
                        "Proximaas : Rapport - Règlements Sinistres: \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['net_a_payer'], reverse=True)
                    docargs = {
                        'doc_ids': data['ids'],
                        'doc_model': data['model'],
                        'date_debut': datetime.strftime(date_debut_obj, '%d/%m/%Y'),
                        'date_fin': datetime.strftime(date_fin_obj, '%d/%m/%Y'),
                        'date_diff': date_diff,
                        'report_kpi': report_kpi,
                        'report_type': report_type,
                        'filter_type': filter_type,
                        'police_filter': police_filter,
                        'police_id': police_id,
                        'police': police.name,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Rapport - Règlements Sinistres: \n\
                        Après recherche, aucun sinistre ne correspond à la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            return report_obj.render('proximas_medical.report_reglements_sinistres_view', docargs)
