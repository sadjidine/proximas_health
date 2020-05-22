# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


import openerp
from openerp import tools
from openerp.tools.translate import _
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import randint

class Assure(models.Model):
    _name = 'proximas.assure'
    _description = 'Assures'
    _inherits = {'res.partner': 'partner_id'}
    _short_name = 'name'

    partner_id = fields.Many2one(
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='restrict',
        index=True,
    )
    sequence = fields.Integer(
        string="Sequence"
    )
    color = fields.Integer(
        string="Color index",
        required=False,
    )
    full_name = fields.Char(
        string="Nom Complet",
        compute='_get_full_name',
    )
    nom = fields.Char(
        string="Nom",
        size=32,
        required=True,
    )
    prenoms = fields.Char(
        string="Prénoms",
        size=64,
        required=True,
    )
    parent_id = fields.Many2one(
        comodel_name="proximas.assure",
        string="Assuré Principal",
        ondelete='restrict',
        index=True,
    )
    child_ids = fields.One2many(
        comodel_name="proximas.assure",
        inverse_name="parent_id",
        string="Ayant-droit",
    )
    code_id = fields.Char(
        string="Code Id.",
        compute="_get_code_id",
        help="Code d'identification unique fourni par le système.!",
        store=True,
        # default=lambda self: self._get_code_id(),
    )
    code_id_externe = fields.Char(
        size=32,
        string='Code ID. Externe',
        help="Code ID. obtenu à partir d'un système exterieur."
    )
    matricule = fields.Char(
        size=32,
        string='N° Matricule',
        help='Numero matricule s\'il y a lieu',
    )
    localite_id = fields.Many2one(
        comodel_name="proximas.localite",
        string="Localité",
        help="Indiquez la localité de rattachement de l'assuré",
    )
    groupe_id = fields.Many2one(
        comodel_name="proximas.groupe",
        string="Groupe",
        required=False,
    )
    # contrat_id = fields.Many2one(
    #     comodel_name="proximas.contrat",
    #     string="Contrat",
    # )
    genre = fields.Selection(
        [
            ('masculin', 'Masculin'),
            ('feminin', 'Feminin'),
        ],
        required=True,
    )
    statut_familial = fields.Selection(
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
    statut = fields.Selection(
        [
            ('conjoint', 'Conjoint(e)'),
            ('enfant', 'Enfant'),
            ('ascendant', 'Ascendant'),
            ('parent', 'Parent'),

        ],
        string="Statut Familial",
        help="Lien de parenté avec l'assuré principal.",
    )
    date_naissance = fields.Date(
        string="Date Naissance",
        required=True,
    )
    date_inscription = fields.Date(
        string="Date Inscription",
        required=True,
        default=fields.Date.today(),
        help="La date d'enregistrement de l'assuré dans le système.",
    )
    date_activation = fields.Date(
        string="Date Activation",
        default=fields.Date.today(),
        help='Indiquer la date d\'activation de l\'assuré.',
    )
    date_fin_prevue = fields.Date(
        string="Date Fin Prévue",
        default=fields.Date.today (),
        help='Indique la date de validité l\'assuré.',
    )
    date_edition_carte = fields.Date(
        string="Date Edition Carte",
    )
    retrait_carte = fields.Boolean(
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
    decede = fields.Boolean(
        compute='_get_date_deces',
        string='Décédé(e)?',
        default=False,
        help='(En cas de décès) A cocher automatiquement si une date de décès est fournie!',
    )
    motif_desactivation = fields.Char(
        string="Motif de désactivation",
        required=False,
    )
    mobile_2 = fields.Char(
        string="Tél. mobile 1",
        size=8
    )
    state = fields.Selection(
        string="Etat",
        selection=[
            ('actif', 'Activé(e)'),
            ('inactif', 'Désactivé(e)'),
            ('suspens', 'Suspension'),
            ('exclu', 'Exclusion)'),
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
    sanction_ids = fields.One2many(
        comodel_name="proximas.sanction",
        inverse_name="assure_id",
        string="Sanction (Supension/Exclusion)",
    )
    assure_actif = fields.Boolean(
        string="Actif?",
        dafault=True,
        halp="Etat de l'assuré : Actif ou non.",
    )
    code_perso = fields.Integer(
        string="Code Perso",
        default=0000,
    )
    code_pass = fields.Integer(
        string="Code Pass",
        compute='_get_code_pass',
        store=True,
    )
    is_assure = fields.Boolean(
        string="Est Assuré?",
        default=True,
        readonly=True,
    )
    cas_chronique = fields.Boolean(
        string="Malade Chronique?",
        default=False
    )
    general_info = fields.Text(
        string='Information General',
    )
    age = fields.Char(
        compute='_compute_age',
        store=True,
    )
    age_details = fields.Char(
        compute='_compute_age',
    )
    est_invalide = fields.Boolean(
        # disponible uniquement pour le statut_familial = Enfant
        string="Enfant invalide?",
        help="Cocher uniquement au cas où l'enfant est considéré comme invalide"
    )
    est_inactif = fields.Boolean(
        # Désactiver manuellement l'assuré (mettre son statut à inactif)
        string="Désactivé(e)?",
        help="Cocher uniquement pour déactiver l'assuré manuellement. (Statut = Désactivé)"
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    # CONTRAT POLICE DETAILS & ADHERENT
    contrat_id = fields.Many2one(
        # comodel_name="proximas.contrat",
        string="Contrat",
        compute='_get_contrat_id',
        store=True,
    )
    num_contrat = fields.Char (
        string="N° Contrat",
        related='contrat_id.num_contrat',
        readonly=True,
        store=True,
    )
    contrat_actif = fields.Boolean(
        string="Contrat Activé?",
        related='contrat_id.active',
        help="Indique l'état du contrat (actif ou non).",
    )
    police_id = fields.Many2one(
        # comodel_name="proximas.police",
        string="Police Couverture",
        related='contrat_id.police_id',
        store=True,
        readonly=True,
    )
    delai_carence = fields.Integer(
        string="Délai de carence",
        help="La période (nbre. de jours) de carence à observer avant de bénéficier de la couverture!",
        default=0,
    )
    structure_id = fields.Many2one(
        comodel_name="res.company",
        string="Organisation",
        related='contrat_id.structure_id',
    )
    plafond_individu = fields.Float(
        string="Plafond individu",
        digits=(9, 0),
        related='contrat_id.plafond_individu',
        default=0,
        readonly=True,
    )
    plafond_famille = fields.Float(
        string="Plafond Famille",
        digits=(9, 0),
        related='contrat_id.plafond_famille',
        default=0,
        readonly=True,
    )
    # Compteur de suivi de prises en charges (individu / famille)
    sous_totaux_assure = fields.Float(
        string="S/Totaux Assuré",
        digits=(9, 0),
        compute='_check_details_pec',
        default=0,
        # store=True,
        # related='assure_id.sous_totaux_pec',
    )
    sous_totaux_contrat = fields.Float(
        string="S/Totaux Contrat",
        digits=(9, 0),
        compute='_check_details_pec',
        default=0,
        # store=True,
        # related='assure_id.sous_totaux_pec',
    )
    nbre_actes_assure = fields.Integer(
        string="Nbre. Actes (Prestations) ",
        compute='_check_details_pec',
        default=0,
        # store=True,
        # related='assure_id.nbre_actes_pec',
    )
    nbre_phcie_assure = fields.Integer(
        string="Nbre. Prescriptions",
        # compute='_check_details_pec',
        default=0,
        store=True,
        # related='assure_id.nbre_actes_pec',
    )
    jours_activation_assure = fields.Integer(
        string="Nbre. jours Contrat",
        # compute='_get_jours_activation',
        default=0,
        readonly=True,
    )

    @api.multi
    def action_desactiver(self):
        for rec in self:
            rec.est_inactif = not rec.est_inactif
        return True

    # @api.multi
    # def state_inactif(self):
    #     for rec in self:
    #         if bool(rec.est_inactif):
    #             rec.state = 'inactif'

    @api.multi
    def _get_contrat_id(self):
        # self.ensure_one()
        for rec in self:
            if rec.statut_familial == 'adherent':
                adherent = self.env['proximas.adherent'].search ([
                    ('assure_id', '=', rec.id),
                ])
                contrat = self.env['proximas.contrat'].search ([('code_id', '=', adherent.code_id)])
                if bool (contrat):
                    rec.contrat_id = contrat.id
            elif rec.statut_familial != 'adherent':
                ayant_droit = self.env['proximas.ayant.droit'].search ([('assure_id', '=', rec.id)])
                if bool (ayant_droit):
                    rec.contrat_id = ayant_droit.contrat_id.id


    @api.multi
    def _check_details_pec(self):
        for rec in self:
            details_pec_assure = self.env['proximas.details.pec'].search (
                [('assure_id', '=', rec.id)]
            )
            details_pec_contrat = self.env['proximas.details.pec'].search(
                [('contrat_id', '=', rec.contrat_id.id)]
            )
            nbre_details_pec_assure = self.env['proximas.details.pec'].search_count ([
                ('assure_id', '=', rec.id),
                ('date_execution', '!=', None),
                ('produit_phcie_id', '=', None)
            ])
            nbre_details_phcie_assure = self.env['proximas.details.pec'].search_count([
                ('assure_id', '=', rec.id),
                ('date_execution', '!=', None),
                ('produit_phcie_id', '!=', None)
            ])
            if details_pec_assure:
                rec.nbre_actes_assure = int(nbre_details_pec_assure) or 0
                rec.nbre_phcie_assure = int(nbre_details_phcie_assure) or 0
                rec.sous_totaux_assure = sum(item.total_pc for item in details_pec_assure) or 0
                rec.sous_totaux_contrat = sum (item.total_pc for item in details_pec_contrat) or 0

    @api.one
    @api.depends('is_assure')
    def _get_code_id(self):
        """Généré un code identifiant pour assuré"""
        for rec_id in self:
            code_genere = int(randint(1, 1e3))
            upper_prenoms = rec_id.prenoms.upper()
            # rec_id.code_id = u'%04d%s%s' % (code_genere, rec_id.nom[:1], upper_prenoms[:1])
            code_prepare = int(rec_id.id) + code_genere
            rec_id.code_id = u'%06d%s%s' % (code_prepare, rec_id.nom[:1], upper_prenoms[:1])
        
    @api.one
    @api.depends('nom', 'prenoms', 'full_name')
    @api.onchange('nom', 'prenoms', 'full_name')
    def _get_full_name(self):
        self.full_name = '%s %s' % (self.nom, self.prenoms)
        if bool(self.full_name):
            self.name = self.full_name
        else:
            self.name = '%s %s' % (self.nom, self.prenoms)


    # @api.one
    # @api.depends('nom', 'prenoms', 'is_assure')
    # @api.onchange('nom', 'prenoms', 'is_assure')
    # def _get_full_name(self):
    #     # self.ensure_one()
    #     self.full_name = '%s %s' % (self.nom, self.prenoms)
    #     self.name = self.full_name


    # @api.multi
    # def _get_jours_activation(self):
    #     for rec in self:
    #         now = fields.Datetime.from_string(fields.Date.today())
    #         if rec.statut_familial == 'adherent':
    #             rec.date_activation = rec.contrat_id.date_activation
    #             rec.delai_carence = rec.contrat_id.delai_carence
    #             date_activation = fields.Datetime.from_string(rec.date_activation) or datetime.now()
    #             jours = now - date_activation
    #             rec.jours_activation_assure = int(jours.days)
    #         elif rec.statut_familial != 'adherent':
    #             date_activation = fields.Datetime.from_string(rec.date_activation) or datetime.now()
    #             jours = now - date_activation
    #             rec.jours_activation_assure = int(jours.days)

    @api.multi
    @api.depends('contrat_actif','code_id', 'state', 'is_assure', 'decede', 'statut_familial', 'age')
    def _get_state_assure(self):
        now = datetime.now()
        for rec in self:
            suspension = self.env['proximas.sanction'].search(
                [
                    ('code_id', '=', rec.code_id),
                    ('type_sanction', '=', 'suspens'),
                    ('en_cours', '=', True),
                ])
            exclusion = self.env['proximas.sanction'].search(
                [
                    ('code_id', '=', rec.code_id),
                    ('type_sanction', '=', 'exclu'),
                ])
            # 1. contrôle décès assuré
            if bool(rec.decede):
                rec.state = 'decede'
            # 2. contrôle sanctions (Suspensions, exclusions)
            elif bool(suspension):
                rec.state = 'suspens'
            elif bool(exclusion):
                rec.state = 'exclu'
            # 3. contrôle désactivation (inactif) manuelle
            if bool(rec.est_inactif):
                rec.state = 'inactif'
            # 4. contrôle contrat assure et age limite adht/Cjt - age majorité enfant
            elif rec.statut_familial == 'adherent':
                contrat = self.env['proximas.contrat'].search(
                    [
                        ('code_id', '=', rec.code_id),
                        ('date_naissance', '=', rec.date_naissance)
                    ]
                )
                age = int(rec.age)
                age_limite_adherent = int(contrat.age_limite_adherent)
                if not contrat.active:
                    rec.state = 'attente'
                elif age > age_limite_adherent > 0:
                    rec.state = 'age'
                else:
                    rec.state = 'actif'
            elif rec.statut_familial != 'adherent':
                ayant_droit = self.env['proximas.ayant.droit'].search(
                    [
                        ('assure_id', '=', rec.id),
                        ('code_id', '=', rec.code_id),
                    ]
                )
                contrat = self.env['proximas.contrat'].search([('id', '=', ayant_droit.contrat_id.id)])
                age_limite_conjoint = int(contrat.age_limite_conjoint)
                age_limite_ascendant = int(contrat.age_limite_ascendant)
                age_limite_parent = int(contrat.age_limite_parent)
                age_majorite_enfant = int(contrat.age_majorite_enfant)
                age_limite_enfant = int(contrat.age_limite_enfant)
                age = int(rec.age)
                if not contrat.active:
                    rec.state = 'attente'
                elif rec.statut_familial == 'conjoint' and age > age_limite_conjoint > 0:
                    rec.state = 'age'
                elif rec.statut_familial == 'ascendant' and age > age_limite_ascendant > 0:
                    rec.state = 'age'
                elif rec.statut_familial == 'parent' and age > age_limite_parent > 0:
                    rec.state = 'age'
                # 4. Vérifier Certificat de Scolarite / Invalidité Enfant
                elif rec.statut_familial == 'enfant':
                    scolarite = self.env['proximas.justificatif.enfant'].search(
                        [
                            ('code_id', '=', rec.code_id),
                            ('type_justificatif', '=', 'scolarite'),
                            ('en_cours', '=', True),
                        ]
                    )
                    invalidite = self.env['proximas.justificatif.enfant'].search(
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
    @api.depends('code_id', 'date_deces')
    def _get_date_deces(self):
        for rec_id in self:
            assure = self.env['proximas.deces'].search([('code_id', 'ilike', rec_id.code_id)])
            if assure:
                rec_id.date_deces = assure.date_deces
                rec_id.decede = True
                rec_id.state = 'decede'

    @api.multi
    @api.depends('date_naissance', 'decede')
    def _compute_age(self):
        now = datetime.now()
        for rec_id in self:
            if rec_id.date_naissance:
                dob = fields.Datetime.from_string(rec_id.date_naissance)
                if bool(rec_id.decede):
                    dod = fields.Datetime.from_string(rec_id.date_deces)
                    delta = relativedelta(dod, dob)
                    deceased = _(' (Décédé(e))')
                else:
                    delta = relativedelta(now, dob)
                    deceased = ''
                years = '%s' % (delta.years)
                years_months_days = '%s%s %s%s %s%s%s' % (
                    delta.years, _(' An(s) -'),
                    delta.months, _(' mois -'),
                    delta.days, _(' jours'), deceased
                )
                rec_id.age_details = years_months_days
                rec_id.age = int(years) + 1
            else:
                years_months_days = _('Aucune Date Naissance!')
                rec_id.age_details = years_months_days


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
            # disease_ids = self.env['medical.patient.disease'].search([
            #     ('patient_id', '=', self.id),
            #     ('active', '=', False),
            # ])
            # disease_ids.action_revalidate()

    # @api.multi
    # @api.depends('nom', 'prenoms', 'name')
    # def _get_display_name(self):
    #     for rec in self:
    #         if bool(rec.name):
    #             rec.display_name = rec.name
    #         else:
    #             rec.name = '%s %s' % (rec.nom, rec.prenoms)
    #             rec.display_name = rec.name
    #         rec.name = '%s %s' % (rec.nom, rec.prenoms)
    #         rec.display_name = rec.name

    # @api.multi
    # @api.depends('nom', 'prenoms', 'full_name', 'name')
    # def _get_full_name(self):
    #     for rec in self:
    #         rec.full_name = '%s %s' % (rec.nom, rec.prenoms)
    #         rec.name = rec.full_name
    #         if bool(rec.full_name):
    #             rec.name = rec.full_name
    #         else:
    #             rec.name = '%s %s' % (rec.nom, rec.prenoms)

    # @api.one
    # @api.depends('nom', 'prenoms')
    # def _get_code_id(self):
    #     """Généré un code identifiant pour assuré"""
    #     code_genere = int(randint(1, 1e3))
    #     upper_prenoms = str(self.prenoms).upper ()
    #     self.code_id = u'%04d%s%s' % (code_genere, self.nom[:1], upper_prenoms[:2])

    # @api.one
    # @api.depends('nom', 'prenoms')
    # def _get_code_id(self):
    #     """Généré un code identifiant pour assuré"""
    #     self.ensure_one()
    #     code_genere = int(randint(1, 1e3))
    #     prenoms = self.prenoms[:2]
    #     self.code_id = u'%04d%s%s' % (code_genere, self.nom[:1], prenoms.strip().upper())
    #     # self.code_id = "%06d%s" % (self.id, self.name[:2])

    @api.multi
    @api.depends('statut')
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
            result.append(
                (record.id,
                 u"%s %s" % (record.nom, record.prenoms)
                 ))
        return result

    @api.multi
    @api.depends('code_perso')
    def _get_code_pass(self):
        for record in self:
            if record.code_perso == 0 or not record.code_perso:
                code_genere = randint(1, 9999)
                record.code_pass = '%04d' % code_genere
            else:
                record.code_pass = record.code_perso

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['is_assure'] = True
        if not vals.get('code_id'):
            sequence = self.env['ir.sequence'].next_by_code('proximas.assure')
            vals['code_id'] = sequence
        return super(Assure, self).create(vals)


    @api.constrains ('date_naissance')
    def _check_date_naissance(self):
        for rec in self:
            if rec.date_naissance > fields.Date.today():
                raise ValidationError(
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


class Adherent(models.Model):
    _name = 'proximas.adherent'
    _inherits = {'proximas.assure': 'assure_id'}
    _description = 'Adherents souscripteurs'

    assure_id = fields.Many2one(
        comodel_name="proximas.assure",
        string="Assure",
        ondelete='cascade',
        required=True,
    )
    ref = fields.Char(
        size=32,
        string='Pièce N°',
        help='Type, N° et Date validité de la CNI, Passport ou autre pièce fournie, s\'il y a lieu',
    )

    # @api.multi
    # # @api.depends('nom', 'prenoms')
    # def _get_full_name(self):
    #     for rec in self:
    #         rec.full_name = '%s %s' % (rec.nom, rec.prenoms)
    #         rec.name = rec.full_name
    #         if bool (rec.full_name):
    #             rec.name = rec.full_name
    #         else:
    #             rec.name = '%s %s' % (rec.nom, rec.prenoms)

    # @api.one
    # @api.onchange('nom', 'prenoms')
    # def _get_full_name(self):
    #     self.ensure_one()
    #     self.name = '%s %s' % (self.nom, self.prenoms

    @api.one
    @api.depends('nom', 'prenoms', 'full_name')
    @api.onchange('nom', 'prenoms', 'full_name')
    def _get_full_name(self):
        self.full_name = '%s %s' % (self.nom, self.prenoms)
        if bool(self.full_name):
            self.name = self.full_name
        else:
            self.name = '%s %s' % (self.nom, self.prenoms)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                 u"%s %s" % (record.nom, record.prenoms)
                 ))
        return result

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['is_adherent'] = True
        if not vals.get('code_id'):
            sequence = self.env['ir.sequence'].next_by_code('proximas.adherent')
            vals['code_id'] = sequence
        return super(Adherent, self).create(vals)


    @api.constrains('date_naissance')
    def _check_date_naissance(self):
        for rec in self:
            if rec.date_naissance > fields.Date.today():
                raise ValidationError(
                    '''
                      Contrôle des règles de Gestion : Proximas
                      La date de naissance doit être inférieure ou égale  à la date du jour ! 
                      Vérifiez s'il n'y a pas d'erreur sur la date saisie ?
                    ''')


    @api.constrains('age')
    def _check_age_limite(self):
        for rec in self:
            # to fetch sale order partner from context.
            # self._context is the shortcut of self.env.context
            police = self._context.get('police_id')
            if rec.age > police.age_limite_adherent:
                raise ValidationError(
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


class AyantDroit(models.Model):
    _name = 'proximas.ayant.droit'
    _inherits = {'proximas.assure': 'assure_id'}
    _description = 'Ayant droits'


    assure_id = fields.Many2one(
        comodel_name="proximas.assure",
        string="Assure",
        ondelete='cascade',
        required=True,
    )
    contrat_id = fields.Many2one(
        comodel_name="proximas.contrat",
        string="Contrat",
    )
    delai_carence = fields.Integer(
        string="Délai de carence",
        help="La période (nbre. de jours) de carence à observer avant de bénéficier de la couverture!",
        default=lambda self: self.contrat_id.delai_carence_police,
    )

    # statut_familial = fields.Selection(
    #     [
    #         ('c', 'Conjoint(e)'),
    #         ('e', 'Enfant'),
    #     ],
    #     string="Statut Familial",
    #     default='e',
    #     help="Lien de parenté avec l'assuré principal.",
    #     required=True,
    # )
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
    @api.depends('date_naissance', 'decede')
    @api.onchange('date_naissance', 'decede')
    def _compute_age(self):
        now = datetime.now()
        for rec_id in self:
            if rec_id.date_naissance:
                dob = fields.Datetime.from_string(rec_id.date_naissance)
                if bool (rec_id.decede):
                    dod = fields.Datetime.from_string(rec_id.date_deces)
                    delta = relativedelta(dod, dob)
                    deceased = _ (' (Décédé(e))')
                else:
                    delta = relativedelta(now, dob)
                    deceased = ''
                years = '%s' % (delta.years)
                years_months_days = '%s%s %s%s %s%s%s' % (
                    delta.years, _(' An(s) -'),
                    delta.months, _(' mois -'),
                    delta.days, _(' jours'), deceased
                )
                rec_id.age_details = years_months_days
                rec_id.age = int(years) + 1
            else:
                years_months_days = _('Aucune Date Naissance!')
                rec_id.age_details = years_months_days

    @api.one
    @api.onchange('genre')
    def _check_genre(self):
        if not bool(self.contrat_id.controle_genre):
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
            result.append(
                (record.id,
                 u"%s %s" % (record.nom, record.prenoms)
                 ))
        return result


    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['is_ayant_droit'] = True
        if not vals.get('code_id'):
            sequence = self.env['ir.sequence'].next_by_code('proximas.ayant.droit')
            vals['code_id'] = sequence
        return super(AyantDroit, self).create(vals)

    @api.constrains('date_naissance')
    def _check_date_naissance(self):
        for rec in self:
            if rec.date_naissance > fields.Date.today():
                raise ValidationError(
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


class DecesWizard(models.TransientModel):
    _name = 'proximas.deces.wizard'
    _description = 'Declaration Deces Wizard'

    code_saisi = fields.Char(
        string="Code ID.",
        required=True,
        help="Veuillez fournir le Code identifiant de l'assuré concerné."
    )

    @api.multi
    def open_popup(self):
        self.ensure_one ()
        user_id = self.env.context.get('uid')
        user = self.env['res.users'].search([('id', '=', user_id)])
        # prestataire = self.env['res.partner'].search ([('id', '=', user.partner_id.id)])
        # prestations = self.env['proximas.prestation'].search ([('prestataire_id', '=', user.partner_id.id)])
        assure = self.env['proximas.assure'].search ([
            '|', ('code_id_externe', '=', self.code_saisi),
            ('code_id', '=', self.code_saisi)
        ])
        info_assure = str(assure.name)
        # 1. Vérification du contrat pour l'assuré.
        if bool(assure) and not bool(assure.police_id):
            raise UserError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, celui-ci ne possède \
                 aucun contrat faisant référence à sa police de couverture. Veuillez contactez les administrateurs pour \
                 plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 2. Vérification de la préeésence de doublon sur l'assuré.
        elif len(assure) > 1:
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion:\n\
                L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                l'objet d'un traitement, car il y a risque de doublon sur l'assuré en question. \
                Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 3. Vérification du statut de décès de l'assuré.
        elif bool(assure) and bool(assure.decede):
            date_deces = fields.Datetime.from_string(self.date_deces)
            date_deces_format = date_deces.strftime('%d-%m-%Y')
            raise ValidationError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                L'assuré: %s - Code ID.: %s est bel et bien enregistré en tant que bénéficiaire. Cependant, \
                a déjà fait l'objet d'une déclaration faisant passer son statut à celui de décédé le : %s.\n \
                Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id, date_deces_format)
                                   )
        elif bool(assure) and bool(assure.num_contrat):
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
            raise ValidationError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 Le Code ID. que vous avez fourni n'est pas un identifiant valide dans le système.\n\
                 Veuillez contactez l 'administrateur en cas de besoin..!"
            )
            )


class DeclarationDeces(models.Model):
    _name = 'proximas.deces'
    _description = 'Declaration Deces'

    # name = fields.Char()
    # assure_id = fields.Ref(
    #     comodel_name="proximas.assure",
    #     string="Assuré",
    #     required=True,
    #     domain=[
    #         ('decede', '=', False)
    #     ],
    # )
    sequence = fields.Integer(
        string="Sequence"
    )
    assure_id = fields.Many2one(
        comodel_name="proximas.assure",
        string="Assure",
        required=True,
    )
    date_deces = fields.Date(
        string="Date Décès",
        required=True,
    )
    ref_certificat = fields.Char(
        size=32,
        string="Réf. du Certificat Décès",
        required=True,
    )
    date_certificat = fields.Date(
        string="Date du Certificat",
        required=True,
    )
    doc_certificat = fields.Binary(
        string="Certificat Scanné",
        attachment=True,
        help='Joindre le certificat scanné au format image (jpeg, jpg ou png)',
    )
    date_reglement = fields.Date(
        string="Date règlement",
    )
    mt_reglement = fields.Float(
        string="Montant Perçu",
        digits=(6, 0),
    )
    mode_reglement = fields.Selection(
        string="Mode Règlement",
        selection=[
            ('espece', 'Espèces'),
            ('cheque', 'Chèque'),
            ('virement', 'Virement'),
        ],
        default='espece',
        required=False,
    )
    ref_reglement = fields.Char(
        size=32,
        string='Réf. Chèque/Virement',
        help='Indiquez les références du chèque ou du virement bancaire',
    )
    beneficiaire = fields.Char(
        string="Héritier/Bénéficiaire",
        help='Identification du bénéficiare : Nom et Prénoms',
    )
    type_piece = fields.Selection(
        string="",
        selection=[
            ('cni', 'Carte Nationale d\'Identité'),
            ('ani', 'Attestation d\'Identité'),
            ('psp', 'Passeport'),
            ('cc', 'Carte Consulaire'),
        ],
        default='cni',
    )
    ref_piece = fields.Char(
        size=32,
        string="Num. Pièce d'identité",
    )
    validite_piece = fields.Date(
        string="Date de validité Pièce",
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # DETAILS ASSURE
    code_id = fields.Char(
        string="Code ID.",
        related='assure_id.code_id',
        readonly=True,
    )
    name = fields.Char(
        string="Nom et Prénoms",
        related='assure_id.name',
        readonly=True,
    )
    date_naissance = fields.Date(
        string="Date Naissance",
        related='assure_id.date_naissance',
        readonly=True,
    )
    statut_familial = fields.Selection(
        string="Statut Familial",
        related="assure_id.statut_familial",
        readonly=True,
    )
    genre = fields.Selection(
        string="",
        related='assure_id.genre',
        readonly=True,
    )
    photo = fields.Binary(
        string="Photo",
        attachment=True,
        related="assure_id.image",
        readonly=True,
    )
    # Infos POLICE
    police_id = fields.Char(
        string="Police",
        compute='_get_police_deces',
    )
    mt_reglement_deces = fields.Float(
        string="Net à Payer",
        digits=(9, 0),
        compute='_get_police_deces',
        default=0,
    )

    @api.one
    @api.depends('code_id')
    def _get_police_deces(self):
        self.ensure_one()
        if self.statut_familial == 'adherent':
            adherent = self.env['proximas.adherent'].search([('code_id', '=', self.code_id)])
            contrat = self.env['proximas.contrat'].search([('adherent_id', '=', adherent.id)])
            capital_deces = contrat.mt_capital_deces
            self.police_id = contrat.police_id.name
            self.mt_reglement_deces = capital_deces
        elif self.statut_familial == 'conjoint' or self.statut_familial == 'enfant':
            ayant_droit = self.env['proximas.ayant.droit'].search([('code_id', '=', self.code_id)])
            contrat = self.env['proximas.contrat'].search([('id', '=', ayant_droit.contrat_id.id)])
            frais_funeraire = contrat.mt_frais_funeraire
            self.police_id = contrat.police_id.name
            self.mt_reglement_deces = frais_funeraire


    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                 u"%s" % record.assure_id.name
                 ))
            return result

    @api.multi
    @api.depends('date_deces')
    def _check_deces(self):
        for rec_id in self:
            if rec_id.date_deces:
                rec_id.assure_id.date_deces = rec_id.date_deces
                rec_id.assure_id.decede = bool(rec_id.date_deces)

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


class SanctionWizard(models.TransientModel):
    _name = 'proximas.sanction.wizard'
    _description = 'Sanction Deces Wizard'

    code_saisi = fields.Char(
        string="Code ID.",
        required=True,
        help="Veuillez fournir le Code identifiant de l'assuré concerné."
    )

    @api.multi
    def open_popup(self):
        self.ensure_one ()
        user_id = self.env.context.get('uid')
        user = self.env['res.users'].search([('id', '=', user_id)])
        # prestataire = self.env['res.partner'].search ([('id', '=', user.partner_id.id)])
        # prestations = self.env['proximas.prestation'].search ([('prestataire_id', '=', user.partner_id.id)])
        assure = self.env['proximas.assure'].search ([
            '|', ('code_id_externe', '=', self.code_saisi),
            ('code_id', '=', self.code_saisi)
        ])
        info_assure = str(assure.name)
        # 1. Vérification du contrat pour l'assuré.
        if bool(assure) and not bool(assure.police_id):
            raise UserError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, celui-ci ne possède \
                 aucun contrat faisant référence à sa police de couverture. Veuillez contactez les administrateurs pour \
                 plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 2. Vérification de la préeésence de doublon sur l'assuré.
        elif len(assure) > 1:
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion:\n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                 l'objet d'un traitement, car il y a risque de doublon sur l'assuré en question. \
                 Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 3. Vérification du statut de décès de l'assuré.
        elif bool(assure) and bool(assure.decede):
            date_deces = fields.Datetime.from_string(self.date_deces)
            date_deces_format = date_deces.strftime('%d-%m-%Y')
            raise ValidationError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien enregistré en tant que bénéficiaire. Cependant, \
                 a déjà fait l'objet d'une déclaration faisant passer son statut à celui de décédé le : %s.\n \
                 Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id, date_deces_format)
                                   )
        elif bool(assure) and bool(assure.num_contrat):
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
            raise ValidationError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 Le Code ID. que vous avez fourni n'est pas un identifiant valide dans le système.\n\
                 Veuillez contactez l 'administrateur en cas de besoin..!"
            )
            )


class Sanction(models.Model):
    _name = 'proximas.sanction'
    _description = 'sanctions assures'

    sequence = fields.Integer(
        string="Sequence"
    )
    assure_id = fields.Many2one(
        comodel_name="proximas.assure",
        string="Assuré",
        required=True,
    )
    ref_piece = fields.Char(
        size=32,
        string="Réf. PV de la sanction",
    )
    pv_sanction = fields.Binary(
        string="PV Décision Scanné",
        attachment=True,
        help='Joindre le PV scanné au format image (jpeg, jpg ou png)',
    )
    type_sanction = fields.Selection(
        string="Nature Sanction",
        selection=[
            ('suspens', 'Suspension'),
            ('exclu', 'Exclusion'),
        ],
        default='suspens',
        required=True,
        help="Indiquer la nature de la sanction. ATTENTION: L'exclusion est définitive.",
    )
    date_debut = fields.Date(
        string="Date Début",
        required=True,
    )
    date_fin = fields.Date(
        string="Date Fin",
    )
    en_cours = fields.Boolean(
        string="Est en Cours?",
        compute='_check_en_cours',
        default=False,
        store=True,
        help="Indique si la sanction est en cours ou non!",
    )
    motif_sanction = fields.Text(
        string="Motif",
        help="Texte précisant le ou les motif(s) de la sanction",
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # DETAILS ASSURE
    code_id = fields.Char(
        string="Code ID.",
        related='assure_id.code_id',
        readonly=True,
    )
    name = fields.Char(
        string="Nom et Prénoms",
        related='assure_id.name',
        readonly=True,
    )
    date_naissance = fields.Date(
        string="Date Naissance",
        related='assure_id.date_naissance',
        readonly=True,
    )
    statut_familial = fields.Selection(
        string="Statut Familial",
        related="assure_id.statut_familial",
        readonly=True,
    )
    genre = fields.Selection(
        string="",
        related='assure_id.genre',
        readonly=True,
    )
    photo = fields.Binary(
        string="Photo",
        attachment=True,
        related="assure_id.image",
        readonly=True,
    )

    @api.multi
    @api.depends('assure_id', 'type_sanction')
    def _check_en_cours(self):
        now = datetime.now()
        for rec in self:
            debut = fields.Datetime.from_string(rec.date_debut)
            fin = fields.Datetime.from_string(rec.date_fin)
            nbre_jours = (now - fin).days
            if rec.date_fin > now:
                rec.en_cours = True


    @api.constrains('date_debut', 'date_fin')
    def _check_date_saisie(self):
        for rec in self:
            if rec.date_debut > rec.date_fin:
                raise ValidationError(
                    '''
                      Contrôle des règles de Gestion : Proximas
                      La date de début doit obligatoirement être inférieure à la date de fin ! 
                      Vérifiez s'il n'y a pas d'erreur sur la date saisie ?
                    ''')

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


class JustificatifEnfantWizard(models.TransientModel):
    _name = 'proximas.justificatif.enfant.wizard'
    _description = 'Justificatif Enfant Wizard'

    code_saisi = fields.Char(
        string="Code ID.",
        required=True,
        help="Veuillez fournir le Code identifiant de l'assuré concerné."
    )

    @api.multi
    def open_popup(self):
        self.ensure_one ()
        user_id = self.env.context.get('uid')
        user = self.env['res.users'].search([('id', '=', user_id)])
        # prestataire = self.env['res.partner'].search ([('id', '=', user.partner_id.id)])
        # prestations = self.env['proximas.prestation'].search ([('prestataire_id', '=', user.partner_id.id)])
        assure = self.env['proximas.assure'].search([
            '|', ('code_id_externe', '=', self.code_saisi),
            ('code_id', '=', self.code_saisi)
        ])
        info_assure = str(assure.name)
        statut_familial = assure.statut
        # 1. Vérification du contrat pour l'assuré.
        if bool(assure) and not bool(assure.police_id):
            raise UserError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, celui-ci ne possède \
                 aucun contrat faisant référence à sa police de couverture. Veuillez contactez les administrateurs pour \
                 plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 2. Vérification de la préeésence de doublon sur l'assuré.
        elif len(assure) > 1:
            raise UserError (_ (
                "Proximaas : Contrôle Règles de Gestion:\n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, ne peut faire \
                 l'objet d'un traitement, car il y a risque de doublon sur l'assuré en question. \
                 Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id)
                             )
        # 3. Vérification du statut de décès de l'assuré.
        elif bool(assure) and bool(assure.decede):
            date_deces = fields.Datetime.from_string(self.date_deces)
            date_deces_format = date_deces.strftime('%d-%m-%Y')
            raise ValidationError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien enregistré en tant que bénéficiaire. Cependant, \
                 a déjà fait l'objet d'une déclaration faisant passer son statut à celui de décédé le : %s.\n \
                 Veuillez contactez les administrateurs pour plus détails..."
            ) % (info_assure, assure.code_id, date_deces_format)
                                   )
        # 4. Vérification du statut familial => enfant de l'assuré.
        elif bool(assure) and statut_familial != 'enfant':
            raise UserError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 L'assuré: %s - Code ID.: %s est bel et bien identifié dans le système. Cependant, celui-ci n'a pas le \
                 statut familial => enfant. Veuillez contactez les administrateurs pour plus détails..."
                ) % (info_assure, assure.code_id)
            )
        # 5. Vérification du contrat de l'assuré.
        elif bool(assure) and bool(assure.num_contrat):
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
            raise ValidationError(_(
                "Proximaas : Contrôle Règles de Gestion: \n\
                 Le Code ID. que vous avez fourni n'est pas un identifiant valide dans le système.\n\
                 Veuillez contactez l 'administrateur en cas de besoin..!"
            )
            )


class JustificatifEnfant(models.Model):
    _name = 'proximas.justificatif.enfant'
    _description = 'Justificatif Enfant'

    sequence = fields.Integer(
        string="Sequence"
    )
    assure_id = fields.Many2one(
                comodel_name="proximas.assure",
                string="Assuré",
                required=True,
                domain=[
                    ('statut_familial', '=', 'enfant'),
                    ],
    )
    type_justificatif = fields.Selection(
        string="Justificatif",
        selection=[
            ('scolarite', 'Scolarité'),
            ('invalide', 'Invalidité'),
        ],
        default='scolarite',
        required=True,
        help="Indiquer la nature du justificatif. Sélectionner entre la scolarité et l'invalidité.",
    )
    doc_justificatif = fields.Binary(
        string="Justificatif Scanné",
        attachment=True,
        help='Joindre le document justificatif scanné au format image (jpeg, jpg ou png)',
    )
    date_delivrance = fields.Date(
        string="Date Délivrance",
        required=True,
    )
    date_validite = fields.Date(
        string="Date validité",
        help="Indiquer s'il y a lieu, la date au-delà de laquelle le document n'est plus valable",
    )
    en_cours = fields.Boolean(
        string="Est en Cours?",
        compute='_check_en_cours',
        default=False,
        store=True,
        help="Indique si le document est en cours ou non!",
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # DETAILS ASSURE
    code_id = fields.Char(
        string="Code ID.",
        related='assure_id.code_id',
        readonly=True,
    )
    name = fields.Char(
        string="Nom et Prénoms",
        related='assure_id.name',
        readonly=True,
    )
    date_naissance = fields.Date(
        string="Date Naissance",
        related='assure_id.date_naissance',
        readonly=True,
    )
    statut_familial = fields.Selection(
        string="Statut Familial",
        related="assure_id.statut_familial",
        readonly=True,
    )
    genre = fields.Selection(
        string="",
        related='assure_id.genre',
        readonly=True,
    )
    photo = fields.Binary(
        string="Photo",
        attachment=True,
        related="assure_id.image",
        readonly=True,
    )

    @api.multi
    @api.depends('date_validite')
    def _check_en_cours(self):
        now = datetime.now()
        for rec in self:
            validite = fields.Datetime.from_string(rec.date_validite)
            if validite >= now:
                rec.en_cours = True


    @api.constrains ('en_cours')
    def auto_check_en_cours(self):
        nbre_encours = self.search_count([('en_cours', '=', True)])
        if nbre_encours > 1:
            raise ValidationError(_(
                u"Proximaas : Règles de Gestion Il ne peut y avoir plus d'un justificatif enregistré avec un statut: \
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
