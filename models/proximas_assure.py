# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


import openerp
from openerp import tools
from openerp.tools.translate import _
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from random import randint
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class Assure (models.Model):
    _name = 'proximas.assure'
    _description = 'Assures'
    _inherits = {'res.partner': 'partner_id'}
    _short_name = 'name'

    partner_id = fields.Many2one (
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='restrict',
        index=True,
    )
    sequence = fields.Integer (
        string="Sequence"
    )
    color = fields.Integer (
        string="Color index",
        required=False,
    )
    full_name = fields.Char (
        string="Nom Complet",
        compute='_get_full_name',
    )
    nom = fields.Char (
        string="Nom",
        size=32,
        required=True,
    )
    prenoms = fields.Char (
        string="Prénoms",
        size=64,
        required=True,
    )
    parent_id = fields.Many2one (
        comodel_name="proximas.assure",
        string="Assuré Principal",
        ondelete='restrict',
        index=True,
    )
    child_ids = fields.One2many (
        comodel_name="proximas.assure",
        inverse_name="parent_id",
        string="Ayant-droit",
    )
    code_id = fields.Char (
        string="Code Id.",
        compute="_get_code_id",
        help="Code d'identification unique fourni par le système.!",
        store=True,
        # default=lambda self: self._get_code_id(),
    )
    code_id_externe = fields.Char (
        size=32,
        string='Code ID. Externe',
        help="Code ID. obtenu à partir d'un système exterieur."
    )
    matricule = fields.Char (
        size=32,
        string='N° Matricule',
        help='Numero matricule s\'il y a lieu',
    )
    localite_id = fields.Many2one (
        comodel_name="proximas.localite",
        string="Localité",
        help="Indiquez la localité de rattachement de l'assuré",
    )
    quartier = fields.Char (
        size=64,
        string='Quartier/Secteur',
        help='Indiquer le secteur ou le quartier de résidence',
    )
    groupe_id = fields.Many2one (
        comodel_name="proximas.groupe",
        string="Groupe",
        required=False,
    )
    # contrat_id = fields.Many2one(
    #     comodel_name="proximas.contrat",
    #     string="Contrat",
    # )
    genre = fields.Selection (
        [
            ('masculin', 'Masculin'),
            ('feminin', 'Feminin'),
        ],
        required=True,
    )
    statut_familial = fields.Selection (
        [
            ('adherent', 'Adhérent'),
            ('conjoint', 'Conjoint(e)'),
            ('enfant', 'Enfant'),
            ('ascendant', 'Ascendant'),
            ('parent', 'Parent'),
        ],
        string="Statut Familial",
        compute='_get_statut_familial',
        default='adherent',
        store=True,
        help="Lien de parenté avec l'assuré principal.",
    )
    statut = fields.Selection (
        [
            ('conjoint', 'Conjoint(e)'),
            ('enfant', 'Enfant'),
            ('ascendant', 'Ascendant'),
            ('parent', 'Parent'),
        ],
        string="Statut Familial",
        help="Lien de parenté avec l'assuré principal.",
    )
    groupe_sanguin = fields.Selection (
        [
            ('a+', 'A+'),
            ('a-', 'A-'),
            ('b+', 'B+'),
            ('b-', 'B-'),
            ('ab+', 'AB+'),
            ('ab-', 'AB-'),
            ('o+', 'O+'),
            ('o-', 'O-'),

        ],
        string="Groupe Sanguin",
        help="Sélectionner un groupe sanguin dans la liste.",
    )
    date_naissance = fields.Date (
        string="Date Naissance",
        required=True,
    )
    date_inscription = fields.Date (
        string="Date Inscription",
        required=True,
        default=fields.Date.today ()
    )
    date_activation = fields.Date (
        string="Date Activation",
        default=fields.Date.today (),
        help='Indiquer la date à laquelle l\'assuré sera actif',
    )
    date_edition_carte = fields.Date (
        string="Date Edition Carte",
    )
    retrait_carte = fields.Boolean (
        string="Retrait Carte?",
        help="Cochez pour la carte rétirée!",
    )
    date_duplicata = fields.Date(
        string="Date Duplicata",
    )
    date_deces = fields.Date(
        string="Date Décès",
        compute='_get_date_deces',
        readonly=True,
    )
    decede = fields.Boolean (
        compute='_get_date_deces',
        string='Décédé(e)?',
        default=False,
        help='(En cas de décès) A cocher automatiquement si une date de décès est fournie!',
    )
    motif_desactivation = fields.Char (
        string="Motif de désactivation",
        required=False,
    )
    mobile_2 = fields.Char (
        string="Tél. mobile 1",
        size=8
    )
    state = fields.Selection (
        string="Etat",
        selection=[
            ('actif', 'Activé(e)'),
            ('suspens', 'Suspension'),
            ('exclu', 'Exclusion'),
            ('attente', 'En attente'),
            ('decede', 'Décédé(e)'),
            ('age', 'Age Limite'),
            ('plafond_ind', 'Plafond individu'),
            ('plafond_fam', 'Plafond famille'),
        ],
        compute='_get_state_assure',
        # store=True,
        default='attente',
        help='Ce champ indiquer le statut de l\'assuré dans la système...',
    )
    sanction_ids = fields.One2many (
        comodel_name="proximas.sanction",
        inverse_name="assure_id",
        string="Sanction (Supension/Exclusion)",
    )
    assure_actif = fields.Boolean (
        string="Actif?",
        dafault=True,
        halp="Etat de l'assuré : Actif ou non.",
    )
    code_perso = fields.Integer (
        string="Code Perso",
        default=0000,
    )
    code_pass = fields.Integer (
        string="Code Pass",
        compute='_get_code_pass',
        store=True,
    )
    is_assure = fields.Boolean (
        string="Est Assuré?",
        default=True,
        readonly=True,
    )
    cas_chronique = fields.Boolean (
        string="Malade Chronique?",
        default=False
    )
    general_info = fields.Text (
        string='Information General',
    )
    age = fields.Char (
        compute='_compute_age',
    )
    age_details = fields.Char (
        compute='_compute_age',
    )
    age_entier = fields.Integer (
        string='Age assuré',
        compute='_compute_age_entier',
        store=True,
    )
    tranche_age = fields.Selection (
        string="Tranche d'âge",
        selection=[
            ('0', '0'),
            ('1', '1'),
            ('2', '2-5'),
            ('3', '6-10'),
            ('4', '11-15'),
            ('5', '16-20'),
            ('6', '21-30'),
            ('7', '31-40'),
            ('8', '41-50'),
            ('9', '51-60'),
            ('10', '+60'),
        ],
        compute='_check_tranche_age',
        store=True,
    )
    est_invalide = fields.Boolean (
        # disponible uniquement pour le statut_familial = Enfant
        string="Enfant invalide?",
        help="Cocher uniquement au cas où l'enfant est considéré comme invalide"
    )
    note = fields.Text (
        string="Notes et Observations",
    )
    delai_carence = fields.Integer (
        string="Délai de carence",
        help="La période (nbre. de jours) de carence à observer avant de bénéficier de la couverture!",
        default=0,
    )
    # POLICE DETAILS & CONTRAT
    contrat_id = fields.Many2one (
        comodel_name="proximas.contrat",
        string="Contrat",
        compute='_get_contrat_id',
        # related='police_id.contrat_id',

    )
    num_contrat = fields.Char (
        string="N° Contrat",
        related='contrat_id.num_contrat',
        store=True,
    )
    contrat_actif = fields.Boolean (
        string="Contrat Activé?",
        related='contrat_id.actif',
        help="Indique l'état du contrat (actif ou non).",
    )
    date_activation_contrat = fields.Date (
        string="Date Prise Effet",
        related='contrat_id.date_activation',
        help='Date à laquelle le contrat est activé (date de prise d\'effet).'
    )
    police_id = fields.Many2one (
        comodel_name="proximas.police",
        string="Police Couverture",
        related='contrat_id.police_id',
        # store=True,
        readonly=True,
    )
    libelle_police = fields.Char (
        string="Police Couverture",
        related='police_id.libelle',
        store=True,
        readonly=True,
    )
    structure_id = fields.Many2one (
        comodel_name="res.company",
        string="Organisation",
        related='contrat_id.structure_id',
    )
    plafond_individu = fields.Float (
        string="Plafond individu",
        digits=(9, 0),
        related='contrat_id.plafond_individu',
        default=0,
        readonly=True,
    )
    plafond_famille = fields.Float (
        string="Plafond Famille",
        digits=(9, 0),
        related='contrat_id.plafond_famille',
        default=0,
        readonly=True,
    )
    date_resiliation_contrat = fields.Date (
        string="Date Résiliation",
        related='contrat_id.date_resiliation',
        help="Date de résiliation du contrat de couverture"
    )
    date_fin_prevue_contrat = fields.Date (
        string="Date Fin Contrat",
        related='contrat_id.date_fin_prevue',
        store=True,
        help="Date de fin prévue du contrat de couverture en rapport avec le délai de validité de la police."
    )
    date_debut_contrat = fields.Date (
        string="Date Début Contrat",
        related='contrat_id.date_debut_contrat',
        help="Date de début du contrat de couverture par rapport avec le délai de validité de la police."
    )
    validite_contrat = fields.Integer (
        string="Délai Validité contrat (jours)",
        related='contrat_id.validite_contrat',
        readonly=True,
    )
    validite_contrat_police = fields.Integer (
        string="Délai Validité contrat (jours)",
        related='contrat_id.validite_contrat_police',
        readonly=True,
    )
    mode_controle_plafond = fields.Selection (
        string="Mode Contrôle Plafond",
        related='contrat_id.mode_controle_plafond',
        readonly=True,
    )
    ############################################
    duree_activation = fields.Char (
        string="Durée Activation (Details)",
        compute='_get_duree_activation',
    )
    jours_activation = fields.Integer (
        string="Durée Activation (Nbre. Jours)",
        compute='_get_duree_activation',
    )
    nbre_renouvellement_contrat = fields.Integer(
        string="Nbre. réconduite(s) contrat",
        compute='_compute_debut_fin_assure',
        help='Nombre de renouvellement du contrat.',
    )
    date_debut_assure = fields.Date (
        string="Date Débur Assuré",
        compute='_compute_debut_fin_assure',
        help="Date de début de la couverture en rapport avec le délai de validité de la police."
    )
    date_fin_prevue_assure = fields.Date (
        string="Date Fin Contrat",
        compute='_compute_debut_fin_assure',
        help="Date de fin prévue de la couverture en rapport avec le délai de validité de la police."
    )
    # SURVEILLANCE DU PORTEFUEILLE DE RISQUES
    sous_totaux_assure = fields.Float (
        string="S/Totaux Assuré",
        digits=(9, 0),
        compute='_check_details_pec',
        default=0,
    )
    sous_totaux_contrat = fields.Float (
        string="S/Totaux Contrat",
        digits=(9, 0),
        compute='_check_details_pec',
        default=0,
    )
    nbre_actes_assure = fields.Integer (
        string="Nbre. Actes (Prestations) ",
        compute='_check_details_pec',
        default=0,
    )
    nbre_phcie_assure = fields.Integer (
        string="Nbre. Prescriptions",
        # compute='_check_details_pec',
        default=0,
    )
    date_maj_assure = fields.Datetime (
        string="Dernière mise à jour",
        required=False,
        help='Date de la dernière mise à jour effectuée',
    )
    compteur_maj_assure = fields.Integer (
        string="Compteur MAJ",
        default=0,
        help="Le nombre de fois que le système a mise à jour les données de l'assuré...",
    )

    # @api.depends('date_activation', 'date_resiliation', 'validite_contrat', 'validite_contrat_police', 'jours_contrat',
    #               'mode_controle_plafond')
    def _compute_debut_fin_assure(self):
        # now = fields.Datetime.from_string (fields.Date.today())
        activation_contrat = fields.Date.from_string(self.date_activation_contrat)
        activation_assure = fields.Date.from_string(self.date_activation)
        date_deces = fields.Date.from_string(self.date_deces)
        date_resiliation = fields.Date.from_string(self.date_resiliation_contrat)
        validite_contrat = int(self.validite_contrat)
        validite_police = int(self.validite_contrat_police)
        if validite_contrat:
            nbre_renouvellement = self.jours_activation / validite_contrat
            self.nbre_renouvellement_contrat = nbre_renouvellement
        elif validite_police:
            nbre_renouvellement = self.jours_activation / validite_police
            self.nbre_renouvellement_contrat = nbre_renouvellement
        # 1. MODE DE CONTROLE PAR EXERCICE
        if self.mode_controle_plafond in ['exercice']:
            exercice = self.env['proximas.exercice'].search ([
                ('res_company_id', '=', self.structure_id.id),
                ('en_cours', '=', True),
            ])
            if exercice and len (exercice) == 1:
                date_debut = fields.Date.from_string (exercice.date_debut)
                date_fin = fields.Date.from_string (exercice.date_fin)
                if date_deces:
                    self.date_debut_assure = activation_contrat
                    self.date_fin_prevue_assure = date_deces
                elif date_resiliation:
                    self.date_debut_assure = activation_contrat
                    self.date_fin_prevue_assure = date_resiliation
                elif activation_contrat > date_debut:
                    self.date_debut_assure = activation_contrat
                    self.date_fin_prevue_assure = date_fin
                else:
                    self.date_debut_assure = date_debut
                    self.date_fin_prevue_assure = date_fin
            else:
                raise UserError(
                    '''
                         Proximaas - Contrôle des règles de Gestion :\n
                         Le mode de contrôle défini pour le plafond famille (contrat)\
                         est l'Exercice. Cependant, le système n'a détecté aucun ou plus d'un exercice\
                         en cours. Pour plus d'informations, veuillez contactez l'administrateur...
                     '''
                )
        # 2. MODE DE CONTROLE PAR CONTRAT
        elif self.mode_controle_plafond in ['contrat']:
            if date_deces:
                self.date_debut_assure = activation_assure
                self.date_fin_prevue_assure = date_deces
            elif date_resiliation:
                self.date_debut_assure = activation_contrat
                self.date_fin_prevue_assure = date_resiliation
            elif self.nbre_renouvellement_contrat >= 1:
                if validite_contrat:
                    self.date_debut_assure = activation_assure + timedelta (days=int(self.validite_contrat))
                    date_debut = fields.Date.from_string(self.date_debut_assure)
                    self.date_fin_prevue_assure = date_debut + timedelta(days=int(self.validite_contrat))
                elif validite_police:
                    self.date_debut_assure = activation_contrat + timedelta(days=int(self.validite_police))
                    date_debut = fields.Date.from_string(self.date_debut_assure)
                    self.date_fin_prevue_assure = date_debut + timedelta(days=int(self.validite_police))
            else:
                if validite_contrat:
                    self.date_debut_assure = activation_assure
                    date_debut = fields.Date.from_string(self.date_debut_assure)
                    self.date_fin_prevue_assure = date_debut + timedelta(days=int(self.validite_contrat))
                elif validite_police:
                    self.date_debut_assure = activation_assure
                    date_debut = fields.Date.from_string(self.date_debut_assure)
                    self.date_fin_prevue_assure = date_debut + timedelta(days=int(self.validite_police))

    # def _compute_date_fin_prevue(self):
    #     if bool (self.contrat_id):
    #         now = fields.Datetime.from_string (fields.Date.today ())
    #         activation_assure = fields.Datetime.from_string (self.date_activation)
    #         date_deces = fields.Datetime.from_string (self.date_deces)
    #         date_fin_prevue = fields.Datetime.from_string (self.date_fin_prevue)
    #         nbre_jours_validite_contrat = int (self.validite_contrat) or 366
    #         nbre_renouvellement = int (self.jours_activation / nbre_jours_validite_contrat) + 1
    #         # Calcul de la date de fin prévue du contrat Adherent
    #         # datetime.now () + timedelta (days=2, hours=4, minutes=3, seconds=12)
    #         if bool (date_deces):
    #             self.date_fin_prevue = date_deces
    #         elif bool (date_fin_prevue) and date_fin_prevue <= now:
    #             self.date_fin_prevue += timedelta (days=int (self.validite_contrat))
    #         else:
    #             self.date_fin_prevue = activation_assure + timedelta (
    #                 days=int (self.validite_contrat) * nbre_renouvellement)

    @api.depends ('date_naissance', 'age')
    def _check_tranche_age(self):
        for rec in self:
            if bool (rec.age):
                if rec.age <= 0:
                    rec.tranche_age = '0'
                elif rec.age == 1:
                    rec.tranche_age = '1'
                elif 2 <= rec.age <= 5:
                    rec.tranche_age = '2'
                elif 6 <= rec.age <= 10:
                    rec.tranche_age = '3'
                elif 11 <= rec.age <= 15:
                    rec.tranche_age = '4'
                elif 16 <= rec.age <= 20:
                    rec.tranche_age = '5'
                elif 21 <= rec.age <= 30:
                    rec.tranche_age = '6'
                elif 31 <= rec.age <= 40:
                    rec.tranche_age = '7'
                elif 41 <= rec.age <= 50:
                    rec.tranche_age = '8'
                elif 51 <= rec.age <= 60:
                    rec.tranche_age = '9'
                elif rec.age > 60:
                    rec.tranche_age = '10'

    @api.multi
    def _check_details_pec(self):
        for rec in self:
            details_pec_assure = self.env['proximas.details.pec'].search (
                [('assure_id', '=', rec.id)]
            )
            details_pec_contrat = self.env['proximas.details.pec'].search (
                [('contrat_id', '=', rec.contrat_id.id)]
            )
            nbre_details_pec_assure = self.env['proximas.details.pec'].search_count ([
                ('assure_id', '=', rec.id),
                ('date_execution', '!=', None),
                ('produit_phcie_id', '=', None)
            ])
            nbre_details_phcie_assure = self.env['proximas.details.pec'].search_count ([
                ('assure_id', '=', rec.id),
                ('date_execution', '!=', None),
                ('produit_phcie_id', '!=', None)
            ])
            if details_pec_assure:
                rec.nbre_actes_assure = int (nbre_details_pec_assure) or 0
                rec.nbre_phcie_assure = int (nbre_details_phcie_assure) or 0
                rec.sous_totaux_assure = sum (item.total_pc for item in details_pec_assure) or 0
                rec.sous_totaux_contrat = sum (item.total_pc for item in details_pec_contrat) or 0

    @api.one
    @api.depends ('is_assure', 'code_id')
    def _get_code_id(self):
        """Généré un code identifiant pour assuré"""
        self.ensure_one ()
        code_genere = int (randint (1, 1e3))
        upper_prenoms = self.prenoms.upper () or ''
        # rec_id.code_id = u'%04d%s%s' % (code_genere, rec_id.nom[:1], upper_prenoms[:1])
        code_id = u'%06d%s%s' % (code_genere, self.nom[:1], upper_prenoms[:1])
        check_code_id = self.search_count ([('code_id', '=', code_id)])
        if check_code_id >= 1:
            code_regenere = randint (1, 1e6)
            code_id = u'%06d%s%s' % (code_regenere, self.nom[:1], upper_prenoms[:1])
            self.code_id = code_id
        self.code_id = code_id

    # @api.one
    @api.depends ('nom', 'prenoms', 'full_name')
    @api.onchange ('nom', 'prenoms', 'full_name')
    def _get_full_name(self):
        for rec in self:
            rec.full_name = '%s %s' % (rec.nom, rec.prenoms)
            if bool (rec.full_name):
                rec.name = rec.full_name
            else:
                rec.name = '%s %s' % (rec.nom, rec.prenoms)

    @api.multi
    # @api.depends('statut_familial', 'code_id', 'contrat_id')
    def _get_contrat_id(self):
        for rec in self:
            if rec.statut_familial == 'adherent':
                adherent = self.env['proximas.adherent'].search ([
                    ('assure_id', '=', rec.id),
                ])
                contrat = self.env['proximas.contrat'].search ([('adherent_id', '=', adherent.id)])
                if bool (contrat):
                    rec.contrat_id = contrat.id
                    # rec.police_id = contrat.police_id
                    # rec.num_contrat =
            elif rec.statut_familial != 'adherent':
                ayant_droit = self.env['proximas.ayant.droit'].search ([('assure_id', '=', rec.id)])
                if bool (ayant_droit):
                    # self.contrat_id = ayant_droit.contrat_id.id
                    rec.contrat_id = ayant_droit.contrat_id.id
                    # rec.police_id = ayant_droit.contrat_id.police_id

    @api.multi
    # @api.depends('code_id', 'state', 'is_assure', 'decede', 'statut_familial', 'age')
    def _get_state_assure(self):
        now = datetime.now ()
        for rec in self:
            suspension = self.env['proximas.sanction'].search (
                [
                    ('code_id', '=', rec.code_id),
                    ('type_sanction', '=', 'suspens'),
                    ('en_cours', '=', True),
                ])
            exclusion = self.env['proximas.sanction'].search (
                [
                    ('code_id', '=', rec.code_id),
                    ('type_sanction', '=', 'exclu'),
                ])
            # 1. contrôle décès assuré
            if bool (rec.decede):
                rec.state = 'decede'
            # 2. contrôle sanctions (Suspensions, exclusions)
            elif bool (suspension):
                rec.state = 'suspens'
            elif bool (exclusion):
                rec.state = 'exclu'
            # 3. contrôle contrat assure et age limite adht/Cjt - age majorité enfant
            elif rec.statut_familial == 'adherent':
                contrat = self.env['proximas.contrat'].search (
                    [
                        ('code_id', '=', rec.code_id),
                        ('date_naissance', '=', rec.date_naissance)
                    ]
                )
                age = int (rec.age)
                age_limite_adherent = int (contrat.age_limite_adherent)
                if not rec.contrat_actif:
                    rec.state = 'attente'
                elif age > age_limite_adherent > 0:
                    rec.state = 'age'
                else:
                    rec.state = 'actif'
            elif rec.statut_familial != 'adherent':
                ayant_droit = self.env['proximas.ayant.droit'].search (
                    [
                        ('assure_id', '=', rec.id),
                        ('code_id', '=', rec.code_id),
                    ]
                )
                contrat = self.env['proximas.contrat'].search ([('id', '=', ayant_droit.contrat_id.id)])
                age_limite_conjoint = int (contrat.age_limite_conjoint)
                age_limite_ascendant = int (contrat.age_limite_ascendant)
                age_limite_parent = int (contrat.age_limite_parent)
                age_majorite_enfant = int (contrat.age_majorite_enfant)
                age_limite_enfant = int (contrat.age_limite_enfant)
                age = int (rec.age)
                if not rec.contrat_actif:
                    rec.state = 'attente'
                elif rec.statut_familial == 'conjoint' and age > age_limite_conjoint > 0:
                    rec.state = 'age'
                elif rec.statut_familial == 'ascendant' and age > age_limite_ascendant > 0:
                    rec.state = 'age'
                elif rec.statut_familial == 'parent' and age > age_limite_parent > 0:
                    rec.state = 'age'
                # 4. Vérifier Certificat de Scolarite / Invalidité Enfant
                elif rec.statut_familial == 'enfant':
                    scolarite = self.env['proximas.justificatif.enfant'].search (
                        [
                            ('code_id', '=', rec.code_id),
                            ('type_justificatif', '=', 'scolarite'),
                            ('en_cours', '=', True),
                        ]
                    )
                    invalidite = self.env['proximas.justificatif.enfant'].search (
                        [
                            ('code_id', '=', rec.code_id),
                            ('type_justificatif', '=', 'invalide'),
                            ('en_cours', '=', True),
                        ]
                    )
                    if age >= age_majorite_enfant > 0 and not scolarite.en_cours:
                        rec.state = 'age'
                    elif age >= age_limite_enfant > 0 and not invalidite.en_cours:
                        rec.state = "age"
                    else:
                        rec.state = 'actif'
                else:
                    rec.state = 'actif'
            else:
                rec.state = 'actif'

    @api.multi
    @api.depends ('code_id', 'date_deces')
    def _get_date_deces(self):
        for rec_id in self:
            assure = self.env['proximas.deces'].search ([('code_id', 'ilike', rec_id.code_id)])
            if assure:
                rec_id.date_deces = assure.date_deces
                rec_id.decede = True
                rec_id.state = 'decede'

    @api.multi
    @api.depends ('date_naissance', 'decede')
    def _compute_age(self):
        now = datetime.now ()
        for rec_id in self:
            if rec_id.date_naissance:
                dob = fields.Datetime.from_string (rec_id.date_naissance)
                if bool (rec_id.decede):
                    dod = fields.Datetime.from_string (rec_id.date_deces)
                    delta = relativedelta (dod, dob)
                    deceased = _ (' (Décédé(e))')
                else:
                    delta = relativedelta (now, dob)
                    deceased = ''
                years = '%s' % (delta.years)
                years_months_days = '%s%s %s%s %s%s%s' % (
                    delta.years, _ (' An(s) -'),
                    delta.months, _ (' mois -'),
                    delta.days, _ (' jours'), deceased
                )
                rec_id.age_details = years_months_days
                rec_id.age = int (years) + 1
            else:
                years_months_days = _ ('Aucune Date Naissance!')
                rec_id.age_details = years_months_days

    @api.multi
    @api.depends ('age')
    def _compute_age_entier(self):
        for rec in self:
            if bool (rec.age):
                rec.age_entier = int (rec.age)

    @api.multi
    def action_invalidate(self):
        for rec_id in self:
            rec_id.active = False
            rec_id.partner_id.active = False
            rec_id.state = 'attente'

    @api.multi
    def action_revalidate(self):
        for rec_id in self:
            rec_id.active = True
            rec_id.partner_id.active = True
            rec_id.state = 'actif'

    @api.multi
    @api.depends ('statut')
    def _get_statut_familial(self):
        """Récupère le statut familial de l'assuré return: statut """
        for rec in self:
            if rec.statut == 'enfant':
                rec.statut_familial = 'enfant'
            elif rec.statut == 'conjoint':
                rec.statut_familial = 'conjoint'
            elif rec.statut == 'ascendant':
                rec.statut_familial = 'ascendant'
            elif rec.statut == 'parent':
                rec.statut_familial = 'parent'
            else:
                rec.statut_familial = 'adherent'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append (
                (record.id,
                 u"%s %s" % (record.nom, record.prenoms)
                 ))
        return result

    @api.multi
    @api.depends ('code_perso')
    def _get_code_pass(self):
        for record in self:
            if record.code_perso == 0 or not record.code_perso:
                code_genere = randint (1, 9999)
                record.code_pass = '%04d' % code_genere
            else:
                record.code_pass = record.code_perso

    @api.model
    @api.returns ('self', lambda value: value.id)
    def create(self, vals):
        vals['is_assure'] = True
        if not vals.get ('code_id'):
            sequence = self.env['ir.sequence'].next_by_code ('proximas.assure')
            vals['code_id'] = sequence
        return super (Assure, self).create (vals)

    @api.constrains ('date_naissance')
    def _check_date_naissance(self):
        for rec in self:
            if rec.date_naissance > fields.Date.today ():
                raise ValidationError (
                    '''
                      Contrôle des règles de Gestion : Proximas
                      La date de naissance doit être inférieure ou égale  à la date du jour ! 
                      Vérifiez s'il n'y a pas d'erreur sur la date saisie ?
                    ''')

    # Contraintes d'integrité SQL sur champs
    sql_constraints = [
        (
            'code_id_unique',
            'UNIQUE(code_id)',
            '''
                Risque de doublon sur Code ID. Assuré!
                Il semble que cet enregistrement existe déjà dans la base de données...
                Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
                '''
        ),
        (
            'nom_prenom_naissance_unique',
            'UNIQUE(nom, prenoms, date_naissance)',
            '''
                Risque de doublon sur Assuré!
                Il semble que cet enregistrement existe déjà dans la base de données...
                Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
                '''
        ),
    ]


class Adherent (models.Model):
    _name = 'proximas.adherent'
    _inherits = {'proximas.assure': 'assure_id'}
    _description = 'Adherents souscripteurs'

    assure_id = fields.Many2one (
        comodel_name="proximas.assure",
        string="Assure",
        ondelete='cascade',
        required=True,
    )
    ref = fields.Char (
        size=32,
        string='Pièce N°',
        help='Type, N° et Date validité de la CNI, Passport ou autre pièce fournie, s\'il y a lieu',
    )

    @api.one
    @api.depends ('nom', 'prenoms', 'full_name')
    @api.onchange ('nom', 'prenoms', 'full_name')
    def _get_full_name(self):
        self.full_name = '%s %s' % (self.nom, self.prenoms)
        if bool (self.full_name):
            self.name = self.full_name
        else:
            self.name = '%s %s' % (self.nom, self.prenoms)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append (
                (record.id,
                 u"%s %s" % (record.nom, record.prenoms)
                 ))
        return result

    @api.model
    @api.returns ('self', lambda value: value.id)
    def create(self, vals):
        vals['is_adherent'] = True
        if not vals.get ('code_id'):
            sequence = self.env['ir.sequence'].next_by_code ('proximas.adherent')
            vals['code_id'] = sequence
        return super (Adherent, self).create (vals)

    @api.constrains ('date_naissance')
    def _check_date_naissance(self):
        for rec in self:
            if rec.date_naissance > fields.Date.today ():
                raise ValidationError (
                    '''
                      Contrôle des règles de Gestion : Proximas
                      La date de naissance doit être inférieure ou égale  à la date du jour ! 
                      Vérifiez s'il n'y a pas d'erreur sur la date saisie ?
                    ''')

    @api.constrains ('age')
    def _check_age_limite(self):
        for rec in self:
            # to fetch sale order partner from context.
            # self._context is the shortcut of self.env.context
            police = self._context.get ('police_id')
            if rec.age > police.age_limite_adherent:
                raise ValidationError (
                    '''
                         PROXIMAS : VIOLATION DE REGLE DE GESTION:
                         Contrôle des règles de Gestion: Age limite Adhérent.
                         L'âge de cet adhérent est supérieur à la limite autorisée.
                     '''
                )

    # CONTRAINTES DE VALIDATION ADHERENT
    sql_constraints = [

        ('nom_prenoms_matricule',
         'UNIQUE (nom, prenoms, matricule)',
         '''
         Risque de doublon sur Adhérent!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
         '''
         ),

        ('code_id_unique',
         'UNIQUE (code_id)',
         '''
         Risque de doublon sur Code ID. Assuré!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
         '''
         ),

        ('matricule_unique',
         'UNIQUE (matricule)',
         '''
         Risque de doublon sur Matricule Adhérent!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
         '''
         )
    ]


class AyantDroit (models.Model):
    _name = 'proximas.ayant.droit'
    _inherits = {'proximas.assure': 'assure_id'}
    _description = 'Ayant droits'

    assure_id = fields.Many2one (
        comodel_name="proximas.assure",
        string="Assure",
        ondelete='cascade',
        required=True,
    )
    contrat_id = fields.Many2one (
        comodel_name="proximas.contrat",
        string="Contrat",
        ondelete='restrict',
    )
    delai_carence = fields.Integer (
        string="Délai de carence",
        help="La période (nbre. de jours) de carence à observer avant de bénéficier de la couverture!",
        default=lambda self: self.contrat_id.delai_carence_police,
    )

    @api.one
    @api.depends ('nom', 'prenoms', 'full_name')
    @api.onchange ('nom', 'prenoms', 'full_name')
    def _get_full_name(self):
        self.full_name = '%s %s' % (self.nom, self.prenoms)
        if bool (self.full_name):
            self.name = self.full_name
        else:
            self.name = '%s %s' % (self.nom, self.prenoms)

    @api.multi
    @api.depends ('date_naissance', 'decede')
    @api.onchange ('date_naissance', 'decede')
    def _compute_age(self):
        now = datetime.now ()
        for rec_id in self:
            if rec_id.date_naissance:
                dob = fields.Datetime.from_string (rec_id.date_naissance)
                if bool (rec_id.decede):
                    dod = fields.Datetime.from_string (rec_id.date_deces)
                    delta = relativedelta (dod, dob)
                    deceased = _ (' (Décédé(e))')
                else:
                    delta = relativedelta (now, dob)
                    deceased = ''
                years = '%s' % (delta.years)
                years_months_days = '%s%s %s%s %s%s%s' % (
                    delta.years, _ (' An(s) -'),
                    delta.months, _ (' mois -'),
                    delta.days, _ (' jours'), deceased
                )
                rec_id.age_details = years_months_days
                rec_id.age = int (years) + 1
            else:
                years_months_days = _ ('Aucune Date Naissance!')
                rec_id.age_details = years_months_days

    @api.one
    @api.onchange ('genre')
    def _check_genre(self):
        if not bool (self.contrat_id.controle_genre):
            if self.statut == 'conjoint' and self.genre == self.contrat_id.genre:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'action_warn',
                    'name': 'Warning',
                    'params': {
                        'title': 'Warning!',
                        'text': 'Entered Quantity is greater than quantity on source.',
                        'sticky': True
                    }
                }

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append (
                (record.id,
                 u"%s %s" % (record.nom, record.prenoms)
                 ))
        return result

    @api.model
    @api.returns ('self', lambda value: value.id)
    def create(self, vals):
        vals['is_ayant_droit'] = True
        if not vals.get ('code_id'):
            sequence = self.env['ir.sequence'].next_by_code ('proximas.ayant.droit')
            vals['code_id'] = sequence
        return super (AyantDroit, self).create (vals)

    @api.constrains ('date_naissance')
    def _check_date_naissance(self):
        for rec in self:
            if rec.date_naissance > fields.Date.today ():
                raise ValidationError (
                    '''
                      Contrôle des règles de Gestion : Proximas
                      La date de naissance doit être inférieure ou égale  à la date du jour ! 
                      Vérifiez s'il n'y a pas d'erreur sur la date saisie ?
                    ''')

    # CONTRAINTES DE VALIDATION AYANT-DROIT
    sql_constraints = [

        ('nom_prenoms_contrat_id',
         'UNIQUE (nom, prenoms, contrat_id)',
         '''
         Risque de doublon sur Ayant-droit!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
         '''
         ),

        ('code_id_unique',
         'UNIQUE (code_id)',
         '''
         Risque de doublon sur Code ID. Assuré!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
         '''
         ),
    ]


class DecesWizard (models.TransientModel):
    _name = 'proximas.deces.wizard'
    _description = 'Declaration Deces Wizard'

    code_saisi = fields.Char (
        string="Code ID.",
        required=True,
        help="Veuillez fournir le Code identifiant de l'assuré concerné."
    )

    @api.multi
    def open_popup(self):
        self.ensure_one ()
        user_id = self.env.context.get ('uid')
        user = self.env['res.users'].search ([('id', '=', user_id)])
        # prestataire = self.env['res.partner'].search ([('id', '=', user.partner_id.id)])
        # prestations = self.env['proximas.prestation'].search ([('prestataire_id', '=', user.partner_id.id)])
        assure = self.env['proximas.assure'].search ([
            '|', ('code_id_externe', '=', self.code_saisi),
            ('code_id', '=', self.code_saisi)
        ])
        info_assure = str (assure.name)
        # 1. Vérification du contrat pour l'assuré.
        if bool (assure) and not bool (assure.police_id):
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, celui-ci ne possède \
                 aucun contrat faisant référence à sa police de couverture. Veuillez contactez les administrateurs pour \
                 plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 2. Vérification de la préeésence de doublon sur l'assuré.
        elif len (assure) > 1:
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion:\n\
                L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                l'objet d'un traitement, car il y a risque de doublon sur l'assuré en question. \
                Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 3. Vérification du statut de décès de l'assuré.
        elif bool (assure) and bool (assure.decede):
            date_deces = fields.Datetime.from_string (self.date_deces)
            date_deces_format = date_deces.strftime ('%d-%m-%Y')
            raise ValidationError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                L'assuré: %s - Code ID.: %s est bel et bien enregistré en tant que bénéficiaire. Cependant, \
                a déjà fait l'objet d'une déclaration faisant passer son statut à celui de décédé le : %s.\n \
                Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id, date_deces_format)
                                   )
        elif bool (assure) and bool (assure.num_contrat):
            if assure.code_id_externe == self.code_saisi:
                code_id = assure.code_id
                return {
                    'name': 'Déclaration Décès Assuré',
                    'view_type': 'form',
                    'view_mode': 'form',
                    # 'target': 'new',
                    'res_model': 'proximas.deces',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_assure_id': assure.id,
                        'default_code_id_externe': self.code_saisi,
                        'default_code_id': code_id,
                        'default_user': user.name,
                        'default_user_id': user.id,
                    },
                }
            else:
                return {
                    'name': 'Déclaration Décès Assuré',
                    'view_type': 'form',
                    'view_mode': 'form',
                    # 'target': 'new',
                    'res_model': 'proximas.deces',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_assure_id': assure.id,
                        'default_code_id': self.code_saisi,
                        'default_user': user.name,
                        'default_user_id': user.id,
                    },
                }
        else:
            raise ValidationError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                 Le Code ID. que vous avez fourni n'est pas un identifiant valide dans le système.\n\
                 Veuillez contactez l 'administrateur en cas de besoin..!"
            )
            )


class DeclarationDeces (models.Model):
    _name = 'proximas.deces'
    _description = 'Declaration Deces'

    sequence = fields.Integer (
        string="Sequence"
    )
    assure_id = fields.Many2one (
        comodel_name="proximas.assure",
        string="Assure",
        required=True,
    )
    date_deces = fields.Date (
        string="Date Décès",
        required=True,
    )
    ref_certificat = fields.Char (
        size=32,
        string="Réf. du Certificat Décès",
        required=True,
    )
    date_certificat = fields.Date (
        string="Date du Certificat",
        required=True,
    )
    doc_certificat = fields.Binary (
        string="Certificat Scanné",
        attachment=True,
        help='Joindre le certificat scanné au format pdf ou autre',
    )
    date_reglement = fields.Date (
        string="Date règlement",
    )
    mt_reglement = fields.Float (
        string="Montant Perçu",
        digits=(6, 0),
    )
    mode_reglement = fields.Selection (
        string="Mode Règlement",
        selection=[
            ('espece', 'Espèces'),
            ('cheque', 'Chèque'),
            ('virement', 'Virement'),
        ],
        default='espece',
        required=False,
    )
    ref_reglement = fields.Char (
        size=32,
        string='Réf. Chèque/Virement',
        help='Indiquez les références du chèque ou du virement bancaire',
    )
    beneficiaire = fields.Char (
        string="Héritier/Bénéficiaire",
        help='Identification du bénéficiare : Nom et Prénoms',
    )
    type_piece = fields.Selection (
        string="Pièce ID.",
        selection=[
            ('cni', 'Carte Nationale d\'Identité'),
            ('ani', 'Attestation d\'Identité'),
            ('psp', 'Passeport'),
            ('cc', 'Carte Consulaire'),
        ],
        default='cni',
    )
    ref_piece = fields.Char (
        size=32,
        string="Num. Pièce d'identité",
    )
    validite_piece = fields.Date (
        string="Date de validité Pièce",
    )
    note = fields.Text (
        string="Notes et Observations",
    )
    # DETAILS ASSURE
    code_id = fields.Char (
        string="Code ID.",
        related='assure_id.code_id',
        readonly=True,
    )
    code_id_externe = fields.Char (
        string="Code ID.",
        related='assure_id.code_id_externe',
        readonly=True,
    )
    name = fields.Char (
        string="Nom et Prénoms",
        related='assure_id.name',
        readonly=True,
    )
    date_naissance = fields.Date (
        string="Date Naissance",
        related='assure_id.date_naissance',
        readonly=True,
    )
    statut_familial = fields.Selection (
        string="Statut Familial",
        related="assure_id.statut_familial",
        readonly=True,
    )
    genre = fields.Selection (
        string="",
        related='assure_id.genre',
        readonly=True,
    )
    photo = fields.Binary (
        string="Photo",
        attachment=True,
        related="assure_id.image",
        readonly=True,
    )
    # Infos POLICE
    police_id = fields.Char (
        string="Police",
        compute='_get_police_deces',
    )
    mt_reglement_deces = fields.Float (
        string="Net à Payer",
        digits=(9, 0),
        compute='_get_police_deces',
        default=0,
    )

    @api.one
    @api.depends ('code_id')
    def _get_police_deces(self):
        self.ensure_one ()
        if self.statut_familial == 'adherent':
            adherent = self.env['proximas.adherent'].search ([('code_id', '=', self.code_id)])
            contrat = self.env['proximas.contrat'].search ([('adherent_id', '=', adherent.id)])
            capital_deces = contrat.mt_capital_deces
            self.police_id = contrat.police_id.name
            self.mt_reglement_deces = capital_deces
        elif self.statut_familial == 'conjoint' or self.statut_familial == 'enfant':
            ayant_droit = self.env['proximas.ayant.droit'].search ([('code_id', '=', self.code_id)])
            contrat = self.env['proximas.contrat'].search ([('id', '=', ayant_droit.contrat_id.id)])
            frais_funeraire = contrat.mt_frais_funeraire
            self.police_id = contrat.police_id.name
            self.mt_reglement_deces = frais_funeraire

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append (
                (record.id,
                 u"%s" % record.assure_id.name
                 ))
            return result

    @api.multi
    @api.depends ('date_deces')
    def _check_deces(self):
        for rec_id in self:
            if rec_id.date_deces:
                rec_id.assure_id.date_deces = rec_id.date_deces
                rec_id.assure_id.decede = bool (rec_id.date_deces)

    # CONTRAINTES
    _sql_constraints = [
        ('assure_id',
         'UNIQUE (assure_id)',
         '''
         PROXIMAS GESTION : Contrôle de Règles de Gestion:
         Il semble que cet identifiant a déjà fait l'objet d'une déclaration de décès...
         Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
         '''
         ),
    ]


class SanctionWizard (models.TransientModel):
    _name = 'proximas.sanction.wizard'
    _description = 'Sanction Deces Wizard'

    code_saisi = fields.Char (
        string="Code ID.",
        required=True,
        help="Veuillez fournir le Code identifiant de l'assuré concerné."
    )

    @api.multi
    def open_popup(self):
        self.ensure_one ()
        user_id = self.env.context.get ('uid')
        user = self.env['res.users'].search ([('id', '=', user_id)])
        # prestataire = self.env['res.partner'].search ([('id', '=', user.partner_id.id)])
        # prestations = self.env['proximas.prestation'].search ([('prestataire_id', '=', user.partner_id.id)])
        assure = self.env['proximas.assure'].search ([
            '|', ('code_id_externe', 'ilike', self.code_saisi),
            ('code_id', 'ilike', self.code_saisi)
        ])
        sanction_assure = self.env['proximas.sanction'].search ([
            ('assure_id', '=', assure.id),
        ])
        info_assure = str (assure.name)
        # 1. Vérification du contrat pour l'assuré.
        if bool (assure) and not bool (assure.police_id):
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, celui-ci ne possède \
                 aucun contrat faisant référence à sa police de couverture. Veuillez contactez les administrateurs pour \
                 plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 2. Vérification de la préeésence de doublon dans la liste sanctions (Suspension & Exclusion).
        elif bool (sanction_assure):
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion:\n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                 l'objet d'un traitement, car l'assuré en question fait l'objet d'une santion en cours. \
                 Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 3. Vérification de la préeésence de doublon sur l'assuré.
        elif len (assure) > 1:
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion:\n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                 l'objet d'un traitement, car il y a risque de doublon sur l'assuré en question. \
                 Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 4. Vérification du statut de décès de l'assuré.
        elif bool (assure) and bool (assure.decede):
            date_deces = fields.Datetime.from_string (self.date_deces)
            date_deces_format = date_deces.strftime ('%d-%m-%Y')
            raise ValidationError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien enregistré en tant que bénéficiaire. Cependant, \
                 a déjà fait l'objet d'une déclaration faisant passer son statut à celui de décédé(e) le : %s.\n \
                 Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id, date_deces_format)
                                   )
        elif bool (assure) and bool (assure.num_contrat):
            if assure.code_id_externe == self.code_saisi:
                code_id = assure.code_id
                return {
                    'name': 'Déclaration Sanction Assuré',
                    'view_type': 'form',
                    'view_mode': 'form',
                    # 'target': 'new',
                    'res_model': 'proximas.sanction',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_assure_id': assure.id,
                        'default_code_id_externe': self.code_saisi,
                        'default_code_id': code_id,
                        'default_user': user.name,
                        'default_user_id': user.id,
                    },
                }
            else:
                return {
                    'name': 'Déclaration Sanction Assuré',
                    'view_type': 'form',
                    'view_mode': 'form',
                    # 'target': 'new',
                    'res_model': 'proximas.sanction',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_assure_id': assure.id,
                        'default_code_id': self.code_saisi,
                        'default_user': user.name,
                        'default_user_id': user.id,
                    },
                }
        else:
            raise ValidationError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                 Le Code ID. que vous avez fourni n'est pas un identifiant valide dans le système.\n\
                 Veuillez contactez l 'administrateur en cas de besoin..!"
            )
            )


class Sanction (models.Model):
    _name = 'proximas.sanction'
    _description = 'sanctions assures'

    sequence = fields.Integer (
        string="Sequence"
    )
    assure_id = fields.Many2one (
        comodel_name="proximas.assure",
        string="Assuré",
        required=True,
    )
    ref_piece = fields.Char (
        size=32,
        string="Réf. PV de la sanction",
    )
    pv_sanction = fields.Binary (
        string="PV Décision Scanné",
        attachment=True,
        help='Joindre le PV scanné de la décision de sanction.)',
    )
    doc_filename = fields.Char (
        "Nom du fichier joint",
    )
    type_sanction = fields.Selection (
        string="Nature Sanction",
        selection=[
            ('suspens', 'Suspension'),
            ('exclu', 'Exclusion'),
        ],
        default='suspens',
        required=True,
        help="Indiquer la nature de la sanction. ATTENTION: L'exclusion est définitive.",
    )
    date_debut = fields.Date (
        string="Date Début",
        required=True,
    )
    date_fin = fields.Date (
        string="Date Fin",
    )
    jours_restant = fields.Float (
        string="Délai (jours)",
        compute='_check_en_cours',
        digits=(6, 0),
        required=False,
    )
    en_cours = fields.Boolean (
        string="Est en Cours?",
        compute='_check_en_cours',
        store=True,
        require=False,
    )
    motif_sanction = fields.Text (
        string="Motif",
        help="Texte précisant le ou les motif(s) de la sanction",
    )
    note = fields.Text (
        string="Notes et Observations",
    )
    # DETAILS ASSURE
    code_id = fields.Char (
        string="Code ID.",
        related='assure_id.code_id',
        readonly=True,
    )
    code_id_externe = fields.Char (
        string="Code ID.",
        related='assure_id.code_id_externe',
        readonly=True,
    )
    name = fields.Char (
        string="Nom et Prénoms",
        related='assure_id.name',
        readonly=True,
    )
    date_naissance = fields.Date (
        string="Date Naissance",
        related='assure_id.date_naissance',
        readonly=True,
    )
    statut_familial = fields.Selection (
        string="Statut Familial",
        related="assure_id.statut_familial",
        readonly=True,
    )
    genre = fields.Selection (
        string="",
        related='assure_id.genre',
        readonly=True,
    )
    photo = fields.Binary (
        string="Photo",
        attachment=True,
        related="assure_id.image",
        readonly=True,
    )

    # @api.one
    @api.depends ('date_debut', 'date_fin', 'jours_restant')
    def _check_en_cours(self):
        now = datetime.now ()
        debut = fields.Datetime.from_string (self.date_debut)
        fin = fields.Datetime.from_string (self.date_fin) or now
        nbre_jours = (fin - now).days
        self.jours_restant = nbre_jours + 1
        if (self.type_sanction == 'exclu') and (debut <= now):
            self.en_cours = True
        elif (self.type_sanction == 'suspens') and (self.jours_restant >= 1):
            self.en_cours = True
        else:
            self.en_cours = False

    @api.constrains ('date_debut', 'date_fin')
    def _check_date_saisie(self):
        for rec in self:
            now = datetime.now ()
            debut = fields.Datetime.from_string (rec.date_debut)
            fin = fields.Datetime.from_string (rec.date_fin) or now
            if (rec.type_sanction == 'suspens') and (debut > fin):
                raise ValidationError (
                    '''
                      Contrôle des règles de Gestion : Proximas
                      La date de début doit obligatoirement être inférieure à la date de fin ! 
                      Vérifiez s'il n'y a pas d'erreur sur la date saisie ?
                    ''')

    @api.constrains ('en_cours')
    def auto_check_en_cours(self):
        nbre_encours = self.search_count (
            [
                ('assure_id', '=', self.assure_id.id),
                # ('type_sanction', '=', self.type_sanction),
                ('en_cours', '=', True)
            ]
        )
        if nbre_encours > 1:
            raise ValidationError (_ (
                "Proximaas : Règles de Gestion \n \
                Il ne peut y avoir plus d'un enregistrement en cours pour un même assuré.\n \
                Vérifiez bien la(es) date(s) de début et/ou de fin. \n Pour plus d'informations, \
                veuillez contactez l'administrateur..."
            )
            )

    # CONTRAINTES SQL
    _sql_constraints = [
        ('assure_date_debut',
         'UNIQUE (assure_id, date_debut)',
         '''
         Risque de doublon sur date suspension assuré!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
         '''
         ),
    ]


class JustificatifEnfantWizard (models.TransientModel):
    _name = 'proximas.justificatif.enfant.wizard'
    _description = 'Justificatif Enfant Wizard'

    code_saisi = fields.Char (
        string="Code ID.",
        required=True,
        help="Veuillez fournir le Code identifiant de l'assuré concerné."
    )

    @api.multi
    def open_popup(self):
        self.ensure_one ()
        user_id = self.env.context.get ('uid')
        user = self.env['res.users'].search ([('id', '=', user_id)])
        # prestataire = self.env['res.partner'].search ([('id', '=', user.partner_id.id)])
        # prestations = self.env['proximas.prestation'].search ([('prestataire_id', '=', user.partner_id.id)])
        assure = self.env['proximas.assure'].search ([
            '|', ('code_id_externe', '=ilike', self.code_saisi),
            ('code_id', '=ilike', self.code_saisi)
        ])
        info_assure = str (assure.name)
        statut_familial = assure.statut
        # 1. Vérification du contrat pour l'assuré.
        if bool (assure) and not bool (assure.police_id):
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, celui-ci ne possède \
                 aucun contrat faisant référence à sa police de couverture. Veuillez contactez les administrateurs pour \
                 plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 2. Vérification de la préeésence de doublon sur l'assuré.
        elif len (assure) > 1:
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion:\n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                 l'objet d'un traitement, car il y a risque de doublon sur l'assuré en question. \
                 Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 3. Vérification du statut de décès de l'assuré.
        elif bool (assure) and bool (assure.decede):
            date_deces = fields.Datetime.from_string (self.date_deces)
            date_deces_format = date_deces.strftime ('%d-%m-%Y')
            raise ValidationError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien enregistré en tant que bénéficiaire. Cependant, \
                 a déjà fait l'objet d'une déclaration faisant passer son statut à celui de décédé le : %s.\n \
                 Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id, date_deces_format)
                                   )
        # 4. Vérification du statut familial => enfant de l'assuré.
        elif bool (assure) and statut_familial != 'enfant':
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, celui-ci n'a pas le \
                 statut familial => enfant. Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 5. Vérification du contrat de l'assuré.
        elif bool (assure) and bool (assure.num_contrat):
            if assure.code_id_externe == self.code_saisi:
                code_id = assure.code_id
                return {
                    'name': 'Déclaration Justificatif Enfant Assuré',
                    'view_type': 'form',
                    'view_mode': 'form',
                    # 'target': 'new',
                    'res_model': 'proximas.justificatif.enfant',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_assure_id': assure.id,
                        'default_code_id_externe': self.code_saisi,
                        'default_code_id': code_id,
                        'default_user': user.name,
                        'default_user_id': user.id,
                    },
                }
            else:
                return {
                    'name': 'Déclaration Justificatif Enfant Assuré',
                    'view_type': 'form',
                    'view_mode': 'form',
                    # 'target': 'new',
                    'res_model': 'proximas.justificatif.enfant',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_assure_id': assure.id,
                        'default_code_id': self.code_saisi,
                        'default_user': user.name,
                        'default_user_id': user.id,
                    },
                }
        else:
            raise ValidationError (_ (
                "Proximaas : Contrôle Règles de Gestion: \n\
                 Le Code ID. que vous avez fourni n'est pas un identifiant valide dans le système.\n\
                 Veuillez contactez l 'administrateur en cas de besoin..!"
            )
            )


class JustificatifEnfant (models.Model):
    _name = 'proximas.justificatif.enfant'
    _description = 'Justificatif Enfant'

    sequence = fields.Integer (
        string="Sequence"
    )
    date_saisie = fields.Date (
        string="Date Saisie",
        default=datetime.now (),
        required=False,
    )
    assure_id = fields.Many2one (
        comodel_name="proximas.assure",
        string="Assuré",
        required=True,
        domain=[
            ('statut_familial', '=', 'enfant'),
        ],
    )
    type_justificatif = fields.Selection (
        string="Justificatif",
        selection=[
            ('scolarite', 'Scolarité'),
            ('invalide', 'Invalidité'),
        ],
        default='scolarite',
        required=True,
        help="Indiquer la nature du justificatif. Sélectionner entre la scolarité et l'invalidité.",
    )
    doc_justificatif = fields.Binary (
        string="Justificatif Scanné",
        attachment=True,
        help='Joindre le document justificatif scanné au format pdf',
    )
    doc_filename = fields.Char (
        "Nom du fichier joint",
    )
    date_delivrance = fields.Date (
        string="Date Délivrance",
        required=True,
    )
    date_validite = fields.Date (
        string="Date validité",
        help="Indiquer s'il y a lieu, la date au-delà de laquelle le document n'est plus valable",
    )
    jours_valide = fields.Float (
        string="Validité (jours)",
        digits=(6, 0),
        compute='_check_en_cours',
        required=False,
    )
    en_cours = fields.Boolean (
        string="Validité(en cours)?",
        compute='_check_en_cours',
        store=True,
        help="Indique si la validité du document est en cours ou non!",
        required=False,
    )
    note = fields.Text (
        string="Notes et Observations",
    )
    # DETAILS ASSURE
    code_id = fields.Char (
        string="Code ID.",
        related='assure_id.code_id',
        readonly=True,
    )
    code_id_externe = fields.Char (
        string="Code ID. Externe",
        related='assure_id.code_id_externe',
        readonly=True,
    )
    name = fields.Char (
        string="Nom et Prénoms",
        related='assure_id.name',
        readonly=True,
    )
    date_naissance = fields.Date (
        string="Date Naissance",
        related='assure_id.date_naissance',
        readonly=True,
    )
    statut_familial = fields.Selection (
        string="Statut Familial",
        related="assure_id.statut_familial",
        readonly=True,
    )
    age = fields.Char (
        string="Age",
        related='assure_id.age',
        readonly=True,
    )
    age_entier = fields.Integer (
        string="Age",
        related='assure_id.age_entier',
        readonly=True,
    )
    genre = fields.Selection (
        string="",
        related='assure_id.genre',
        store=True,
    )
    photo = fields.Binary (
        string="Photo",
        attachment=True,
        related="assure_id.image",
        readonly=True,
    )
    num_contrat = fields.Char (
        string="N° Contrat",
        related='assure_id.num_contrat',
        store=True,
    )
    police_id = fields.Many2one (
        comodel_name="proximas.police",
        string="Police Couverture",
        related='assure_id.police_id',
        readonly=True,
    )
    libelle_police = fields.Char (
        string="Police Couverture",
        related='police_id.libelle',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends ('date_validite', 'jours_valide')
    def _check_en_cours(self):
        for rec in self:
            now = datetime.now ()
            validite = fields.Datetime.from_string (rec.date_validite) or now
            nbre_jours = (validite - now).days
            rec.jours_valide = nbre_jours + 1
            if (rec.jours_valide >= 1):
                rec.en_cours = True
            else:
                rec.en_cours = False

    @api.constrains ('en_cours')
    def auto_check_en_cours(self):
        nbre_encours = self.search_count (
            [
                ('assure_id', '=', self.assure_id.id),
                ('type_justificatif', '=', self.type_justificatif),
                ('en_cours', '=', True)
            ]
        )
        if nbre_encours > 1:
            raise ValidationError (_ (
                "Proximaas : Règles de Gestion Il ne peut y avoir plus d'un justificatif enregistré avec un statut: \
                en cours. Vérifiez si vous n'avez pas enregistrer plus d'un justificatifs. \n Pour plus d'informations, \
                veuillez contactez l'administrateur..."
            )
            )

    # CONTRAINTES
    _sql_constraints = [
        ('unique_assure_date_delivre',
         'UNIQUE (assure_id, date_delivrance)',
         '''
         Risque de doublon sur nom de document justificatif!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y a pas de doublon ou contactez l'administrateur.
         '''
         ),
    ]
