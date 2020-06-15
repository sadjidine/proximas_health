# -*- coding:utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE - Sadjidine
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp.tools.translate import _
from openerp import api, fields, models
from openerp.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from random import randint
from openerp.tools import amount_to_text_fr


class PriseEnCharge(models.Model):
    _name = 'proximas.prise.charge'
    _description = 'Prise en charge'
    _order = 'date_saisie desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    # name = fields.Char()
    sequence = fields.Integer(
        string="Sequence",
    )
    num_bon = fields.Char(
        string="Num. Bon",
        help="Indiquer le N° du bon physique(Pré-imprimé)",
    )
    code_pec = fields.Char(
        string="Code PEC",
        compute='_get_code_pec',
        store=True,
        help='Code généré automatiquement par la système'
    )
    code_pc = fields.Char (
        string="Code PC",
        compute='_get_code_pc',
        help="Code PC généré par la système.",
    )
    date_saisie = fields.Datetime(
        string="Date Enregistrement",
        default=fields.Datetime.now,
        readonly=False,
    )
    adherent_id = fields.Many2one(
        comodel_name="proximas.adherent",
        string="Adhérent (Remboursement)",
    )
    state = fields.Selection(
        string="Etat",
        selection=[
                ('cours', 'En cours'),
                ('oriente', 'Orientation'),
                ('dispense', 'Dispensation'),
                ('termine', 'Terminée'),
                ('expire', 'Expirée'),
                ],
        default="cours",
    )
    code_saisi = fields.Char(
        string="Code ID.",
    )
    pathologie_id = fields.Many2one (
        comodel_name="proximas.pathologie",
        string="Code Affection (Principale)",
        required=True,
        help='Veuillez Indiquer le code de l\'affection( pathologie) principale.',
    )
    pathologie_ids = fields.Many2many (
        comodel_name="proximas.pathologie",
        string="Affections Associées",
        help='Veuillez Indiquer les affections associées à la pathologie principale.',
        required=False,
    )
    details_pec_soins_ids = fields.One2many(
        comodel_name="proximas.details.pec",
        inverse_name="pec_id",
        domain=[
            ('prestation_id', '!=', None),
            ('prestataire_id', '!=', False),
            ('prestation_crs_id', '=', None),
            ('prestation_demande_id', '=', None),
            ('produit_phcie_id', '=', None)
        ],
        # ondelete='cascade',
        string='Exécution Prestation Médicale',
        track_visibility='always',
    )
    details_pec_demande_crs_ids = fields.One2many(
        comodel_name="proximas.details.pec",
        inverse_name="pec_id",
        domain=[
            ('prestation_demande_id', '!=', None),
            # ('arret_prestation', '=', False),
        ],
        # ondelete='cascade',
        string='Demande/Exécution Prestation Médicale',
        track_visibility='always',
    )
    details_pec_soins_crs_ids = fields.One2many(
        comodel_name="proximas.details.pec",
        inverse_name="pec_id",
        domain=[
            ('prestation_demande_id', '!=', None),
        ],
        # domain=['|',
        #         ('prestation_demande_id', '!=', None),
        #         ('prestation_crs_id', '!=', None),
        # ],
        # ondelete='restrict',
        track_visibility='always',
        string='Prestation Médicale',
    )
    # details_pec_soins_crs_ids = fields.One2many (
    #     comodel_name="proximas.details.pec",
    #     inverse_name="pec_id",
    #     domain=['|',
    #             ('prestation_demande_id', '!=', None),
    #             ('prestation_crs_id', '!=', None),
    #     ],
    #     # ondelete='restrict',
    #     string='Exécution Prestation Médicale',
    # )
    details_pec_phcie_ids = fields.One2many(
        comodel_name="proximas.details.pec",
        inverse_name="pec_id",
        domain=[
            ('produit_phcie_id', '!=', None),
            # ('arret_produit', '=', False),

        ],
        # ondelete='restrict',
        string='Prescription/Dispensation Médicament',
        track_visibility='always',
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    # Champs relatifs Identifiants Assuré
    code_id = fields.Char(
        string="Code ID.",
        related="assure_id.code_id",
        store=True,
        readonly=True,
    )
    code_id_externe = fields.Char (
        string="Code ID. Externe",
        related="assure_id.code_id_externe",
        store=True,
        readonly=True,
    )
    assure_id = fields.Many2one(
        comodel_name="proximas.assure",
        string="Assuré",
    )
    nom = fields.Char(
        string="Nom",
        related="assure_id.nom",
        readonly=True,
    )
    prenoms = fields.Char(
        string="Prénom(s)",
        related="assure_id.prenoms",
        readonly=True,
    )
    name = fields.Char(
        string="Noms et Prénoms",
        related="assure_id.display_name",
        readonly=True,
    )
    statut_familial = fields.Selection(
        string="Statut Familial",
        related='assure_id.statut_familial',
        readonly=True,
    )
    genre = fields.Selection(
        string="Genre",
        related='assure_id.genre',
        readonly=True,
    )
    date_naissance = fields.Date(
        string="Date Naissance",
        related="assure_id.date_naissance",
        readonly=True,
    )
    date_activation = fields.Date(
        string="Date Activation",
        related="assure_id.date_activation",
        readonly=True,
    )
    age = fields.Char(
        string="Age",
        related="assure_id.age",
        readonly=True,
    )
    age_details = fields.Char(
        string="Age",
        related="assure_id.age_details",
        readonly=True,
    )
    image = fields.Binary(
        string="Photo",
        related="assure_id.image",
        readonly=True,
    )
    prestataire_id = fields.Many2one(
        comodel_name='res.partner',
        string="Prestataire CRO",
        domain=[('is_prestataire', '=', True)],
        # default='_get_partner',
    )
    prestataire_crs_id = fields.Many2one(
        comodel_name="res.partner",
        string="Prestataire CRS",
        domain=[('is_prestataire', '=', True)],
        required=False,
    )
    prestataire_phcie_id = fields.Many2one(
        comodel_name="res.partner",
        string="Pharmacie/Officine",
        domain=[('is_prestataire', '=', True)],
        required=False,
    )
    # prestataire_cro_id = fields.Many2one(
    #     comodel_name='res.partner',
    #     string="Prestataire CRO",
    #     compute='_get_prestataire_cro',
    # )
    pool_medical_id = fields.Many2one(
        comodel_name="proximas.pool.medical",
        string="Médecin",
        required=False,
    )
    prestataire_cro = fields.Char(
        string="Prestataire CRO",
        related='prestataire_id.name',
        required=False,
    )
    prestataire_crs = fields.Char(
        string="Prestataire CRS",
        related='prestataire_crs_id.name',
        required=False,
    )
    prestataire_phcie = fields.Char(
        string="Prestataire Phcie",
        related='prestataire_phcie_id.name',
        required=False,
    )
    # prestataire_crs_id = fields.Many2one(
    #     comodel_name='res.partner',
    #     string="Prestataire CRS",
    # )
    # prestataire_phcie_1_id = fields.Many2one(
    #     comodel_name='res.partner',
    #     string="Prestataire Phcie 1",
    # )
    # prestataire_phcie_2_id = fields.Many2one(
    #     comodel_name='res.partner',
    #     string="Prestataire Phcie 2",
    # )
    contrat_id = fields.Many2one(
        comodel_name="proximas.contrat",
        string="Contrat Assuré",
        related='assure_id.contrat_id',
        # compute='_get_contrat_assure',
        readonly=True,
    )
    num_contrat = fields.Char(
        string="Num. Contrat",
        related='contrat_id.num_contrat',
        readonly=True,
    )
    police_id = fields.Many2one(
        # comodel_name="proximas.police",
        string="Police Assuré",
        related='contrat_id.police_id',
        # compute='_get_police_assure',
        readonly=True,
    )
    structure_id = fields.Many2one(
        omodel_name="res.company",
        string="Organisation(SAM)",
        related='contrat_id.structure_id',
        readonly=True,
    )
    organisation = fields.Char(
        string="Organisation",
        related='structure_id.name',
        readonly=True,
    )
    adherent = fields.Many2one(
        comodel_name="proximas.adherent",
        string="Adhérent",
        related='contrat_id.adherent_id',
        require=False,
        store=True,
        readonly=True,
    )
    matricule = fields.Char(
        string="Matricule",
        related='adherent.matricule',
        readonly=True,
    )
    # Compteur de suivi de prises en charges (individu / famille)
    # structure_id = fields.Many2one(
    #     comodel_name="res.company",
    #     string="Organisation",
    #     related='police_id.structure_id',
    # )
    plafond_individu = fields.Float(
        string="Plafond individu",
        digits=(9, 0),
        related='police_id.plafond_individu',
        default=0,
        readonly=True,
    )
    plafond_famille = fields.Float(
        string="Plafond Famille",
        digits=(9, 0),
        related='police_id.plafond_famille',
        default=0,
        readonly=True,
    )
    sous_totaux_assure = fields.Float(
        string="S/Totaux Assuré",
        digits=(9, 0),
        compute='_compute_details_pec',
        store=True,
        default=0,
        #related='assure_id.sous_totaux_pec',
    )
    sous_totaux_contrat = fields.Float(
        string="S/Totaux Contrat",
        digits=(9, 0),
        compute='_compute_details_pec',
        store=True,
        default=0,
        # related='assure_id.sous_totaux_pec',
    )
    nbre_actes_contrat = fields.Integer(
        string="Nbre. Actes Contrat",
        compute='_compute_details_pec',
        store=True,
        default=0,
        #related='assure_id.nbre_actes_pec',
    )
    nbre_actes_assure = fields.Integer(
        string="Nbre. Actes Assuré",
        compute='_compute_details_pec',
        store=True,
        default=0,
        # related='assure_id.nbre_actes_pec',
    )
    niveau_sinistre_assure = fields.Float(
        string="Niveau Sinistre Assuré",
        compute='_compute_details_pec',
        store=True,
        default=0,
    )
    niveau_sinistre_contrat = fields.Float(
        string="Niveau Sinistre Contrat",
        compute='_compute_details_pec',
        store=True,
        default=0,
    )
    totaux_contrat = fields.Float(
        string="S/Totaux Famille",
        digits=(9, 0),
        related='contrat_id.sous_totaux_contrat',
        default=0,
        readonly=True,
        # related='contrat_id.compteur',
    )
    sous_totaux_pec = fields.Float(
        string="S/Totaux PEC",
        digits=(9, 0),
        compute='_compute_details_pec',
        store=True,
        default=0,
    )
    sous_totaux_npc_pec = fields.Float(
        string="S/Totaux (Non Couverts)",
        digits=(9, 0),
        compute='_compute_details_pec',
        store=True,
        default=0,
    )
    part_sam_pec = fields.Float(
        string="Net Part SAM",
        digits=(9, 0),
        compute='_compute_details_pec',
        store=True,
        default=0,
    )
    ticket_moderateur_pec = fields.Float(
        string="Net Ticket Modérateur",
        digits=(9, 0),
        compute='_compute_details_pec',
        store=True,
        default=0,
    )
    net_prestataire_pec = fields.Float(
        string="Totaux (Net A Payer)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    # Champs calculés par prestataire (CRO-CRS-Phcie)
    # 1. S/totaux
    mt_totaux_cro = fields.Float(
        string="S/Totaux (CRO)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    mt_totaux_crs = fields.Float(
        string="S/Totaux (CRS)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    mt_totaux_phcie = fields.Float(
        string="S/Totaux (Phcie)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    # 2. Net à payer
    net_prestataire_cro = fields.Float(
        string="Net à payer (CRO)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    net_prestataire_crs = fields.Float (
        string="Net à payer (CRS)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    net_prestataire_phcie = fields.Float (
        string="Net à payer (Phcie)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    # 3. Part SAM
    part_sam_cro = fields.Float(
        string="S/Totaux Part SAM (CRO)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    part_sam_crs = fields.Float(
        string="S/Totaux Part SAM (CRS)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    part_sam_phcie = fields.Float(
        string="S/Totaux Part SAM (Phcie)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    # 4. Ticket Modérateur
    ticket_moderateur_cro = fields.Float(
        string="Ticket modérateur (CRO)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    ticket_moderateur_crs = fields.Float(
        string="Ticket modérateur (CRS)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    ticket_moderateur_phcie = fields.Float(
        string="Ticket modérateur (Phcie)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    # 5. Ticket exigible
    ticket_exigible_cro = fields.Float(
        string="Ticket exigible (CRO)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    ticket_exigible_crs = fields.Float(
        string="Ticket exigible (CRS)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    ticket_exigible_phcie = fields.Float(
        string="Ticket exigible (Phcie)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    # 6.  Encaissement - Paye Assure
    mt_encaisse_cro = fields.Float(
        string="Montant Encaissé (CRO)",
        digits=(9, 0),
        #compute='_compute_details_pec',
        default=0,
        help='Montant total perçu de la part de l\'assuré, au titre de règlement du ticket modérateur',
    )
    mt_encaisse_crs = fields.Float(
        string="Montant Encaissé (CRS)",
        digits=(9, 0),
        #compute='_compute_details_pec',
        default=0,
        help='Montant total perçu de la part de l\'assuré, au titre de règlement du ticket modérateur',
    )
    mt_encaisse_phcie = fields.Float(
        string="Montant Encaissé (Phcie)",
        digits=(9, 0),
        #compute='_compute_details_pec',
        default=0,
        help='Montant total perçu de la part de l\'assuré, au titre de règlement du ticket modérateur',
    )
    # autrres champs calculés
    paye_assure_pec = fields.Float(
        string="Totaux Payés (Assuré)",
        digits=(9, 0),
        compute='_compute_details_pec',
        default=0,
    )
    net_remboursement_pec = fields.Float(
        string="Totaux (Net A Payer (Remb.)",
        digits=(9, 0),
        compute='_compute_details_pec',
        store=True,
        default=0,
    )
    totaux_ticket_exigible = fields.Float(
        string="S/totaux Ticket exigible",
        digits=(9, 0),
        default=0,
        required=False,
    )
    debit_assure = fields.Float(
        string="Montant débit",
        digits=(9, 0),
        default=0,
        help='Montant à devoir par l\'assuré',
    )
    date_last_pec = fields.Date(
        string="Dernière PEC",
        compute='_check_date_last_pec',
        help='Date de la dernière prise en charge de l\'assuré concerné',
        readonly=True,
    )
    delai_pec = fields.Integer(
        string="Délai (Heures)",
        compute='_compute_delai_pec',
        readonly=True,
        help='Délai du PEC exprimé en heures',
        default=0,
    )
    nbre_prestations_fournies = fields.Integer(
        string="Prestations Fournies",
        compute='_check_nbre_details_pec',
        # readonly=True,
        # store=True,
        help='Nombre de Prestations médicales et paramédicales Fournies',
        default=0,
    )
    nbre_prestations_demandes = fields.Integer(
        string="Prestations Demandées",
        compute='_check_nbre_details_pec',
        # readonly=True,
        # store=True,
        help='Nombre de Prestations médicales et paramédicales Demandées',
        default=0,
    )
    nbre_prescriptions = fields.Integer(
        string="Prescriptions",
        compute='_check_nbre_details_pec',
        # readonly=True,
        # store=True,
        help='Nombre de Prescriptions médicaments',
        default=0,
    )
    totaux_phcie = fields.Float(
        string="Totaux Pharmacie",
        compute='_check_nbre_details_pec',
        readonly=True,
        help='Totaux Prescriptions médicaments',
        default=0,
    )
    totaux_phcie_estimation = fields.Float(
        string="Totaux Estimatifs Phcie",
        compute='_check_nbre_details_pec',
        digits=(9, 0),
        readonly=True,
        help='Totaux estimatifs de prescriptions médicaments',
        default=0,
    )
    # exo_id = fields.Many2one(
    #     comodel_name='proximas.exercice',
    #     string="Exercice",
    #     compute='_check_exo_sam',
    #     required=False,
    # )
    validite_pec = fields.Integer(
        string="Validité (Heures)",
        related='contrat_id.validite_pec',
        help='Délai de validité d\'une prise en charge exprimé en heures',
        readonly=True,
        default=0,
    )
    nbre_prescription_maxi = fields.Integer(
        string="Nbre. maxi Prescriptions",
        related='police_id.nbre_prescription_maxi',
        readonly=True,
    )
    mt_plafond_prescription = fields.Float(
        string="Montant Plafond/Prescription",
        related='police_id.mt_plafond_prescription',
        readonly=True,
    )
    leve_plafond_prescription = fields.Boolean(
        string="Lever Plafond Prescription",
        help='Attention! En cochant, cela permet de lever le plafond pour les prescriptions. le système ne contrôlera \
        plus les montants de plafond pour les prescription sur cette prise en charge uniquement.',
    )
    marge_medicament = fields.Float(
        string='Marge/Produit Phcie.',
        help="Marge tolérée sur le coût des produits pharmaceutiques",
        digits=(5, 0),
        related='police_id.marge_medicament',
        readonly=True,
    )
    date_user = fields.Datetime(
        string="Date User",
        compute='_get_date_user',
        default=datetime.now(),  # fields.Date.today(),
        readonly=True,
    )
    current_user = fields.Many2one(
        comodel_name="res.users",
        string="Utilisateur en cours",
        compute='_get_current_user',
        required=False,
    )
    user_prestataire = fields.Char(
        string="Partner (User)",
        compute='_get_current_user',
        required=False,
    )
    user_prise_charge = fields.Boolean(
        string="Utitlisateur/Prise charge?",
        compute='_get_current_user',
        #store=True,
        help='Défini si l\'utilisateur courant est le prestataire exécutant de la prise en charge?',
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Créee Par",
        required=False,
    )
    is_valide = fields.Boolean(
        string="PEC valide?",
        compute='_check_valide_pec',
        help="Indique si la prise en charge est valide (PEC) ou non",
    )
    is_termine = fields.Boolean(
        string="Processus Terminé?",
        compute='_check_termine_pec',
        default=False,
        help="Indique si la prise en charge est valide (PEC) ou non",
    )
    info_clinique = fields.Text (
        string="Infos clinique",
        halp='Informations cliniques à communiquer (Facultatif)',
    )
    doc_info_clinique = fields.Binary (
        string="Copie de la demande",
        attachment=True,
        help='Joindre le document justificatif de la demande.',
    )
    doc_filename = fields.Char (
        "Nom fichier joint",
    )
    # Using Kanban stages and features
    color = fields.Integer('Color Index')
    priority = fields.Selection(
        [('0', 'Low'),
         ('1', 'Normal'),
         ('2', 'High')],
        'Priority', default='1')
    kanban_state = fields.Selection(
        [('normal', 'In Progress'),
         ('blocked', 'Blocked'),
         ('done', 'Ready for next stage')],
        'Kanban State', default='normal')


    @api.multi
    def _check_valide_pec(self):
        for rec in self:
            if 0 < int(rec.validite_pec) < int(rec.delai_pec):
                rec.is_valide = False
                #return rec.write({'pec_valide': False})
            else:
                rec.is_valide = True
                # return rec.write({'pec_valide': True})

    @api.multi
    def _check_termine_pec(self):
        for rec in self:
            if rec.state == 'termine':
                rec.is_termine = True
            else:
                rec.is_termine = False


    @api.one
    @api.depends('details_pec_soins_crs_ids', 'details_pec_soins_ids', 'details_pec_demande_crs_ids','details_pec_phcie_ids')
    @api.onchange('details_pec_soins_crs_ids', 'details_pec_soins_ids', 'details_pec_demande_crs_ids','details_pec_phcie_ids')
    def _check_nbre_details_pec(self):
        self.ensure_one()
        details_pec_assure = self.env['proximas.details.pec'].search([
            ('assure_id', '=', self.assure_id.id),
            ('pec_id', '=', self.id),
            ('produit_phcie_id', '!=', None),
        ])
        self.nbre_prestations_fournies = len(self.details_pec_soins_ids)
        self.nbre_prestations_demandes = len(self.details_pec_soins_crs_ids) or len(self.details_pec_demande_crs_ids)
        # self.nbre_prestations_demandes = len (self.details_pec_demande_crs_ids)
        self.nbre_prescriptions = len(self.details_pec_phcie_ids)
        self.totaux_phcie = sum(item.total_pc for item in details_pec_assure) or 0
        self.totaux_phcie_estimation = sum(item.prix_indicatif_produit for item in details_pec_assure) or 0


    # @api.multi
    # def _get_user_prestataire(self):
    #     for rec in self:
    #         if rec.prestataire_cro == rec.user_prestataire:
    #             rec.user_prise_charge = True

    @api.multi
    def action_en_cours(self):
        self.state = 'cours'
        # action = {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        #     'params': {
        #         # 'menu_action': 'proximas_user_list_pec_action',
        #         'menu_id': 129
        #     }
        # }
        # return action

    @api.multi
    def action_expire(self):
        self.state = 'expire'

    @api.multi
    def action_orienter(self):
        if int(self.nbre_prescriptions) >= 1:
            raise UserError(_(
                u"Cette prise en charge contient : %d prescription(s). Une prise en charge qui contient des \
                prescriprions ne peut faire l'objet d'une orientation vers un autre prestataire de soins. Vous \
                devez en tenir compte, avant de procéder à l'orientation du patient. \
                Pour plus d'informations, veuillez contactez l'administrateur..."
                ) % self.nbre_prescriptions
            )
        elif int(self.nbre_prestations_demandes) == 0:
            raise UserError(_(
                u"Cette prise en charge ne contient aucune prestation demandée. Une prise en charge qui ne contient pas \
                de prestation demandée ne peut faire l'objet d'une orientation vers un autre prestataire de soins. \
                Vous devez en tenir compte, avant de procéder à l'orientation du patient.\n \
                Pour plus d'informations, veuillez contactez l'administrateur..."
                )
            )
        elif not self.pathologie_id:
            raise UserError(_(
                u"Cette prise en charge ne contient aucune pathologie (affection) diagnostiquée. Il faudra renseigner\
                 au moins un code affection avant de pouvoir orienter le patient vers un autre prestataire de soins. \
                 Pour plus d'informations, veuillez contactez l'administrateur..."
                )
            )
        elif 0 < self.ticket_exigible_cro > self.mt_encaisse_cro:
            raise UserError(_(
                u"Vous êtes tenus d'encaisser la somme de : %d F.cfa, au titre de ticket modérateur. \
                  Par conséquent, vous devez absolument confirmer le paiement du ticket modérateur \
                  exigé et le notifier en renseignant le montant exact dans le champ indiqué. Faute \
                  de quoi, vos données ne seront pas validées. Pour plus d'informations, veuillez \
                  contactez l'administrateur..."
                ) % self.ticket_exigible_cro
            )
        else:
            self.state = 'oriente'
            menu_id = self.env['ir.ui.menu'].search([('sequence', '=', 2010), ]).id
            action = {
                'type': 'ir.actions.client',
                'tag': 'reload',
                'params': {
                    # 'menu_id': menu_ids and menu_ids[0] or menu_ids[1] or menu_ids[2] or False,
                    'menu_id': menu_id,
                }
            }
            return action

    @api.multi
    def action_dispenser(self):
        if not self.pathologie_id:
            raise UserError(_(
                u"Cette prise en charge ne contient aucune pathologie (affection) diagnostiquée. Il faudra renseigner\
                 au moins un code affection avant de pouvoir transférer la prise ne charge vers une pharmacie pour \
                 dispensation. Pour plus d'informations, veuillez contactez l'administrateur..."
                )
            )
        elif 0 < self.ticket_exigible_cro > self.mt_encaisse_cro:
            raise UserError (_ (
                u"Vous êtes tenus d'encaisser la somme de : %d F.cfa, au titre de ticket modérateur. \
                  Par conséquent, vous devez absolument confirmer le paiement du ticket modérateur \
                  exigé et le notifier en renseignant le montant exact dans le champ indiqué. Faute \
                  de quoi, vos données ne seront pas validées. Pour plus d'informations, veuillez \
                  contactez l'administrateur..."
                ) % self.ticket_exigible_cro
            )
        elif 0 < self.ticket_exigible_crs > self.mt_encaisse_crs:
            raise UserError(_(
                u"Vous êtes tenus d'encaisser la somme de : %d F.cfa, au titre de ticket modérateur. \
                Par conséquent, vous devez absolument confirmer le paiement du ticket modérateur \
                exigé et le notifier en renseignant le montant exact dans le champ indiqué. Faute \
                de quoi, vos données ne seront pas validées. Pour plus d'informations, veuillez \
                contactez l'administrateur..."
                ) % self.ticket_exigible_crs
            )
        else:
            self.state = 'dispense'
            menu_id = self.env['ir.ui.menu'].search([('sequence', '=', 2010),]).id
            action = {
                'type': 'ir.actions.client',
                'tag': 'reload',
                'params': {
                    'menu_id': menu_id,
                }
            }
            return action

    @api.multi
    def action_terminer(self):
        if int(self.nbre_prestations_fournies) == 0:
            raise UserError(_(
                u"Cette prise en charge ne contient aucune prestation fournie. Une prise en charge qui ne contient pas \
                  de prestation fournie ne peut faire l'objet d'une validation. Vous devez en tenir compte, avant de \
                  procéder à la validation de la prise en charge. \
                  Pour plus d'informations, veuillez contactez l'administrateur..."
                )
            )
        elif not self.pathologie_id:
            raise UserError(_(
                u"Cette prise en charge ne contient aucune pathologie (affection) diagnostiquée. Il faudra renseigner\
                 au moins un code affection avant de pouvoir orienter le patient vers un autre prestataire de soins. \
                 Pour plus d'informations, veuillez contactez l'administrateur..."
                )
            )
        elif 0 < self.ticket_exigible_cro > self.mt_encaisse_cro:
            raise UserError (_ (
                u"Vous êtes tenus d'encaisser la somme de : %d F.cfa, au titre de ticket modérateur. \
                  Par conséquent, vous devez absolument confirmer le paiement du ticket modérateur \
                  exigé et le notifier en renseignant le montant exact dans le champ indiqué. Faute \
                  de quoi, vos données ne seront pas validées. Pour plus d'informations, veuillez \
                  contactez l'administrateur..."
                ) % self.ticket_exigible_cro
            )
        elif 0 < self.ticket_exigible_crs > self.mt_encaisse_crs:
            raise UserError (_ (
                u"Vous êtes tenus d'encaisser la somme de : %d F.cfa, au titre de ticket modérateur. \
                  Par conséquent, vous devez absolument confirmer le paiement du ticket modérateur \
                  exigé et le notifier en renseignant le montant exact dans le champ indiqué. Faute \
                  de quoi, vos données ne seront pas validées. Pour plus d'informations, veuillez \
                  contactez l'administrateur..."
                ) % self.ticket_exigible_crs
            )
        elif 0 < self.ticket_exigible_phcie > self.mt_encaisse_phcie:
            raise UserError (_ (
               u"Vous êtes tenus d'encaisser la somme de : %d F.cfa, au titre de ticket modérateur. \
                Par conséquent, vous devez absolument confirmer le paiement du ticket modérateur \
                exigé et le notifier en renseignant le montant exact dans le champ indiqué. Faute \
                de quoi, vos données ne seront pas validées. Pour plus d'informations, veuillez \
                contactez l'administrateur..."
                ) % self.ticket_exigible_phcie
            )
        else:
            # self.env.user.notify_info('La Prise en charge : %s a été sauvegardée et terminée avec succès.') % self.name
            self.state = 'termine'
            menu_id = self.env['ir.ui.menu'].search ([('sequence', '=', 2010), ]).id
            action = {
                'type': 'ir.actions.client',
                'tag': 'reload',
                'params': {
                    # 'menu_id': menu_ids and menu_ids[0] or menu_ids[1] or menu_ids[2] or False,
                    'menu_id': menu_id,
                }
            }
            return action

    # @api.multi
    # def _get_prestataire_cro(self):
    #     if bool(self.prestataire_id):
    #         user_id = self.env.context.get('uid')
    #         group_id = self.env.context.get('gid')
    #         user = self.env['res.users'].search([('id', '=', user_id)])
    #         group = self.env['res.groups'].search([('id', '=', group_id)])
    #         prestataire = self.env['res.partner'].search([('id', '=', user.partner_id.id)])

    @api.one
    @api.onchange('pathologie_ids')
    def _check_pathologie_ids(self):
        # CONTROLE ANTECEDANT POLICE
        for pathologie in self.pathologie_ids:
            pathologie_id = pathologie.id
            controle_affection = self.env['proximas.controle.antecedent'].search([
                ('police_id', '=', self.police_id.id), ('pathologie_id', '=', pathologie_id)
            ])
            if controle_affection:
                # Si Le contrôle Antécédant est activé (renseigné), alors;
                # selfherche l'ensemble des prises en charge de l'assuré
                prise_en_charge_individu = self.env['proximas.prise.charge'].search([
                    ('assure_id', '=', self.assure_id.id)
                ])
                # selfherche l'ensemble des prises en charge de la famille (contrat)
                prise_en_charge_famille = self.env['proximas.prise.charge'].search([
                    ('contrat_id', '=', self.contrat_id.id)
                ])
                if bool(prise_en_charge_individu):
                    # pour chaque prise en charge de l'assuré, alors,
                    for item in prise_en_charge_individu:
                        details_pec = self.env['proximas.details.pec'].search([
                            ('pec_id', '=', item.id),
                        ])
                        totaux_pathologie_assure = 0
                        nombre_pec_assure = 0
                        # on vérifie si elle est reliée à la pathologie (affection)
                        pathologie_relie_pec_assure = self.env['proximas.pathologie.proximas.prise.charge.rel'].search(
                            [
                                ('proximas_pathologie_id', '=', pathologie_id),
                                ('proximas_prise_charge_id', '=', item.id),
                            ])
                        pathologies_assure = []
                        # S'il y a des liens entre la prise en charge et la pathologie,
                        if pathologie_relie_pec_assure:
                            # dans ce cas, on récupère le montant total prise en charge (total_pc) et on incrémente
                            # le compteur pour le nombre de prises en charge
                            pathologies_assure += pathologie_relie_pec_assure
                            totaux_pathologie_assure += sum(detail.total_pc or 0 for detail in details_pec)
                            nombre_pec_assure += 1
                            # On vérifie ainsi, si le contrôle de nombre de prises en charge est atteint ou pas ?
                            if 0 < int(controle_affection.nbre_pec) <= int(nombre_pec_assure):
                                # Si le contrôle de nombre de prises en charge est différent de 0 et est atteint, alors
                                # on lève une exception sur la validation des données...
                                # On vérifie si le facteur du contrôle est bloquant ou pas ? si OUI alors,
                                if bool(controle_affection.controle_strict):
                                    raise ValidationError (_ (
                                         u"Proximas :contrôle Règles de gestion ==> Nbre. Limite PEC Antécédant:\n L'assuré concerné\
                                         a atteint le quota de prise en charge faisant apparaître cette pathologie : %s.\n \
                                         Par conséquent, vos données ne pourront être validées.\n \
                                         Pour plus d'informations, veuillez contactez l'administrateur..."
                                        ) % pathologie_id.libelle
                                    )
                                else:
                                    # Sinon, une simple alerte envoyée à l'utilisateur.
                                    return {'value': {},
                                            'warning': {
                                                'title': u'Proximas :contrôle Règles de gestion ==> Nbre. Limite PEC Antécédant:',
                                                'message': u"L'assuré concerné a atteint le quota de prise en charge \
                                                faisant apparaître cette pathologie : %r.\n Par conséquent, vos données ne \
                                                pourront être validées.\n Pour plus d'informations, veuillez contactez \
                                                l'administrateur..." % pathologie_id.libelle
                                            }
                                            }
                            # Sinon, on vérifie si le plafond individuel pour la pathologie est atteint ou pas
                            elif 0 < int(controle_affection.plafond_individu) <= int(totaux_pathologie_assure):
                                # Si le plafond individuel pour la pathologie est différent de 0 et est atteint ou dépassé,alors
                                # on lève une exception sur la validation des données...
                                # On vérifie si le facteur du contrôle est bloquant ou pas ? si OUI alors,
                                if bool(controle_affection.controle_strict):
                                    raise ValidationError (_ (
                                        u"Proximas : Contrôle Règles de gestion - Plafond Individu sur Antécédant:\n \
                                        L'assuré concerné atteint le plafond individuel pour la pathologie : %r. \
                                        Par conséquent, vos données ne pourront être validées.Pour plus d'informations,\
                                         veuillez contactez l'administrateur..."
                                        ) % pathologie_id.libelle
                                    )
                                else:
                                    # Sinon, une simple alerte envoyée à l'utilisateur.
                                    return {'value': {},
                                            'warning': {
                                                'title': u'Proximas : Contrôle Règles de gestion => Plafond Individu sur Antécédant:',
                                                'message': u"L'assuré concerné a atteint le plafond individuel pour la \
                                                pathologie : %s. Par conséquent, vos données ne pourront être \
                                                validées. Pour plus d'informations, veuillez contactez \
                                                l'administrateur..." % pathologie_id.libelle
                                            }
                                            }
                        # CONTROLE DELAI D'ATTENTE ENTRE 2 PATHOLOGIES DE MEME NATURE
                        now = datetime.now ()
                        dernier_pathologie_pec_id = max(pathologie.pec_id for pathologie in pathologies_assure)
                        dernier_prise_charge = self.search([
                            ('id', '=', dernier_pathologie_pec_id)
                        ])
                        date_pec = fields.Datetime.from_string(dernier_prise_charge.date_saisie)
                        nbre_jours_ecoules = int(now - date_pec)
                        delai_attente = int(controle_affection.delai_attente)
                        if 0 < delai_attente <= nbre_jours_ecoules:
                            # Si contrôle strict pour le caractère bloquant du contrôle?
                            if bool(controle_affection.controle_strict):
                                raise ValidationError (_ (
                                    u"Proximas : Contrôle Règles de Gestion: Délai d'Attente Pathologie:\n \
                                     L'assuré concerné a déjà fait l'objet d'une prise en charge au cours de laquelle la \
                                     pathologie : (%d)s a été diagnostiquée le : (%s). Par conséquent, il doit \
                                     impérativement respecter un délai d'attente de : (%d) jours.\n \
                                     Pour plus d'informations,veuillez contactez l'administrateur..."
                                    ) % (pathologie_id, date_pec, delai_attente)
                                )
                            else:
                                # Sinon, une simple alerte envoyée à l'utilisateur.
                                return {'value': {},
                                        'warning': {
                                            'title': u'Contrôle Règles de Gestion ==> Délai d\'attente Pathologie:',
                                            'message': u"L'assuré concerné a déjà fait l'objet d'une prise en charge au cours de laquelle la \
                                                        pathologie : (%d)s a été diagnostiquée le : (%s). Par conséquent, il doit \
                                                        impérativement respecter un délai d'attente de : (%d) jours.\n \
                                                        Pour plus d'informations,veuillez contactez l'administrateur..."
                                                       % (pathologie_id, date_pec, delai_attente)
                                            }
                                        }
                if bool(prise_en_charge_famille):
                    # pour chaque prise en charge de la famille (contrat), alors,
                    for item in prise_en_charge_famille:
                        details_pec = self.env['proximas.details.pec'].search([('pec_id', '=', item.id)])
                        totaux_pathologie_famille = 0
                        # on vérifie si elle est reliée à la pathologie (affection)
                        pathologie_relie_pec_famille = self.env[
                            'proximas_pathologie_proximas_prise_charge_rel'].search([
                            ('proximas_pathologie_id', '=', pathologie_id),
                            ('proximas_prise_charge_id', '=', item.id),
                        ])
                        # S'il y a des liens entre la prise en charge et la pathologie,
                        if pathologie_relie_pec_famille:
                            # dans ce cas, on récupère le montant total prise en charge (total_pc)
                            totaux_pathologie_famille += sum(detail.total_pc for detail in details_pec) or 0
                            # Sinon, on vérifie si le plafond individuel pour la pathologie est atteint ou pas
                            if 0 < int(controle_affection.plafond_famille) <= int(totaux_pathologie_famille):
                                # Si le plafond famille pour la pathologie est différent de 0 et est atteint ou dépassé,alors
                                # on lève une exception sur la validation des données...
                                if bool(controle_affection.controle_strict):
                                    raise ValidationError(_(
                                        u"Proximas : Contrôle Règles de gestion ==> Plafond Famille sur Antécédant:\n L'assuré concerné\
                                         a atteint le plafond famille pour la pathologie : %s. Par conséquent, vos données \
                                         ne pourront être validées. Pour plus d'informations, veuillez contactez \
                                         l'administrateur..."
                                        ) % pathologie_id.libelle
                                    )
                                else:
                                    # Sinon, une simple alerte envoyée à l'utilisateur.
                                    return {'value': {},
                                            'warning': {
                                                'title': u'Proximas : Contrôle Règles de gestion => Plafond Famille sur Antécédant:',
                                                'message': u"L'assuré concerné a atteint le plafond famille pour la \
                                                pathologie : %s. Par conséquent, vos données ne pourront être validées. \
                                                Pour plus d'informations, veuillez contactez l'administrateur..."
                                                % pathologie_id
                                                }
                                            }

    @api.multi
    def _get_date_user(self):
        for rec in self:
            rec.date_user = datetime.now()

    @api.multi
    def _get_current_user(self):
        for rec in self:
            user_id = self.env.context.get('uid')
            group_id = self.env.context.get('gid')
            user = self.env['res.users'].search([('id', '=', user_id)])
            prestataire = self.env['res.partner'].search([('id', '=', user.partner_id.id)])
            rec.current_user = user_id
            rec.user_prestataire = user.partner_id.name
            if rec.prestataire_cro == rec.user_prestataire:
                rec.user_prise_charge = True

    # @api.multi
    # def action_expirer(self):
    #     self.state = 'expire'

    @api.multi
    def _check_date_last_pec(self):
        for rec in self:
            pec_assure = self.env['proximas.prise.charge'].search([
                ('assure_id', '=', rec.assure_id.id),
            ])
            if bool(pec_assure):
                count_pec = len(pec_assure)
                if count_pec == 1:
                    rec.date_last_pec = pec_assure.date_saisie
                else:
                    last_pec = pec_assure[1]
                    rec.date_last_pec = last_pec.date_saisie

    @api.one
    @api.depends('date_saisie')
    def _compute_delai_pec(self):
        date_pec = fields.Datetime.from_string(self.date_saisie)
        now = datetime.now()
        delai_pec = now - date_pec
        hours = delai_pec.seconds / 3600
        days_hours = delai_pec.days * 24
        self.delai_pec = days_hours + hours
        # if self.delai_pec > self.validite_pec and (self.state == 'oriente' or self.state == 'termune'):
        #     self.state = 'expire'

    # @api.multi
    @api.onchange('details_pec_soins_ids', 'details_pec_soins_crs_ids', 'details_pec_phcie_ids')
    def _check_validite_pec_onchange(self):
        # self.ensure_one()
        if 0 < int(self.validite_pec) < int(self.delai_pec):
            action = {'warning': {
                            'title': u'Proximaas : Règles de Gestion',
                              'message': u"Les modifications effectuées ne peuvent être validées pour des \
                              raisons de validité de délai de traitement.Cette prise en charge a été générée \
                              depuis : %d heures, alors que le délai maximum (en heures) autorisé avant \
                              expiration est de : %d heures. \n Pour plus d'informations, veuillez contactez \
                              l'administrateur..." % (self.delai_pec, self.validite_pec)
                            }
                    }
            return action

    # @api.multi
    @api.constrains('details_pec_soins_ids', 'details_pec_soins_crs_ids', 'details_pec_phcie_ids')
    def _validate_validite_pec(self):
        # self.ensure_one()
        if 0 < int(self.validite_pec) < int(self.delai_pec):
            raise ValidationError(_(
                u"Proximas : Contrôle de Règles de Gestion (Délai Validité PEC) :\n \
                Les modifications effectuées ne peuvent être validées pour des raisons de validité de délai de traitement.\
                Cette prise en charge a été générée depuis : %d heures, alors que le délai maximum \
                (en heures) autorisé avant expiration est de : %d heures. \n \
                Pour plus d'informations, veuillez contactez l'administrateur..."
                ) % (self.delai_pec, self.validite_pec)
            )


    @api.onchange('details_pec_phcie_ids', 'nbre_prescriptions', 'nbre_prescription_maxi')
    def _check_details_prescription(self):
        if 0 < int (self.nbre_prescription_maxi) < int(self.nbre_prescriptions):
            return {'warning':
                        {'title': u'Proximas : Contrôle de règles de Gestion => Nombre Maxi Prescriptions:',
                         'message': u"Cette prise en charge ne peut contenir plus de : (%d) prescriptions. Par conséquent,\
                                     vous devez en tenir compte pour pouvoir valider les données. \
                                     Pour plus d'informations, veuillez contactez l'administrateur..."
                                    % self.nbre_prescription_maxi
                         }
                    }
        elif 0 < int(self.mt_plafond_prescription) <= int(self.totaux_phcie) and not bool (
                self.leve_plafond_prescription):
            return {'warning':
                        {'title': u'Proximas : Contrôle de règles de Gestion => Plafond Prescriptions :',
                         'message': u"Cette prise en charge ne peut excéder le plafond pour les prescriptions: (%d).  \
                        Par conséquent, vous devez en tenir compte pour pouvoir valider les données.  \
                        Pour plus d'informations, veuillez contactez l'administrateur..."
                        % self.mt_plafond_prescription
                        }
            }

    # @api.multi
    @api.constrains('details_pec_phcie_ids', 'nbre_prescriptions')
    def _validate_details_prescriptions(self):
        if 0 < int(self.nbre_prescription_maxi) < int(self.nbre_prescriptions):
            raise ValidationError(_(
                u"Proximas : Contrôle de règles de Gestion => Nombre Maxi Prescriptions:\n \
                Cette prise en charge ne peut contenir plus de : (%d) prescriptions. Par conséquent,\
                vous devez en tenir compte pour pouvoir valider les données. \
                Pour plus d'informations, veuillez contactez l'administrateur..."
                ) % self.nbre_prescription_maxi
            )
        elif 0 < int(self.mt_plafond_prescription) < int(self.totaux_phcie) and not bool(self.leve_plafond_prescription):
            raise ValidationError(_(
                u"Proximas : Contrôle de règles de Gestion => Plafond Prescriptions : :\n \
                Cette prise en charge ne peut excéder le plafond pour les prescriptions: (%d).  \
                Par conséquent, vous devez en tenir compte pour pouvoir valider les données. \
                Pour plus d'informations, veuillez contactez l'administrateur..."

                ) % self.mt_plafond_prescription
            )


    # @api.one
    # @api.constrains('details_pec_phcie_ids', 'nbre_prescriptions', 'nbre_prescription_maxi')
    # def _check_maxi_prescription_validation(self):
    #     if int(self.nbre_prescriptions) > int(self.nbre_prescription_maxi):
    #         raise ValidationError(_(
    #             u"Proximas : Contrôle de règles de Gestion - Nbre. Maxi Prescriptions : \n \
    #             Cette prise en charge ne peut contenir plus de %d Prescriptions. Par conséquent, vous devez en tenir \
    #             compte et supprimer le(s) surplus de prescriptions au choix.\n Pour plus d'informations, veuillez \
    #             contactez l'administrateur..."
    #             % self.nbre_prescription_maxi
    #             )
    #         )

    # @api.one
    # @api.onchange('details_pec_phcie_ids')
    # def _check_doublon_details_pec(self):
    #     for item in self.details_pec_phcie_ids:
    #         nbre_produit_phcie = self.env['proximas.details.pec'].search_count([
    #             ('pec_id', '=', self.id),
    #             ('produit_phcie_id', '=', item.produit_phcie_id.id)
    #         ])
    #         if nbre_produit_phcie > 1:
    #             raise UserError(_(
    #                 u"Proximas: Risque de doublon sur Médicament\n\
    #                 Il semble que le médicament: %s %s %s ait déjà été prescrit pour cette prise en charge.\
    #                 Par conséquent, il ne peut y avoir plus d\'une fois le même médicament prescrit sur une \
    #                 même prise en charge. Vérifiez s'il n'y pas de doublon ou contactez l'administrateur."
    #                 % (item.produit_phcie_id.name, item.produit_phcie_id.forme_galenique, item.produit_phcie_id.dosage)
    #             )
    #             )

    @api.constrains('details_pec_soins_ids', 'details_pec_soins_crs_ids', 'details_pec_phcie_ids',)
    def _validate_ticket_exigible_and_encaissement(self):
        # 1. Controle cas de CRO
        if self.state == 'cours' and 0 < int(self.ticket_exigible_cro) > int(self.mt_encaisse_cro):
            raise ValidationError(_(
                u"Proximas : Contrôle de règles de Gestion => Montant Ticket Exigible:\n \
                Cette prise en charge exige l'encaissement d'un ticket modérateur de : (%d Fcfa).\n \
                Le montant encaissé est de : (%d Fcfa) inférieur au montant exigé. Par conséquent,\
                vous devez en tenir compte pour pouvoir valider les données. Pour plus d'informations, \
                veuillez contactez l'administrateur..."
                ) % (self.ticket_exigible_cro, self.mt_encaisse_cro)
            )
        # 2. Controle cas de CRS
        if self.state == 'oriente' and 0 < int (self.ticket_exigible_crs) > int (self.mt_encaisse_crs):
            raise ValidationError (_ (
                u"Proximas : Contrôle de règles de Gestion => Montant Ticket Exigible:\n \
                Cette prise en charge exige l'encaissement d'un ticket modérateur de : (%d Fcfa).\n \
                Le montant encaissé est de : (%d Fcfa) inférieur au montant exigé. Par conséquent,\
                vous devez en tenir compte pour pouvoir valider les données. Pour plus d'informations, \
                veuillez contactez l'administrateur..."
                ) % (self.ticket_exigible_crs, self.mt_encaisse_crs)
            )
        # 3. Controle cas de PHARMACIE
        if self.state == 'dispense' and 0 < int(self.ticket_exigible_phcie) > int(self.mt_encaisse_phcie):
            raise ValidationError(_(
                u"Proximas : Contrôle de règles de Gestion => Montant Ticket Exigible:\n \
                Cette prise en charge exige l'encaissement d'un ticket modérateur de : (%d Fcfa).\n \
                Le montant encaissé est de : (%d Fcfa) inférieur au montant exigé. Par conséquent,\
                vous devez en tenir compte pour pouvoir valider les données. Pour plus d'informations, \
                veuillez contactez l'administrateur..."
                ) % (self.ticket_exigible_phcie, self.mt_encaisse_phcie)
            )

    @api.one
    @api.depends('details_pec_soins_ids', 'details_pec_soins_crs_ids', 'details_pec_phcie_ids',)
    def _stuff_note(self):
        note = u"Ajout d'une prestation par %s." % self.user_id.name
        stuff_to_notes = str(note)
        self.note = stuff_to_notes

    @api.one
    @api.depends('details_pec_soins_ids', 'details_pec_soins_crs_ids', 'details_pec_phcie_ids', 'nbre_prescriptions',
                 'nbre_prestations_fournies')
    @api.onchange('details_pec_soins_ids', 'details_pec_soins_crs_ids', 'details_pec_phcie_ids', 'nbre_prescriptions',
                  'nbre_prestations_fournies')
    def _compute_details_pec(self):
        self.ensure_one()
        details_pec_assure = self.env['proximas.details.pec'].search(
            [
                ('assure_id', '=', self.assure_id.id),
                ('code_id', '=', self.code_id)
            ]
        )
        details_pec_contrat = self.env['proximas.details.pec'].search([
            # ('adherent_id', '=', self.adherent.id),
            ('contrat_id', '=', self.contrat_id.id),
            ('date_execution', '!=', None),
        ])
        nbre_details_pec_contrat = self.env['proximas.details.pec'].search_count([
            # ('adherent_id', '=', self.adherent.id),
            ('contrat_id', '=', self.contrat_id.id),
            ('date_execution', '!=', None),
        ])
        nbre_details_pec_assure = self.env['proximas.details.pec'].search_count([
            ('assure_id', '=', self.assure_id.id),
            ('prestation_id', '!=', None),
            ('date_execution', '!=', None),
        ])
        totaux_details_pec = self.env['proximas.details.pec'].search([('pec_id', '=', self.id)])
        totaux_details_pec_cro = self.env['proximas.details.pec'].search([
            ('pec_id', '=', self.id),
            ('prestataire', '=', self.prestataire_id.id),
            ('date_execution', '!=', None),
        ])
        totaux_details_pec_crs = self.env['proximas.details.pec'].search([
            ('pec_id', '=', self.id),
            ('prestataire', '=', self.prestataire_crs_id.id),
            ('date_execution', '!=', None),
        ])
        totaux_details_pec_phcie = self.env['proximas.details.pec'].search([
            ('pec_id', '=', self.id),
            ('prestataire', '=', self.prestataire_phcie_id.id),
            ('produit_phcie_id', '!=', None),
            ('date_execution', '!=', None),


        ])

        if bool(details_pec_assure):
            self.nbre_actes_assure = int(nbre_details_pec_assure)
            self.nbre_actes_contrat = int(nbre_details_pec_contrat)
            self.sous_totaux_assure = sum(item.total_pc for item in details_pec_assure) or 0
            self.sous_totaux_contrat = sum(item.total_pc for item in details_pec_contrat) or 0
            self.sous_totaux_pec = sum(item.total_pc for item in totaux_details_pec) or 0
            self.sous_totaux_npc_pec = sum(item.total_npc for item in totaux_details_pec)
            self.part_sam_pec = sum(item.net_tiers_payeur for item in totaux_details_pec)
            self.ticket_moderateur_pec = sum(item.ticket_moderateur for item in totaux_details_pec)
            self.net_prestataire_pec = sum(item.net_prestataire for item in totaux_details_pec)
            self.net_remboursement_pec = sum(item.mt_remboursement for item in totaux_details_pec)
            self.paye_assure_pec = sum(item.mt_paye_assure for item in totaux_details_pec)
            self.niveau_sinistre_assure = (self.sous_totaux_assure * 100 / self.plafond_individu) \
                if bool(self.plafond_individu) else 0
            self.niveau_sinistre_contrat = (self.sous_totaux_contrat * 100 / self.plafond_famille) \
                if bool(self.plafond_famille) else 0
            # self.totaux_contrat = sum(item.total_pc for item in details_pec_contrat)
            # Calculs des S/Totaux (CRO-CRS-Phcie)
            # 1. S/Totaux
            self.mt_totaux_cro = sum(item.total_pc for item in totaux_details_pec_cro) or 0
            self.mt_totaux_crs = sum(item.total_pc for item in totaux_details_pec_crs) or 0
            self.mt_totaux_phcie = sum (item.total_pc for item in totaux_details_pec_phcie) or 0
            # 2. Part SAM
            self.part_sam_cro = sum(item.net_tiers_payeur for item in totaux_details_pec_cro) or 0 
            self.part_sam_crs = sum(item.net_tiers_payeur for item in totaux_details_pec_crs) or 0
            self.part_sam_phcie = sum(item.net_tiers_payeur for item in totaux_details_pec_phcie) or 0
            # 3. Ticket Modérateur
            self.ticket_moderateur_cro = sum(item.ticket_moderateur for item in totaux_details_pec_cro) or 0
            self.ticket_moderateur_crs = sum(item.ticket_moderateur for item in totaux_details_pec_crs) or 0
            self.ticket_moderateur_phcie = sum(item.ticket_moderateur for item in totaux_details_pec_phcie) or 0
            # 4. Ticket Exigible
            self.ticket_exigible_cro = sum(
                item.ticket_moderateur for item in totaux_details_pec_cro if bool(item.ticket_exigible) or 0
            )
            self.ticket_exigible_crs = sum(
                item.ticket_moderateur for item in totaux_details_pec_crs if bool(item.ticket_exigible) or 0
            )
            self.ticket_exigible_phcie = sum(
                item.ticket_moderateur for item in totaux_details_pec_phcie if bool(item.ticket_exigible) or 0
            )
            # 5. Net à Payer
            self.net_prestataire_cro = sum(item.net_prestataire for item in totaux_details_pec_cro) or 0
            self.net_prestataire_crs = sum(item.net_prestataire for item in totaux_details_pec_crs) or 0
            self.net_prestataire_phcie = sum(item.net_prestataire for item in totaux_details_pec_phcie) or 0
            # 6. Totaux Encaissement
            # self.mt_encaisse_cro = sum(item.mt_paye_assure or 0 for item in totaux_details_pec_cro)
            # self.mt_encaisse_crs = sum(item.mt_paye_assure or 0 for item in totaux_details_pec_crs)
            # self.mt_encaisse_phcie = sum(item.mt_paye_assure or 0 for item in totaux_details_pec_phcie)

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id,
                 "%s - %s" % (rec.code_pec, rec.assure_id.name)
                 ))
        return result

    @api.one
    @api.depends('code_saisi')
    def _get_code_pec(self):
        self.ensure_one()
        """ Généré un code identifiant pour PEC """
        date_saisie = fields.Datetime.from_string(self.date_saisie)
        annee_format = datetime.strftime(date_saisie, '%y')
        code_genere = int(randint(1, 1e6))
        code_pec = u'%s%06d' % (annee_format, code_genere)
        # code_pec = str(annee_format) + str(code_genere)
        check_code_pec = self.search_count([('code_pec', '=', code_pec)])
        if check_code_pec >= 1:
            code_regenere = int(randint(1, 1e6))
            code_pec = u'%s%06d' % (annee_format, code_regenere)
            # code_pec = str(annee_format) + str(code_regenere)
            self.code_pec = code_pec
        self.code_pec = code_pec

    @api.one
    def _get_code_pc(self):
        self.ensure_one()
        self.code_pc = self.code_pec



    @api.constrains('code_pec')
    def validate_code_pec(self):
        check_code_pec = self.search_count([('code_pec', '=', self.code_pec)])
        if check_code_pec > 1:
            raise ValidationError(_(
                u"Proximaas : Contrôle Contrôle Règles de Gestion ; \n \
                Risque de doublon pour le Code PEC : %s. Le code PEC généré par le système existe déjà pour une autre \
                prise en charge. Cependant, ce code doit être unique par prise en charge.\n \
                Veuillez contactez les administrateurs pour plus détails..."
                ) % self.code_pec
            )


class PecWizard(models.TransientModel):
    _name = 'proximas.pec.wizard'
    _description = 'PEC CRO Wizard'

    code_saisi = fields.Char(
        string="Code ID",
        required=True,
        help="Veuillez fournir le Code ID. de l'assuré concerné."
    )



    @api.multi
    def open_popup(self):
        # self.ensure_one()
        user_id = self.env.context.get('uid')
        user = self.env['res.users'].search([('id', '=', user_id)])
        prestataire = self.env['res.partner'].search([('id', '=', user.partner_id.id)])
        prestations = self.env['proximas.prestation'].search([('prestataire_id', '=', user.partner_id.id)])
        assure = self.env['proximas.assure'].search([
            '|', ('code_id_externe', '=ilike', self.code_saisi),
            ('code_id', '=ilike', self.code_saisi)
        ])
        info_assure = assure.name
        # 1. Vérification de la présence de doublon sur l'assuré.
        if len(assure) > 1:
            raise UserError (_ (
                u"Proximaas : Contrôle Règles de Gestion:\n\
                L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                l'objet d'une prise en charge actuellement, car il y a un doublon du code ID. \
                Veuillez contactez les administrateurs pour plus détails..."
                ) % (info_assure, self.code_saisi)
            )
        # 2. Vérification du contrat pour l'assuré.
        elif bool(assure) and not bool(assure.police_id):
            raise UserError(_(
                u"Proximaas : Contrôle Règles de Gestion: \n\
                L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                l'objet d'une prise en charge actuellement, pour absence de contrat faisant référence à sa police de \
                couverture. Veuillez contactez les administrateurs pour plus détails..."
                ) % (assure.name, assure.code_id)
            )
        # 3. Vérification du statut de l'assuré (actif ou non).
        elif bool(assure) and assure.state != 'actif':
            raise ValidationError(_(
                u"Proximaas : Contrôle Règles de Gestion: \n\
                L'assuré: %s - Code ID.: %s est bel et bien enregistré en tant que bénéficiaire. Cependant, \
                ne peut faire l'objet d'une prise en charge actuellement, en rapport avec son statut.\n \
                Veuillez contactez les administrateurs pour plus détails..."
                ) % (assure.name, assure.code_id)
            )
        elif bool(assure) and assure.state == 'actif':
            if assure.code_id_externe == self.code_saisi:
                code_id = assure.code_id
                return {
                    'name': 'Création PEC Assuré',
                    'view_type': 'form',
                    'view_mode': 'form',
                    # 'target': 'new',
                    'res_model': 'proximas.prise.charge',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_assure_id': assure.id,
                        'default_code_id_externe': self.code_saisi,
                        'default_code_id': code_id,
                        'default_prestataire_id': prestataire.id,
                        'default_user': user.name,
                        'default_user_id': user.id,
                    },
                }
            else:
                return {
                    'name': 'Création PEC Assuré',
                    'view_type': 'form',
                    'view_mode': 'form',
                    # 'target': 'new',
                    'res_model': 'proximas.prise.charge',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_assure_id': assure.id,
                        'default_code_id': self.code_saisi,
                        'default_prestataire_id': prestataire.id,
                        'default_user': user.name,
                        'default_user_id': user.id,
                    },
                }
        else:
            raise ValidationError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 Le Code ID. que vous avez fourni n'est pas un identifiant valide dans le système.\n\
                 Veuillez contactez l 'administrateur en cas de besoin..!"
            )
            )


class PecMajWizard(models.TransientModel):
    _name = 'proximas.pec.maj.wizard'
    _description = 'PEC Wizard'

    code_pec = fields.Char(
        string="Code Prise en charge",
        required=True,
        help="Veuillez fournir le Code de la prise en charge concernée."
    )

    @api.multi
    def crs_open_popup(self):
        self.ensure_one()
        user_id = self.env.context.get('uid')
        group_id = self.env.context.get('gid')
        user = self.env['res.users'].search([('id', '=', user_id)])
        prestataire = self.env['res.partner'].search([('id', '=', user.partner_id.id)])
        # prestations = self.env['proximas.prestation'].search([('prestataire_id', '=', user.partner_id.id)])
        pec = self.env['proximas.prise.charge'].search([('code_pec', '=', self.code_pec)])
        pec_id = pec.id
        info_assure = pec.assure_id.name
        delai_pec = int(pec.delai_pec)
        validite_pec = int(pec.validite_pec)
        pec_maj = self.env['proximas.pec.maj.wizard']
        # Contrôle de l'existence du code PEC
        if not bool(pec):
            raise ValidationError(_(
                u"Le code que vous avez fourni n'est pas un Code PEC de Prise en charge valide.\n "
                " Pour plus d'informations, veuillez contactez l'administrateur en cas de besoin..!"
                )
            )
        # Contrôle du statut Assuré - assure.state == 'actif'
        elif bool (pec) and (pec.assure_id.state != 'actif'):
            # bool(pec_id) and (pec.state != 'oriente' or pec.state != 'termine'):
            raise ValidationError(_(
                u"PROXIMAS : Contrôle du Statut PEC >> :\n \
                Le code PEC concerné : %s existe bel et bien en tant que prise en charge. Cependant, ne peut faire \
                l'objet d'un traitement à cause du statut non actif de l'assuré: %s. \
                Veuillez contacter au besoin, les administrateurs pour plus détails..."
                ) % (pec.code_pec, info_assure)
            )
        # Contrôle de délai PEC
        elif bool(pec) and (0 < validite_pec < delai_pec):
            # bool(pec_id) and (pec.state != 'oriente' or pec.state != 'termine'):
            raise ValidationError(_(
                u"PROXIMAS : Contrôle du Statut PEC >> : " + str(pec.code_pec) + ' (' + str(info_assure) + ').' +
                "Le code PEC concerné est bien enregistré en tant que prise en charge. Cependant, ne peut faire \
                l'objet d'un traitement à cause de son délai de validité qui a expiré. \
                Veuillez contacter au besoin, les administrateurs pour plus détails..."
                )
            )
        elif bool(pec) and pec.state == 'oriente' and prestataire.categorie_id != 'Pharmacie':
            # Rediriger vers le formulaire de prise en charge pour Prestations CRS
            pec.prestataire_crs_id = prestataire.id
            view_id = self.env.ref('proximas_medical.proximas_pec_form', False).id
            action = {
                'name': 'Mise à jour Prise en charge Assuré (CRS)',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'views': [(view_id, 'form')],
                'res_model': 'proximas.prise.charge',
                'view_id': view_id,
                'res_id': pec_id,
                'type': 'ir.actions.act_window',
                'context': {
                    # 'form_view_ref': 'proximas_medical.prise_charge_view_search',
                    # 'active_ids': pec_id,
                    'default_assure_id': pec.assure_id.id,
                    'default_police_id': pec.assure_id.police_id.id,
                    'default_code_pec': self.code_pec,
                    'default_prestataire_crs_id': prestataire.id,
                    'default_user': user.name,
                    'default_user_id': user.id,
                },
            }
            return action
        else:
            # bool(pec_id) and (pec.state != 'oriente' or pec.state != 'termine'):
            raise ValidationError(_(
                u"PROXIMAS : Contrôle du Statut PEC :\n \
                Le code PEC concerné : %s -%s est bel et bien enregistré en tant que prise en charge. Cependant, \
                vous n'y avez pas accès, parce que cette prise en charge n'a pas été transmise en Orientation. \
                Pour plus d'informations, veuillez contactez les administrateurs..."
                ) % (pec.code_pec, info_assure)
            )

    @api.multi
    def phcie_open_popup(self):
        # Ouverture du formulaire de selfherche prise en charge (dispensation médicament)
        self.ensure_one()
        user_id = self.env.context.get('uid')
        group_id = self.env.context.get('gid')
        user = self.env['res.users'].search([('id', '=', user_id)])
        prestataire = self.env['res.partner'].search([('id', '=', user.partner_id.id)])
        # prestations = self.env['proximas.prestation'].search([('prestataire_id', '=', user.partner_id.id)])
        pec = self.env['proximas.prise.charge'].search([('code_pec', '=', self.code_pec)])
        pec_id = pec.id
        info_assure = pec.assure_id.name
        delai_pec = int(pec.delai_pec)
        validite_pec = int(pec.validite_pec)
        pec_maj = self.env['proximas.pec.maj.wizard']

        # Contrôle de l'existence du code PEC
        if not bool(pec):
            raise ValidationError(_(
                u"L'identifiant que vous avez fourni n'est pas un Code PEC de Prise en charge valide.\n \
                Pour plus d'informations, veuillez contactez l'administrateur en cas de besoin..!"
                )
            )
        # Contrôle du statut Assuré - assure.state == 'actif'
        elif bool (pec) and (pec.assure_id.state != 'actif'):
            # bool(pec_id) and (pec.state != 'oriente' or pec.state != 'termine'):
            raise ValidationError(_(
                u"PROXIMAS : Contrôle du Statut PEC >> :\n \
                Le code PEC concerné : %s existe bel et bien en tant que prise en charge. Cependant, ne peut faire \
                l'objet d'un traitement à cause du statut non actif de l'assuré: %s. \
                Veuillez contacter au besoin, les administrateurs pour plus détails..."
                ) % (pec.code_pec, info_assure)
            )
        # Contrôle de délai PEC
        elif bool(pec) and (0 < validite_pec < delai_pec):
            # bool(pec_id) and (pec.state != 'oriente' or pec.state != 'termine'):
            raise ValidationError(_(
                u"PROXIMAS : Contrôle du Statut PEC >> : " + str(pec.code_pec) + ' (' + str(info_assure) + ').\n' +
                "Le code PEC concerné est bien enregistré en tant que prise en charge. Cependant, ne peut faire \
                l'objet d'un traitement à cause de son délai de validité qui a expiré.\n \
                Veuillez contacter au besoin, les administrateurs pour plus détails..."
            )
            )
        elif bool(pec_id) and pec.state == 'dispense':
            # Rediriger vers le formulaire de prise en charge pour Dispensation Médicaments
            pec.prestataire_phcie_id = prestataire.id
            view_id = self.env.ref('proximas_medical.proximas_pec_form', False).id
            action = {
                'name': 'Mise à jour Prise en charge Assuré (Pharmacie)',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'views': [(view_id, 'form')],
                'res_model': 'proximas.prise.charge',
                'view_id': view_id,
                'res_id': pec_id,
                'type': 'ir.actions.act_window',
                'context': {
                    # 'form_view_ref': 'proximas_medical.prise_charge_view_search',
                    # 'active_ids': pec_id,
                    'default_assure_id': pec.assure_id.id,
                    'default_police_id': pec.assure_id.police_id.id,
                    'default_code_pec': self.code_pec,
                    'default_prestataire_phcie_id': prestataire.id,
                    'default_user': user.name,
                    'default_user_id': user.id,
                },
            }
            return action
        else:
            # bool(pec_id) and (pec.state != 'oriente' or pec.state != 'termine'):
            raise ValidationError(_(
                u"PROXIMAS : Contrôle du Statut PEC :\n \
                Le code PEC concerné : %s -%s est bel et bien enregistré en tant que prise en charge. Cependant, \
                vous n'y avez pas accès, parce que cette prise en charge n'a pas été transmise en Dipensation. \
                Pour plus d'informations, veuillez contactez les administrateurs..."
                ) % (pec.code_pec, info_assure)
            )


class DetailsPec(models.Model):
    # _inherit = ['mail.thread']
    _name = 'proximas.details.pec'
    _description = 'Details Prise en Charge'
    _order = 'date_execution desc'

    # name = fields.Char()
    sequence = fields.Integer(
        string="Sequence"
    )
    pec_id = fields.Many2one(
        comodel_name="proximas.prise.charge",
        string="ID. Prise en charge",
        ondelete='restrict',
    )
    rfm_id = fields.Many2one(
        comodel_name="proximas.remboursement.pec",
        string="ID. Remb. frais médicaux",
        ondelete='restrict',
    )
    date_saisie_rfm = fields.Datetime (
        string="Date Emission Facture",
        related='rfm_id.date_saisie',
        # store=True,
    )
    facture_id = fields.Many2one (
        comodel_name="proximas.facture",
        string="Réf. Facture",
        ondelete='set null',
    )
    date_emission = fields.Date (
        string="Date Emission Facture",
        related='facture_id.date_emission',
        # store=True,
    )
    date_execution = fields.Date(
        string="Date Exécution",
        # default=fields.Date.today(),
        required=False,
        help='Entrez la date d\'éxécution de l\'acte médical',
    )
    date_demande = fields.Date(
        string="Date Demande",
        # default=fields.Date.today(),
        required=False,
        help='Entrez la date de demande de la prestation médicale',
    )
    prestation_cro_id = fields.Many2one(
        comodel_name="proximas.prestation",
        string="Prestation médicale CRO",
        required=False,
        domain=[
            ('arret_prestation', '=', False),
        ],
    )
    prestation_crs_id = fields.Many2one(
        comodel_name="proximas.prestation",
        string="Prestation CRS ",
        required=False,
        domain=[
            ('arret_prestation', '=', False),
        ],
    )
    prestation_demande_id = fields.Many2one(
        comodel_name="proximas.code.prestation",
        string="Prestation demandée",
        help="Indiquer la prestation médicale ou paramédicale demandée.",
    )
    prestation_rembourse_id = fields.Many2one(
        comodel_name="proximas.prestation",
        string="Prestation médicale Rembourse.",
        required=False,
        domain=[
            ('arret_prestation', '=', False),
        ]
    )
    prestation_id = fields.Many2one(
        comodel_name="proximas.prestation",
        string="Prestation médicale",
        compute='_check_prestation_id',
        #index=True,
        store=True,
    )
    pool_medical_id = fields.Many2one(
        comodel_name="proximas.pool.medical",
        string="Médecin CRO",
        # store=True,
    )
    pool_medical = fields.Many2one (
        comodel_name="proximas.pool.medical",
        string="Médecin Pool Médical",
        compute='_get_pool_medical',
    )
    medecin_id = fields.Many2one(
        comodel_name="proximas.medecin",
        string="Médecin traitant",
        compute='_get_medecin_id',
        store=True,
    )
    medecin_traitant = fields.Char(
        string="Medecin traitant",
        related='medecin_id.full_name',
        required=False,
    )
    pool_medical_crs_id = fields.Many2one(
        comodel_name="proximas.pool.medical",
        string="Médecin Exécutant",
        help='Médecin dans le pool médical du prestataire, ayant exécuté la prestation médicale dans le cdre d\'une \
         orientation...',
        required=False,
    )
    produit_phcie_id = fields.Many2one(
        comodel_name="proximas.produit.pharmacie",
        string="Médicament Prescrit",
        domain=[
            ('arret_medicament', '=', False),
        ]
    )
    produit_phcie = fields.Char(
        string="Médicament Prescrit",
        compute='_get_produit_phcie',
        required=False,
    )
    substitut_phcie_id = fields.Many2one(
        comodel_name="proximas.produit.pharmacie",
        string="Substitution Médicament",
        domain=[
            ('arret_medicament', '=', False),
        ]
    )
    substitut_phcie = fields.Char(
        string="Substitut Prescrit",
        compute='_get_produit_phcie',
        required=False,
    )
    medicament = fields.Char(
        string="Médicament",
        compute='_get_produit_phcie',
        required=False,
        help="Médicament dispensé: produit pharmacie prescrit ou substitut",
    )
    details_prestation = fields.Char(
        string="Prestation médicale",
        compute='_get_details_prestation',
        required=False,
    )
    # Champs relatifs Médicaments (Produit Pharmacie)
    prix_indicatif_produit = fields.Float(
        string="Prix indicatif Produit",
        digits=(6, 0),
        related='produit_phcie_id.prix_indicatif',
        default=0,
    )
    marge_produit = fields.Float(
        string="Marge sur Produit",
        digits=(6, 0),
        related='produit_phcie_id.marge_medicament',
        default=0,
    )
    prix_indicatif_substitut = fields.Float(
        string="Prix indicatif Substitut",
        digits=(6, 0),
        related='substitut_phcie_id.prix_indicatif',
        default=0,
    )
    marge_substitut = fields.Float(
        string="Marge sur Substitut",
        digits=(6, 0),
        related='substitut_phcie_id.marge_medicament',
        default=0,
    )
    marge_medicament_police = fields.Float(
        string='Marge/Produit Phcie.',
        help="Marge tolérée sur le coût des produits pharmaceutiques",
        digits=(5, 0),
        related='pec_id.marge_medicament',
        readonly=True,
    )
    marge_medicament_produit = fields.Float (
        string='Marge/Produit Phcie.',
        help="Marge tolérée sur le coût du médicament",
        digits=(6, 0),
        related='produit_phcie_id.marge_medicament',
        readonly=True,
    )
    marge_medicament_substitut = fields.Float(
        string='Marge/Produit Phcie.',
        help="Marge tolérée sur le coût du médicament",
        digits=(6, 0),
        related='substitut_phcie_id.marge_medicament',
        readonly=True,
    )
    arret_produit = fields.Boolean(
        string="Produit en arrêt?",
        related='produit_phcie_id.arret_medicament',
        readonly=True,
    )
    arret_substitut = fields.Boolean(
        string="Substitut en arrêt?",
        related='substitut_phcie_id.arret_medicament',
        readonly=True,
    )
    # Gestion de délai à observer pour dispenser le même médicament
    delai_attente_produit = fields.Integer(
        string="Délai d'attente (nbre. jours) Produit",
        related='produit_phcie_id.delai_attente',
        default=0,
        readonly=True,
        help="Nombre de jours à observer avant de dispenser le même médicament"
    )
    delai_attente_substitut = fields.Integer(
        string="Délai d'attente (nbre. jours) Substitut",
        related='substitut_phcie_id.delai_attente',
        default=0,
        readonly=True,
        help="Nombre de jours à observer avant de dispenser le même médicament"
    )
    zone_couverte = fields.Boolean(
        string="Zone Couverte?",
        default=True,
        help="Cocher pour indiquer que le prestataire est situé dans une zone couverte par le réseau de soins."
    )
    prestataire_public = fields.Boolean(
        string="Ets. Public?",
        default=True,
        help="Cocher pour indiquer que le prestataire de soins est de type public."
    )
    cout_unit = fields.Float(
        string="Coût unitaire",
        digits=(6, 0),
    )
    cout_unite = fields.Float(
        string="Coût unitaire",
        # compute='_check_cout_unitaire',
        digits=(6, 0),
        default=0,
    )
    quantite = fields.Integer(
        string="Qté. demandée",
        default=0,
        help="Indiquer la quantité demandée"
    )
    mt_paye_assure = fields.Float(
        string="Montant Payé (assuré)",
        digits=(6, 0),
        # default='_check_ticket_exigible()',
        required=False,
    )
    # mt_paye_saisie = fields.Float(
    #     string="Montant Encaissé (assuré)",
    #     digits=(6, 0),
    #     required=False,
    # )

    # Détails pour la partie Pharmacie
    # produit_id = fields.Many2one(comodel_name="", string="Produit", required=False, )
    # prestataire_id = fields.Many2one(comodel_name="proximas.prestataire", string="Prestataire", required=False,
    #                                 domain=[('category_id', 'ilike', 'pharmacie')])
    posologie = fields.Char(
        string="Posologie",
        size=128,
        required=False,
    )

    quantite_livre = fields.Integer(
        string="Qté. fournie",
        default=0,
        help="Indiquer la quantité réelle fournie",
        required=False,
    )
    mt_exclusion = fields.Float(
        string="Mt. Exclusion",
        digits=(6, 0),
        default=0,
        help="Indiquer s'il y a lieu le montant à exclure."
    )
    motif_exclusion = fields.Text(
        string="Motif Exclusion",
        help='Motif d\'exclusion (requis si un montant à exclure est fourni.)',
    )
    # Champs relatif Assuré
    num_pec = fields.Char(
        string="Code PEC",
        related='pec_id.code_pec',
        store=True,
        required=False,
    )
    num_rfm = fields.Char(
        string="Code RFM",
        related='rfm_id.code_rfm',
        store=True,
        required=False,
    )
    assure = fields.Many2one(
        # comodel_name="proximas.assure",
        string="Identification Assuré",
        related='pec_id.assure_id',
        store=True,
        readonly=True,
    )
    code_id_rfm = fields.Char(
        string="Code ID. Patient",
        required=False,
        help="Entrez lz code identifiant (ID.) de l'assuré concerné."
    )
    assure_id = fields.Many2one(
        comodel_name="proximas.assure",
        string="Assuré",
        compute='_get_assure_id',
        store=True,
    )
    code_id = fields.Char(
        string="Code ID.",
        related="assure_id.code_id",
        readonly=True,
    )
    nom = fields.Char(
        string="Nom",
        related='assure_id.nom',
        required=False,
        readonly=True,
    )
    prenoms = fields.Char(
        string="Prénoms",
        related='assure_id.prenoms',
        required=False,
        readonly=True,
    )
    name = fields.Char(
        string="Noms & Prénoms",
        related='assure_id.display_name',
        required=False,
        readonly=True,
    )
    statut_familial = fields.Selection(
        string="Statut Familial",
        related='assure_id.statut_familial',
        store=True,
        readonly=True,
    )
    genre = fields.Selection(
        string="Genre",
        related='assure_id.genre',
        store=True,
        readonly=True,
    )
    date_naissance = fields.Date(
        string="Date Naissance",
        related="assure_id.date_naissance",
        # store=True,
        readonly=True,
    )
    age = fields.Char(
        string="Age",
        related='assure_id.age',
        # store=True,
        required=False,
        readonly=True,
    )
    tranche_age = fields.Selection(
        string="Tranche d'âge",
        related='assure_id.tranche_age',
    )
    age_entier = fields.Integer(
        string='Age assuré',
        related='assure_id.age_entier',
    )
    age_details = fields.Char(
        string="Age",
        related="assure_id.age_details",
        readonly=True,
    )
    date_activation = fields.Date(
        string="Date Activation",
        related="assure_id.date_activation",
        readonly=True,
    )
    image = fields.Binary(
        string="Photo",
        related="assure_id.image",
        readonly=True,
    )
    contrat_id = fields.Many2one(
        # comodel_name="proximas.contrat",
        string="Contrat Assuré",
        related='assure_id.contrat_id',
        store=True,
    )
    groupe_id = fields.Many2one(
        # comodel_name="promimas.groupe",
        string="Groupe/Organe",
        related='contrat_id.groupe_id',
        store=True,
    )
    localite_id = fields.Many2one (
        # comodel_name="proximas.localite",
        string="Localité",
        related='assure_id.localite_id',
        store=True,
    )
    zone_id = fields.Many2one (
        # comodel_name="proximas.zone",
        string="Localité",
        related='localite_id.zone_id',
        store=True,
    )
    num_contrat = fields.Char(
        string="Num. Contrat",
        related='contrat_id.num_contrat',
        #store=True,
        readonly=True,
    )
    adherent_id = fields.Many2one(
        # omodel_name="proximas.adherent",
        string="Adhérent",
        related='contrat_id.adherent_id',
        store=True,
        readonly=True,
    )
    adherent = fields.Char(
        string="Adhérent",
        related='adherent_id.name',
        # store=True,
        required=False,
        readonly=True,
    )
    police_id = fields.Many2one(
        comodel_name="proximas.police",
        string="Police Assuré",
        related='contrat_id.police_id',
        store=True,
        required=False,
        readonly=True,
    )
    police = fields.Char(
        string="PoliCe",
        related='police_id.name',
        required=False,
        readonly=True,
    )
    structure_id = fields.Many2one(
        string="Organisation",
        related='contrat_id.structure_id',
        readonly=True,
    )
    mt_encaisse_cro = fields.Float(
        string="Montant Perçu (Ticket Mod.)",
        digits=(9, 0),
        related='pec_id.mt_encaisse_cro',
        readonly=True,
        help='Montant total perçu de la part de l\'assuré, au titre de règlement du ticket modérateur',
    )
    mt_encaisse_crs = fields.Float(
        string="Montant Perçu (Ticket Mod.)",
        digits=(9, 0),
        related='pec_id.mt_encaisse_crs',
        readonly=True,
        default=0,
        help='Montant total perçu de la part de l\'assuré, au titre de règlement du ticket modérateur',
    )
    mt_encaisse_phcie = fields.Float(
        string="Montant Perçu (Ticket Mod.)",
        digits=(9, 0),
        related='pec_id.mt_encaisse_phcie',
        readonly=True,
        default=0,
        help='Montant total perçu de la part de l\'assuré, au titre de règlement du ticket modérateur',
    )
    # Champs relatifs Prestataire
    prestataire_id = fields.Many2one(
        comodel_name="res.partner",
        related='pec_id.prestataire_id',
        string="Prestataire CRO",
        help='Prestataire avec le statut de Centre de Référence Obligatoire (CRO)',
        required=False,
    )
    prestataire_crs_id = fields.Many2one(
        comodel_name="res.partner",
        related='pec_id.prestataire_crs_id',
        string="Prestataire CRS",
        help='Prestataire avec le statut de Centre de Référence Standard (CRS)',
        required=False,
    )
    prestataire_phcie_id = fields.Many2one(
        comodel_name="res.partner",
        related='pec_id.prestataire_phcie_id',
        string="Prestataire Pharmacie/Officine",
        help='Prestataire avec le statut de Pharmacie (Officine), pour la dispensation de médicaments',
        required=False,
    )
    prestataire_phcie = fields.Char(
        string="Pharmacie",
        related='prestataire_phcie_id.name',
        readonly=True,
    )
    prestataire_rembourse_id = fields.Many2one(
        comodel_name="res.partner",
        related='rfm_id.prestataire_id',
        string="Ets. Non Conventionné ",
        help='Etablissement de soins médicaux non conventionné (Cas de remboursement de frais médicaux).',
        required=False,
    )
    prestataire = fields.Many2one(
        string="Prestataire",
        related='prestation_id.prestataire_id',
        store=True,
        readonly=True,
    )
    # prestataire = fields.Char(
    #     string="Prestataire Soins",
    #     compute='_get_prestataire',
    #     required=False,
    # )

    # prestataire_phcie_1_id = fields.Many2one(
    #     comodel_name="res.partner",
    #     related='pec_id.prestataire_phcie_ 1_id',
    #     string="Prestataire Phcie 1",
    #     required=False,
    # )
    # prestataire_phcie_2_id = fields.Many2one(
    #     comodel_name="res.partner",
    #     related='pec_id.prestataire_phcie_2_id',
    #     string="Prestataire Phcie 2",
    #     required=False,
    # )
    # Champs relatifs Prestation
    code_prestation_id = fields.Many2one(
        comodel_name="proximas.code.prestation",
        string="Prestation",
        related='prestation_id.code_prestation_id',
        readonly=True,
    )
    cout_unitaire = fields.Float(
        comodel_name="proximas.prestation",
        string="Cout Unitaire Prestation",
        digits=(6, 0),
        related='prestation_id.mt_cout_unit',
        readonly=True,
    )
    coefficient = fields.Integer(
        comodel_name="proximas.prestation",
        string="Coeff. Prestation",
        related='prestation_id.coefficient',
        readonly=True,
    )
    code_non_controle = fields.Boolean(
        related='prestation_id.code_non_controle',
        readonly=True,
    )
    forfait_sam = fields.Float(
        comodel_name="proximas.prestation",
        string="Forfait SAM",
        digits=(6, 0),
        related='prestation_id.forfait_sam',
        readonly=True,
    )
    forfait_ticket = fields.Float (
        comodel_name="proximas.prestation",
        string="Forfait Ticket",
        digits=(6, 0),
        related='prestation_id.forfait_ticket',
        readonly=True,
    )
    mt_forfait = fields.Float(
        string="Mt. Forfait",
        default=0,
        digits=(9, 0),
        compute='_calcul_couts_details_pec',
    )
    remise_prestation = fields.Integer(
        string="Taux Remise (%)",
        default=0,
        related='prestation_id.remise',
        readonly=True,
        help='Taux de la remise à appliquer sur la prestation médicale en pourcentage (%)',

    )
    mt_rabais = fields.Float(
        comodel_name="proximas.prestation",
        string="Rabais Prestation",
        digits=(6, 0),
        related='prestation_id.mt_rabais',
        readonly=True,
    )
    code_medical_id = fields.Many2one(
        string="Code Médical",
        # compute='_check_prestation_id',
        related='prestation_id.code_medical_id',
        store=True,
        readonly=True,
    )
    rubrique_id = fields.Many2one(
        string="Rubrique",
        # compute='_check_prestation_id',
        related='code_medical_id.rubrique_id',
        store=True,
        readonly=True,
    )
    ticket_exigible = fields.Boolean(
        string="Ticket Exigible?",
        compute='_calcul_couts_details_pec',
        readonly=True,
    )
    accord_prealable = fields.Boolean(
        string="Soumise à accord?",
        related='prestation_id.accord_prealable',
        # readonly=True,
    )
    accord_prestation_demande = fields.Boolean(
        string="Soumise à accord?",
        related='prestation_demande_id.accord_prealable',
        readonly=True,
    )
    delai_attente_prestation = fields.Integer(
        string="Délai Attente",
        related='prestation_id.delai_attente',
        readonly=True,
    )
    # Champs relatifs Prise.charge (PEC)
    pec_state = fields.Selection(
        string="Etat PEC",
        related='pec_id.state',
        store=True,
        readonly=True,
    )
    accorde = fields.Boolean (
        string="Accord?",
        default=False,
        help='Reservé au Médecin Conseil pour accorder l\'exécution d\'une prestation par orientation',
    )
    non_accorde = fields.Boolean(
        string="Refus?",
        default=False,
        help='Reservé au Médecin Conseil pour refuser l\'exécution d\'une prestation par orientation',
    )
    motif_non_accord = fields.Text(
        string="Motif Rejet Accord",
        halp='Motif(s) de non autorisation de la prestation (Facultatif)',
    )
    info_clinique = fields.Text(
        string="Infos clinique",
        halp='Informations cliniques à communiquer (Facultatif)',
    )
    doc_info_clinique = fields.Binary(
        string="Copie de la demande",
        attachment=True,
        help='Joindre le document justificatif de la demande.',
    )
    doc_filename = fields.Char(
        "Nom fichier joint",
    )
    date_dernier_acte = fields.Date (
        string="Date dernier Acte",
        compute='_check_delai_attente_prestation',
        default=fields.Date.today (),
        help='Date de la dernière fois où le patient a bénéficié de cette prestation.',
    )
    delai_prestation = fields.Integer (
        string="Délai Prestation (En jours)",
        compute='_check_delai_attente_prestation',
        default=0,
        help='Calcul le nombre de jours écoulés entre la dernière prestation liée et aujourd\'hui',
        readonly=True,
    )
    cout_modifiable = fields.Boolean(
        string="Coût Prestation Modifiable?",
        related='prestation_id.cout_modifiable',
        readonly=True,
    )
    arret_prestation = fields.Boolean(
        string="Arrêt de la prestation?",
        related='prestation_id.arret_prestation',
        readonly=True,
    )
    quantite_exige = fields.Boolean(
        string="Quantité exigée?",
        related='prestation_id.quantite_exige',
        readonly=True,
    )
    # Champs calculés à definir ==> computed fields
    quantite_reste = fields.Integer(
        # Phcie Uniquement : Calculer la quantité restante à livrer
        string="Reste à livrer",
        required=False,
        default=0,
        help="Indique la quantité restant à livrer"
    )
    # CHAMPS CALCULES AUTOMATIQUEMENT
    cout_total = fields.Float(
        digits=(6, 0),
        string="Coût Total",
        store=True,
        compute='_calcul_couts_details_pec',
        default=0,
    )
    total_pc = fields.Float(
        digits=(6, 0),
        string="Total PC",
        store=True,
        compute='_calcul_couts_details_pec',
        default=0,
    )
    # cout_total - total_pc
    total_npc = fields.Float(
        string="Total NPC",
        digits=(6, 0),
        compute='_calcul_couts_details_pec',
        store=True,
        default=0,
    )
    taux_couvert = fields.Float(
        string="Taux Couv.(%)",
        digits=(3, 0),
        compute='_calcul_couts_details_pec',
        # default=lambda self: self.police_id.tx_couv_prive_couvert,
    )
    net_tiers_payeur = fields.Float(
        string="Part SAM",
        default=0,
        digits=(9, 0),
        compute='_calcul_couts_details_pec',
        store=True,
    )   # total_pc x taux_couvert
    ticket_moderateur = fields.Float(
        string="Ticket Modérateur",
        default=0,
        digits=(6, 0),
        compute='_calcul_couts_details_pec',
        store=True,
    )   # total_pc - tiers_payeur
    net_prestataire = fields.Float(
        string="S/Total Net Prestataire",
        default=0,
        digits=(9, 0),
        compute='_calcul_couts_details_pec',
        store=True,
    )
    mt_remboursement = fields.Float(
        string="S/Total Net Remboursement",
        compute='_calcul_couts_details_pec',
        default=0,
        digits=(6, 0),
        store=True,
    )   # = net_tiers_payeur
    debit_ticket = fields.Float(
        string="Débit Ticket",
        digits=(6, 0),
        compute='_calcul_couts_details_pec',
        default=0,
        store=True,
    )   # = ticket_moderateur - paye_assure
    mt_plafond = fields.Float (
        string="Mt. PLafond",
        digits=(6, 0),
        compute='_calcul_couts_details_pec',
        default=0,
    )
    net_a_payer = fields.Float (
        string="Net A Payer",
        digits=(6, 0),
        compute='_compute_net_a_payer',
        default=0,
        store=True
    )
    nbre_produit_phcie = fields.Integer(
        string="Nbre. Produits Pharmacie",
        compute='_check_nbre_prestations',
        default=0,
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    current_user = fields.Many2one(
        comodel_name="res.users",
        string="Utilisateur en cours",
        compute='_get_current_user',
        required=False,
    )
    user_prestataire = fields.Char(
        string="Prestataire (User)",
        compute='_get_current_user',
        required=False,
    )
    user_prestation = fields.Boolean(
        string="Utitlisateur/Prestation?",
        compute='_get_current_user',
        # store=True,
        help='Défini si l\'utilisateur courant est le prestataire exécutant de la prise en charge?',
    )
    prestataire_name = fields.Char(
        string="Prestataire (Dénomination)",
        compute='_get_current_user',
        required=False,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Créee Par",
        # default=lambda self: self.env.user,
        required=False,
    )
    is_valide = fields.Boolean(
        string="Valide?",
        default=False,
        help="Indique si la ligne de détails de la prise en charge est validée = cochée ou non = non cochée.",
    )
    motif_validation = fields.Text(
        string="Motif de non validation",
        required=False,
    )
    # Champs relatifs à l'exercice
    exercice_id = fields.Many2one(
        comodel_name="proximas.exercice",
        string="Exercice SAM",
        compute='_get_exo_sam',
        # store=True,
    )
    date_debut_exo = fields.Date(
        string="Date début Exo.",
        related='exercice_id.date_debut',
        readonly=True,
    )
    date_fin_exo = fields.Date(
        string="Date fin Exo.",
        related='exercice_id.date_fin',
        readonly=True,
    )
    cloture_exo = fields.Boolean(
        string="Cloturé?",
        related='exercice_id.cloture',
        readonly=True,
    )
    en_cours_exo = fields.Boolean(
        string="En Cours?",
        related='exercice_id.en_cours',
        readonly=True,
    )
    # exo_id = fields.Integer(
    #     string="Exo. SAM",
    #     related='exercice_id.id',
    #     store=True,
    # )
    exo_name = fields.Char(
        string="Exercice",
        related='exercice_id.name',
        readonly=True,
        store=True,
    )
    res_company_id = fields.Many2one(
        string="Structure",
        related='exercice_id.res_company_id',
        readonly=True,
    )

    # @api.multi
    # def write(self, values):
    #     user_id = self.env.context.get('uid')
    #     group_id = self.env.context.get ('gid')
    #     user = self.env['res.users'].search ([('id', '=', user_id)])
    #     prestataire = self.env['res.partner'].search ([('id', '=', user.partner_id.id)])
    #     self = self.with_context(prestataire_id=prestataire.id)
    #     res = super(proximas.prise.charge, self).write(values)
    #     # print "Get Context value", self._context.get('key')
    #     return res

    @api.multi
    def action_valider(self):
        for rec in self:
            rec.is_valide = not rec.is_valide
        return True

    @api.model
    def do_clear_valide(self):
        valides = self.search([('is_valide', '=', True)])
        valides.write({'is_valide': False})
        return True

    @api.multi
    def action_accorder(self):
        for rec in self:
            rec.accorde = not rec.accorde
        return True

    @api.multi
    def action_non_accorder(self):
        for rec in self:
            rec.non_accorde = not rec.non_accorde
        return True

    @api.onchange('accorde', 'non_accorde')
    def _check_action_accorder(self):
        for rec in self:
            if bool (rec.accorde) and bool (rec.non_accorde):
                warning = {
                    'title': _ (u'Proximaas : Contrôle de Règles de Gestion.'),
                    'message': _ (u"Attention! Vous ne pouvez pas à la fois, autoriser et rejeter la demande  \
                     d'exécution de la prestation : %s. Pour plus d'informations, veuillez contactez l'administrateur..."
                                  ) % rec.prestation_demande_id.name
                }
                return {'warning': warning}
            elif bool (rec.non_accorde) and not bool (rec.motif_non_accord):
                warning = {
                    'title': _ (u'Proximaas : Contrôle de Règles de Gestion.'),
                    'message': _ (u"Attention! Vous devez absolument motiver le rejet (refus) de l'exécution de la\
                         prestation : %s. En cas de refus, le champ motif de refus doit impérativement être renseigné.\
                          Pour plus d'informations, veuillez contactez l'administrateur...")
                               % rec.prestation_demande_id.name
                }
                return {'warning': warning}

    @api.constrains('accorde', 'non_accorde')
    def _validate_action_accorder(self):
        for rec in self:
            if bool(rec.accorde) and bool(rec.non_accorde):
                raise ValidationError(
                    _ (u"Attention! Vous ne pouvez pas à la fois, autoriser et rejeter la demande  \
                        d'exécution de la prestation : %s. Pour plus d'informations, \
                        veuillez contactez l'administrateur..."
                       ) % rec.prestation_demande_id.name
                )
            elif bool(rec.non_accorde) and not bool(rec.motif_non_accord):
                raise ValidationError(
                    _ (u"Attention! Vous devez absolument motiver le rejet (refus) de l'exécution de la\
                        la prestation : %s.En cas de refus, le champ motif de refus doit impérativement \
                        être renseigné. Pour plus d'informations, veuillez contactez l'administrateur..."
                       ) % rec.prestation_demande_id.name
                )

    @api.multi
    def _get_details_prestation(self):
        for rec_id in self:
            if bool(rec_id.produit_phcie):
                rec_id.details_prestation = rec_id.medicament
            else:
                prestation = rec_id.code_prestation_id.name
                rec_id.details_prestation = prestation

    @api.multi
    @api.depends('pool_medical_id', 'pool_medical_crs_id')
    def _get_pool_medical(self):
        for rec in self:
            if bool(rec.pool_medical_crs_id):
                pool_medical_id = rec.pool_medical_crs_id.id
                rec.pool_medical = pool_medical_id
            else:
                pool_medical_id = rec.pec_id.pool_medical_id.id
                rec.pool_medical = pool_medical_id


    # @api.one
    @api.depends('pool_medical')
    def _get_medecin_id(self):
        for rec in self:
            medecin_id = rec.pool_medical.medecin_id.id
            rec.medecin_id = medecin_id


    # @api.multi
    @api.onchange('date_execution', 'date_demande')
    def _check_date_details_pec(self):
        for rec in self:
            now = datetime.now()
            date_execution = fields.Datetime.from_string (rec.date_execution)
            date_demande = fields.Datetime.from_string (rec.date_demande)
            if bool(date_execution) and date_execution > now:
                # date = rec.date_execution.strftime('%d-%m-%Y')
                date = datetime.strftime(date_execution, '%d-%m-%Y')
                warning = {
                    'title': _(u'Proximaas : Contrôle de Règles de Gestion.'),
                    'message': _(u"Vous avez fourni des informations sur la date d'exécution de la prestation: %s. \
                                  Cependant, cette date est postérieure à la date du jour. La prestation ne peut être \
                                  antidatée. Veuillez corriger la date d'exécution de la prestation. Pour plus \
                                  d'informations, veuillez contactez l'administrateur...") % date
                }
                return {'warning': warning}
            if bool(date_demande) and date_demande > now:
                # date = rec.date_execution.strftime('%d-%m-%Y')
                date = datetime.strftime (date_demande, '%d-%m-%Y')
                warning = {
                    'title': _(u'Proximaas : Contrôle de Règles de Gestion.'),
                    'message': _(u"Vous avez fourni des informations sur la date de demande de la prestation: %s. \
                                  Cependant, cette date est postérieure à la date du jour. La prestation ne peut être \
                                  antidatée. Veuillez corriger la date d'exécution de la prestation. Pour plus \
                                  d'informations, veuillez contactez l'administrateur...") % date
                }
                return {'warning': warning}

    # @api.one
    @api.constrains('date_execution', 'date_demande')
    def _validate_date_details_pec(self):
        for rec_id in self:
            now = datetime.now()
            date_execution = fields.Datetime.from_string(rec_id.date_execution)
            date_demande = fields.Datetime.from_string(rec_id.date_demande)
            if bool(date_execution) and date_execution > now:
                date = datetime.strftime(date_execution, '%d-%m-%Y')
                raise ValidationError(_(
                    u"Proximaas : Contrôle de Règles de Gestion.\n\
                    Vous avez fourni des informations sur la date d'exécution de la prestation: %s.\
                    Cependant, cette date est postérieure à la date du jour. La prestation ne peut être \
                    antidatée. Veuillez corriger la date d'exécution de la prestation. Pour plus d'informations,\
                    veuillez contactez l'administrateur..."
                    ) % date
                )
            if bool(date_demande) and date_demande > now:
                date = datetime.strftime(date_demande, '%d-%m-%Y')
                raise ValidationError(_(
                    u"Proximaas : Contrôle de Règles de Gestion.\n\
                    Vous avez fourni des informations sur la date de demande de la prestation: %s.\
                    Cependant, cette date est postérieure à la date du jour. La prestation ne peut être \
                    antidatée. Veuillez corriger la date d'exécution de la prestation. Pour plus d'informations,\
                    veuillez contactez l'administrateur..."
                    ) % date
                )

    @api.multi
    @api.onchange('produit_phcie_id', 'substitut_phcie_id', 'prestation_cro_id', 'prestation_crs_id',
                   'prestation_demande_id')
    # @api.depends('produit_phcie_id')
    def _check_nbre_prestations(self):
        for rec in self:
            if bool(rec.produit_phcie_id):
                nbre_produit_phcie = self.env['proximas.details.pec'].search_count([
                    ('pec_id', '=', rec.pec_id.id),
                    ('produit_phcie_id', '=', rec.produit_phcie_id.id),
                ])
                rec.nbre_produit_phcie = int(nbre_produit_phcie)
                if int(nbre_produit_phcie) >= 1:
                    # produit_phcie = '%s %s %s' %(rec.produit_phcie_id.name, rec.produit_phcie_id.forme_galenique_id.name or '',
                    #        rec.produit_phcie_id.dosage)
                    return {'value': {},
                            'warning': {'title': u'Proximaas : Contrôle de Règles de Gestion.',
                                        'message': u"Il semble que le médicament: => (%s) ait déjà été prescrit pour \
                                         cette prise en charge. Par conséquent, il ne peut y avoir plus d'une fois le même \
                                         médicament prescrit sur la même prise en charge. Vérifiez s'il n'y pas de doublon \
                                         ou contactez l'administrateur." % rec.produit_phcie
                                        }
                            }
            elif bool(rec.substitut_phcie_id):
                nbre_substitut_phcie = self.search_count([
                    ('pec_id', '=', rec.pec_id.id),
                    ('assure', '=', rec.assure.id),
                    '|', ('substitut_phcie_id', '=', rec.substitut_phcie_id.id),
                    ('produit_phcie_id', '=', rec.substitut_phcie_id.id),
                ])
                if int (nbre_substitut_phcie) >= 1:
                    substitut_phcie = rec.substitut_phcie
                    return {'value': {},
                            'warning': {'title': u'Proximaas : Contrôle de Règles de Gestion.',
                                        'message': u"Il semble que le médicament: => (%s) ait déjà été prescrit pour \
                                        cette prise en charge. Par conséquent, il ne peut y avoir plus d'une fois le même \
                                        médicament prescrit sur la même prise en charge. Vérifiez s'il n'y pas de doublon \
                                        ou contactez l'administrateur." % substitut_phcie
                                        }
                            }
            elif bool(rec.prestation_id):
                nbre_prestation = self.search_count ([
                    ('pec_id', '=', rec.pec_id.id),
                    ('assure', '=', rec.assure.id),
                    ('produit_phcie_id', '=', None),
                    ('prestation_id', '=', rec.prestation_id.id),
                ])
                if int (nbre_prestation) >= 1:
                    return {'value': {},
                            'warning': {'title': u'Proximaas : Contrôle de Règles de Gestion.',
                                        'message': u"Il semble que la prestation : (%s) ait déjà été fournie pour cette \
                                        prise en charge. Par conséquent, il ne peut y avoir plus d'une fois la même \
                                        prestation offerte sur la même prise en charge. Vérifiez s'il n'y pas de doublon \
                                        ou contactez l'administrateur." % rec.prestation_id.name
                                        }
                            }

    # @api.one
    @api.constrains('prestation_cro_id', 'prestation_crs_id', 'prestation_demande_id', 'produit_phcie_id',
                     'substitut_phcie_id')
    def _validate_nbre_prestations(self):
        for rec in self:
            if bool (rec.produit_phcie_id):
                nbre_produit_phcie = self.search_count ([
                    ('pec_id', '=', rec.pec_id.id),
                    ('produit_phcie_id', '=', rec.produit_phcie_id.id),
                ])
                if int (nbre_produit_phcie) > 1:
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n\
                        Il semble que le produit (médicament): (%s) ait déjà été prescrit pour cette prise en charge.\
                        Par conséquent, il ne peut y avoir plus d'une fois le même médicament prescrit sur la \
                        même prise en charge: (%s). Vérifiez s'il n'y pas de doublon ou contactez l'administrateur."
                        ) % (rec.produit_phcie, rec.pec_id.name)
                    )
            elif bool (rec.substitut_phcie_id):
                nbre_substitut_phcie = self.search_count([
                    ('pec_id', '=', rec.pec_id.id),
                    ('substitut_phcie_id', '=', rec.substitut_phcie_id.id),
                ])
                if nbre_substitut_phcie > 1:
                    raise ValidationError (_ (
                        "Proximaas : Contrôle de Règles de Gestion.\n\
                        Il semble que le produit (médicament): (%s) ait déjà été prescrit pour cette prise en charge.\
                        Par conséquent, il ne peut y avoir plus d'une fois le même médicament prescrit sur la \
                        même prise en charge : (%s). Vérifiez s'il n'y pas de doublon ou contactez l'administrateur."
                        ) % (rec.substitut_phcie, rec.pec_id.name)
                    )
            elif bool (rec.prestation_demande_id):
                nbre_prestation_demande = self.search_count ([
                    ('pec_id', '=', rec.pec_id.id),
                    ('prestation_demande_id', '=', rec.prestation_demande_id.id),
                ])
                if int (nbre_prestation_demande) > 1:
                    raise ValidationError (_ (
                        "Proximaas : Contrôle de Règles de Gestion: Demande Centre d'orientation (CRS).\n\
                        Il semble que la prestation : (%s) ait déjà été fournie pour cette prise en charge.\
                        Par conséquent, il ne peut y avoir plus d'une fois la même prestation offerte sur une \
                        même prise en charge : (%s). Vérifiez s'il n'y pas de doublon ou contactez l'administrateur."
                        ) % (rec.prestation_demande_id.name, rec.pec_id.name)
                    )
            elif bool (rec.prestation_cro_id):
                nbre_prestation_cro = self.search_count ([
                    ('pec_id', '=', rec.pec_id.id),
                    ('prestation_cro_id', '=', rec.prestation_cro_id.id),
                ])
                if int (nbre_prestation_cro) > 1:
                    raise ValidationError (_ (
                        "Proximaas : Contrôle de Règles de Gestion.\n\
                        Il semble que la prestation: (%s) ait déjà été fournie pour cette prise en charge.\
                        Par conséquent, il ne peut y avoir plus d'une fois la même prestation offerte sur une \
                        même prise en charge : (%s). Vérifiez s'il n'y pas de doublon ou contactez l'administrateur."
                        ) % (rec.prestation_cro_id.name, rec.pec_id.name)
                    )

    # @api.one
    @api.depends('produit_phcie_id', 'substitut_phcie_id')
    def _get_produit_phcie(self):
        for rec in self:
            if bool(rec.substitut_phcie_id):
                rec.substitut_phcie = '%s - %s %s' % (rec.substitut_phcie_id.name,
                                                   rec.produit_phcie_id.forme_galenique_id.name or '',
                                                   rec.substitut_phcie_id.dosage or '')
                rec.medicament = rec.substitut_phcie
            elif bool(rec.produit_phcie_id):
                rec.produit_phcie = '%s - %s %s' % (rec.produit_phcie_id.name,
                                                 rec.produit_phcie_id.forme_galenique_id.name or '',
                                                 rec.produit_phcie_id.dosage or '')
                rec.medicament = rec.produit_phcie


    @api.multi
    def _get_current_user(self):
        for rec in self:
            user_id = self.env.context.get('uid')
            group_id = self.env.context.get('gid')
            user = self.env['res.users'].search([('id', '=', user_id)])
            prestataire = self.env['res.partner'].search([('id', '=', user.partner_id.id)])
            rec.current_user = user_id
            rec.user_prestataire = prestataire.name
            prestataire_executant = rec.prestataire.name
            rec.prestataire_name = prestataire_executant
            if rec.prestataire_name == rec.user_prestataire:
                rec.user_prestation = True

    # TRAITEMENT DES  ACCORDS PREALABLES SUR PRESTATIONS

    # @api.multi
    @api.onchange('prestation_demande_id')
    @api.depends('prestation_demande_id')
    # @api.onchange('prestation_demande_id')
    def send_accord_pec_mail(self):
        # self.ensure_one()
        for rec in self:
            if bool(rec.accord_prealable) and not bool (rec.accorde):
                # Find the e-mail template
                template = rec.env.ref ('proximas_medical.accord_pec_mail_template')
                # You can also find the e-mail template like this:
                # template = rec.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

                # Send out the e-mail template to the user
                rec.env['mail.template'].browse (template.id).send_mail (rec.id)
                action = {
                    'warning': {
                        'title': _(u'Proximaas : Contrôle de Règles de Gestion.'),
                        'message': _(u"La prestation: %s est soumise à l'accord préalable du médecin conseil. \
                                    A cet effet, il faudra impérativement l'autorisation expresse du médecin avant \
                                    l'exécution de la prestation concernée. Une notification a été envoyée au médecin \
                                    pour validation. Pour plus d'informations, veuillez contactez l'administrateur..."
                                    ) % rec.prestation_id.name
                    },
                }
                return action

    # @api.multi
    @api.onchange('date_demande', 'prestation_id', 'date_execution', 'pool_medical_crs_id')
    def _check_accord_prealable(self):
        for rec in self:
            if bool(rec.accord_prealable):
                if not bool(rec.accorde) and rec.pec_state == 'cours':
                    action = {
                        'warning': {
                            'title': _(u'Proximaas : Contrôle de Règles de Gestion.'),
                            'message': _(u"La prestation: %s est soumise à l'accord préalable du médecin conseil. \
                                         A cet effet, il faudra impérativement l'autorisation expresse du médecin avant\
                                         l'exécution de la prestation concernée. Une notification est envoyée au médecin\
                                         pour validation. Pour plus d'informations, veuillez contactez \
                                         l'administrateur."
                                        ) % rec.prestation_id.name
                        },
                    }
                    return action

    @api.onchange('prestation_crs_id',)
    def _warning_crs_prestation(self):
        for rec in self:
            if bool(rec.prestation_crs_id) and not bool(rec.prestation_demande_id):
                action = {
                    'warning': {
                        'title': _ (u'Proximaas : Contrôle de Règles de Gestion.'),
                        'message': _ (u"La prestation: %s que vous allez fournir est soumise à la validation  \
                                     du médecin conseil. \n A cet effet, il faudra impérativement l'autorisation \
                                     expresse de celui-ci. Sans cela, la prestation concernée ne figurera pas dans \
                                     votre facture. Pour plus d'informations, veuillez contactez l'administrateur."
                                      ) % rec.prestation_id.name
                    },
                }
                return action

    @api.constrains('accord_prealable')
    def _validate_accord_prealable(self):
        for rec_id in self:
            if bool(rec_id.accord_prealable):
                if not bool(rec_id.accorde) and rec_id.pec_state != 'cours':
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n\
                        La prestation: %s est soumise à l'accord préalable du médecin conseil. A cet effet, il faudra \
                        attendre l'autorisation expresse de ce dernier avant l'exécution de la prestation concernée. \
                        Une notification est envoyée au médecin pour validation. Pour plus d'informations, veuillez \
                        contactez l'administrateur..."
                        ) % rec_id.prestation_id.name
                    )

    # IDENTIFICATION DES PRESTATIONS FOURNIES
    # @api.one
    @api.depends('prestation_demande_id', 'produit_phcie_id', 'substitut_phcie_id', 'prestation_cro_id', 'code_id_rfm',
                 'prestation_crs_id', 'pool_medical_crs_id', 'prestation_rembourse_id', 'prestataire_rembourse_id')
    def _check_prestation_id(self):
        # self.ensure_one()
        for rec in self:
            if bool(rec.prestation_crs_id):
                # Récupérer la prestation médicale du CRS
                rec.prestation_id = rec.prestation_crs_id.id
            elif bool (rec.prestation_cro_id):
                # Récupérer la prestation médicale du CRO
                rec.prestation_id = rec.prestation_cro_id.id

            elif bool (rec.prestation_demande_id) and bool (rec.prestataire_crs_id) and bool (
                    rec.pool_medical_crs_id):
                # Récupérer la prestation médicale demandée du CRS
                code_prestation_id = rec.prestation_demande_id.id
                prestataire_id = rec.prestataire_crs_id.id
                prestation = self.env['proximas.prestation'].search (
                    [
                        ('code_prestation_id', '=', code_prestation_id),
                        ('prestataire_id', '=', prestataire_id)
                    ]
                )
                if prestation:
                    rec.prestation_id = prestation.id
                    rec.prestation_crs_id = prestation.id

            # REMBOURSEMENT - PHARMACIE
            elif bool (rec.code_id_rfm) and bool (rec.prestataire_rembourse_id) and bool (rec.produit_phcie_id):
                # Récupérer la prestation médicale pour la pharmacie (Dispensation Médicaments)
                pharmacie_rembourse_id = rec.prestataire_rembourse_id.id
                if bool (pharmacie_rembourse_id):
                    prestation = self.env['proximas.prestation'].search (
                        [
                            ('prestataire_id', '=', pharmacie_rembourse_id),
                            ('rubrique', '=', 'PHARMACIE')
                        ]
                    )
                    if bool (prestation):
                        # rec.ensure_one()
                        rec.prestation_id = prestation.id
            # Cas de remboursement de frais médicaux
            elif bool (rec.code_id_rfm) and bool (rec.prestation_rembourse_id):
                # Récupérer le prestataire vde soins et la prestation médicale concernée
                rec.prestation_id = rec.prestation_rembourse_id.id
            # PHARMACIE PEC
            elif (bool (rec.prestataire_phcie_id) or bool (rec.produit_phcie_id)) or bool (
                    rec.substitut_phcie_id) and rec.date_execution:
                # Récupérer la prestation médicale pour la pharmacie (Dispensation Médicaments)
                pharmacie_id = rec.prestataire_phcie_id.id
                if bool (pharmacie_id):
                    pharmacie = rec.prestataire_phcie_id.name
                    prestation = self.env['proximas.prestation'].search (
                        [
                            ('prestataire_id', '=', pharmacie_id),
                            ('rubrique', 'ilike', 'PHARMACIE')
                        ]
                    )
                    if bool (prestation):
                        # rec.ensure_one()
                        rec.prestation_id = prestation.id

    @api.one
    @api.onchange('prestation_demande_id', 'produit_phcie_id', 'substitut_phcie_id', 'prestation_cro_id',
                     'code_id_rfm', 'prestation_crs_id', 'pool_medical_crs_id', 'prestation_rembourse_id',
                     'prestataire_rembourse_id')
    @api.constrains('prestation_demande_id', 'produit_phcie_id', 'substitut_phcie_id', 'prestation_cro_id',
                    'code_id_rfm', 'prestation_crs_id', 'pool_medical_crs_id', 'prestation_rembourse_id',
                    'prestataire_rembourse_id')
    def _valide_prestation_id(self):
        self.ensure_one()
        if bool(self.prestation_demande_id) and bool(self.prestataire_crs_id) and bool(self.pool_medical_crs_id):
            # Récupérer la prestation médicale du CRS
            code_prestation_id = self.prestation_demande_id.id
            prestataire_id = self.prestataire_crs_id.id
            prestation = self.env['proximas.prestation'].search(
                [
                    ('code_prestation_id', '=', code_prestation_id),
                    ('prestataire_id', '=', prestataire_id)
                ]
            )
            if not bool(prestation):
                raise UserError (_ (
                    u"Proximaas : Contrôle de Règles de Gestion:\n \
                    La prestation demandée: %s ne figure pas dans la liste des prestations fournies par le\
                    prestataire: %s. Par conséquent, cette prestation ne peut être prise en compte dans le cadre \
                    de la convention signée avec le prestataire concernée. Pour plus d'informations, \
                    veuillez contactez l'administrateur..."
                    ) % (self.prestation_demande_id.name, self.prestataire_crs_id.name)
                )
        # self.code_medical_id = self.prestation_crs_id.code_medical_id.id
        # REMBOURSEMENT - PHARMACIE
        elif bool(self.code_id_rfm) and bool(self.prestataire_rembourse_id) and bool(self.produit_phcie_id):
            # Récupérer la prestation médicale pour la pharmacie (Dispensation Médicaments)
            pharmacie_rembourse_id = self.prestataire_rembourse_id.id
            if bool(pharmacie_rembourse_id):
                prestation = self.env['proximas.prestation'].search (
                    [
                        ('prestataire_id', '=', pharmacie_rembourse_id),
                        ('rubrique', '=', 'PHARMACIE')
                    ]
                )
                if not bool(prestation):
                    raise UserError(_(
                        u"Proximaas : Contrôle de Règles de Gestion:\n \
                        Le prestataire concerné : %s n'a pas été parametré pour fournir les médicaments (Pharmacie).\
                        Par conséquent, vous ne pourrez dispenser de médicament(s) pour le compte de celui-ci. \
                        Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % self.prestataire_rembourse_id.name
                    )
            else:
                raise UserError(_(
                    u"Proximaas : Contrôle de Règles de Gestion:\n \
                    Aucun prestataire (Pharmacie) n'est défini. Par conséquent, vous ne pourrez dipenser\
                    de médicament(s) pour le prestaire concerné. \
                    Pour plus d'informations, veuillez contactez l'administrateur..."
                    )
                )
        # PHARMACIE PEC
        elif (bool(self.prestataire_phcie_id) or bool(self.produit_phcie_id)) or bool(
                self.substitut_phcie_id) and self.date_execution:
            # Récupérer la prestation médicale pour la pharmacie (Dispensation Médicaments)
            pharmacie_id = self.prestataire_phcie_id.id
            if bool(pharmacie_id):
                pharmacie = self.prestataire_phcie_id.name
                prestation = self.env['proximas.prestation'].search (
                    [
                        ('prestataire_id', '=', pharmacie_id),
                        ('rubrique', 'ilike', 'PHARMACIE')
                    ]
                )
                if not bool(prestation):
                    raise UserError (_ (
                        u"Proximaas : Contrôle de Règles de Gestion:\n \
                        Le prestataire concerné: {}, n'a pas été parametré pour dispenser les médicaments (Pharmacie).\
                        Par conséquent, vous ne pourrez enregistrer les produits pour le compte de celui-ci. \
                        Pour plus d'informations, veuillez contactez l'administrateur..."
                        ).format(pharmacie)
                    )
            else:
                raise UserError(_(
                    u"Proximaas : Contrôle de Règles de Gestion:\n \
                    Aucun prestataire (Pharmacie) n'est défini. Par conséquent, vous ne pourrez dispenser\
                    des médicaments pour le prestataire concerné. Pour plus d'informations, veuillez contactez \
                    l'administrateur..."
                    )
                )

    # IDENTIFICATION ASSURE - PATIENT
    @api.depends('code_id_rfm', 'assure')
    @api.onchange('code_id_rfm', 'assure')
    @api.constrains('code_id_rfm', 'assure')
    def _get_assure_id(self):
        """
        Récupération de l'identifiant de l'assuré
        :return: assure.name
        """
        for rec in self:
            adherent = rec.rfm_id.adherent_id
            contrat_adherent = self.env['proximas.contrat'].search(
                [('adherent_id', '=', rec.rfm_id.adherent_id.id)])
            assure = self.env['proximas.assure'].search(
                ['|', ('code_id', '=', rec.code_id_rfm),
                 ('code_id_externe', '=', rec.code_id_rfm)
                 ])
            # Cas de remboursement de frais médicaux
            if bool(rec.rfm_id) and bool(rec.code_id_rfm) and bool(assure):
                # Vérification du statut familial de l'assuré
                if assure.statut_familial != 'adherent':
                    ayant_droit = self.env['proximas.ayant.droit'].search(
                        [('assure_id', '=', assure.id)])
                    contrat_assure = ayant_droit.contrat_id
                    if contrat_adherent.id == contrat_assure.id:
                        rec.assure_id = assure.id
                    else:
                        raise UserError(_(
                            u"Proximaas : Contrôle de Règles de Gestion.\n \
                             Le code ID. que vous avez renseigné est celui de l'assuré: %s (Code ID.: %s) \
                             qui n'est pas déclaré en tant que'un des ayant-droits pour le compte de l'adhérent \
                             concerné: %s. Pour plus d'informations, veuillez contactez l'administrateur..."
                            ) % (assure.name, assure.code_id, adherent.name)
                        )
                elif assure.statut_familial == 'adherent':
                    if assure.code_id == adherent.code_id:
                        rec.assure_id = assure.id
                    else:
                        raise UserError(_(
                            u"Proximaas : Contrôle de Règles de Gestion.\n \
                             Le code ID. que vous avez renseigné est celui de l'assuré: %s (Code ID.: %s) \
                             ne correspondant pas à celui indiqué comme demandeur du remboursement : %s. \
                             Pour plus d'informations, veuillez contactez l'administrateur..."
                            ) % (assure.name, assure.code_id, adherent.name)
                        )
            elif bool(rec.code_id_rfm) and not bool(assure):
                raise UserError(_(
                    u"Proximaas : Contrôle de Règles de Gestion.\n \
                     Le code ID. assuré que vous avez renseigné ne correspondant à aucun assuré dans le système.\
                     Pour plus d'informations, veuillez contactez l'administrateur..."
                    )
                )
            elif bool(rec.assure) and not bool(rec.code_id_rfm):
                rec.assure_id = rec.assure.id


    # CONTROLES A EFFECTUER SUR PRESTATIONS MEDICALE ET CONTROLES POLICE
    # 1. CONTROLE RUBRIQUE MEDICALE POLICE
    @api.one
    @api.depends('prestation_id', 'prestation_cro_id', 'prestation_crs_id', 'prestation_demande_id',
                  'produit_phcie_id', 'substitut_phcie_id', 'prestation_rembourse_id')
    @api.onchange('prestation_id', 'prestation_cro_id', 'prestation_crs_id', 'prestation_demande_id',
                  'produit_phcie_id','substitut_phcie_id', 'prestation_rembourse_id')
    @api.constrains('prestation_id', 'prestation_cro_id', 'prestation_crs_id', 'prestation_demande_id',
                     'produit_phcie_id', 'substitut_phcie_id', 'prestation_rembourse_id')
    def _get_rubrique_medicale(self):
        """
        contyrôles à effectuer sur la rubrique médicale de la prestation
        :return: None
        """
        # details_prise_charge = self.env['proximas.details.pec'].search ([
        self.ensure_one()
        controle_rubrique = self.env['proximas.controle.rubrique'].search(
            [('rubrique_id', '=', self.rubrique_id.id), ('police_id', '=', self.police_id.id)]
        )
        # Contrôles à effectuer sur la rubrique médicale
        if bool(controle_rubrique):
            # Si la rubrique médicale existe dans la table de contrôles rubriques médicales
            genre_rubrique = str(controle_rubrique.genre)
            statut_familial_rubrique = str(controle_rubrique.statut_familial)
            plafond_individu_rubrique = int(controle_rubrique.plafond_individu)
            plafond_famille_rubrique = int(controle_rubrique.plafond_famille)
            delai_carence_rubrique = int(controle_rubrique.delai_carence)
            age_limite_rubrique = int(controle_rubrique.age_limite)
            nbre_actes_individu_rubrique = int(controle_rubrique.nbre_actes_maxi_individu)
            nbre_actes_famille_rubrique = int(controle_rubrique.nbre_actes_maxi_famille)
            delai_attente_rubrique = int(controle_rubrique.delai_attente)
            verou_rubrique = bool(controle_rubrique.controle_strict)
            ticket_exigible_rubrique = bool(controle_rubrique.ticket_exigible)
            # self.rubrique_id = controle_rubrique.id
            self.ticket_exigible = bool(ticket_exigible_rubrique)
            # 1. Contrôle sur le genre de l'assuré
            if str(self.assure_id.genre) != str(genre_rubrique) and genre_rubrique != 'tous':
                if bool(verou_rubrique):
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n\
                        L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son genre: %s.\
                        La prestation est exclusivement reservée aux assurés du genre: %s. Pour plus d'informations, \
                        veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.genre, genre_rubrique)
                    )
                else:
                    raise UserError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n\
                        L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son genre: %s.\
                        La prestation est exclusivement reservée aux assurés du genre: %s. Pour plus d'informations,\
                        veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.genre, genre_rubrique)
                    )

            # 2. Contrôle sur le statut familial de l'assuré
            elif self.assure_id.statut_familial != statut_familial_rubrique and statut_familial_rubrique not in [
                'adherent_conjoint', 'adherent_enfant', 'conjoint_enfant', 'tous']:
                if bool (verou_rubrique):
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                          L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son statut \
                          familial: %s. La prestation est exclusivement reservée aux assurés dont la statut familial \
                          est: %s. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.statut_familial, statut_familial_rubrique)
                    )
                else:
                    raise UserError (_ (
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                          L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son statut \
                          familial: %s. La prestation est exclusivement reservée aux assurés dont la statut familial \
                          est: %s. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.statut_familial, statut_familial_rubrique)
                    )

            elif self.assure_id.statut_familial == 'enfant' and statut_familial_rubrique == 'adherent_conjoint':
                if bool (verou_rubrique):
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son statut \
                         familial: %s. La prestation est exclusivement reservée aux assurés dont la statut familial \
                         est:%s. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.statut_familial, statut_familial_rubrique)
                    )
                else:
                    raise UserError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son statut \
                         familial: %s. La prestation est exclusivement reservée aux assurés dont la statut familial est:\
                         %s. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.statut_familial, statut_familial_rubrique)
                    )
            elif self.assure_id.statut_familial == 'conjoint' and statut_familial_rubrique == 'adherent_enfant':
                if bool (verou_rubrique):
                    raise ValidationError (_ (
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son statut \
                         familial: %s. La prestation est exclusivement reservée aux assurés dont la statut familial est:\
                         %s. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.statut_familial, statut_familial_rubrique)
                    )
                else:
                    raise UserError (_ (
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son statut \
                         familial: %s. La prestation est exclusivement reservée aux assurés dont la statut familial est:\
                         %s. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.statut_familial, statut_familial_rubrique)
                    )
            elif self.assure_id.statut_familial == 'adherent' and statut_familial_rubrique == 'conjoint_enfant':
                if bool(verou_rubrique):
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son statut \
                         familial: %s. La prestation est exclusivement reservée aux assurés dont la statut familial est:\
                         %s. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.statut_familial, statut_familial_rubrique)
                    )
                else:
                    raise UserError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation compte tenu de son statut \
                         familial: %s. La prestation est exclusivement reservée aux assurés dont la statut familial est:\
                         %s. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, self.assure_id.statut_familial, statut_familial_rubrique)
                    )
            # 3. Contrôles sur plafonds de la rubrique médicale
            pec_rubrique_assure = self.env['proximas.details.pec'].search (
                [('assure_id', '=', self.assure_id.id), ('rubrique_id', '=', self.rubrique_id.id)]
            )
            pec_rubrique_contrat = self.env['proximas.details.pec'].search (
                [('contrat_id', '=', self.contrat_id.id), ('rubrique_id', '=', self.rubrique_id.id)]
            )
            nbre_pec_rubrique_assure = self.env['proximas.details.pec'].search_count (
                [('assure_id', '=', self.assure_id.id), ('rubrique_id', '=', self.rubrique_id.id)]
            )
            nbre_pec_rubrique_contrat = self.env['proximas.details.pec'].search_count (
                [('contrat_id', '=', self.contrat_id.id), ('rubrique_id', '=', self.rubrique_id.id)]
            )
            totaux_rubrique_assure = sum(item.total_pc for item in pec_rubrique_assure)
            totaux_rubrique_contrat = sum(item.total_pc for item in pec_rubrique_contrat)

            # 3.1. Contrôle Plafond Individu pour la rubrique
            if 0 < plafond_individu_rubrique <= totaux_rubrique_assure:
                if bool(verou_rubrique):
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le plafond par individu \
                         fixé à : %d pour la rubrique médicale : %s est atteint. Pour plus d'informations, veuillez \
                         contactez l'administrateur..."
                        ) % (self.assure_id.name, controle_rubrique.plafond_individu,
                         controle_rubrique.rubrique_name)
                    )
                else:
                    raise UserError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le plafond par individu \
                         fixé à : %d pour la rubrique médicale : %s est atteint. Pour plus d'informations, veuillez \
                         contactez l'administrateur..."
                        ) % (self.assure_id.name, controle_rubrique.plafond_individu,
                         controle_rubrique.rubrique_name)
                    )
            # 3.2. Contrôle Plafond famille (contrat)
            elif 0 < plafond_famille_rubrique <= totaux_rubrique_contrat:
                if bool (verou_rubrique):
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le plafond par famille \
                         fixé à : %s pour la rubrique médicale : %s est atteint. Pour plus d'informations, veuillez \
                         contactez l'administrateur..."
                        ) % (self.assure_id.name, controle_rubrique.plafond_famille, controle_rubrique.rubrique_name)
                    )
                else:
                    raise UserError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le plafond par famille \
                         fixé à : %s pour la rubrique médicale : %s est atteint. Pour plus d'informations, veuillez \
                         contactez l'administrateur..."
                        ) % (self.assure_id.name, controle_rubrique.plafond_famille, controle_rubrique.rubrique_name)
                    )
            # 4. Contrôle Delai de carence pour la rubrique médicale
            now = datetime.now()
            debut_carence = fields.Datetime.from_string (
                self.assure_id.date_activation) or fields.Datetime.from_string (fields.Date.today ())
            jours_activation = (now - debut_carence).days  # => différence en les 2 dates en nombre de jours.
            if 0 < delai_carence_rubrique >= int (jours_activation):
                if bool(verou_rubrique):
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le délai de carence à \
                         observé est fixé à : %d pour la rubrique médicale : %s. Pour plus d'informations, veuillez \
                         contactez l'administrateur..."
                        ) % (self.assure_id.name, delai_carence_rubrique, controle_rubrique.rubrique_name)
                    )
                else:
                    raise UserError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                          L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le délai de carence à \
                          observé est fixé à : %d pour la rubrique médicale : %s. Pour plus d'informations, veuillez \
                          contactez l'administrateur..."
                        ) % (self.assure_id.name, delai_carence_rubrique, controle_rubrique.rubrique_name)
                    )
            # 5. Contrôle age limite pour la rubrique
            elif 0 < age_limite_rubrique < int(self.assure_id.age):
                if bool(verou_rubrique):
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. L'âge limite est fixé à : \
                         (%d) an(s) pour la rubrique médicale : (%s). Pour plus d'informations, veuillez contactez \
                         l'administrateur..."
                        ) % (self.assure_id.name, age_limite_rubrique, controle_rubrique.rubrique_name)
                    )
                else:
                    raise UserError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                        L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. L'âge limite est fixé à :\
                        (%d) an(s) pour la rubrique médicale : (%s). Pour plus d'informations, veuillez contactez \
                        l'administrateur..."
                        ) % (self.assure_id.name, age_limite_rubrique, controle_rubrique.rubrique_name)
                    )
            # 6. Contrôle Nombre d'actes par individu pour la rubrique
            elif 0 < nbre_actes_individu_rubrique < nbre_pec_rubrique_assure:
                if bool(verou_rubrique):
                    raise ValidationError (_ (
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le nombre d'actes limite\
                         par assuré est fixé à : (%d) pour la rubrique médicale : (%s). Pour plus d'informations, \
                         veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, nbre_actes_individu_rubrique, controle_rubrique.rubrique_name)
                    )
                else:
                    raise UserError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le nombre d'actes limite \
                         par assuré est fixé à : (%d) pour la rubrique médicale : (%s). Pour plus d'informations,\
                         veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, nbre_actes_individu_rubrique, controle_rubrique.rubrique_name)
                    )
            # 7. Contrôle nombre d'actes par famille pour la rubrique
            elif 0 < nbre_actes_famille_rubrique < nbre_pec_rubrique_contrat:
                if bool(verou_rubrique):
                    raise ValidationError(_(
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                          L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le nombre d'actes limite \
                          par famille(contrat) est fixé à : (%d) pour la rubrique médicale : (%s). Pour plus \
                          d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, nbre_actes_famille_rubrique, controle_rubrique.rubrique_name)
                    )
                else:
                    raise UserError (_ (
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                          L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Le nombre d'actes limite\
                          par famille(contrat) est fixé à : (%d) pour la rubrique médicale : (%s). Pour plus \
                          d'informations, veuillez contactez l'administrateur..."
                        ) % (self.assure_id.name, nbre_actes_famille_rubrique, controle_rubrique.rubrique_name)
                    )
            # 8. Contrôle délai d'attente à observer
            if bool(pec_rubrique_assure):
                # Contrôles si les prestations fournies à l'assuré sont liées à la rubrique
                # si OUI, sélectionner la dernière prestation liée à la rubrique
                dernier_acte_rubrique_assure = pec_rubrique_assure[0]
                # Récupérer la date de la dernière prestation liée à la rubrique
                date_dernier_acte = fields.Datetime.from_string(dernier_acte_rubrique_assure.date_execution) or \
                                    fields.Datetime.from_string(fields.Date.today ())
                # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
                nbre_jours_dernier_acte = (now - date_dernier_acte).days
                # Comparer le délai d'attente prévu par la rubrique et le nombre de jours écoulés
                if 0 < int(delai_attente_rubrique) >= int(nbre_jours_dernier_acte) != 0:
                    if bool(verou_rubrique):
                        raise ValidationError (_ (
                            u"Proximaas : Contrôle de Règles de Gestion.\n \
                             L'assuré(e) concerné(e) : %s ne peut bénéficier de cette prestation. Le délai d'attente à \
                             observer est fixé à : (%d) jour(s) pour la rubrique médicale : (%s). Pour plus \
                             d'informations, veuillez contactez l'administrateur..."
                            ) % (self.assure_id.name, delai_attente_rubrique, controle_rubrique.rubrique_name)
                        )
                    else:
                        raise UserError (_ (
                            u"Proximas : Proximaas : Contrôle de Règles de Gestion.\n \
                             L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation. Car le délai d'attente\
                             à observer est fixé à : (%d) jour(s) pour la rubrique médicale : (%s). Pour plus \
                             d'informations, veuillez contactez l'administrateur..."
                            ) % (self.assure_id.name, delai_attente_rubrique, controle_rubrique.rubrique_name)
                        )
    @api.multi
    def _compute_net_a_payer(self):
        for rec in self:
            if rec.pec_id:
                rec.net_a_payer = rec.net_prestataire
            elif rec.rfm_id:
                rec.net_a_payer = rec.mt_remboursement
            else:
                rec.net_a_payer = 0
        # if bool (self.rfm_id):
        #     self.net_a_payer = self.mt_remboursement
        # elif bool (self.net_prestataire):
        #     self.net_a_payer = self.net_prestataire
        # else:
        #     self.net_a_payer = 0

    # CALCULS DES COUTS DES ACTES / PRESTATIONS & MEDICAMENTS
    @api.one
    @api.depends('prestation_id', 'prestation_cro_id', 'prestation_crs_id', 'prestation_rembourse_id', 'produit_phcie_id',
                 'mt_exclusion', 'code_id_rfm', 'prestataire_public', 'zone_couverte', 'prestataire','ticket_exigible',
                 'substitut_phcie_id', 'cout_unit', 'quantite', 'quantite_livre', 'cout_unite')
    # @api.onchange('prestation_cro_id', 'prestation_crs_id', 'prestation_rembourse_id', 'produit_phcie_id', 'mt_exclusion',
    #               'substitut_phcie_id', 'mt_exclusion', 'cout_unit', 'quantite', 'quantite_livre', 'code_id_rfm',
    #               'cout_unite', 'prestataire_public', 'zone_couverte', 'prestataire')
    @api.constrains('cout_unitaire', 'cout_unit', 'quantite_livre', 'taux_couvert', 'mt_paye_assure', 'mt_exclusion')
    def _calcul_couts_details_pec(self):
        self.ensure_one()
        if bool(self.prestation_id):
            # Vérifier si la prestation est identifiée
            controle_rubrique = self.env['proximas.controle.rubrique'].search([
                ('rubrique_id', '=', self.rubrique_id.id),
                ('police_id', '=', self.police_id.id)
            ])
            code_medical_police = self.env['proximas.code.medical.police'].search ([
                ('police_id', '=', self.police_id.id),
                ('code_medical_id', '=', self.code_medical_id.id)
            ])

            ticket_exigible = bool (controle_rubrique.ticket_exigible)
            self.ticket_exigible = ticket_exigible
            ############################################################################################################
            # Sinon, traitement de prise en charge normal : appliquer le taux de couverture selon les cas.             #
            ############################################################################################################
            ############################################################################################################
            # Taux de couverture PEC Ou Temboursement
            if bool (self.rfm_id):
                if bool (self.zone_couverte) and bool (self.prestataire_public):
                    self.taux_couvert = int (self.police_id.tx_couv_public_couvert)
                # Taux Couverture (Remboursement) Zone Non Couverte et prestataire public
                elif not bool (self.zone_couverte) and bool (self.prestataire_public):
                    self.taux_couvert = int (self.police_id.tx_couv_public)
                # Taux Couverture (Remboursement) Zone Couverte et prestataire privé
                elif bool (self.zone_couverte) and not bool (self.prestataire_public):
                    self.taux_couvert = int (self.police_id.tx_couv_prive_couvert)
                elif not bool (self.zone_couverte) and not bool (self.prestataire.is_public):
                    self.taux_couvert = int (self.police_id.tx_couv_prive)
            elif bool (code_medical_police):
                if bool (self.prestataire.is_public) or bool (self.prestataire_public):
                    self.taux_couvert = int (code_medical_police.tx_public)
                elif not bool (self.prestataire.is_public) or not bool (self.prestataire_public):
                    self.taux_couvert = int (code_medical_police.tx_prive)
            elif bool (self.prestataire.is_public):
                self.taux_couvert = int (self.police_id.tx_couv_public)
            else:
                self.taux_couvert = int (self.police_id.tx_couv_prive)
            ##################################################################
            # Récupérer le coût unitaire
            if bool (self.cout_unit):
                self.cout_unite = self.cout_unit
            elif bool (self.cout_unitaire):
                self.cout_unite = self.cout_unitaire
            else:
                self.cout_unite = 0
            ####################################################################
            taux_couvert = self.taux_couvert
            plafond = 0
            forfait = 0
            if bool (code_medical_police):
                plafond = int (code_medical_police.mt_plafond)
            self.mt_plafond = plafond

            if bool (self.substitut_phcie_id):
                # Cas de substitution de produit pharmacie (médicaments)
                prix_substitut = int (self.prix_indicatif_substitut)
                prix_produit = int (self.prix_indicatif_produit)
                if prix_substitut > prix_produit:
                    # Vérifier si le prix indicatif du substitut est inférieur à celui du produit prescrit
                    raise UserError (_ (
                        u"Proximaas : Contrôle de Règles de Gestion.\n \
                        Le prix indicatif du médicament prescrit est de: (%d Fcfa). Cependant, vous vous ne pouvez pas\
                        le substituer à un autre dont le prix indicatif est supérieur : (%d Fcfa). Pour plus \
                        d'informations, veuillez contactez l'administrateur..."
                    ) % (prix_produit, prix_substitut)
                                     )
                cout_produit = int (self.cout_unite)
                quantite_prescrite = int (self.quantite)
                quantite = int (self.quantite_livre)
                quantite_reste = int (quantite_prescrite) - int (quantite)
                marge_police = int (self.marge_medicament_police)
                marge_substitut = int (self.marge_medicament_substitut)
                prix_majore = 0
                if 0 < marge_substitut:
                    prix_majore = int (prix_substitut + marge_substitut)
                elif 0 < marge_police:
                    prix_majore = int (prix_substitut + marge_police)
                if 0 < prix_majore < cout_produit:
                    if quantite_prescrite > quantite:
                        self.cout_total = cout_produit * quantite
                        self.total_pc = (prix_majore * quantite)  # - self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    elif quantite_prescrite < quantite:
                        raise UserError (_ (
                            u"Proximaas : Contrôle de Règles de Gestion.\n \
                             Vous ne pourrez pas valider vos saisies, car la quantité quantité à livrer est de:\
                             (%d), ce qui est supérieure à la quantité prescrite : (%d). Pour plus d'informations, \
                             veuillez contactez l'administrateur..."
                        ) % (quantite, quantite_prescrite)
                                         )
                    else:
                        self.cout_total = cout_produit * quantite
                        self.total_pc = (prix_majore * quantite)  # - self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                else:
                    if quantite_prescrite > quantite:
                        self.cout_total = cout_produit * quantite
                        self.total_pc = self.cout_total  # - self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    elif quantite_prescrite < quantite:
                        raise UserError (_ (
                            u"Proximaas : Contrôle de Règles de Gestion.\n \
                            Vous ne pourrez pas valider vos saisies, car la quantité quantité à livrer est de:\
                            (%d), ce qui est supérieure à la quantité prescrite : (%d). Pour plus d'informations, \
                            veuillez contactez l'administrateur..."
                        ) % (quantite, quantite_prescrite)
                                         )
                    else:
                        self.cout_total = cout_produit * quantite
                        self.total_pc = self.cout_total  # - self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
            elif bool (self.produit_phcie_id):
                # Cas de produit pharmacie (médicaments)
                cout_produit = int (self.cout_unite)
                prix_produit = int (self.prix_indicatif_produit)
                quantite_prescrite = int (self.quantite)
                quantite = int (self.quantite_livre)
                quantite_reste = int (quantite_prescrite) - int (quantite)
                marge_police = int (self.marge_medicament_police)
                marge_produit = int (self.marge_medicament_produit)
                prix_majore = 0
                if 0 < marge_produit:
                    prix_majore = int (prix_produit + marge_produit)
                elif 0 < marge_police:
                    prix_majore = int (prix_produit + marge_police)
                if 0 < prix_majore < cout_produit:
                    if quantite_prescrite > quantite:
                        self.cout_total = cout_produit * quantite
                        self.total_pc = (prix_majore * quantite)  # - self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    elif quantite_prescrite < quantite:
                        raise UserError (_ (
                            u"Proximaas : Contrôle de Règles de Gestion.\n \
                            Vous ne pourrez pas valider vos saisies, car la quantité quantité à livrer est de:\
                            (%d), ce qui est supérieure à la quantité prescrite : (%d). Pour plus d'informations, \
                            veuillez contactez l'administrateur..."
                        ) % (quantite, quantite_prescrite)
                                         )
                    else:
                        self.cout_total = cout_produit * quantite
                        self.total_pc = (prix_majore * quantite)  # - self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                else:
                    if quantite_prescrite > quantite:
                        self.cout_total = cout_produit * quantite
                        self.total_pc = self.cout_total  # - self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    elif quantite_prescrite < quantite:
                        raise UserError (_ (
                            "Proximaas : Contrôle de Règles de Gestion.\n \
                            Vous ne pourrez pas valider vos saisies, car la quantité quantité à livrer est de:\
                            (%d), ce qui est supérieure à la quantité prescrite : (%d). Pour plus d'informations, \
                            veuillez contactez l'administrateur..."
                        ) % (quantite, quantite_prescrite)
                                         )
                    else:
                        self.cout_total = cout_produit * quantite
                        self.total_pc = self.cout_total  # - self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
            # 1. Prestation Cas de cout modifiable et quantité exigé
            elif bool (self.cout_modifiable) and bool (self.quantite_exige):
                quantite = self.quantite_livre
                cout_unitaire = self.cout_unite
                code_non_controle = self.code_non_controle
                # 1. Si oui, alors vérifier si le coût de la prestation est modifiable

                if 0 < plafond < cout_unitaire and not code_non_controle:
                    # Si OUI, alors vérifier le montant plafond n'est pas nulle et est inférieur au cout unitaire
                    # donné par l'utilisateur
                    if self.mt_rabais > 0:
                        # Si OUI, alors s'il y a un montant de rabais prédéfini et non nulle
                        self.cout_total = int (cout_unitaire * self.coefficient * quantite) - int (self.mt_rabais)
                        self.total_pc = int (plafond * self.coefficient * quantite) - int (
                            self.mt_rabais)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    elif self.remise_prestation > 0:
                        # Si OUI, alors s'il y a un taux de remise prédéfini non nulle
                        cout_total = int (cout_unitaire * self.coefficient * quantite)
                        taux_remise = int (self.remise_prestation)
                        remise = cout_total - int (cout_total * taux_remise / 100)
                        self.cout_total = cout_total - remise
                        self.total_pc = int (self.plafond * self.coefficient * quantite) - int (
                            remise)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    else:
                        # Sinon, alors il y a ni rabais, ni remise
                        self.cout_total = int (cout_unitaire * self.coefficient * quantite)
                        self.total_pc = int (plafond * self.coefficient * quantite)  # - int(self.mt_exclusion)
                        self.total_npc = self.cout_total - self.total_pc
                else:
                    # Sinon, il n'y pas de plafond applicable
                    if self.mt_rabais > 0:
                        # Si OUI, il y a t-il un montant de rabais prédéfini et non nulle?
                        self.cout_total = int (
                            cout_unitaire * self.coefficient * quantite) - int (self.mt_rabais)
                        self.total_pc = int (
                            cout_unitaire * self.coefficient * quantite) - int (
                            self.mt_rabais)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc

                    elif self.remise_prestation > 0:
                        # Sinon, alors s'il y a t-il un taux de remise prédéfini non nulle?
                        cout_total = int (cout_unitaire * self.coefficient * quantite)
                        taux_remise = int (self.remise_prestation)
                        remise = cout_total - int (cout_total * taux_remise / 100)
                        self.cout_total = cout_total - remise
                        self.total_pc = cout_total - int (remise)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    else:
                        # Sinon, alors il y a ni rabais, ni remise
                        self.cout_total = int (cout_unitaire * self.coefficient * quantite)
                        self.total_pc = int (
                            cout_unitaire * self.coefficient * quantite)  # - int(self.mt_exclusion)
                        self.total_npc = self.cout_total - self.total_pc
            #########################################
            # 2. Prestation Cas de cout modifiable et non Quantité exigée
            elif bool (self.cout_modifiable) and not bool (self.quantite_exige):
                cout_unitaire = self.cout_unite
                code_non_controle = self.code_non_controle
                # 1. Si oui, alors vérifier si le coût de la prestation est modifiable
                if 0 < plafond < cout_unitaire and not code_non_controle:
                    # Si OUI, alors vérifier le montant plafond n'est pas nulle et est inférieur au cout unitaire
                    # donné par l'utilisateur
                    if self.mt_rabais > 0:
                        # Si OUI, alors s'il y a un montant de rabais prédéfini et non nulle
                        self.cout_total = int (cout_unitaire * self.coefficient) - int (self.mt_rabais)
                        self.total_pc = int (plafond * self.coefficient) - int (
                            self.mt_rabais)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    elif self.remise_prestation > 0:
                        # Si OUI, alors s'il y a un taux de remise prédéfini non nulle
                        cout_total = int (cout_unitaire * self.coefficient)
                        taux_remise = int (self.remise_prestation)
                        remise = cout_total - int (cout_total * taux_remise / 100)
                        self.cout_total = cout_total - remise
                        self.total_pc = int (self.plafond * self.coefficient) - int (
                            remise)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    else:
                        # Sinon, alors il y a ni rabais, ni remise
                        self.cout_total = int (cout_unitaire * self.coefficient)
                        self.total_pc = int (plafond * self.coefficient)  # - int(self.mt_exclusion)
                        self.total_npc = self.cout_total - self.total_pc
                else:
                    # Sinon, il n'y pas de plafond applicable
                    if self.mt_rabais > 0:
                        # Si OUI, il y a t-il un montant de rabais prédéfini et non nulle?
                        self.cout_total = int (
                            cout_unitaire * self.coefficient) - self.mt_rabais
                        self.total_pc = int (
                            cout_unitaire * self.coefficient) - int (
                            self.mt_rabais)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc

                    elif self.remise_prestation > 0:
                        # Sinon, alors s'il y a t-il un taux de remise prédéfini non nulle?
                        cout_total = int (cout_unitaire * self.coefficient)
                        taux_remise = int (self.remise_prestation)
                        remise = cout_total - int (cout_total * taux_remise / 100)
                        self.cout_total = cout_total - remise
                        self.total_pc = cout_total - int (remise)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    else:
                        # Sinon, alors il y a ni rabais, ni remise
                        self.cout_total = int (cout_unitaire * self.coefficient)
                        self.total_pc = int (
                            cout_unitaire * self.coefficient)  # - int(self.mt_exclusion)
                        self.total_npc = self.cout_total - self.total_pc
            #########################################################
            # 3. Prestation Cas de quantité exigée et non cout modifiable
            elif bool (self.quantite_exige) and not bool (self.cout_modifiable):
                quantite = self.quantite_livre
                cout_unitaire = self.cout_unite
                code_non_controle = self.code_non_controle
                # 1. Si oui, alors vérifier si le coût de la prestation est modifiable
                if 0 < plafond < cout_unitaire and code_non_controle:
                    # Si OUI, alors vérifier le montant plafond n'est pas nulle et est inférieur au cout unitaire
                    # donné par l'utilisateur
                    if self.mt_rabais > 0:
                        # Si OUI, alors s'il y a un montant de rabais prédéfini et non nulle
                        self.cout_total = int (cout_unitaire * self.coefficient * quantite) - int (
                            self.mt_rabais)
                        self.total_pc = int (plafond * self.coefficient * quantite) - int (
                            self.mt_rabais)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    elif self.remise_prestation > 0:
                        # Si OUI, alors s'il y a un taux de remise prédéfini non nulle
                        cout_total = int (cout_unitaire * self.coefficient * quantite)
                        taux_remise = int (self.remise_prestation)
                        remise = cout_total - int (cout_total * taux_remise / 100)
                        self.cout_total = cout_total - remise
                        self.total_pc = int (self.plafond * self.coefficient * quantite) - int (
                            remise)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    else:
                        # Sinon, alors il y a ni rabais, ni remise
                        self.cout_total = int (cout_unitaire * self.coefficient * quantite)
                        self.total_pc = int (plafond * self.coefficient * quantite)  # - int(self.mt_exclusion)
                        self.total_npc = self.cout_total - self.total_pc
                else:
                    # Sinon, il n'y pas de plafond applicable
                    if self.mt_rabais > 0:
                        # Si OUI, il y a t-il un montant de rabais prédéfini et non nulle?
                        self.cout_total = int (
                            cout_unitaire * self.coefficient * quantite) - self.mt_rabais
                        self.total_pc = int (
                            cout_unitaire * self.coefficient * quantite) - int (
                            self.mt_rabais)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc

                    elif self.remise_prestation > 0:
                        # Sinon, alors s'il y a t-il un taux de remise prédéfini non nulle?
                        cout_total = int (cout_unitaire * self.coefficient * quantite)
                        taux_remise = int (self.remise_prestation)
                        remise = cout_total - int (cout_total * taux_remise / 100)
                        self.cout_total = cout_total - remise
                        self.total_pc = cout_total - int (remise)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    else:
                        # Sinon, alors il y a ni rabais, ni remise
                        self.cout_total = int (cout_unitaire * self.coefficient * quantite)
                        self.total_pc = int (
                            cout_unitaire * self.coefficient * quantite)  # - int(self.mt_exclusion)
                        self.total_npc = self.cout_total - self.total_pc
            # Forfait éclaté ( forfait SAM + Forfait Assuré)
            elif 0 < int (self.forfait_sam + self.forfait_ticket) and int (
                    self.forfait_sam + self.forfait_ticket) <= int (self.cout_unite):
                forfait = int (self.forfait_sam + self.forfait_ticket)
                self.mt_forfait = forfait
                # Sinon, si le coût de la prestation n'est pas modifiable, il y a t-il un forfait SAM et forfait Ticket
                if 0 < int (plafond * self.coefficient) < forfait:
                    # s'il y a t-il un plafond pour la prestation
                    if self.mt_rabais:
                        # S'il y a t-il un Rabais
                        self.cout_total = int (forfait) - int (self.mt_rabais)  # + self.mt_exclusion
                        self.total_pc = int (plafond * self.coefficient) - int (self.mt_rabais)
                        self.total_npc = self.cout_total - self.total_pc
                    elif self.remise_prestation:
                        # S'il y a t-il une Remise
                        cout_total = int (forfait)
                        total_pc = int (plafond * self.coefficient)
                        taux_remise = int (self.remise_prestation)
                        remise_cout_total = cout_total - int (cout_total * taux_remise / 100)
                        remise_total_pc = total_pc - int (total_pc * taux_remise / 100)
                        self.cout_total = cout_total - remise_cout_total
                        self.total_pc = total_pc - remise_total_pc  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    else:
                        self.cout_total = int (forfait)  # - int(self.mt_exclusion)
                        self.total_pc = int (plafond * self.coefficient)
                        self.total_npc = self.cout_total - self.total_pc
                else:
                    forfait = int (self.forfait_sam + self.forfait_ticket)
                    self.mt_forfait = forfait
                    if self.mt_rabais:
                        self.cout_total = int (forfait) - int (self.mt_rabais)
                        self.total_pc = int (forfait) - int (self.mt_rabais)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    elif self.remise_prestation:
                        # S'il y a t-il une Remise
                        cout_total = int (forfait)
                        total_pc = int (forfait)
                        taux_remise = int (self.remise_prestation)
                        remise = cout_total - int (cout_total * taux_remise / 100)
                        self.cout_total = cout_total - remise
                        self.total_pc = total_pc - int (remise)  # + self.mt_exclusion
                        self.total_npc = self.cout_total - self.total_pc
                    else:
                        self.cout_total = int (forfait)
                        self.total_pc = int (forfait)  # - int(self.mt_exclusion)
                        self.total_npc = self.cout_total - self.total_pc
            elif 0 < plafond < self.cout_unite and not self.code_non_controle:
                if self.mt_rabais:
                    self.cout_total = int (self.cout_unite * self.coefficient) - int (self.mt_rabais)
                    self.total_pc = int (plafond * self.coefficient) - int (self.mt_rabais)  # + self.mt_exclusion
                    self.total_npc = self.cout_total - self.total_pc
                else:
                    self.cout_total = int (self.cout_unite * self.coefficient)
                    self.total_pc = int (plafond * self.coefficient)  # - int(self.mt_exclusion)
                    self.total_npc = self.cout_total - self.total_pc
            elif plafond == 0:
                if self.mt_rabais:
                    self.cout_total = int (self.cout_unite * self.coefficient) - int (self.mt_rabais)
                    self.total_pc = int (self.cout_unite * self.coefficient) - int (
                        self.mt_rabais)  # + self.mt_exclusion
                    self.total_npc = self.cout_total - self.total_pc
                else:
                    self.cout_total = int (self.cout_unite * self.coefficient)
                    self.total_pc = int (self.cout_unite * self.coefficient)  # - int(self.mt_exclusion)
                    self.total_npc = self.cout_total - self.total_pc
            else:
                self.total_pc = int (self.cout_unite * self.coefficient) - int (self.mt_rabais)
                self.cout_total = int (self.cout_unite * self.coefficient) - int (
                    self.mt_rabais)  # + self.mt_exclusion
                self.total_npc = self.cout_total - self.total_pc
            self.total_npc = int (self.cout_total) - int (self.total_pc)
            total_pc = int (self.total_pc)
            total_npc = int (self.total_npc)
            diff_ticket_mt_paye = 0
            if bool(forfait):
                self.net_tiers_payeur = int (self.forfait_sam)
                self.ticket_moderateur = int (self.forfait_ticket)
                # self.ticket_exigible = bool (controle_rubrique.ticket_exigible)
                diff_ticket_mt_paye = int (self.mt_paye_assure) - int (self.ticket_moderateur)
                # Calculs détails pour le remboursements
                if bool (self.rfm_id):
                    self.mt_remboursement = self.net_tiers_payeur
                    self.net_prestataire = 0
                    self.debit_ticket = 0
            else:
                self.net_tiers_payeur = total_pc * int (taux_couvert) / 100
                taux_ticket = 100 - int (taux_couvert)
                self.ticket_moderateur = total_pc * int (taux_ticket) / 100
                # self.ticket_exigible = bool (controle_rubrique.ticket_exigible)
                diff_ticket_mt_paye = int (self.mt_paye_assure) - int (self.ticket_moderateur)

            if bool (ticket_exigible):
                self.net_prestataire = int (self.net_tiers_payeur)
                self.debit_ticket = int (self.ticket_moderateur + self.total_npc) - int (self.mt_paye_assure)
            elif not bool (self.ticket_exigible) and (diff_ticket_mt_paye >= 0):
                self.net_prestataire = total_pc - int (self.ticket_moderateur)
                self.debit_ticket = int (self.ticket_moderateur + self.total_npc) - int (self.mt_paye_assure)

            # Calculs détails pour le remboursements
            if bool (self.rfm_id):
                self.mt_remboursement = self.net_tiers_payeur
                self.net_prestataire = 0
                self.debit_ticket = 0
                self.mt_remboursement -= self.mt_exclusion
            else:
                self.net_prestataire = int (self.net_tiers_payeur)
                self.net_prestataire -= self.mt_exclusion


    # @api.multi
    @api.onchange('substitut_phcie_id', 'cout_unit', 'date_execution', 'quantite_livre', 'mt_paye_assure', 'quantite')
    def _check_quantite_prescription(self):
        for rec in self:
            if bool(rec.produit_phcie_id) and rec.quantite == 0:
                return {'value': {},
                        'warning': {'title': u'Proximaas : Règles de Gestion : Erreur Quantité Prescription.',
                                    'message': u"Vous essayez de dispenser le produit: %s, dont la quantité prescrite \
                                    n'est pas indiquée. Veuillez définir la quantité exacte prescrite par le médecin. \
                                    Pour plus de détails, veuillez contacter l'administrateur..." % rec.produit_phcie
                                    }
                        }
            if bool(rec.produit_phcie_id) and bool(rec.date_execution) and int (rec.cout_unit) > 0 and int (
                    rec.quantite_livre) == 0:
                return {'value': {},
                        'warning': {'title': u'Proximaas : Règles de Gestion : Erreur Quantité Fournie.',
                                    'message': u"Il semble que vous avez omis de renseigner la quantité fournie \
                                    (livrée) concerant le produit: %s. Veuillez bien renseigner la quantité exacte \
                                    dispensée. Pour plus de détails, veuillez contacter l'administrateur..."
                                    % rec.produit_phcie
                                    }
                        }

    @api.constrains('produit_phcie_id', 'quantite_livre', 'quantite')
    def _validate_quantite_prescription(self):
        for rec_id in self:
            if bool(rec_id.produit_phcie_id) and rec_id.quantite == 0:
                raise ValidationError(_(
                    u"Proximaas : Contrôle de Règles de Gestion.\n\
                      Vous êtes tenus de renseigner la quantité demandée (prescrite) concernant le produit: %s.\
                      Veuillez à bien renseigner la quantité exacte demandée par le médecin traitant. Pour plus de\
                      détails, veuillez contacter l'administrateur..."
                    ) % rec_id.produit_phcie
                )
            if bool(rec_id.produit_phcie_id) and bool(
                    rec_id.date_execution) and rec_id.cout_unit > 0 and rec_id.quantite_livre == 0:
                raise ValidationError(_(
                    u"Proximaas : Contrôle de Règles de Gestion.\n\
                      Il semble que vous avez omis de renseigner la quantité fournie \
                      (livrée) concerant le produit: %s. Veuillez bien renseigner la quantité exacte \
                      dispensée. Pour plus de détails, veuillez contacter l'administrateur..."
                    ) % rec_id.produit_phcie
                )

    # @api.multi
    # @api.onchange('prestation_cro_id', 'prestation_crs_id', 'date_execution', 'mt_paye_assure', 'produit_phcie_id',
    #               'substitut_phcie_id', 'prestation_rembourse_id')
    # def _check_ticket_exigible(self):
    #     # self.ensure_one()
    #     for rec in self:
    #         if bool(rec.ticket_exigible) and bool(rec.date_execution):
    #             # rec.mt_paye_assure = int(rec.ticket_moderateur)
    #             if bool (rec.produit_phcie_id) and 0 <= int(rec.mt_paye_assure) < int (rec.ticket_moderateur):
    #                 return {
    #                     'warning': {
    #                         'title': _ (u'Proximaas : Contrôle de Règles de Gestion.'),
    #                         'message': _ (u"Le Produit (médicament) : (%s) exige le paiement du ticket modérateur par \
    #                                      l'assuré. Vous êtes tenu d'encaisser la somme de : %d F.cfa, au titre de ticket \
    #                                      modérateur. Par conséquent, vous devez absolument confirmer le paiement du ticket \
    #                                      modérateur exigé et le notifier en renseignant le montant exact dans le champ \
    #                                      indiqué. Faute de quoi, vos données ne seront pas validées. Pour plus \
    #                                      d'informations, veuillez contactez l'administrateur..."
    #                                       ) % (rec.produit_phcie, rec.ticket_moderateur)
    #                     }
    #                 }
    #             elif 0 <= int(rec.mt_paye_assure) < int(rec.ticket_moderateur):
    #                 return {
    #                     'warning': {
    #                         'title': _(u'Proximaas : Contrôle de Règles de Gestion.'),
    #                         'message': _(u"La prestation : (%s) exige le paiement du ticket modérateur par l'assuré. \
    #                                     Vous êtes tenus d'encaisser la somme de : %d F.cfa, au titre de ticket modérateur. \
    #                                     Par conséquent, vous devez absolument confirmer le paiement du ticket modérateur \
    #                                     exigé et le notifier en renseignant le montant exact dans le champ indiqué. Faute \
    #                                     de quoi, vos données ne seront pas validées. Pour plus d'informations, veuillez \
    #                                     contactez l'administrateur..."
    #                                     ) % (rec.prestation_id.name, rec.ticket_moderateur)
    #                     }
    #                 }


    # CONTROLE DELAI ATTENTE
    # @api.one
    @api.depends ('date_execution', 'prestation_id', 'prestation_cro_id', 'prestation_crs_id',
                  'prestation_demande_id',
                  'produit_phcie_id', 'substitut_phcie_id', 'prestation_rembourse_id')
    @api.onchange ('date_execution', 'prestation_id', 'prestation_cro_id', 'prestation_crs_id',
                   'prestation_demande_id',
                   'produit_phcie_id', 'substitut_phcie_id', 'prestation_rembourse_id')
    def _check_delai_attente_prestation(self):
        '''
        Contrôle à affecuer sur la prestation, médicament fournis pour vérifier le délai d'attente à observer
        :return: UserError or None
        '''
        # Contrôle du délai d'attente Substitut Médicament
        # 1. Vérifier s'il s'agit d'une substitution de médicament?
        # self.ensure_one()
        for rec in self:
            if bool (rec.substitut_phcie_id):
                # Récupère la date du jour
                now = datetime.now ()
                substitut_phcie = rec.substitut_phcie
                # Si OUI, y a-t-il un délai d'attente à observer pour le substitut?
                if 0 < int (rec.delai_attente_substitut):
                    # Si OUI, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
                    pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
                        [
                            ('date_execution', '!=', None),
                            ('assure_id', '=', rec.assure_id.id),
                            '|', ('produit_phcie_id', '=', rec.substitut_phcie_id.id),
                            ('substitut_phcie_id', '=', rec.substitut_phcie_id.id),
                        ]
                    )
                    if bool (pec_produit_phcie_assure):
                        # Récupérer la dernière fourniture du médicament prescrit ou substituer
                        dernier_acte_assure = pec_produit_phcie_assure[0]
                        # Récupérer la date de la dernière prescription ou substitution liée au médicament
                        date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
                                            fields.Datetime.from_string (fields.Date.today ())
                        rec.date_dernier_acte = dernier_acte_assure.date_execution
                        # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
                        nbre_jours_dernier_acte = (now - date_dernier_acte).days
                        # => différence en les 2 dates en nombre de jours.
                        rec.delai_prestation = int (nbre_jours_dernier_acte)
                        # Vérifier si le délai d'attente pour le produit est écoulé ou pas?
                        if int (rec.delai_attente_substitut) <= int (nbre_jours_dernier_acte):
                            # Sinon, rejeter la prescription
                            return {'value': {},
                                    'warning': {'title': u"Proximaas : Contrôle de Règles de Gestion.",
                                                'message': u"L'assuré(e) concerné(e): %s ne peut bénéficier de cette \
                                                prescription commme substitut médicament. Le délai d'attente à observer\
                                                 pour le produit : (%s) est fixé à : (%d) jour(s). Ce produit a été \
                                                 prescrit à l'assuré  concerné il y a de cela : (%d) jours. Pour plus \
                                                 d'informations, veuillez contactez l'administrateur..."
                                                           % (rec.assure_id.name, substitut_phcie,
                                                              rec.delai_attente_substitut,
                                                              int (nbre_jours_dernier_acte))
                                                }
                                    }
                        else:
                            pass
                    else:
                        # Si aucun acte trouvé concernant la pretation pour l'assuré concerné
                        rec.date_dernier_acte = rec.date_execution
                        rec.delai_prestation = 0
                else:
                    # Si NON, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
                    pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
                        [
                            ('date_execution', '!=', None),
                            ('assure_id', '=', rec.assure_id.id),
                            '|', ('produit_phcie_id', '=', rec.substitut_phcie_id.id),
                            ('substitut_phcie_id', '=', rec.substitut_phcie_id.id),
                        ]
                    )
                    if bool (pec_produit_phcie_assure):
                        # Récupérer la dernière fourniture du médicament prescrit ou substituer
                        dernier_acte_assure = pec_produit_phcie_assure[0]
                        # Récupérer la date de la dernière prescription ou substitution liée au médicament
                        date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
                                            fields.Datetime.from_string (fields.Date.today ())
                        rec.date_dernier_acte = dernier_acte_assure.date_execution
                        # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
                        nbre_jours_dernier_acte = (now - date_dernier_acte).days
                        # => différence en les 2 dates en nombre de jours.
                        rec.delai_prestation = int (nbre_jours_dernier_acte)
                    else:
                        # Si aucun acte trouvé concernant la pretation pour l'assuré concerné
                        rec.date_dernier_acte = rec.date_execution
                        rec.delai_prestation = 0
            # 2. Vérifier s'il s'agit d'une prescription de médicament?
            elif bool (rec.produit_phcie_id):
                # Récupère la date du jour
                now = datetime.now ()
                produit_phcie = rec.produit_phcie
                # Si OUI, y a-t-il un délai d'attente à observer pour le produit prescrit?
                if 0 < int (rec.delai_attente_produit):
                    # Si OUI, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
                    pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
                        [
                            ('date_execution', '!=', None),
                            ('assure_id', '=', rec.assure_id.id),
                            '|', ('produit_phcie_id', '=', rec.produit_phcie_id.id),
                            ('substitut_phcie_id', '=', rec.produit_phcie_id.id),
                        ]
                    )
                    if bool (pec_produit_phcie_assure):
                        # Récupérer la dernière fourniture du médicament prescrit ou substituer
                        dernier_acte_assure = pec_produit_phcie_assure[0]
                        # Récupérer la date de la dernière prescription ou substitution liée au médicament
                        date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
                                            fields.Datetime.from_string (fields.Date.today ())
                        rec.date_dernier_acte = dernier_acte_assure.date_execution
                        # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
                        nbre_jours_dernier_acte = (now - date_dernier_acte).days
                        # => différence en les 2 dates en nombre de jours.
                        rec.delai_prestation = int (nbre_jours_dernier_acte)
                        # Vérifier si le délai d'attente pour le produit est écoulé ou pas?
                        if int (rec.delai_attente_produit) >= int (nbre_jours_dernier_acte):
                            # Sinon, rejeter la prescription
                            return {'value': {},
                                    'warning': {'title': u'Proximaas : Contrôle de Règles de Gestion.',
                                                'message': u"Proximaas : Contrôle de Règles de Gestion.\n \
                            L'assuré(e) concerné(e): %s ne peut bénéficier de la prescription de ce médicament. \
                            Le délai d'attente à observer pour le produit : (%s) est fixé à : (%d) jour(s). Ce produit\
                            a été prescrit à l'assuré il y a de cela : (%d) jours. Pour plus d'informations, veuillez \
                            contactez l'administrateur..." % (rec.assure_id.name, produit_phcie,
                                                              rec.delai_attente_produit,
                                                              int (nbre_jours_dernier_acte))
                                                }
                                    }
                        else:
                            pass
                    else:
                        # Si aucun acte trouvé concernant la pretation pour l'assuré concerné
                        rec.date_dernier_acte = rec.date_execution
                        rec.delai_prestation = 0
                else:
                    # Si NON, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
                    pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
                        [
                            ('date_execution', '!=', None),
                            ('assure_id', '=', rec.assure_id.id),
                            '|', ('produit_phcie_id', '=', rec.produit_phcie_id.id),
                            ('substitut_phcie_id', '=', rec.produit_phcie_id.id),
                        ]
                    )
                    if bool (pec_produit_phcie_assure):
                        # Récupérer la dernière fourniture du médicament prescrit ou substituer
                        dernier_acte_assure = pec_produit_phcie_assure[0]
                        # Récupérer la date de la dernière prescription ou substitution liée au médicament
                        date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
                                            fields.Datetime.from_string (fields.Date.today ())
                        rec.date_dernier_acte = dernier_acte_assure.date_execution
                        # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
                        nbre_jours_dernier_acte = (now - date_dernier_acte).days
                        # => différence en les 2 dates en nombre de jours.
                        rec.delai_prestation = int (nbre_jours_dernier_acte)
                    else:
                        # Si aucun acte trouvé concernant la pretation pour l'assuré concerné
                        rec.date_dernier_acte = rec.date_execution
                        rec.delai_prestation = 0
            # 3. Vérifier s'il s'agit d'une prestation médicale?
            # delai_attente = int(rec.delai_attente_prestation)
            elif int (rec.delai_attente_prestation) != 0 and rec.pec_state != 'dispense':
                # Si OUI, Récupère la date du jour
                now = datetime.now ()
                # Vérifier s'il y a til un délai d'attente à observer pour la prestation concernée?
                # Si OUI, chercher les prestations de l'assure contenant la prestation concernée
                pec_prestations_assure = self.env['proximas.details.pec'].search ([
                    ('date_execution', '!=', False),
                    ('assure_id', '=', rec.assure_id.id),
                    ('prestation_id', '=', rec.prestation_id.id),
                ])
                count_pec_prestations_assure = self.env['proximas.details.pec'].search_count (
                    [
                        ('date_execution', '!=', False),
                        ('assure_id', '=', rec.assure_id.id),
                        ('prestation_id', '=', rec.prestation_id.id),
                    ]
                )
                if int (count_pec_prestations_assure) >= 1:
                    # Récupérer la dernier acte liée à la prestation offerte à l'assuré
                    dernier_acte_assure = pec_prestations_assure[0]
                    # Récupérer la date de la dernière prescription ou substitution liée au médicament
                    date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
                                        fields.Datetime.from_string (fields.Date.today ())
                    date_acte_format = datetime.strftime (date_dernier_acte, '%d-%m-%Y')
                    rec.date_dernier_acte = dernier_acte_assure.date_execution
                    # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
                    nbre_jours_dernier_acte = (now - date_dernier_acte).days
                    # => différence en les 2 dates en nombre de jours.
                    rec.delai_prestation = int (nbre_jours_dernier_acte)
                    # Vérifier si le délai d'attente pour la prestation est écoulé ou pas?
                    if int (rec.delai_attente_prestation) >= int (nbre_jours_dernier_acte):
                        # Sinon, rejeter la prestation
                        raise UserError (_ (
                            u"Proximaas : Contrôle de Règles de Gestion.\n \
                            L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation médicale. \
                            Car le délai d'attente à observer pour la prestation: (%s) est fixé à : (%d) jour(s).\
                            La dernière fois que cet assuré a bénéficié de cette prestation (%s) remonte à : \
                            (%d) jours. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (rec.assure_id.name, rec.prestation_id.name, rec.delai_attente_prestation,
                             date_acte_format, int (nbre_jours_dernier_acte))
                                         )
                    else:
                        pass
                else:
                    # Si aucun acte trouvé concernant la pretation pour l'assuré concerné
                    rec.date_dernier_acte = rec.date_execution
                    rec.delai_prestation = 0
            else:
                # Si NON, Récupère la date du jour
                now = datetime.now ()
                # Vérifier s'il y a til un délai d'attente à observer pour la prestation concernée?
                # Si OUI, chercher les prestations de l'assure contenant la prestation concernée
                pec_prestations_assure = self.env['proximas.details.pec'].search ([
                    ('date_execution', '!=', False),
                    ('assure_id', '=', rec.assure_id.id),
                    ('prestation_id', '=', rec.prestation_id.id),
                ])
                count_pec_prestations_assure = self.env['proximas.details.pec'].search_count (
                    [
                        ('date_execution', '!=', False),
                        ('assure_id', '=', rec.assure_id.id),
                        ('prestation_id', '=', rec.prestation_id.id),
                    ]
                )
                if int (count_pec_prestations_assure) >= 1:
                    # Récupérer la dernier acte liée à la prestation offerte à l'assuré
                    dernier_acte_assure = pec_prestations_assure[0]
                    # Récupérer la date de la dernière prescription ou substitution liée au médicament
                    date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
                                        fields.Datetime.from_string (fields.Date.today ())
                    rec.date_dernier_acte = dernier_acte_assure.date_execution
                    # Calcul le nombre de jours écoulés entre la dernière prestation liée et aujourd'hui
                    nbre_jours_dernier_acte = (now - date_dernier_acte).days
                    rec.delai_prestation = int (nbre_jours_dernier_acte)
                else:
                    # Si aucun acte trouvé concernant la pretation pour l'assuré concerné
                    rec.date_dernier_acte = rec.date_execution
                    rec.delai_prestation = 0

    @api.constrains ('date_execution', 'prestation_id', 'prestation_cro_id', 'prestation_crs_id',
                     'prestation_demande_id',
                     'produit_phcie_id', 'substitut_phcie_id', 'prestation_rembourse_id')
    def _validate_delai_attente_prestation(self):
        '''
        Contrôle à affecuer sur la prestation, médicament fournis pour vérifier le délai d'attente à observer
        :return: UserError or None
        '''
        # Contrôle du délai d'attente Substitut Médicament
        # 1. Vérifier s'il s'agit d'une substitution de médicament?
        # self.ensure_one()
        for rec in self:
            if bool (rec.substitut_phcie_id):
                # Récupère la date du jour
                now = datetime.now ()
                substitut_phcie = rec.substitut_phcie
                # Si OUI, y a-t-il un délai d'attente à observer pour le substitut?
                if 0 < int (rec.delai_attente_substitut):
                    # Si OUI, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
                    pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
                        [
                            ('date_execution', '!=', None),
                            ('assure_id', '=', rec.assure_id.id),
                            '|', ('produit_phcie_id', '=', rec.substitut_phcie_id.id),
                            ('substitut_phcie_id', '=', rec.substitut_phcie_id.id),
                        ]
                    )
                    if bool (pec_produit_phcie_assure):
                        # Récupérer la dernière fourniture du médicament prescrit ou substituer
                        dernier_acte_assure = pec_produit_phcie_assure[0]
                        # Récupérer la date de la dernière prescription ou substitution liée au médicament
                        date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
                                            fields.Datetime.from_string (fields.Date.today ())
                        # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
                        nbre_jours_dernier_acte = (
                                now - date_dernier_acte).days  # => différence en les 2 dates en nombre de jours.
                        # Vérifier si le délai d'attente pour le produit est écoulé ou pas?
                        if int (rec.delai_attente_substitut) >= int (nbre_jours_dernier_acte):
                            # Sinon, rejeter la prescription
                            raise ValidationError (_ (
                                u"Proximaas : Contrôle de Règles de Gestion.\n \
                                 L'assuré(e) concerné(e): %s ne peut bénéficier de cette prescription commme substitut \
                                 médicament. Le délai d'attente à observer pour le produit : (%s) est fixé à : \
                                 (%d) jour(s). Ce produit a été prescrit à l'assuré  concerné il y a de cela : (%d) \
                                 jours. Pour plus d'informations, veuillez contactez l'administrateur..."
                            ) % (rec.assure_id.name, substitut_phcie, rec.delai_attente_substitut,
                                 int (nbre_jours_dernier_acte))
                                                   )
            # 2. Vérifier s'il s'agit d'une prescription de médicament?
            elif bool (rec.produit_phcie_id):
                # Récupère la date du jour
                now = datetime.now ()
                produit_phcie = rec.produit_phcie
                # Si OUI, y a-t-il un délai d'attente à observer pour le produit prescrit?
                if 0 < int (rec.delai_attente_produit):
                    # Si OUI, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
                    pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
                        [
                            ('date_execution', '!=', None),
                            ('assure_id', '=', rec.assure_id.id),
                            '|', ('produit_phcie_id', '=', rec.produit_phcie_id.id),
                            ('substitut_phcie_id', '=', rec.produit_phcie_id.id),
                        ]
                    )
                    if bool (pec_produit_phcie_assure):
                        # Récupérer la dernière fourniture du médicament prescrit ou substituer
                        dernier_acte_assure = pec_produit_phcie_assure[0]
                        # Récupérer la date de la dernière prescription ou substitution liée au médicament
                        date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
                                            fields.Datetime.from_string (fields.Date.today ())
                        # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
                        nbre_jours_dernier_acte = (
                                now - date_dernier_acte).days  # => différence en les 2 dates en nombre de jours.
                        # Vérifier si le délai d'attente pour le produit est écoulé ou pas?
                        if int (rec.delai_attente_produit) >= int (nbre_jours_dernier_acte):
                            # Sinon, rejeter la prescription
                            raise ValidationError (_ (
                                u"Proximaas : Contrôle de Règles de Gestion.\n \
                                 L'assuré(e) concerné(e): %s ne peut bénéficier de la prescription de ce médicament. Le délai \
                                 d'attente à observer pour le produit : (%s) est fixé à : (%d) jour(s). Ce produit a été \
                                 prescrit à l'assuré il y a de cela : (%d) jours. Pour plus d'informations, veuillez \
                                 contactez l'administrateur..."
                            ) % (rec.assure_id.name, produit_phcie, rec.delai_attente_produit,
                                 int (nbre_jours_dernier_acte))
                                                   )
            # 3. Vérifier s'il s'agit d'une prestation médicale?
            # delai_attente = int(rec.delai_attente_prestation)
            elif int (rec.delai_attente_prestation) != 0 and self.pec_state != 'dispense':
                # Si OUI, Récupère la date du jour
                now = datetime.now ()
                # Vérifier s'il y a til un délai d'attente à observer pour la prestation concernée?
                # Si OUI, chercher les prestations de l'assure contenant la prestation concernée
                pec_prestations_assure = self.env['proximas.details.pec'].search ([
                    ('date_execution', '!=', False),
                    ('assure_id', '=', rec.assure_id.id),
                    ('prestation_id', '=', rec.prestation_id.id),
                ])
                count_pec_prestations_assure = self.env['proximas.details.pec'].search_count ([
                    ('date_execution', '!=', False),
                    ('assure_id', '=', rec.assure_id.id),
                    ('prestation_id', '=', rec.prestation_id.id),
                ])
                if int (count_pec_prestations_assure) >= 1:
                    # Récupérer la dernier acte liée à la prestation offerte à l'assuré
                    dernier_acte_assure = pec_prestations_assure[0]
                    # Récupérer la date de la dernière prescription ou substitution liée au médicament
                    date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
                                        fields.Datetime.from_string (fields.Date.today ())
                    date_acte_format = datetime.strftime (date_dernier_acte, '%d-%m-%Y')
                    # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
                    nbre_jours_dernier_acte = (now - date_dernier_acte).days
                    # => différence en les 2 dates en nombre de jours.
                    # Vérifier si le délai d'attente pour la prestation est écoulé ou pas?
                    if int (rec.delai_attente_prestation) >= int (nbre_jours_dernier_acte):
                        # Sinon, rejeter la prestation
                        raise ValidationError (_ (
                            u"Proximaas : Contrôle de Règles de Gestion.\n \
                            L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation médicale. \
                            Car le délai d'attente à observer pour la prestation: (%s) est fixé à : (%d) jour(s).\
                            La dernière fois que cet assuré a bénéficié de cette prestation (%s) remonte à : \
                            (%d) jours. Pour plus d'informations, veuillez contactez l'administrateur..."
                        ) % (rec.assure_id.name, rec.prestation_id.name, rec.delai_attente_prestation,
                             date_acte_format, int (nbre_jours_dernier_acte))
                                               )

    # @api.multi
    # @api.onchange('date_execution', 'prestation_id', 'prestation_cro_id', 'prestation_crs_id', 'prestation_demande_id',
    #               'produit_phcie_id', 'substitut_phcie_id', 'prestation_rembourse_id')
    # def _check_delai_attente_prestation(self):
    #     '''
    #     Contrôle à affecuer sur la prestation, médicament fournis pour vérifier le délai d'attente à observer
    #     :return: UserError or None
    #     '''
    #     # Contrôle du délai d'attente Substitut Médicament
    #     # 1. Vérifier s'il s'agit d'une substitution de médicament?
    #    # self.ensure_one()
    #     for rec in self:
    #         if bool(rec.substitut_phcie_id):
    #             # Récupère la date du jour
    #             now = datetime.now ()
    #             substitut_phcie = rec.substitut_phcie
    #             # Si OUI, y a-t-il un délai d'attente à observer pour le substitut?
    #             if 0 < int (rec.delai_attente_substitut):
    #                 # Si OUI, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
    #                 pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
    #                     [
    #                         ('date_execution', '!=', None),
    #                         ('assure_id', '=', rec.assure_id.id),
    #                         '|', ('produit_phcie_id', '=', rec.substitut_phcie_id.id),
    #                         ('substitut_phcie_id', '=', rec.substitut_phcie_id.id),
    #                     ]
    #                 )
    #                 if bool (pec_produit_phcie_assure):
    #                     # Récupérer la dernière fourniture du médicament prescrit ou substituer
    #                     dernier_acte_assure = pec_produit_phcie_assure[0]
    #                     # Récupérer la date de la dernière prescription ou substitution liée au médicament
    #                     date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
    #                                         fields.Datetime.from_string (fields.Date.today ())
    #                     # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
    #                     nbre_jours_dernier_acte = (
    #                             now - date_dernier_acte).days  # => différence en les 2 dates en nombre de jours.
    #                     # Vérifier si le délai d'attente pour le produit est écoulé ou pas?
    #                     if int (rec.delai_attente_substitut) >= int(nbre_jours_dernier_acte):
    #                         # Sinon, rejeter la prescription
    #                         return {'value': {},
    #                                 'warning': {'title': u"Proximaas : Contrôle de Règles de Gestion.",
    #                                             'message': u"L'assuré(e) concerné(e): %s ne peut bénéficier de cette \
    #                                             prescription commme substitut médicament. Le délai d'attente à observer\
    #                                              pour le produit : (%s) est fixé à : (%d) jour(s). Ce produit a été \
    #                                              prescrit à l'assuré  concerné il y a de cela : (%d) jours. Pour plus \
    #                                              d'informations, veuillez contactez l'administrateur..."
    #                                              % (rec.assure_id.name, substitut_phcie,
    #                                                 rec.delai_attente_substitut,
    #                                                 int (nbre_jours_dernier_acte))
    #                                             }
    #                                 }
    #         # 2. Vérifier s'il s'agit d'une prescription de médicament?
    #         elif bool (rec.produit_phcie_id):
    #             # Récupère la date du jour
    #             now = datetime.now ()
    #             produit_phcie = rec.produit_phcie
    #             # Si OUI, y a-t-il un délai d'attente à observer pour le produit prescrit?
    #             if 0 < int (rec.delai_attente_produit):
    #                 # Si OUI, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
    #                 pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
    #                     [
    #                         ('date_execution', '!=', None),
    #                         ('assure_id', '=', rec.assure_id.id),
    #                         '|', ('produit_phcie_id', '=', rec.produit_phcie_id.id),
    #                         ('substitut_phcie_id', '=', rec.produit_phcie_id.id),
    #                     ]
    #                 )
    #                 if bool (pec_produit_phcie_assure):
    #                     # Récupérer la dernière fourniture du médicament prescrit ou substituer
    #                     dernier_acte_assure = pec_produit_phcie_assure[0]
    #                     # Récupérer la date de la dernière prescription ou substitution liée au médicament
    #                     date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
    #                                         fields.Datetime.from_string (fields.Date.today ())
    #                     # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
    #                     nbre_jours_dernier_acte = (
    #                             now - date_dernier_acte).days  # => différence en les 2 dates en nombre de jours.
    #                     # Vérifier si le délai d'attente pour le produit est écoulé ou pas?
    #                     if int (rec.delai_attente_produit) >= int (nbre_jours_dernier_acte):
    #                         # Sinon, rejeter la prescription
    #                         return {'value': {},
    #                                 'warning': {'title': u'Proximaas : Contrôle de Règles de Gestion.',
    #                                             'message': u"Proximaas : Contrôle de Règles de Gestion.\n \
    #                         L'assuré(e) concerné(e): %s ne peut bénéficier de la prescription de ce médicament. \
    #                         Le délai d'attente à observer pour le produit : (%s) est fixé à : (%d) jour(s). Ce produit\
    #                         a été prescrit à l'assuré il y a de cela : (%d) jours. Pour plus d'informations, veuillez \
    #                         contactez l'administrateur..." % (rec.assure_id.name, produit_phcie,
    #                                                                rec.delai_attente_produit,
    #                                                                int(nbre_jours_dernier_acte))
    #                                             }
    #                                 }
    #         # 3. Vérifier s'il s'agit d'une prestation médicale?
    #         # delai_attente = int(rec.delai_attente_prestation)
    #         elif int (rec.delai_attente_prestation) != 0:
    #             # Si OUI, Récupère la date du jour
    #             now = datetime.now()
    #             # Vérifier s'il y a til un délai d'attente à observer pour la prestation concernée?
    #             # Si OUI, chercher les prestations de l'assure contenant la prestation concernée
    #             pec_prestations_assure = self.env['proximas.details.pec'].search (
    #                 [
    #                     ('date_execution', '!=', False),
    #                     ('assure_id', '=', rec.assure_id.id),
    #                     ('prestation_id', '=', rec.prestation_id.id),
    #                 ]
    #             )
    #             count_pec_prestations_assure = self.env['proximas.details.pec'].search_count (
    #                 [
    #                     ('date_execution', '!=', False),
    #                     ('assure_id', '=', rec.assure_id.id),
    #                     ('prestation_id', '=', rec.prestation_id.id),
    #                 ]
    #             )
    #             if int (count_pec_prestations_assure) >= 1:
    #                 # Récupérer la dernier acte liée à la prestation offerte à l'assuré
    #                 dernier_acte_assure = pec_prestations_assure[0]
    #                 # Récupérer la date de la dernière prescription ou substitution liée au médicament
    #                 date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
    #                                     fields.Datetime.from_string (fields.Date.today ())
    #                 date_acte_format = datetime.strftime(date_dernier_acte, '%d-%m-%Y')
    #                 # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
    #                 nbre_jours_dernier_acte = (
    #                         now - date_dernier_acte).days  # => différence en les 2 dates en nombre de jours.
    #                 # Vérifier si le délai d'attente pour la prestation est écoulé ou pas?
    #                 if int (rec.delai_attente_prestation) >= int (nbre_jours_dernier_acte):
    #                     # Sinon, rejeter la prestation
    #                     raise UserError(_(
    #                         u"Proximaas : Contrôle de Règles de Gestion.\n \
    #                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation médicale. \
    #                         Car le délai d'attente à observer pour la prestation: (%s) est fixé à : (%d) jour(s).\
    #                         La dernière fois que cet assuré a bénéficié de cette prestation (%s) remonte à : \
    #                         (%d) jours. Pour plus d'informations, veuillez contactez l'administrateur..."
    #                         ) % (rec.assure_id.name, rec.prestation_id.name, rec.delai_attente_prestation,
    #                            date_acte_format, int(nbre_jours_dernier_acte))
    #                     )
    #
    # @api.constrains('date_execution', 'prestation_id', 'prestation_cro_id', 'prestation_crs_id', 'prestation_demande_id',
    #                'produit_phcie_id', 'substitut_phcie_id', 'prestation_rembourse_id')
    # def _validate_delai_attente_prestation(self):
    #     '''
    #     Contrôle à affecuer sur la prestation, médicament fournis pour vérifier le délai d'attente à observer
    #     :return: UserError or None
    #     '''
    #     # Contrôle du délai d'attente Substitut Médicament
    #     # 1. Vérifier s'il s'agit d'une substitution de médicament?
    #     # self.ensure_one()
    #     for rec in self:
    #         if bool  (rec.substitut_phcie_id):
    #             # Récupère la date du jour
    #             now = datetime.now ()
    #             substitut_phcie = rec.substitut_phcie
    #             # Si OUI, y a-t-il un délai d'attente à observer pour le substitut?
    #             if 0 < int (rec.delai_attente_substitut):
    #                 # Si OUI, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
    #                 pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
    #                     [
    #                         ('date_execution', '!=', None),
    #                         ('assure_id', '=', rec.assure_id.id),
    #                         '|', ('produit_phcie_id', '=', rec.substitut_phcie_id.id),
    #                         ('substitut_phcie_id', '=', rec.substitut_phcie_id.id),
    #                     ]
    #                 )
    #                 if bool (pec_produit_phcie_assure):
    #                     # Récupérer la dernière fourniture du médicament prescrit ou substituer
    #                     dernier_acte_assure = pec_produit_phcie_assure[0]
    #                     # Récupérer la date de la dernière prescription ou substitution liée au médicament
    #                     date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
    #                                         fields.Datetime.from_string (fields.Date.today ())
    #                     # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
    #                     nbre_jours_dernier_acte = (
    #                             now - date_dernier_acte).days  # => différence en les 2 dates en nombre de jours.
    #                     # Vérifier si le délai d'attente pour le produit est écoulé ou pas?
    #                     if int (rec.delai_attente_substitut) >= int (nbre_jours_dernier_acte):
    #                         # Sinon, rejeter la prescription
    #                         raise ValidationError (_ (
    #                             u"Proximaas : Contrôle de Règles de Gestion.\n \
    #                              L'assuré(e) concerné(e): %s ne peut bénéficier de cette prescription commme substitut \
    #                              médicament. Le délai d'attente à observer pour le produit : (%s) est fixé à : \
    #                              (%d) jour(s). Ce produit a été prescrit à l'assuré  concerné il y a de cela : (%d) \
    #                              jours. Pour plus d'informations, veuillez contactez l'administrateur..."
    #                             ) % (rec.assure_id.name, substitut_phcie, rec.delai_attente_substitut,
    #                                int (nbre_jours_dernier_acte))
    #                         )
    #         # 2. Vérifier s'il s'agit d'une prescription de médicament?
    #         elif bool(rec.produit_phcie_id):
    #             # Récupère la date du jour
    #             now = datetime.now ()
    #             produit_phcie = rec.produit_phcie
    #             # Si OUI, y a-t-il un délai d'attente à observer pour le produit prescrit?
    #             if 0 < int (rec.delai_attente_produit):
    #                 # Si OUI, chercher les prescriptions de l'assure contenant le médicament (ou substituer)
    #                 pec_produit_phcie_assure = self.env['proximas.details.pec'].search (
    #                     [
    #                         ('date_execution', '!=', None),
    #                         ('assure_id', '=', rec.assure_id.id),
    #                         '|', ('produit_phcie_id', '=', rec.produit_phcie_id.id),
    #                         ('substitut_phcie_id', '=', rec.produit_phcie_id.id),
    #                     ]
    #                 )
    #                 if bool (pec_produit_phcie_assure):
    #                     # Récupérer la dernière fourniture du médicament prescrit ou substituer
    #                     dernier_acte_assure = pec_produit_phcie_assure[0]
    #                     # Récupérer la date de la dernière prescription ou substitution liée au médicament
    #                     date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
    #                                         fields.Datetime.from_string (fields.Date.today ())
    #                     # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
    #                     nbre_jours_dernier_acte = (
    #                             now - date_dernier_acte).days  # => différence en les 2 dates en nombre de jours.
    #                     # Vérifier si le délai d'attente pour le produit est écoulé ou pas?
    #                     if int (rec.delai_attente_produit) >= int (nbre_jours_dernier_acte):
    #                         # Sinon, rejeter la prescription
    #                         raise ValidationError (_ (
    #                             u"Proximaas : Contrôle de Règles de Gestion.\n \
    #                              L'assuré(e) concerné(e): %s ne peut bénéficier de la prescription de ce médicament. Le délai \
    #                              d'attente à observer pour le produit : (%s) est fixé à : (%d) jour(s). Ce produit a été \
    #                              prescrit à l'assuré il y a de cela : (%d) jours. Pour plus d'informations, veuillez \
    #                              contactez l'administrateur..."
    #                             ) % (rec.assure_id.name, produit_phcie, rec.delai_attente_produit,
    #                                int (nbre_jours_dernier_acte))
    #                         )
    #         # 3. Vérifier s'il s'agit d'une prestation médicale?
    #         # delai_attente = int(rec.delai_attente_prestation)
    #         elif int(rec.delai_attente_prestation) != 0:
    #             # Si OUI, Récupère la date du jour
    #             now = datetime.now ()
    #             # Vérifier s'il y a til un délai d'attente à observer pour la prestation concernée?
    #             # Si OUI, chercher les prestations de l'assure contenant la prestation concernée
    #             pec_prestations_assure = self.env['proximas.details.pec'].search (
    #                 [
    #                     ('date_execution', '!=', False),
    #                     ('assure_id', '=', rec.assure_id.id),
    #                     ('prestation_id', '=', rec.prestation_id.id),
    #                 ]
    #             )
    #             count_pec_prestations_assure = self.env['proximas.details.pec'].search_count (
    #                 [
    #                     ('date_execution', '!=', False),
    #                     ('assure_id', '=', rec.assure_id.id),
    #                     ('prestation_id', '=', rec.prestation_id.id),
    #                 ]
    #             )
    #             if int(count_pec_prestations_assure) >= 1:
    #                 # Récupérer la dernier acte liée à la prestation offerte à l'assuré
    #                 dernier_acte_assure = pec_prestations_assure[0]
    #                 # Récupérer la date de la dernière prescription ou substitution liée au médicament
    #                 date_dernier_acte = fields.Datetime.from_string (dernier_acte_assure.date_execution) or \
    #                                     fields.Datetime.from_string (fields.Date.today ())
    #                 date_acte_format = datetime.strftime (date_dernier_acte, '%d-%m-%Y')
    #                 # Calcul le nombre de jours écoulés entre la dernière prestation liée à la rubrique et aujourd'hui
    #                 nbre_jours_dernier_acte = (
    #                         now - date_dernier_acte).days  # => différence en les 2 dates en nombre de jours.
    #                 # Vérifier si le délai d'attente pour la prestation est écoulé ou pas?
    #                 if int (rec.delai_attente_prestation) >= int (nbre_jours_dernier_acte):
    #                     # Sinon, rejeter la prestation
    #                     raise ValidationError (_ (
    #                         u"Proximaas : Contrôle de Règles de Gestion.\n \
    #                         L'assuré(e) concerné(e): %s ne peut bénéficier de cette prestation médicale. \
    #                         Car le délai d'attente à observer pour la prestation: (%s) est fixé à : (%d) jour(s).\
    #                         La dernière fois que cet assuré a bénéficié de cette prestation (%s) remonte à : \
    #                         (%d) jours. Pour plus d'informations, veuillez contactez l'administrateur..."
    #                         ) % (rec.assure_id.name, rec.prestation_id.name, rec.delai_attente_prestation,
    #                            date_acte_format, int (nbre_jours_dernier_acte))
    #                     )

    @api.constrains('prestation_id')
    def _validate_prestation_crs(self):
        for rec in self:
            if bool(rec.pool_medical_crs_id) and not bool(rec.prestation_id):
                raise ValidationError(_(
                    u"Proximaas : Contrôle de Règles de Gestion:\n \
                    La prestation demandée: %s ne figure pas dans la liste des prestations fournies par \
                    le prestataire: %s. Par conséquent, cette prestation ne peut être prise en compte dans le cadre \
                    de la convention signée avec le prestataire concernée. Pour plus d'informations, \
                    veuillez contactez l'administrateur..."
                    ) % (rec.prestation_demande_id.name, rec.prestataire_crs_id.name)
                )

    # @api.depends('police_id', 'structure_id', 'prestation_id')
    #@api.onchange('date_execution', 'date_demande')
    # @api.multi
    @api.constrains('date_execution', 'date_demande', 'exercice_id')
    @api.depends('date_execution', 'date_demande', 'exercice_id')
    def _get_exo_sam(self):
        for rec in self:
            exercices = self.env['proximas.exercice'].search([
                ('res_company_id', '=', rec.structure_id.id),
                ('cloture', '=', False),
            ])
            if bool(exercices):
                for exo in exercices:
                    date_debut = fields.Date.from_string (exo.date_debut)
                    date_fin = fields.Date.from_string (exo.date_fin)
                    if bool(rec.date_execution) and not bool(rec.date_demande):
                        date_execution = fields.Date.from_string (rec.date_execution)
                        if date_debut <= date_execution <= date_fin:
                            rec.exercice_id = exo.id
                    elif bool(rec.date_execution) and bool(rec.date_demande):
                        date_execution = fields.Date.from_string (rec.date_execution)
                        if date_debut <= date_execution <= date_fin:
                            rec.exercice_id = exo.id
                    elif bool(rec.date_demande):
                        date_demande = fields.Date.from_string (rec.date_demande)
                        if date_debut <= date_demande <= date_fin:
                            rec.exercice_id = exo.id
                if rec.date_execution and not bool(rec.exercice_id):
                    date_execution = fields.Datetime.from_string (self.date_execution)
                    date_execution_format = datetime.strftime (date_execution, '%d-%m-%Y')
                    raise ValidationError (_ (
                        u"Proximaas : Contrôle de Règles de Gestion:\n \
                        La date d'exécution renseignée ici: %s n'est conforme à aucun des exercices \
                        paramétrés à cet effet ou l'exercice concerné est  clôturé. Par conséquent, les prestations\
                        offertes à cette période ne peuvent plus faire l'objet d'un traitement dans le système.\
                        Pour plus d'informations, veuillez contactez l'administrateur..."
                    ) % date_execution_format
                                           )
                elif rec.date_demande and not bool(rec.exercice_id):
                    date_demande = fields.Datetime.from_string (self.date_demande)
                    date_demande_format = datetime.strftime (date_demande, '%d-%m-%Y')
                    raise ValidationError (_ (
                        u"Proximaas : Contrôle de Règles de Gestion:\n \
                        La date d'exécution renseignée ici: %s n'est conforme à aucun des exercices \
                        paramétrés à cet effet ou l'exercice concerné est  clôturé. Par conséquent, les prestations\
                        offertes à cette période ne peuvent plus faire l'objet d'un traitement dans le système.\
                        Pour plus d'informations, veuillez contactez l'administrateur..."
                    ) % date_demande_format
                                           )

                    # elif bool(exo.en_cours):
                    #     rec.exercice_id = exo.id


    # @api.one
    # @api.depends('prestation_crs_id')
    # def need_action_validation(self, cr, uid, context):
    #     if not (self.prestation_demande_id) and not (self.date_demande):
    #         group = self.env['res.groups'].search([('category_id.name', 'ilike', 'Admin-SAM')])
    #         recipient_partners = []
    #         for recipient in group.users:
    #             recipient_partners.append(
    #                 [(4, recipient.partner_id.id)]
    #             )
    #         self.env['mail.message'].create({
    #             'message_type': "notification",
    #             'subtype': self.env.ref("mail.mt_comment").id,
    #             'subject': u"Demande Validation Prestations CRS",
    #             'body': u"Le Centre d'orientation (CRS) : %s est en attente de la validation \
    #                       de la prestation suivante : \n Date Exécution:%s\n \
    #                       Prestation médicale: %s \n Code PEC: %s \n Code ID.: %s \n Assuré: %s \n Genre: %s \n \
    #                       Statut familial: %s."
    #                     % (self.prestataire.name, self.date_execution, self.details_prestation,
    #                        self.num_pec, self.code_id, self.assure_id.name, self.genre, self.statut_familial
    #                        ),
    #             'needaction_partner_ids': recipient_partners,
    #             'model': self._name,
    #             'res_id': self.id,
    #         })
    #         post_vars = {
    #             'subject': "Demande Validation Prestations CRS",
    #             'body': "Le Centre d'orientation (CRS) : %s est en attente de la validation \
    #                     de la prestation suivante : \n Date Exécution:%s\n \
    #                     Prestation médicale: %s \n Code PEC: %s \n Code ID.: %s \n Assuré: %s \n Genre: %s \n \
    #                     Statut familial: %s."
    #                     % (
    #                         self.prestataire.name, self.date_execution, self.details_prestation,
    #                         self.num_pec, self.code_id, self.assure_id.name, self.genre, self.statut_familial
    #                     ),
    #             'partner_ids': recipient_partners,
    #         }
    #         thread_pool = self.pool.get('mail.thread')
    #         thread_pool.message_post(
    #             cr, uid, False,
    #             type="notification",
    #             subtype="mt_comment",
    #             context=context,
    #             **post_vars
    #         )

    @api.onchange('date_execution', 'date_demande')
    def _check_exo_sam(self):
        if bool (self.date_execution) and not bool(self.exercice_id):
            date_execution = fields.Datetime.from_string (self.date_execution)
            date_execution_format = datetime.strftime (date_execution, '%d-%m-%Y')
            raise UserError (_ (
                u"Proximaas : Contrôle de Règles de Gestion:\n \
                La date d'exécution renseignée ici: %s n'est conforme à aucun des exercices \
                paramétrés à cet effet ou l'exercice concerné est clôturé. Par conséquent, les prestations\
                offertes à cette période ne peuvent plus faire l'objet d'un traitement dans le système.\
                Pour plus d'informations, veuillez contactez l'administrateur..."
            ) % date_execution_format
                             )
        elif bool(self.date_demande) and not bool(self.exercice_id):
            date_demande = fields.Datetime.from_string (self.date_demande)
            date_demande_format = datetime.strftime (date_demande, '%d/%m/%Y')
            raise UserError (_ (
                u"Proximaas : Contrôle de Règles de Gestion:\n \
                La date de la demande renseignée ici: %s n'est conforme à aucun des exercices \
                paramétrés à cet effet ou l'exercice concerné est clôturé. Par conséquent, les prestations\
                offertes à cette période ne peuvent plus faire l'objet d'un traitement dans le système.\
                Pour plus d'informations, veuillez contactez l'administrateur..."
            ) % date_demande_format
                             )

    # @api.constrains('date_demande', 'date_execution')
    # def _validate_exo_sam(self):
    #     for rec in self:
    #         if bool(rec.date_execution) and not bool(rec.exercice_id):
    #             date_execution = fields.Datetime.from_string(rec.date_execution)
    #             date_execution_format = datetime.strftime(date_execution, '%d-%m-%Y')
    #             raise ValidationError(_(
    #                 u"Proximaas : Contrôle de Règles de Gestion:\n \
    #                 La date d'exécution renseignée ici: %s n'est conforme à aucun des exercices \
    #                 paramétrés à cet effet ou l'exercice concerné est  clôturé. Par conséquent, les prestations\
    #                 offertes à cette période ne peuvent plus faire l'objet d'un traitement dans le système.\
    #                 Pour plus d'informations, veuillez contactez l'administrateur..."
    #                 ) % date_execution_format
    #             )
    #         elif bool(rec.date_demande) and not bool(rec.exercice_id):
    #             date_demande = fields.Datetime.from_string (rec.date_demande)
    #             date_demande_format = datetime.strftime (date_demande, '%d/%m/%Y')
    #             raise ValidationError (_ (
    #                 u"Proximaas : Contrôle de Règles de Gestion:\n \
    #                 La date de la demande renseignée ici: %s n'est conforme à aucun des exercices \
    #                 paramétrés à cet effet ou l'exercice concerné est  clôturé. Par conséquent, les prestations\
    #                 offertes à cette période ne peuvent plus faire l'objet d'un traitement dans le système.\
    #                 Pour plus d'informations, veuillez contactez l'administrateur..."
    #                 ) % date_demande_format
    #             )

    sql_constraints = [
        (
            'unique_prestation_cro',
            'UNIQUE(pec_id,prestation_cro_id)',
            '''
            Proximas: Risque de doublon sur Prestation: Centre de référence obligatoire (CRO)!
            Il semble que cette prestation ait déjà été fournie pour cette prise en charge. Par conséquent, il ne peut 
            y avoir plus d'une fois la même prestation offerte sur une même prise en charge.
            Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
            '''
        ),
        (
            'unique_prestation_crs',
            'UNIQUE(pec_id,prestation_crs_id)',
            '''
            Proximas: Risque de doublon sur Prestation: Centre d'orientation (CRS)!
            Il semble que cette prestation ait déjà été fournie pour cette prise en charge. Par conséquent, il ne peut 
            y avoir plus d'une fois la même prestation offerte sur une même prise en charge.
            Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
            '''
        ),
        (
            'unique_prestation_demande',
            'UNIQUE(pec_id,prestation_demande_id)',
            '''
            Proximas: Risque de doublon sur Prestation: Demande de Prestation Centre d'orientation (CRS)!
            Il semble que cette prestation ait déjà été fournie pour cette prise en charge. Par conséquent, il ne peut 
            y avoir plus d'une fois la même prestation offerte sur une même prise en charge.
            Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
            '''
        ),
        (
            'unique_produit_phcie',
            'UNIQUE(pec_id,produit_phcie_id)',
            '''
            Proximas: Risque de doublon sur Médicament: 
            Il semble que ce médicament ait déjà été prescrit pour cette prise en charge. Par conséquent, il ne peut 
            y avoir plus d'une fois le même médicament prescrit sur une même prise en charge.
            Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
            '''
        ),
        (
            'unique_substitut_phcie',
            'UNIQUE(pec_id,substitut_phcie_id)',
            '''
            Proximas: Risque de doublon sur Substitut Médicament: 
            Il semble que ce médicament ait déjà été fourni comme substitut pour cette prise en charge. Par conséquent, 
            il ne peut y avoir plus d'une fois le même substitut médicament sur une même prise en charge.
            Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
            '''
        ),
    ]

# from openerp.osv import osv, fields
# import logging
#
# class proximas_details_pec(osv.osv):
#     _inherit = 'proximas.details.pec'
#     _columns = {}
#
#     issue = ''
#     templtate = ''
#
#     def create(self, cr, uid, vals, context=None):
#         res = super(proximas_details_pec, self).create(cr, uid, vals, context=context)
#
#         self.issue = self.pool.get('proximas.details.pec').browse(cr, uid, res, context=context)
#
#         manager = self.issue.project_id.user_id.partner_id.id
#         #
#         # assignTo = self.issue.user_id.partner_id.id
#
#         post_vars = {
#             'subject': ("Issue {} has been created".format(self.issue.name)),
#             'body': ("PEC {} has been created".format(self.issue.name)),
#             'partner_ids': [(4, manager)],
#         }
#         thread_pool = self.pool.get('mail.thread')
#         thread_pool.message_post(cr, uid, False,
#                                  context=context,
#                                  **post_vars)
#         return res

########################################################################################################################
#                                    GESTION REMBOURSEMENT FRAIS MEDICAUX                                              #
########################################################################################################################

class RemboursementPEC(models.Model):
    _name = 'proximas.remboursement.pec'
    _description = 'Remboursement Frais Medicaux'
    _order = 'date_saisie desc'
    _inherit = ['mail.thread']

    # name = fields.Char()
    sequence = fields.Integer(
        string="Sequence",
    )
    num_fiche = fields.Char(
        string="Réf./Num. Fiche",
        help="Indiquer le N° de référence de la fiche de remboursement",
    )
    code_rfm = fields.Char(
        string="Code Remboursement",
        compute='_get_code_rfm',
        store=True,
        help='Code de référence du dossier de remboursement généré automatiquement par la système.'
    )
    code_remb = fields.Char(
        string="Code RFM",
        compute='_get_code_remb',
        help="Code RFM généré par la système.",
    )
    date_saisie = fields.Datetime(
        string="Date Enregistrement",
        default=fields.Datetime.now,
        readonly=False,
    )
    date_depot = fields.Date(
        string="Date Dépôt",
        readonly=False,
    )
    date_transmis = fields.Date(
        string="Date Emission",
        default=fields.Datetime.now,
        help="Indiquer la date à laquelle le remboursement a été émise à la comptabilité pour règlement..."
    )
    state = fields.Selection(
        string="Statut",
        selection=[
                ('create', 'Création'),
                ('valide', 'Validation'),
                ('boucle', 'Terminé')
                ],
        default="create",
    )
    code_saisi = fields.Char(
        string="Code ID. Adhérent",
    )
    prestataire_id = fields.Many2one(
        comodel_name='res.partner',
        string="Ets. Non Conventionné",
        domain=[
            ('is_prestataire', '=', True),
        ],
    )
    details_rfm_soins_ids = fields.One2many(
        comodel_name="proximas.details.pec",
        inverse_name="rfm_id",
        domain=[
            ('rfm_id', '!=', None),
            ('produit_phcie_id', '=', None)
        ],
        string='Exécution Prestation Médicale',
        required=False,
    )
    details_rfm_phcie_ids = fields.One2many(
        comodel_name="proximas.details.pec",
        inverse_name="rfm_id",
        domain=[
            ('rfm_id', '!=', None),
            ('produit_phcie_id', '!=', None),
            # ('arret_produit', '=', False),

        ],
        string='Dispensation Médicament',
    )
    doc_joint = fields.Binary(
        string="Facture pièce jointe",
        # attachment=True,
    )
    doc_filename = fields.Char (
        "Nom du fichier joint",
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # POLICE DETAILS & ADHERENT
    # Champs relatifs Identifiants Assuré
    contrat_id = fields.Many2one(
        comodel_name="proximas.contrat",
        string="Contrat",
        # compute='_get_contrat_id',
        # store=True,

    )
    adherent_id = fields.Many2one(
        comodel_name="proximas.adherent",
        string="Adhérent",
        related='contrat_id.adherent_id',
        # store=True,
        readonly=True,
    )
    contrat_actif = fields.Boolean(
        string="Contrat Activé?",
        related='contrat_id.actif',
        help="Indique l'état du contrat (actif ou non).",
    )
    date_activation = fields.Date(
        string="Date Prise Effet",
        related='contrat_id.date_activation',
        help='Date à laquelle le contrat est activé (date de prise d\'effet).'
    )
    police_id = fields.Many2one(
        # comodel_name="proximas.police",
        string="Police Couverture",
        related='contrat_id.police_id',
        store=True,
        readonly=True,
    )
    num_contrat = fields.Char(
        string="Num. Contrat",
        related='contrat_id.num_contrat',
        readonly=True,
    )
    structure_id = fields.Many2one(
        omodel_name="res.company",
        string="Organisation(SAM)",
        related='contrat_id.structure_id',
        readonly=True,
    )
    groupe_id = fields.Many2one (
        string="Organisation(SAM)",
        related='contrat_id.groupe_id',
        readonly=True,
    )
    matricule = fields.Char (
        string="Matricule",
        related='adherent_id.matricule',
        readonly=True,
    )
    code_id = fields.Char(
        string="Code ID.",
        related="adherent_id.code_id",
        store=True,
        readonly=True,
    )
    code_id_externe = fields.Char(
        string="Code ID. Externe",
        related="adherent_id.code_id_externe",
        store=True,
        readonly=True,
    )
    nom = fields.Char (
        string="Nom",
        related="adherent_id.nom",
        readonly=True,
    )
    prenoms = fields.Char(
        string="Prénom(s)",
        related="adherent_id.prenoms",
        readonly=True,
    )
    name = fields.Char(
        string="Noms et Prénoms",
        related="adherent_id.display_name",
        readonly=True,
    )
    statut_familial = fields.Selection(
        string="Statut Familial",
        related='adherent_id.statut_familial',
        readonly=True,
    )
    genre = fields.Selection(
        string="Genre",
        related='adherent_id.genre',
        readonly=True,
    )
    date_naissance = fields.Date (
        string="Date Naissance",
        related="adherent_id.date_naissance",
        readonly=True,
    )
    age = fields.Char (
        string="Age",
        related="adherent_id.age",
        readonly=True,
    )
    age_details = fields.Char(
        string="Age",
        related="adherent_id.age_details",
        readonly=True,
    )
    image = fields.Binary(
        string="Photo",
        related="adherent_id.image",
        readonly=True,
    )
    # Champs de contrôle contrat police
    mode_controle_plafond = fields.Selection(
        string="Mode Contrôle Plafond Contrat?",
        related='police_id.mode_controle_plafond',
        readonly=True,
    )
    validite_demande_remb = fields.Integer(
        string="Délai Validité Remb. (jours)",
        related='police_id.validite_demande_remb',
        readonly=True,
        help='Délai de validité pour le remboursement de l\'acte médical(en nombre de jours).',
    )
    nbre_maxi_demande = fields.Integer(
        string="Nbre. maxi de demandes de remboursement",
        related='police_id.nbre_maxi_demande',
        readonly=True,
    )
    mt_plafond_remb_demande = fields.Float (
        string="Montant Plafond/Demande (remboursement)",
        digits=(6, 0),
        related='police_id.mt_plafond_remb_demande',
        readonly=True,
    )
    mt_plafond_remb_individu = fields.Float (
        string="Montant Plafond/Individu (remboursement)",
        digits=(6, 0),
        related='police_id.mt_plafond_remb_individu',
        readonly=True,
    )
    mt_plafond_remb_famille = fields.Float (
        string="Montant Plafond/Famille (remboursement)",
        digits=(6, 0),
        related='police_id.mt_plafond_remb_famille',
        readonly=True,
    )
    plafond_individu = fields.Float(
        string="Plafond individu",
        digits=(9, 0),
        related='police_id.plafond_individu',
        readonly=True,
    )
    plafond_famille = fields.Float(
        string="Plafond Famille",
        digits=(9, 0),
        related='police_id.plafond_famille',
        default=0,
        readonly=True,
    )
    # Contrôles relatifs au contrat global
    niveau_sinistre_assure = fields.Float(
        string="Niveau Sinistre Assuré",
        compute='_compute_rfm_details',
        default=0,
    )
    niveau_sinistre_contrat = fields.Float(
        string="Niveau Sinistre Contrat",
        compute='_compute_rfm_details',
        default=0,
    )
    totaux_contrat = fields.Float(
        string="S/Totaux Famille",
        digits=(9, 0),
        related='contrat_id.sous_totaux_contrat',
        default=0,
        readonly=True,
    )
    # Sous-Totaux Actes Remboursement Adhérent
    nbre_actes_remb = fields.Integer(
        string="Nbre. Actes Médicaux",
        compute='_compute_rfm_details',
        default=0,
    )
    sous_totaux_actes_remb = fields.Float(
        string="S/Totaux Actes Remb.",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    sous_totaux_actes_pc_remb = fields.Float (
        string="S/Totaux Actes(Couverts)",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    sous_totaux_actes_npc_remb = fields.Float(
        string="S/Totaux Actes(Non Couverts)",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    sous_totaux_part_sam_remb = fields.Float (
        string="S/Totaux Part SAM",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    sous_totaux_ticket_moderateur_remb = fields.Float (
        string="S/Totaux Net Ticket Modérateur",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    sous_totaux_exclusions_remb = fields.Float (
        string="S/Totaux Exclusions.",
        digits=(6, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    net_remboursement_actes_remb = fields.Float(
        string="Totaux (Net A Payer Actes(Remb.)",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    # Sous-Totaux Prescriptions Remboursement Adhérent
    nbre_presciptions_remb = fields.Integer(
        string="Nbre. Prescriptions",
        compute='_compute_rfm_details',
        default=0,
    )
    sous_totaux_phcie_remb = fields.Float(
        string="S/Totaux Remb. Phcie.",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    net_part_sam_phcie = fields.Float (
        string="Net Part SAM (Phcie.)",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    net_ticket_moderateur_phcie = fields.Float (
        string="Net Part SAM (Phcie.)",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    net_exclusions_phcie = fields.Float (
        string="Net Exclusions (Phcie.)",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    net_remboursement_phcie = fields.Float (
        string="Net Remb.(Phcie.)",
        digits=(9, 0),
        compute='_compute_rfm_details',
        default=0,
    )
    # Calculs de synthèse remboursement
    # Sous-Totaux Cumuls (Actes + Prescriptions) Remboursement Adhérent
    net_totaux_rfm = fields.Float(
        string="Totaux Remb.",
        digits=(9, 0),
        compute='_compute_rfm_details',
        # store=True,
        default=0,
        # related='assure_id.sous_totaux_pec',
    )
    net_part_sam_rfm = fields.Float(
        string="Net Remb. Part SAM",
        digits=(9, 0),
        compute='_compute_rfm_details',
        # store=True,
        default=0,
    )
    net_ticket_moderateur_rfm = fields.Float (
        string="Net Remb. Ticket Mod.",
        digits=(9, 0),
        compute='_compute_rfm_details',
        # store=True,
        default=0,
    )
    net_exclusions_rfm = fields.Float (
        string="Net Exclusions",
        digits=(9, 0),
        compute='_compute_rfm_details',
        # store=True,
        default=0,
    )
    net_remboursement_rfm = fields.Float(
        string="Totaux (Net A Payer (Remb.)",
        digits=(9, 0),
        compute='_compute_rfm_details',
        # store=True,
        default=0,
    )
    net_remb_texte = fields.Char(
        string="MNet Remb.(Taxte)",
        compute="montant_en_text",
        readonly=True,
    )
    nbre_prestations_fournies = fields.Integer(
        string="nbre. Prestations",
        compute='_check_nbre_details_rfm',
        required=False,
    )
    nbre_prescriptions = fields.Integer(
        string="nbre. Prescriptions",
        compute='_check_nbre_details_rfm',
        required=False,
    )
    ####################################################################################################################
    date_last_rfm = fields.Date(
        string="Dernière PEC",
        compute='_check_date_last_rfm',
        help='Date de la dernière prise en charge de l\'assuré concerné',
        readonly=True,
    )

    nbre_prescription_maxi = fields.Integer(
        string="Nbre. maxi Prescriptions",
        related='police_id.nbre_prescription_maxi',
        readonly=True,
    )
    mt_plafond_prescription = fields.Float(
        string="Montant Plafond/Prescription",
        related='police_id.mt_plafond_prescription',
        readonly=True,
    )
    leve_plafond_prescription = fields.Boolean(
        string="Lever Plafond Prescription",
        help='Attention! En cochant, cela permet de lever le plafond pour les prescriptions. le système ne contrôlera \
        plus les montants de plafond pour les prescription sur cette prise en charge uniquement.',
    )
    marge_medicament = fields.Float(
        string='Marge/Produit Phcie.',
        help="Marge tolérée sur le coût des produits pharmaceutiques",
        digits=(5, 0),
        related='police_id.marge_medicament',
        readonly=True,
    )
    date_user = fields.Datetime(
        string="Date User",
        compute='_get_date_user',
        default=datetime.now(),  # fields.Date.today(),
        readonly=True,
    )
    current_user = fields.Many2one(
        comodel_name="res.users",
        string="Utilisateur en cours",
        compute='_get_current_user',
        required=False,
    )
    user_prise_charge = fields.Boolean(
        string="Utitlisateur/Prise charge?",
        compute='_get_current_user',
        #store=True,
        help='Défini si l\'utilisateur courant est le prestataire exécutant de la prise en charge?',
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Créee Par",
        required=False,
    )
    is_valide = fields.Boolean(
        string="PEC valide?",
        compute='_check_valide_rfm',
        help="Indique si la prise en charge est valide (PEC) ou non",
    )


    @api.multi
    def _get_contrat_id(self):
        for rec in self:
            adherent = self.env['proximas.adherent'].search([
                ('id', '=', rec.adherent_id.id),
            ])
            contrat = self.env['proximas.contrat'].search([('adherent_id', '=', adherent.id)])
            if bool(contrat):
                rec.contrat_id = contrat.id

    @api.multi
    def action_creer(self):
        self.state = 'create'

    @api.multi
    def action_valider(self):
        self.state = 'valide'

    @api.multi
    def action_boucler(self):
        self.state = 'termine'


    @api.multi
    def _check_valide_rfm(self):
        for rec in self:
            if rec.state == 'valide':
                rec.is_valie = True
            else:
                rec.is_valie = False


    @api.multi
    def _get_date_user(self):
        for rec in self:
            rec.date_user = datetime.now()

    @api.multi
    def _get_current_user(self):
        for rec in self:
            user_id = self.env.context.get('uid')
            group_id = self.env.context.get('gid')
            user = self.env['res.users'].search([('id', '=', user_id)])
            prestataire = self.env['res.partner'].search([('id', '=', user.partner_id.id)])
            rec.current_user = user_id
            rec.user_prestataire = user.partner_id.name
            if rec.prestataire_cro == rec.user_prestataire:
                rec.user_prise_charge = True


    @api.multi
    def _check_date_last_rfm(self):
        for rec in self:
            rfm_adherent = self.env['proximas.remboursement.pec'].search([
                ('adherent_id', '=', rec.adherent_id.id),
            ])
            if bool(rfm_adherent):
                count_rfm = len(rfm_adherent)
                if count_rfm == 1:
                    rec.date_last_rfm = rfm_adherent.date_saisie
                else:
                    last_rfm = rfm_adherent[1]
                    rec.date_last_rfm = last_rfm.date_saisie


    @api.depends('details_rfm_soins_ids', 'details_rfm_phcie_ids')
    @api.onchange('details_rfm_soins_ids', 'details_rfm_phcie_ids')
    def _check_nbre_details_rfm(self):
        for rec in self:
            rec.nbre_prestations_fournies = len(rec.details_rfm_soins_ids)
            # self.nbre_prestations_demandes = len(self.details_rfm_soins_crs_ids)
            rec.nbre_prescriptions = len(rec.details_rfm_phcie_ids)
            # self.totaux_phcie = sum(item.total_pc for item in details_pec_assure) or 0
            # self.totaux_phcie_estimation = sum(item.prix_indicatif_produit for item in details_pec_assure) or 0

    # GESTION DE CONTRÔLES SUR LES PLAFONDS
    # @api.onchange('nbre_maxi_demande', 'mt_plafond_remb_demande', 'mt_plafond_remb_famille', 'plafond_famille')
    # def check_state_plafond(self):
    #     pass

    @api.one
    @api.depends('nbre_actes_remb', 'net_remboursement_rfm', 'details_rfm_soins_ids', 'details_rfm_phcie_ids')
    def montant_en_text(self):
        self.ensure_one()
        convert_lettre = amount_to_text_fr(self.net_remboursement_rfm, 'Francs')
        list_text = convert_lettre.split()
        montant_text = " ".join(list_text[0:-2])
        self.net_remb_texte = montant_text.upper()
        return montant_text.upper()

    @api.one
    @api.onchange('nbre_actes_remb', 'net_remboursement_rfm', 'details_rfm_soins_ids', 'details_rfm_phcie_ids')
    # @api.onchange('net_remboursement_rfm', 'details_rfm_soins_ids', 'details_rfm_phcie_ids')
    def _computed_details_rfm(self):
        self.ensure_one()
        if bool(self.details_rfm_soins_ids):
            # 1. Calculs détails Actes médicaux
            details_actes_rfm = self.details_rfm_soins_ids
            self.nbre_actes_remb = len(details_actes_rfm)
            self.sous_totaux_actes_remb = sum(item.cout_total for item in details_actes_rfm) or 0
            self.sous_totaux_actes_pc_remb = sum(item.total_pc for item in details_actes_rfm) or 0
            self.sous_totaux_actes_npc_remb = sum(item.total_npc for item in details_actes_rfm) or 0
            self.sous_totaux_part_sam_remb = sum (item.net_tiers_payeur for item in details_actes_rfm) or 0
            self.sous_totaux_ticket_moderateur_remb = sum (item.ticket_moderateur for item in details_actes_rfm) or 0
            self.sous_totaux_exclusions_remb = sum (item.mt_exclusion for item in details_actes_rfm) or 0
            self.net_remboursement_actes_remb = sum (item.mt_remboursement for item in details_actes_rfm) or 0
        if bool(self.details_rfm_phcie_ids):
            # 2. Calculs détails Pharmacie
            details_phcie_rfm = self.details_rfm_phcie_ids
            self.nbre_prescriptions_remb = len (details_phcie_rfm)
            self.sous_totaux_phcie_remb = sum (item.cout_total for item in details_phcie_rfm) or 0
            self.net_part_sam_phcie = sum (item.net_tiers_payeur for item in details_phcie_rfm) or 0
            self.net_ticket_moderateur_phcie = sum (item.ticket_moderateur for item in details_phcie_rfm) or 0
            self.net_exclusions_phcie = sum(item.mt_exclusion for item in details_phcie_rfm) or 0
            self.net_remboursement_phcie = sum (item.mt_remboursement for item in details_phcie_rfm) or 0
        # 3. Calculs Cumuls Actes médicaux + Médicaments
        self.net_totaux_rfm = self.sous_totaux_actes_remb + self.sous_totaux_phcie_remb
        self.net_part_sam_rfm = self.sous_totaux_part_sam_remb + self.net_part_sam_phcie
        self.net_ticket_moderateur_rfm = self.sous_totaux_ticket_moderateur_remb + self.net_ticket_moderateur_phcie
        self.net_exclusions_rfm = self.sous_totaux_exclusions_remb + self.net_exclusions_phcie
        self.net_remboursement_rfm = self.net_remboursement_actes_remb + self.net_remboursement_phcie
    
    @api.multi
    def _compute_rfm_details(self):
        for rec in self:
            if bool(rec.details_rfm_soins_ids):
                # 1. Calculs détails Actes médicaux
                details_actes_rfm = rec.details_rfm_soins_ids
                rec.nbre_actes_remb = len (details_actes_rfm)
                rec.sous_totaux_actes_remb = sum (item.cout_total for item in details_actes_rfm) or 0
                rec.sous_totaux_actes_pc_remb = sum (item.total_pc for item in details_actes_rfm) or 0
                rec.sous_totaux_actes_npc_remb = sum (item.total_npc for item in details_actes_rfm) or 0
                rec.sous_totaux_part_sam_remb = sum (item.net_tiers_payeur for item in details_actes_rfm) or 0
                rec.sous_totaux_ticket_moderateur_remb = sum (
                    item.ticket_moderateur for item in details_actes_rfm) or 0
                rec.sous_totaux_exclusions_remb = sum (item.mt_exclusion for item in details_actes_rfm) or 0
                rec.net_remboursement_actes_remb = sum (item.mt_remboursement for item in details_actes_rfm) or 0
            if bool (rec.details_rfm_phcie_ids):
                # 2. Calculs détails Pharmacie
                details_phcie_rfm = rec.details_rfm_phcie_ids
                rec.nbre_prescriptions_remb = len (details_phcie_rfm)
                rec.sous_totaux_phcie_remb = sum (item.cout_total for item in details_phcie_rfm) or 0
                rec.net_part_sam_phcie = sum (item.net_tiers_payeur for item in details_phcie_rfm) or 0
                rec.net_ticket_moderateur_phcie = sum (item.ticket_moderateur for item in details_phcie_rfm) or 0
                rec.net_exclusions_phcie = sum (item.mt_exclusion for item in details_phcie_rfm) or 0
                rec.net_remboursement_phcie = sum (item.mt_remboursement for item in details_phcie_rfm) or 0
            # 3. Calculs Cumuls Actes médicaux + Médicaments
            rec.net_totaux_rfm = rec.sous_totaux_actes_remb + rec.sous_totaux_phcie_remb
            rec.net_part_sam_rfm = rec.sous_totaux_part_sam_remb + rec.net_part_sam_phcie
            rec.net_ticket_moderateur_rfm = rec.sous_totaux_ticket_moderateur_remb + rec.net_ticket_moderateur_phcie
            rec.net_exclusions_rfm = rec.sous_totaux_exclusions_remb + rec.net_exclusions_phcie
            rec.net_remboursement_rfm = rec.net_remboursement_actes_remb + rec.net_remboursement_phcie

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id,
                 u"%s - %s" % (rec.code_rfm, rec.adherent_id.name)
                 ))
        return result

    @api.one
    @api.depends('code_saisi')
    def _get_code_rfm(self):
        self.ensure_one()
        """ Généré un code identifiant pour PEC """
        date_saisie = fields.Datetime.from_string(self.date_saisie)
        annee_format = datetime.strftime(date_saisie, '%y')
        code_genere = int(randint(1, 1e6))
        code_rfm = u'%s%06d' % (annee_format, code_genere)
        check_code_rfm = self.search_count([('code_rfm', '=', code_rfm)])
        if check_code_rfm >= 1:
            code_regenere = int(randint(1, 1e6))
            code_rfm = u'%s%06d' % (annee_format, code_regenere)
            self.code_rfm = code_rfm
        self.code_rfm = code_rfm

    @api.one
    def _get_code_remb(self):
        self.ensure_one()
        self.code_remb = self.code_rfm

    @api.constrains('code_pec')
    def validate_code_rfm(self):
        check_code_rfm = self.search_count([('code_rfm', '=', self.code_rfm)])
        if check_code_rfm > 1:
            raise ValidationError(_(
                "Proximaas : Contrôle Contrôle Règles de Gestion ; \n \
                Risque de doublon pour le Code PEC : %s. Le code PEC généré par le système existe déjà pour une autre \
                prise en charge. cependant, le code PEC doit être unique par prise en charge.\n \
                Veuillez contactez les administrateurs pour plus détails..."
                ) % self.code_rfm
            )

    @api.constrains('details_rfm_soins_ids', 'date_transmis', 'code_saisi', 'prestataire_id', 'details_rfm_soins_ids',
                    'details_rfm_phcie_ids', 'doc_joint')
    def validate_rfm_boucle(self):
        if self.state == 'boucle':
            raise ValidationError (_ (
                u"Proximaas : Contrôle Contrôle Règles de Gestion \n \
                Désolé! Vous essayez de modifier des données de la fiche de ramboursement : %s. \n \
                Cette fiche a été déjà traitée et terminée. Par conséquent, aucune modification n'est autorisée.\n \
                Veuillez contactez les administrateurs pour plus détails..."
                ) % self.num_fiche
            )

    _sql_constraints = [
        ('code_rfm_uniq',
         'UNIQUE (code_rfm)',
         '''
         Risque de doublons Code RFM!
         Il semble que ce code de Remboursement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.
         ''')
    ]


class RemboursementWizard(models.TransientModel):
    _name = 'proximas.remboursement.wizard'
    _description = 'Remboursement Frais Medicaux Wizard'

    code_saisi = fields.Char(
        string="Code ID Adhérent",
        required=True,
        help="Veuillez fournir le Code ID. de l'adhérent principal concerné par la demande de remboursement."
    )
    num_fiche = fields.Char(
        string="Réf./Num. Fiche",
        help="Indiquer le N° de référence de la fiche de remboursement",
    )
    date_depot = fields.Date (
        string="Date Dépôt Remb.",
        readonly=False,
    )

    @api.multi
    def open_popup(self):
        self.ensure_one()
        user_id = self.env.context.get('uid')
        user = self.env['res.users'].search([('id', '=', user_id)])
        # prestataire = self.env['res.partner'].search([('id', '=', user.partner_id.id)])
        # prestations = self.env['proximas.prestation'].search([('prestataire_id', '=', user.partner_id.id)])
        # 1. Vérifier si le code saisi correspond à un assure
        assure = self.env['proximas.assure'].search([
            '|', ('code_id_externe', '=', self.code_saisi),
            ('code_id', '=', self.code_saisi)
        ])
        info_assure = assure.name
        # 2. Vérifier si le code saisi correspond à un adhérent
        adherent = self.env['proximas.adherent'].search([
            '|', ('code_id_externe', '=', self.code_saisi),
            ('code_id', '=', self.code_saisi)
        ])
        info_adherent = adherent.name
        # recupérer le contrat de couverture maladie de l'adherent
        contrat = self.env['proximas.contrat'].search([('adherent_id', '=', adherent.id)])

        if not bool(adherent):
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                Le code identifiant : %s ne correspond à aucun adhérent identifié dans le système. \
                par conséquent, ne peut faire l'objet de remboursement de frais médicaux. \
                Veuillez contactez les administrateurs pour plus détails..."
                ) % self.code_saisi
            )

        # 3. Vérification du contrat pour l'assuré.
        if bool(assure) and not bool(contrat):
            raise UserError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                l'objet d'une prise en charge actuellement, pour absence de contrat faisant référence à sa police de \
                couverture. Veuillez contactez les administrateurs pour plus détails..."
                ) % (assure.name, assure.code_id)
            )
        # 4. Vérification de la présence de doublon sur l'assuré.
        elif len(assure) > 1:
            raise UserError(_(
                "Proximaas : Contrôle Règles de Gestion:\n\
                L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                l'objet d'une prise en charge actuellement, car il y a risque de doublon sur l'assuré en question. \
                Veuillez contactez les administrateurs pour plus détails..."
                ) % (assure.name, assure.code_id)
            )

        elif bool(assure) and bool(adherent) and bool(contrat):
            return {
                'name': 'Création Remboursement Adhérent',
                'view_type': 'form',
                'view_mode': 'form',
                # 'target': 'new',
                'res_model': 'proximas.remboursement.pec',
                'type': 'ir.actions.act_window',
                'context': {
                    'default_num_fiche': self.num_fiche,
                    'default_date_depot': self.date_depot,
                    'default_contrat_id': contrat.id,
                    'default_num_contrat': contrat.num_contrat,
                    'default_structure_id': contrat.structure_id.id,
                    'default_code_id': assure.code_id,
                    'default_code_saisi': self.code_saisi,
                    'default_user': user.name,
                    'default_user_id': user.id,
                },
            }
        else:
            raise ValidationError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 Le Code ID. que vous avez fourni ne correspond à aucun adhérent dans le système.\n\
                 Réverifiez le code ID. ou contacter l'administrateur en cas de besoin..!"
                )
            )


# class ReportSinistreRecapWizard(models.TransientModel):
#     _name = 'proximas.sinistre.report.wizard'
#     _description = 'Details PEC Report Wizard'
#
#     date_debut = fields.Date(
#         string="Date Début",
#         default=fields.Date.today,
#         required=True,
#     )
#     date_fin = fields.Date(
#         string="Date Fin",
#         default=fields.Date.today,
#         required=True,
#     )
#     report_kpi = fields.Selection(
#         string="Indicateur de sinistralité",
#         selection=[
#             ('police', 'Police Couverture(Produit)'),
#             ('contrat', 'Famille (Contrat)'),
#             ('assure', 'Assuré (Bénéficiare)'),
#             ('prestataire', 'Prestataire Soins médicaux'),
#             ('medecin', 'Médecin Traitant'),
#             ('rubrique', 'Rubrique Médicale'),
#             ('prestation', 'Prestation Médicale'),
#             ('groupe', 'Regroupement (Groupe)'),
#             ('localite', 'Localité'),
#             ('zone', 'Zone adminsitrative'),
#         ],
#         default='police',
#         required=True,
#     )
#     report_type = fields.Selection(
#         string="Type de rapport",
#         selection=[
#             ('groupe', 'Regroupement (Récap.)'),
#             ('detail', 'Détaillé (Sinistres)'),
#         ],
#         default='groupe',
#         required=True,
#     )
#     contrat_id = fields.Many2one(
#         comodel_name="proximas.contrat",
#         string="Contrat Adhérent",
#         required=False,
#     )
#     assure_id = fields.Many2one(
#         comodel_name="proximas.assure",
#         string="Assuré (Bénéficiaire)",
#         required=False,
#     )
#     medecin_id = fields.Many2one(
#         comodel_name="proximas.medecin",
#         string="Médecin Traitant",
#         required=False,
#     )
#     rubrique_id = fields.Many2one(
#         comodel_name="proximas.rubrique.medicale",
#         string="Rubrique Médicale",
#         required=False,
#     )
#     prestation_id = fields.Many2one(
#         comodel_name="proximas.code.prestation",
#         string="Prestation médicale",
#         required=False,
#     )
#     police_id = fields.Many2one(
#         comodel_name="proximas.police",
#         string="Police Couverture",
#         required=False,
#     )
#     prestataire_id = fields.Many2one (
#         comodel_name="res.partner",
#         string="Prestataire de soins",
#         domain=[('is_prestataire', '=', True)],
#         required=False,
#     )
#     groupe_id = fields.Many2one(
#         comodel_name="proximas.groupe",
#         string="Groupe",
#         required=False,
#     )
#     zone_id = fields.Many2one(
#         comodel_name="proximas.zone",
#         string="Zone Géographique",
#         required=False,
#     )
#     localite_id = fields.Many2one(
#         comodel_name="proximas.localite",
#         string="Localité",
#         required=False,
#     )
#
#     @api.multi
#     def get_report(self):
#         """"
#             Methode à appeler au clic sur le bouton "Valider" du formulaire Wuzard
#         """
#         data = {
#             'ids': self.ids,
#             'model': self._name,
#             'form': {
#                 'date_debut': self.date_debut,
#                 'date_fin': self.date_fin,
#                 'report_kpi': self.report_kpi,
#                 'report_type': self.report_type,
#                 'police_id': self.police_id.id,
#                 'rubrique_id': self.rubrique_id.id,
#                 'contrat_id': self.contrat_id.id,
#                 'prestataire_id': self.prestataire_id.id,
#                 'prestation_id': self.prestation_id.id,
#                 'assure_id': self.assure_id.id,
#                 'medecin_id': self.medecin_id.id,
#                 'groupe_id': self.groupe_id.id,
#                 'localite_id': self.localite_id.id,
#                 'zone_id': self.zone_id.id,
#             },
#         }
#
#         return self.env['report'].get_action(self, 'proximas_medical.report_suivi_sinistres_view', data=data)
#         # use module_name.report_id as reference
#         # report_action() will call get_report_values() and pass data automatically
#         # return self.env.ref('proximas_medical.sinistre_recap_report_view').report_action(self, data=data)
#         # return {
#         #     'type':'ir.actions.report',
#         #     'report_name': 'proximas_medical.sinistre_recap_report',
#         #     'report_type': "qweb-pdf",
#         #     'data': data,
#         # }
#
#
#
# from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
#
#
# class ReportPecDetailsRecap(models.AbstractModel):
#     """
#         Abstract Model for report template.
#         for '_name' model, please use 'report.' as prefix then add 'module_name.report_name'.
#     """
#     _name = 'report.proximas_medical.report_suivi_sinistres_view'
#
#     @api.multi
#     def render_html(self, data=None):
#         report_obj = self.env['report']
#         # print'>>>>>>>>>>>>>>>>>......', report_obj
#         report = report_obj._get_report_from_name('proximas_medical.report_suivi_sinistres_view')
#         # print'>>>>>>>>>>>>>>>>>......', report
#         date_debut = data['form']['date_debut']
#         date_fin = data['form']['date_fin']
#         report_kpi = data['form']['report_kpi']
#         report_type = data['form']['report_type']
#         date_debut_obj = datetime.strptime(date_debut, DATE_FORMAT)
#         date_fin_obj = datetime.strptime(date_fin, DATE_FORMAT)
#         date_diff = (date_fin_obj - date_debut_obj).days + 1
#         contrat_id = data['form']['contrat_id']
#         police_id = data['form']['police_id']
#         rubrique_id = data['form']['rubrique_id']
#         assure_id = data['form']['assure_id']
#         prestataire_id = data['form']['prestataire_id']
#         prestation_id = data['form']['prestation_id']
#         medecin_id = data['form']['medecin_id']
#         groupe_id = data['form']['groupe_id']
#         localite_id = data['form']['localite_id']
#         zone_id = data['form']['zone_id']
#
#         docs = []
#         docargs = {}
#
#         # 1.1. Rapport Détaillé par Rubrique
#         if report_kpi == 'rubrique' and report_type == 'detail':
#             # Récupérer les sinistres de la rubrique sélectionnée
#             details_pec = self.env['proximas.details.pec'].search([
#                 ('rubrique_id', '=', rubrique_id),
#                 ('date_execution', '!=', None),
#                 ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
#                 ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
#             ])
#             rubrique = self.env['proximas.rubrique.medicale'].search([
#                 ('id', '=', rubrique_id),
#             ])
#             if bool(details_pec):
#                 for detail in details_pec:
#                     docs.append(detail)
#
#                 docs = sorted(docs, key=lambda x: x['date_execution'], reverse=True)
#                 docargs = {
#                     'doc_ids': data['ids'],
#                     'doc_model': data['model'],
#                     'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
#                     'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),  # date_fin_obj.strftime(DATETIME_FORMAT),
#                     'date_diff': date_diff,
#                     'rubrique_medicale': rubrique.name,
#                     'report_kpi': report_kpi,
#                     'report_type': report_type,
#                     'docs': docs,
#                 }
#             else:
#                 raise UserError(_(
#                 "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
#                 Aucun sinistre n'a été enregistré sur la période indiquée pour la Rubrique médicale : %s.  \
#                 Par conséquent, le système ne peut vous fournir un rapport donr le contenu est vide. \
#                 Veuillez contacter les administrateurs pour plus détails..."
#                     ) % rubrique.name
#                 )
#         # 1.2. Rapport de synthèse par Rubrique
#         elif report_kpi == 'rubrique' and report_type == 'groupe':
#
#             # Récuperer la liste complète des rubriques médicales
#             rubriques = self.env['proximas.rubrique.medicale'].search([], order='name asc')
#
#             for rubrique in rubriques:
#                 details_pec = self.env['proximas.details.pec'].search([
#                     ('rubrique_id', '=', rubrique.id),
#                     ('date_execution', '!=', None),
#                     ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
#                     ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
#                 ], order='date_execution desc')
#
#                 if bool(details_pec):
#                     rubrique_id = rubrique.id
#                     rubrique_medicale = rubrique.name
#                     nbre_actes = len(details_pec) or 0
#                     cout_total = sum(item.cout_total for item in details_pec) or 0
#                     total_pc = sum(item.total_pc for item in details_pec) or 0
#                     total_npc = sum(item.total_npc for item in details_pec) or 0
#                     total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
#                     ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
#                     net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
#
#                     docs.append({
#                         'rubrique_id': rubrique_id,
#                         'rubrique_medicale': rubrique_medicale,
#                         'nbre_actes': int(nbre_actes),
#                         'cout_total': int(cout_total),
#                         'total_pc': int(total_pc),
#                         'total_npc': int(total_npc),
#                         'total_exclusion': int(total_exclusion),
#                         'ticket_moderateur': int(ticket_moderateur),
#                         'net_tiers_payeur': int(net_tiers_payeur),
#                     })
#             if bool(docs):
#                 docs = sorted(docs, key=lambda x: x['net_tiers_payeur'], reverse=True)
#                 docargs = {
#                     'doc_ids': data['ids'],
#                     'doc_model': data['model'],
#                     'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
#                     'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),  # date_fin_obj.strftime(DATETIME_FORMAT),
#                     'date_diff': date_diff,
#                     'report_kpi': report_kpi,
#                     'report_type': report_type,
#                     'docs': docs,
#                 }
#             else:
#                 raise UserError(_(
#                     "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
#                     Aucun sinistre n'a été enregistré sur la période indiquée.\
#                     Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
#                     Veuillez contacter les administrateurs pour plus détails..."
#                     )
#                 )
#         # 2.1. Rapport Détaillé par Contrat
#         if report_kpi == 'contrat' and report_type == 'detail':
#             # Récupérer les sinistres du contrat concerné
#             details_pec = self.env['proximas.details.pec'].search([
#                 ('contrat_id', '=', contrat_id),
#                 ('date_execution', '!=', None),
#                 ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
#                 ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
#             ])
#             contrat = self.env['proximas.contrat'].search([
#                 ('id', '=', contrat_id),
#             ])
#             if bool(details_pec):
#                 for detail in details_pec:
#                     docs.append(detail)
#
#                 docs = sorted(docs, key=lambda x: x['date_execution'], reverse=True)
#                 docargs = {
#                     'doc_ids': data['ids'],
#                     'doc_model': data['model'],
#                     'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
#                     'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),
#                     'date_diff': date_diff,
#                     'contrat_adherent': '%s - %s' % (contrat.num_contrat, contrat.adherent_id.name),
#                     'police_id': contrat.police_id.libelle,
#                     'report_kpi': report_kpi,
#                     'report_type': report_type,
#                     'docs': docs,
#                 }
#             else:
#                 raise UserError(_(
#                     "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
#                     Aucun sinistre n'a été enregistré sur la période indiquée pour le contrat : %s.  \
#                     Par conséquent, le système ne peut vous fournir un rapport donr le contenu est vide. \
#                     Veuillez contacter les administrateurs pour plus détails..."
#                     ) % contrat.adherent_id.name
#                 )
#         # 2.2. Rapport de synthèse par Contrat Adhérent
#         elif report_kpi == 'contrat' and report_type == 'groupe':
#
#             # Récuperer la liste complète des sinistres par contrat adhérent
#             contrats = self.env['proximas.contrat'].search([], order='name asc')
#
#             for contrat in contrats:
#                 details_pec = self.env['proximas.details.pec'].search([
#                     ('contrat_id', '=', contrat.id),
#                     ('date_execution', '!=', None),
#                     ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
#                     ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
#                 ], order='date_execution desc')
#
#                 if bool(details_pec):
#                     contrat_id = contrat.id
#                     contrat_adherent = contrat.adherent_id.name
#                     nbre_actes = len(details_pec) or 0
#                     cout_total = sum(item.cout_total for item in details_pec) or 0
#                     total_pc = sum(item.total_pc for item in details_pec) or 0
#                     total_npc = sum(item.total_npc for item in details_pec) or 0
#                     total_exclusion = sum(item.mt_exclusion for item in details_pec) or 0
#                     ticket_moderateur = sum(item.ticket_moderateur for item in details_pec) or 0
#                     net_tiers_payeur = sum(item.net_tiers_payeur for item in details_pec) or 0
#
#                     docs.append({
#                         'contrat_id': contrat_id,
#                         'contrat_adherent': contrat_adherent,
#                         'nbre_actes': int(nbre_actes),
#                         'cout_total': int(cout_total),
#                         'total_pc': int(total_pc),
#                         'total_npc': int(total_npc),
#                         'total_exclusion': int(total_exclusion),
#                         'ticket_moderateur': int(ticket_moderateur),
#                         'net_tiers_payeur': int(net_tiers_payeur),
#                     })
#             if bool(docs):
#                 docs = sorted(docs, key=lambda x: x['net_tiers_payeur'], reverse=True)
#                 # docs = docs[:200]
#                 docargs = {
#                     'doc_ids': data['ids'],
#                     'doc_model': data['model'],
#                     'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
#                     'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),  # date_fin_obj.strftime(DATETIME_FORMAT),
#                     'date_diff': date_diff,
#                     'report_kpi': report_kpi,
#                     'report_type': report_type,
#                     'docs': docs,
#                 }
#             else:
#                 raise UserError(_(
#                     "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
#                     Aucun sinistre n'a été enregistré sur la période indiquée. \
#                     Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
#                     Veuillez contacter les administrateurs pour plus détails..."
#                     )
#                 )
#         # 3.1. Rapport Détaillé par Assuré
#         if report_kpi == 'assure' and report_type == 'detail':
#             # Récupérer les sinistres de l'assuré concerné
#             details_pec = self.env['proximas.details.pec'].search([
#                 ('assure_id', '=', assure_id),
#                 ('date_execution', '!=', None),
#                 ('date_execution', '>=', date_debut_obj.strftime (DATETIME_FORMAT)),
#                 ('date_execution', '<=', date_fin_obj.strftime (DATETIME_FORMAT)),
#             ])
#             assure = self.env['proximas.assure'].search([
#                 ('id', '=', assure_id),
#             ])
#             if bool(details_pec):
#                 for detail in details_pec:
#                     docs.append(detail)
#
#                 docs = sorted(docs, key=lambda x: x['date_execution'], reverse=True)
#                 docargs = {
#                     'doc_ids': data['ids'],
#                     'doc_model': data['model'],
#                     'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
#                     'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),
#                     'date_diff': date_diff,
#                     'assure': '%s - %s' % (assure.code_id, assure.name),
#                     'police_id': assure.police_id.libelle,
#                     'report_kpi': report_kpi,
#                     'report_type': report_type,
#                     'docs': docs,
#                 }
#             else:
#                 raise UserError(_(
#                     "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
#                     Aucun sinistre n'a été enregistré sur la période indiquée pour le compte de l'assuré : %s.  \
#                     Par conséquent, le système ne peut vous fournir un rapport donr le contenu est vide. \
#                     Veuillez contacter les administrateurs pour plus détails..."
#                     ) % assure.name
#                 )
#         # 3.2. Rapport de synthèse par Assuré
#         elif report_kpi == 'assure' and report_type == 'groupe':
#
#             # Récuperer la liste complète des sinistres assuré
#             assures = self.env['proximas.assure'].search([], order='name asc')
#
#             for assure in assures:
#                 details_pec = self.env['proximas.details.pec'].search([
#                     ('assure_id', '=', assure.id),
#                     ('date_execution', '!=', None),
#                     ('date_execution', '>=', date_debut_obj.strftime(DATETIME_FORMAT)),
#                     ('date_execution', '<=', date_fin_obj.strftime(DATETIME_FORMAT)),
#                 ], order='date_execution desc')
#
#                 if bool(details_pec):
#                     assure_id = assure.id
#                     code_id = assure.code_id
#                     assure_beneficiaire = assure.name
#                     statut_familial = assure.statut_familial
#                     nbre_actes = len (details_pec) or 0
#                     cout_total = sum (item.cout_total for item in details_pec) or 0
#                     total_pc = sum (item.total_pc for item in details_pec) or 0
#                     total_npc = sum (item.total_npc for item in details_pec) or 0
#                     total_exclusion = sum (item.mt_exclusion for item in details_pec) or 0
#                     ticket_moderateur = sum (item.ticket_moderateur for item in details_pec) or 0
#                     net_tiers_payeur = sum (item.net_tiers_payeur for item in details_pec) or 0
#
#                     docs.append({
#                         'assure_id': assure_id,
#                         'assure_beneficiaire': assure_beneficiaire,
#                         'code_id': code_id,
#                         'statut_familial': statut_familial,
#                         'adherent': assure.contrat_id.adherent_id.name,
#                         'nbre_actes': int(nbre_actes),
#                         'cout_total': int(cout_total),
#                         'total_pc': int(total_pc),
#                         'total_npc': int(total_npc),
#                         'total_exclusion': int(total_exclusion),
#                         'ticket_moderateur': int(ticket_moderateur),
#                         'net_tiers_payeur': int(net_tiers_payeur),
#                     })
#             if bool(docs):
#                 docs = sorted(docs, key=lambda x: x['net_tiers_payeur'], reverse=True)
#                 # docs = docs[:200]
#                 docargs = {
#                     'doc_ids': data['ids'],
#                     'doc_model': data['model'],
#                     'date_debut': datetime.strftime(date_debut_obj, '%d-%m-%Y'),
#                     'date_fin': datetime.strftime(date_fin_obj, '%d-%m-%Y'),
#                     'date_diff': date_diff,
#                     'report_kpi': report_kpi,
#                     'report_type': report_type,
#                     'docs': docs,
#                 }
#             else:
#                 raise UserError(_(
#                     "Proximaas : Rapport de Suivi Portafeuillz de Risque: \n\
#                     Aucun sinistre n'a été enregistré sur la période indiquée. \
#                     Par conséquent, le système ne peut vous fournir un rapport dont le contenu est vide. \
#                     Veuillez contacter les administrateurs pour plus détails..."
#                     )
#                 )
#
#         return report_obj.render('proximas_medical.report_suivi_sinistres_view', docargs)

    # @api.multi
    # def check_report(self):
    #     data = {}
    #     data['form'] = self.read(['date_debut', 'date_fin'])[0]
    #     return self._print_report(data)
    #
    # def _print_report(self, data):
    #     data['form'].update(self.read('date_debut', 'date_fin')[0])
    #     date_debut = fields.Datetime.from_string (self.date_debut)
    #     date_fin = fields.Datetime.from_string (self.date_fin)
    #     details_pec = self.env['proximas.details.pec'].search([
    #         ('pec_state', '=', 'termine'),
    #         ('date_execution', '>=', date_debut),
    #         ('date_execution', '<=', date_fin),
    #     ])
    #
    #     return self.env['report'].get_action(self, 'proximas_medical.report_details_pec_rubrique', data=data)
    #
    #
    # @api.multi
    # def get_report(self, data=None):
    #     report_obj = self.env['report']
    #     print'>>>>>>>>>>>>>>>>>......', report_obj
    #     report = report_obj._get_report_from_name('proximas_medical.report_details_pec_rubrique')
    #     print'>>>>>>>>>>>>>>>>>......', report
    #     date_debut = fields.Datetime.from_string (self.date_debut)
    #     date_fin = fields.Datetime.from_string(self.date_fin)
    #     # Chercher et regrouper les détails PEC par RUBRIQUE MEDICALE
    #     data = self.env['proximas.details.pec'].search([
    #         ('pec_state', '=', 'termine'),
    #         ('date_execution', '>=', date_debut),
    #         ('date_execution', '<=', date_fin),
    #     ])
    #     data = self.env['proximas.details.pec'].read_group([
    #             ('date_execution', '>=', date_debut),
    #             ('date_execution', '<=', date_fin),
    #     ],
    #     [
    #             'rubrique_id', 'cout_total', 'total_pc', 'total_npc', 'ticket_moderateur', 'net_tiers_payeur',
    #             'mt_exclusion', 'structure_id',
    #     ], ['rubrique_id',],
    #     )
    #     docargs = {
    #         'doc_ids': self._ids,
    #         'doc_model': report.model,
    #         'data': data,
    #         'docs': self,
    #     }
    #     return report_obj.render('proximas_medical.report_details_pec_rubrique', docargs)
        # return self.env['report'].get_action(self, 'proximas_medical.report_details_pec_rubrique', docargs)

