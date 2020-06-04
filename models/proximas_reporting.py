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
        default=fields.Date.today,
        required=True,
    )
    date_fin = fields.Date(
        string="Date Fin",
        default=fields.Date.today,
        required=True,
    )
    report_kpi = fields.Selection(
        string="Indicateur de sinistralité",
        selection=[
            ('police', 'Police Couverture(Produit)'),
            ('contrat', 'Famille (Contrat)'),
            ('assure', 'Assuré (Bénéficiare)'),
            ('prestataire', 'Prestataire Soins médicaux'),
            ('medecin', 'Médecin Traitant'),
            ('rubrique', 'Rubrique Médicale'),
            ('prestation', 'Prestation Médicale'),
            ('groupe', 'Regroupement (Groupe)'),
            ('localite', 'Localité'),
            ('zone', 'Zone adminsitrative'),
        ],
        default='police',
        required=True,
    )
    report_type = fields.Selection(
        string="Type de rapport",
        selection=[
            ('groupe', 'Regroupement (Récap.)'),
            ('detail', 'Détaillé (Sinistres)'),
        ],
        default='groupe',
        required=True,
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
    medecin_id = fields.Many2one(
        comodel_name="proximas.medecin",
        string="Médecin Traitant",
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
    police_id = fields.Many2one(
        comodel_name="proximas.police",
        string="Police Couverture",
        required=False,
    )
    prestataire_id = fields.Many2one (
        comodel_name="res.partner",
        string="Prestataire de soins",
        domain=[('is_prestataire', '=', True)],
        required=False,
    )
    groupe_id = fields.Many2one(
        comodel_name="proximas.groupe",
        string="Groupe",
        required=False,
    )
    zone_id = fields.Many2one(
        comodel_name="proximas.zone",
        string="Zone Géographique",
        required=False,
    )
    localite_id = fields.Many2one(
        comodel_name="proximas.localite",
        string="Localité",
        required=False,
    )

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
                'police_id': self.police_id.id,
                'rubrique_id': self.rubrique_id.id,
                'contrat_id': self.contrat_id.id,
                'prestataire_id': self.prestataire_id.id,
                'prestation_id': self.prestation_id.id,
                'assure_id': self.assure_id.id,
                'medecin_id': self.medecin_id.id,
                'groupe_id': self.groupe_id.id,
                'localite_id': self.localite_id.id,
                'zone_id': self.zone_id.id,
            },
        }

        return self.env['report'].get_action(self, 'proximas_medical.report_suivi_sinistres_view', data=data)
        # use module_name.report_id as reference
        # report_action() will call get_report_values() and pass data automatically
        # return self.env.ref('proximas_medical.sinistre_recap_report_view').report_action(self, data=data)
        # return {
        #     'type':'ir.actions.report',
        #     'report_name': 'proximas_medical.sinistre_recap_report',
        #     'report_type': "qweb-pdf",
        #     'data': data,
        # }





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
        date_debut_obj = datetime.strptime(date_debut, DATE_FORMAT)
        date_fin_obj = datetime.strptime(date_fin, DATE_FORMAT)
        date_diff = (date_fin_obj - date_debut_obj).days + 1
        contrat_id = data['form']['contrat_id']
        police_id = data['form']['police_id']
        rubrique_id = data['form']['rubrique_id']
        assure_id = data['form']['assure_id']
        prestataire_id = data['form']['prestataire_id']
        prestation_id = data['form']['prestation_id']
        medecin_id = data['form']['medecin_id']
        groupe_id = data['form']['groupe_id']
        localite_id = data['form']['localite_id']
        zone_id = data['form']['zone_id']

        docs = []
        docargs = {}

        # 1.1. Rapport Détaillé par Rubrique
        if report_kpi == 'rubrique' and report_type == 'detail':
            # Récupérer les sinistres de la rubrique sélectionnée
            details_pec = self.env['proximas.details.pec'].search([
                ('rubrique_id', '=', rubrique_id),
                ('date_execution', '!=', None),
                ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
            ])
            rubrique = self.env['proximas.rubrique.medicale'].search([
                ('id', '=', rubrique_id),
            ])
            if bool(details_pec):
                for detail in details_pec:
                    docs.append(detail)

                docs = sorted(docs, key=lambda x: x['date_execution'], reverse=True)
                docargs = {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
                    'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),  # date_fin_obj.strftime(DATETIME_FORMAT),
                    'date_diff': date_diff,
                    'rubrique_medicale': rubrique.name,
                    'report_kpi': report_kpi,
                    'report_type': report_type,
                    'docs': docs,
                }
            else:
                raise UserError(_(
                "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
                Aucun sinistre n'a été enregistré sur la période indiquée pour la Rubrique médicale : %s.  \
                Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                Veuillez contacter les administrateurs pour plus détails..."
                    ) % rubrique.name
                )
        # 1.2. Rapport de synthèse par Rubrique
        elif report_kpi == 'rubrique' and report_type == 'groupe':

            # Récuperer la liste complète des rubriques médicales
            rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')

            for rubrique in rubriques:
                details_pec = self.env['proximas.details.pec'].search([
                    ('rubrique_id', '=', rubrique.id),
                    ('date_execution', '!=', None),
                    ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                    ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                ], order='date_execution desc')

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
                    })
            if bool(docs):
                docs = sorted(docs, key=lambda x: x['net_tiers_payeur'], reverse=True)
                docargs = {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
                    'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),  # date_fin_obj.strftime(DATETIME_FORMAT),
                    'date_diff': date_diff,
                    'report_kpi': report_kpi,
                    'report_type': report_type,
                    'docs': docs,
                }
            else:
                raise UserError(_(
                    "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
                    Aucun sinistre n'a été enregistré sur la période indiquée.\
                    Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                    Veuillez contacter les administrateurs pour plus détails..."
                    )
                )
        # 2.1. Rapport Détaillé par Contrat
        if report_kpi == 'contrat' and report_type == 'detail':
            # Récupérer les sinistres du contrat concerné
            details_pec = self.env['proximas.details.pec'].search([
                ('contrat_id', '=', contrat_id),
                ('date_execution', '!=', None),
                ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
            ])
            contrat = self.env['proximas.contrat'].search([
                ('id', '=', contrat_id),
            ])
            if bool(details_pec):
                for detail in details_pec:
                    docs.append(detail)

                docs = sorted(docs, key=lambda x: x['date_execution'], reverse=True)
                docargs = {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
                    'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),
                    'date_diff': date_diff,
                    'contrat_adherent': '%s - %s' % (contrat.num_contrat, contrat.adherent_id.name),
                    'police_id': contrat.police_id.libelle,
                    'report_kpi': report_kpi,
                    'report_type': report_type,
                    'docs': docs,
                }
            else:
                raise UserError(_(
                    "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
                    Aucun sinistre n'a été enregistré sur la période indiquée pour le contrat : %s.  \
                    Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                    Veuillez contacter les administrateurs pour plus détails..."
                    ) % contrat.adherent_id.name
                )
        # 2.2. Rapport de synthèse par Contrat Adhérent
        elif report_kpi == 'contrat' and report_type == 'groupe':

            # Récuperer la liste complète des sinistres par contrat adhérent
            contrats = self.env['proximas.contrat'].search([], order='name asc')

            for contrat in contrats:
                details_pec = self.env['proximas.details.pec'].search([
                    ('contrat_id', '=', contrat.id),
                    ('date_execution', '!=', None),
                    ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                    ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                ], order='date_execution desc')

                if bool(details_pec):
                    contrat_id = contrat.id
                    contrat_adherent = contrat.adherent_id.name
                    nbre_actes = len(details_pec) or 0
                    cout_total = sum(item.cout_total for item in details_pec) or 0
                    total_pc = sum(item.total_pc for item in details_pec) or 0
                    total_npc = sum(item.total_npc for item in details_pec) or 0
                    total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0

                    docs.append({
                        'contrat_id': contrat_id,
                        'contrat_adherent': contrat_adherent,
                        'nbre_actes': int(nbre_actes),
                        'cout_total': int(cout_total),
                        'total_pc': int(total_pc),
                        'total_npc': int(total_npc),
                        'total_exclusion': int(total_exclusion),
                        'ticket_moderateur': int(ticket_moderateur),
                        'net_tiers_payeur': int(net_tiers_payeur),
                    })
            if bool(docs):
                docs = sorted(docs, key=lambda x: x['net_tiers_payeur'], reverse=True)
                # docs = docs[:200]
                docargs = {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
                    'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),  # date_fin_obj.strftime(DATETIME_FORMAT),
                    'date_diff': date_diff,
                    'report_kpi': report_kpi,
                    'report_type': report_type,
                    'docs': docs,
                }
            else:
                raise UserError(_(
                    "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
                    Aucun sinistre n'a été enregistré sur la période indiquée. \
                    Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                    Veuillez contacter les administrateurs pour plus détails..."
                    )
                )
        # 3.1. Rapport Détaillé par Assuré
        if report_kpi == 'assure' and report_type == 'detail':
            # Récupérer les sinistres de l'assuré concerné
            details_pec = self.env['proximas.details.pec'].search([
                ('assure_id', '=', assure_id),
                ('date_execution', '!=', None),
                ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
            ])
            assure = self.env['proximas.assure'].search([
                ('id', '=', assure_id),
            ])
            if bool(details_pec):
                for detail in details_pec:
                    docs.append(detail)

                docs = sorted(docs, key=lambda x: x['date_execution'], reverse=True)
                docargs = {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
                    'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),
                    'date_diff': date_diff,
                    'assure': '%s - %s' % (assure.code_id, assure.name),
                    'police_id': assure.police_id.libelle,
                    'report_kpi': report_kpi,
                    'report_type': report_type,
                    'docs': docs,
                }
            else:
                raise UserError(_(
                    "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
                    Aucun sinistre n'a été enregistré sur la période indiquée pour le compte de l'assuré : %s.  \
                    Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                    Veuillez contacter les administrateurs pour plus détails..."
                    ) % assure.name
                )
        # 3.2. Rapport de synthèse par Assuré
        elif report_kpi == 'assure' and report_type == 'groupe':

            # Récuperer la liste complète des sinistres assuré
            assures = self.env['proximas.assure'].search([], order='name asc')

            for assure in assures:
                details_pec = self.env['proximas.details.pec'].search([
                    ('assure_id', '=', assure.id),
                    ('date_execution', '!=', None),
                    ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                    ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                ], order='date_execution desc')

                if bool(details_pec):
                    assure_id = assure.id
                    code_id = assure.code_id
                    assure_beneficiaire = assure.name
                    statut_familial = assure.statut_familial
                    nbre_actes = len (details_pec) or 0
                    cout_total = sum (item.cout_total for item in details_pec) or 0
                    total_pc = sum (item.total_pc for item in details_pec) or 0
                    total_npc = sum (item.total_npc for item in details_pec) or 0
                    total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
                    ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
                    net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0

                    docs.append({
                        'assure_id': assure_id,
                        'assure_beneficiaire': assure_beneficiaire,
                        'code_id': code_id,
                        'statut_familial': statut_familial,
                        'adherent': assure.contrat_id.adherent_id.name,
                        'nbre_actes': int(nbre_actes),
                        'cout_total': int(cout_total),
                        'total_pc': int(total_pc),
                        'total_npc': int(total_npc),
                        'total_exclusion': int(total_exclusion),
                        'ticket_moderateur': int(ticket_moderateur),
                        'net_tiers_payeur': int(net_tiers_payeur),
                    })
            if bool(docs):
                docs = sorted(docs, key=lambda x: x['net_tiers_payeur'], reverse=True)
                # docs = docs[:200]
                docargs = {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
                    'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),
                    'date_diff': date_diff,
                    'report_kpi': report_kpi,
                    'report_type': report_type,
                    'docs': docs,
                }
            else:
                raise UserError(_(
                    "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
                    Aucun sinistre n'a été enregistré sur la période indiquée. \
                    Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                    Veuillez contacter les administrateurs pour plus détails..."
                    )
                )

        return report_obj.render('proximas_medical.report_suivi_sinistres_view', docargs)

    class ReglementSinistresReportWizard (models.TransientModel):
        _name = 'proximas.reglement.sinistres.report.wizard'
        _description = 'Reglements Sinistres Report Wizard'

        date_debut = fields.Date(
            string="Date Début",
            default=fields.Date.today,
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
                ('groupe', 'Synthèse (Regroupement)'),
                ('detail', 'Détails'),
            ],
            default='groupe',
            required=True,
        )
        filter_type = fields.Selection(
            string="Type de Filtre",
            selection=[
                ('pec', 'Prises en Charge / Prestataire'),
                ('rfm', 'Reboursements Adhérent'),
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
                now = datetime.now()
                rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')
                police = self.env['proximas.police'].search([('id', '=', police_id)], order='name asc')
                facture = self.env['proximas.facture'].search([('id', '=', facture_id)])
                rfm = self.env['proximas.remboursement.pec'].search([('id', '=', rfm_id)])
                adherent = self.env['proximas.adherent'].search([('id', '=', adherent_id)])
                prestataire = self.env['res.partner'].search([
                    ('id', '=', prestataire_id), ('is_prestataire', '=', True)], order='name asc')
                date_emission = fields.Datetime.from_string(facture.date_emission) or now
                date_reception = fields.Datetime.from_string(facture.date_reception)or now
                montant_facture = facture.montant_en_text() or ''
                date_saisie = fields.Datetime.from_string(rfm.date_saisie) or now
                date_depot = fields.Datetime.from_string(rfm.date_depot) or now
                montant_rfm = rfm.net_remb_texte or ''

                for rubrique in rubriques:
                    if filter_type == 'pec' and bool(prestataire_id) and bool(facture_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            # ('date_emission', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            # ('date_emission', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('facture_id', '=', facture_id),
                            # ('prestataire_id', '=', prestataire.id),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif filter_type == 'pec' and bool(prestataire_id) and bool(facture_id) and not police_filter :
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            # ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            # ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('facture_id', '=', facture_id),
                            # ('prestataire_id', '=', prestataire.id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif filter_type == 'rfm' and bool(adherent_id) and bool(rfm_id) and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            # ('date_saisie_rfm', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                            # ('date_saisie_rfm', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                            ('rfm_id', '!=', None),
                            ('pec_id', '=', None),
                            ('rfm_id', '=', rfm_id),
                            ('adherent_id', '=', adherent_id),
                            ('police_id', '=', police_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    elif filter_type == 'rfm' and bool(adherent_id) and bool(rfm_id) and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            # ('date_saisie_rfm', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            # ('date_saisie_rfm', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('rfm_id', '!=', None),
                            ('pec_id', '=', None),
                            ('rfm_id', '=', rfm_id),
                            ('adherent_id', '=', adherent_id),
                            ('rubrique_id', '=', rubrique.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
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
                    docs = sorted(docs, key=lambda x: x['cout_total'], reverse=True)
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
                        'ref_facture': facture.name,
                        'ref_interne': facture.ref_interne,
                        'num_facture': facture.num_facture,
                        'date_emission': datetime.strftime(date_emission, '%d/%m/%Y'),
                        'date_reception': datetime.strftime(date_reception, '%d/%m/%Y'),
                        'montant_facture': montant_facture,
                        'city': facture.city,
                        'phone': facture.phone,
                        'mobile': facture.mobile,
                        'note': facture.note,
                        'ref_rfm': rfm.code_rfm,
                        'date_saisie': datetime.strftime(date_saisie, '%d/%m/%Y'),
                        'date_depot': datetime.strftime(date_depot, '%d/%m/%Y'),
                        'montant_rfm': rfm.net_remb_texte,
                        'num_fiche': rfm.num_fiche,
                        'code_saisi': rfm.code_saisi,
                        'contrat_id': rfm.contrat_id,
                        'num_contrat': rfm.num_contrat,
                        'matricule': rfm.matricule,
                        'photo': rfm.image,
                        'docs': docs,
                    }
                else:
                    raise UserError(_(
                        "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
                        Aucun sinistre n'a été enregistré sur la période indiquée.\
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
                    factures = self.env['proximas.facture'].search ([
                        ('date_emission', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_emission', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                    ])
                elif filter_type == 'rfm':
                    remboursements = self.env['proximas.remboursement.pec'].search ([
                        ('date_saisie_rfm', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                        ('date_saisie_rfm', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
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
                                "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
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
                                "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
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
                                "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
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
                                "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
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
                    docs = sorted(docs, key=lambda x: x['cout_total'], reverse=True)
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
                        "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
                        Aucun sinistre n'a été enregistré sur la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    )
                    )
            # 2.1. ETAT DETAILLE PAR PRESTATION MEDICALE
            if report_kpi == 'prestation' and report_type == 'detail':
                prestations = self.env['proximas.code.prestation'].search([])
                police = self.env['proximas.police'].search([('id', '=', police_id)], order='name asc')
                facture = self.env['proximas.facture'].search([('id', '=', facture_id)])
                rfm = self.env['proximas.remboursement.pec'].search([('id', '=', rfm_id)])
                adherent = self.env['proximas.adherent'].search([('id', '=', adherent_id)])
                prestataire = self.env['res.partner'].search([
                    ('id', '=', prestataire_id), ('is_prestataire', '=', True)], order='name asc')
                date_emission = fields.Datetime.from_string(facture.date_emission)
                date_reception = fields.Datetime.from_string(facture.date_reception)
                montant_facture = facture.montant_en_text()
                date_saisie = fields.Datetime.from_string(rfm.date_saisie)
                date_depot = fields.Datetime.from_string(rfm.date_depot)
                montant_facture_rfm = rfm.montant_en_text()

                for prestation in prestations:
                    if filter_type == 'pec' and bool(prestataire_id) and bool(facture_id) and police_filter:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('date_execution', '!=', None),
                            ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('facture_id', '!=', None),
                            ('pec_id', '!=', None),
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
                            ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('facture_id', '!=', None),
                            ('pec_id', '!=', None),
                            ('facture_id', '=', facture_id),
                            ('prestataire_id', '=', prestataire_id),
                            ('code_prestation_id', '=', prestation.id),
                        ])
                    elif filter_type == 'rfm' and bool(adherent_id) and bool (rfm_id) and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_saisie_rfm', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_saisie_rfm', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('rfm_id', '!=', None),
                            ('pec_id', '=', None),
                            ('rfm_id', '=', rfm_id),
                            ('adherent_id', '=', adherent_id),
                            ('police_id', '=', police_id),
                            ('code_prestation_id', '=', prestation.id),
                        ])
                    elif filter_type == 'rfm' and bool (adherent_id) and bool (rfm_id) and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('date_execution', '!=', None),
                            ('date_saisie_rfm', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_saisie_rfm', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('rfm_id', '!=', None),
                            ('pec_id', '=', None),
                            ('rfm_id', '=', rfm_id),
                            ('adherent_id', '=', adherent_id),
                            ('code_prestation_id', '=', prestation.id),
                        ])
                    else:
                        raise UserError (_ (
                            "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
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
                        net_a_payer = sum(item.net_a_payer for item in details_pec) or 0

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
                    docs = sorted(docs, key=lambda x: x['cout_total'], reverse=True)
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
                        'ref_facture': facture.name,
                        'ref_interne': facture.ref_interne,
                        'num_facture': facture.num_facture,
                        'date_emission': datetime.strftime (date_emission, '%d/%m/%Y'),
                        'date_reception': datetime.strftime (date_reception, '%d/%m/%Y'),
                        'montant_facture': montant_facture,
                        'city': facture.city,
                        'phone': facture.phone,
                        'mobile': facture.mobile,
                        'note': facture.note,
                        'ref_rfm': rfm.code_rfm,
                        'date_saisie': datetime.strftime(date_saisie, '%d/%m/%Y'),
                        'date_depot': datetime.strftime(date_depot, '%d/%m/%Y'),
                        'montant_rfm': rfm.montant_rfm,
                        'num_fiche': rfm.num_fiche,
                        'code_saisi': rfm.code_saisi,
                        'contrat_id': rfm.contrat_id,
                        'num_contrat': rfm.num_contrat,
                        'matricule': rfm.matricule,
                        'photo': rfm.image,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
                        Aucun sinistre n'a été enregistré sur la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            # 2.2. ETAT SYNTHESE PAR RUBRIQUE MEDICALE
            if report_kpi == 'prestation' and report_type == 'groupe':
                # Récuperer la liste complète des prestations médicales
                prestations = self.env['proximas.code.prestation'].search([])
                police = self.env['proximas.police'].search([('id', '=', police_id)], order='name asc')

                for prestation in prestations:
                    if filter_type == 'pec' and police_filter:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('code_prestation_id', '=', prestation.id),
                            ('date_execution', '!=', None),
                            ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('facture_id', '!=', None),
                            ('pec_id', '!=', None),
                            ('police_id', '=', police_id),
                        ])
                    elif filter_type == 'pec' and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        details_pec = self.env['proximas.details.pec'].search([
                            ('code_prestation_id', '=', prestation.id),
                            ('date_execution', '!=', None),
                            ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('facture_id', '!=', None),
                            ('pec_id', '!=', None),
                        ])
                    elif filter_type == 'rfm' and police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search([
                            ('code_prestation_id', '=', prestation.id),
                            ('date_execution', '!=', None),
                            ('date_saisie_rfm', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_saisie_rfm', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('rfm_id', '!=', None),
                            ('police_id', '=', police_id),
                        ])
                    elif filter_type == 'rfm' and not police_filter:
                        # DETAILS PEC TRAITES ET LIES A UN REMBOURSEMENT ADHERENT
                        details_pec = self.env['proximas.details.pec'].search ([
                            ('code_prestation_id', '=', prestation.id),
                            ('date_execution', '!=', None),
                            ('date_saisie_rfm', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                            ('date_saisie_rfm', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                            ('rfm_id', '!=', None),
                        ])
                    if bool (details_pec):
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
                        net_a_payer = sum (item.net_a_payer for item in details_pec) or 0

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
                    docs = sorted(docs, key=lambda x: x['cout_total'], reverse=True)
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
                        "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
                        Aucun sinistre n'a été enregistré sur la période indiquée.\
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
                    factures = self.env['proximas.facture'].search([('prestataire_id', '=', prestataire_id)])
                    for facture in factures:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        date_emission = facture.date_emission
                        date_reception = facture.date_reception
                        if police_id:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('date_execution', '!=', None),
                                ('date_emission', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                                ('date_emission', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                                ('facture_id', '!=', None),
                                ('pec_id', '!=', None),
                                ('facture_id', '=', facture.id),
                                ('prestataire_id', '=', prestataire_id),
                                ('police_id', '=', police_id),
                            ])
                        else:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('date_execution', '!=', None),
                                ('date_emission', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                                ('date_emission', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                                ('facture_id', '!=', None),
                                ('pec_id', '!=', None),
                                ('facture_id', '=', facture.id),
                                ('prestataire_id', '=', prestataire_id),
                            ])
                        if bool(details_pec):
                            facture_id = facture.id
                            num_facture = facture.num_facture
                            date_emission = date_emission
                            date_reception = date_reception
                            nbre_actes = len(details_pec) or 0
                            cout_total = sum(item.cout_total for item in details_pec) or 0
                            total_pc = sum(item.total_pc for item in details_pec) or 0
                            total_npc = sum(item.total_npc for item in details_pec) or 0
                            total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                            ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                            net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                            net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                            net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                            net_a_payer = sum(item.net_a_payer for item in details_pec) or 0

                            docs.append({
                                'facture_id': facture_id,
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
                    rfms = self.env['proximas.remboursement.pec'].search(['adherent_id', '=', adherent.id])
                    for remboursement in rfms:
                        date_saisie = remboursement.date_saisie
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        if police_id:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('date_execution', '!=', None),
                                ('date_saisie_rfm', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                                ('date_saisie_rfm', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                                ('rfm_id', '!=', None),
                                ('pec_id', '=', None),
                                ('rfm_id', '=', remboursement.id),
                                ('adherent_id', '=', adherent_id),
                                ('police_id', '=', police_id),
                            ])
                        else:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('date_execution', '!=', None),
                                ('date_saisie_rfm', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                                ('date_saisie_rfm', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                                ('rfm_id', '!=', None),
                                ('pec_id', '=', None),
                                ('rfm_id', '=', remboursement.id),
                                ('adherent_id', '=', adherent_id),
                            ])
                        if bool(details_pec):
                            rfm_id = remboursement.id
                            num_rfm = remboursement.num_rfm
                            date_saisie = date_saisie
                            nbre_actes = len(details_pec) or 0
                            cout_total = sum(item.cout_total for item in details_pec) or 0
                            total_pc = sum(item.total_pc for item in details_pec) or 0
                            total_npc = sum(item.total_npc for item in details_pec) or 0
                            total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                            ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                            net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                            net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                            net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                            net_a_payer = sum(item.net_a_payer for item in details_pec) or 0

                            docs.append({
                                'rfm_id': rfm_id,
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
                        "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
                        Aucun sinistre n'a été enregistré sur la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['cout_total'], reverse=True)
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
                        'num_contrat': adherent.num_contrat,
                        'matricule': adherent.matricule,
                        'photo': adherent.image,
                        'docs': docs,
                    }
                else:
                    raise UserError (_ (
                        "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
                        Aucun sinistre n'a été enregistré sur la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))

            # 3.2. ETAT SYNTHESE PAR FACTURE / REMBOURSEMENT
            if report_kpi == 'facture' and report_type == 'groupe':
                police = self.env['proximas.police'].search([('id', '=', police_id)], order='name asc')
                if filter_type == 'pec':
                    factures = self.env['proximas.facture'].search([])
                    for facture in factures:
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        date_emission = facture.date_emission
                        date_reception = facture.date_reception
                        if police_id:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('date_execution', '!=', None),
                                ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                                ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                                ('facture_id', '!=', None),
                                ('pec_id', '!=', None),
                                ('facture_id', '=', facture.id),
                                ('police_id', '=', police_id),
                            ])
                        else:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('date_execution', '!=', None),
                                ('date_emission', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
                                ('date_emission', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
                                ('facture_id', '!=', None),
                                ('pec_id', '!=', None),
                                ('facture_id', '=', facture.id),
                            ])
                        if bool(details_pec):
                            facture_id = facture.id
                            name_length = len(facture.prestataire_id.name)
                            if int(name_length) > 60:
                                facture_prestataire = facture.prestataire_id.name[:60] + '...'
                            else:
                                facture_prestataire = facture.prestataire_id.name
                            num_facture = facture.num_facture
                            date_emission = date_emission
                            date_reception = date_reception
                            nbre_actes = len(details_pec) or 0
                            cout_total = sum(item.cout_total for item in details_pec) or 0
                            total_pc = sum(item.total_pc for item in details_pec) or 0
                            total_npc = sum(item.total_npc for item in details_pec) or 0
                            total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                            ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                            net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
                            net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                            net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                            net_a_payer = sum(item.net_a_payer for item in details_pec) or 0

                            docs.append({
                                'facture_id': facture_id,
                                'facture_prestataire': facture_prestataire,
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
                    rfms = self.env['proximas.remboursement.pec'].search(['adherent_id', '=', adherent.id])
                    for remboursement in rfms:
                        # fields.Datetime.from_string(remboursement.date_saisie)
                        date_saisie = remboursement.date_saisie
                        # DETAILS PEC TRAITES ET LIES A UNE FACTURE PRESTATAIRE
                        if police_id:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('date_execution', '!=', None),
                                ('date_saisie_rfm', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                                ('date_saisie_rfm', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                                ('rfm_id', '!=', None),
                                ('pec_id', '=', None),
                                ('rfm_id', '=', remboursement.id),
                                ('adherent_id', '=', adherent_id),
                                ('police_id', '=', police_id),
                            ])
                        else:
                            details_pec = self.env['proximas.details.pec'].search ([
                                ('date_execution', '!=', None),
                                ('date_saisie_rfm', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
                                ('date_saisie_rfm', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
                                ('rfm_id', '!=', None),
                                ('pec_id', '=', None),
                                ('rfm_id', '=', remboursement.id),
                                ('adherent_id', '=', adherent_id),
                            ])
                        if bool(details_pec):
                            rfm_id = remboursement.id
                            name_length = len(remboursement.adherent_id.name)
                            if int(name_length) > 60:
                                rfm_adherent = remboursement.adherent_id.name[:60]
                            else:
                                rfm_adherent = remboursement.adherent_id.name
                            num_rfm = remboursement.num_rfm
                            date_saisie = date_saisie
                            nbre_actes = len(details_pec) or 0
                            cout_total = sum(item.cout_total for item in details_pec) or 0
                            total_pc = sum(item.total_pc for item in details_pec) or 0
                            total_npc = sum(item.total_npc for item in details_pec) or 0
                            total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
                            ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
                            net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
                            net_prestataire = sum(item.net_prestataire for item in details_pec) or 0
                            net_remboursement = sum(item.mt_remboursement for item in details_pec) or 0
                            net_a_payer = sum(item.net_a_payer for item in details_pec) or 0

                            docs.append({
                                'rfm_id': rfm_id,
                                'rfm_adherent': rfm_adherent,
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
                        "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
                        Aucun sinistre n'a été enregistré sur la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
                if bool(docs):
                    docs = sorted(docs, key=lambda x: x['cout_total'], reverse=True)
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
                        "Proximaas : Edition Rapport de Sinistralité - Actes Confirmés: \n\
                        Aucun sinistre n'a été enregistré sur la période indiquée.\
                        Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
                        Veuillez contacter les administrateurs pour plus détails..."
                    ))
            return report_obj.render('proximas_medical.report_reglements_sinistres_view', docargs)
