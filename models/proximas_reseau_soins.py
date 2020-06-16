# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE - Sadjidine
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import openerp
from openerp import tools
from openerp.tools.translate import _
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta



class StatutReseau(models.Model):
    _name = 'proximas.statut.reseau'
    _description = 'Statut Reseau'

    # Definit le statut des prestataires dans le réseau de soins (Centre de reference Obligatoire (CRO),
    # Centre de Référence Standard (CRS), Pharmacie, Jocker)
    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Statut",
        size=24,
        required=True,
    )
    libelle = fields.Char(
        string="Libellé Statut",
        size=128,
        required=True
    )
    active = fields.Boolean(default=True)
    note = fields.Text(
        string="Notes et Observations",
    )
    # CONTRAINTES
    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         '''
         Risque de doublons Statut!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]


class CategoriePrestataire(models.Model):
    _name = 'proximas.categorie.prestataire'
    _description = 'forme prestataire'
    _short_name = 'ref'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Catégorie",
        size=32,
        help='nom de référence de la catégorie',
        required=True,
    )
    libelle = fields.Char(
        string="Libellé",
        help="Libellé de la catégorie s\'il ya lieu.",
        required=False,
    )
    active = fields.Boolean(default=True)
    note = fields.Text(
        string="Notes et Observations",
    )

    # CONTRAINTES
    _sql_constraints = [
        ('ref_uniq',
         'UNIQUE (name)',
         '''
         Risque de doublons Catégorie!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]


class Standing(models.Model):
    _name = 'proximas.standing'
    _description = 'Standing Police'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Integer(
        string="Nbre. d'étoiles",
        default=1,
        help='Le niveau de standing (Nbre. d\'étoiles)',
        required=True,
    )
    libelle = fields.Char(
        string="Libellé",
        help="Libellé de la catégorie s\'il ya lieu.",
        required=False,
    )
    police_ids = fields.One2many(
        comodel_name="proximas.police",
        inverse_name='standing_id',
        string="Police",
    )
    prestataire_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="standing_id",
        string="Prestataires",
    )
    active = fields.Boolean(
        default=True
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                 u"%d %s" % (record.name, record.libelle)
                 ))
        return result

    # CONTRAINTES
    _sql_constraints = [
        ('ref_uniq',
         'UNIQUE (name)',
         '''
         Risque de doublons Standing!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]


class Medecin(models.Model):
    _name = 'proximas.medecin'
    _description = 'Medecin Corps Medical'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(
        string="Sequence"
    )
    # display_name = fields.Char (
    #     string="Nom et prénoms",
    #     compute='_get_full_name',
    #     readonly=True,
    # )
    nom = fields.Char(
        string="Nom",
        size=32,
        required=True,
    )
    prenoms = fields.Char(
        string="Prénoms",
        size=128,
    )
    full_name = fields.Char(
        string="Nom",
        compute='_get_full_name',
        store=True,
    )
    genre = fields.Selection(
        [
            ('masculin', 'Masculin'),
            ('feminin', 'Feminin'),
        ],
        required=True,
    )
    num_ordre = fields.Char(
        string="Num. Ordre Médecin",
        required=False,
    )
    is_medecin = fields.Boolean(
        string="Est Médecin?",
        default=True,
        help="Indiquer si Oui le concerné est un membre du corp médical!"
    )
    is_conseil = fields.Boolean(
        string="Medecin Conseil?",
        help="Cocher pour indiquer que le médecin est un conseil.",
    )
    grade_id = fields.Many2one(
        comodel_name="proximas.grade.medecin",
        string="Grade",
        required=False,
        help='Indique le grade de la personne dans le corps médical',
    )
    specialite_id = fields.Many2one(
        comodel_name="proximas.specialite",
        string="Spécialité",
    )
    phone_2 = fields.Char(
        string="Téléphone #2",
        size=32
    )

    # CONTRAINTES
    _sql_constraints = [
        ('num_ordre_uniq',
         'UNIQUE (num_ordre)',
         '''
         Risque de doublons Pool Médical!
         Il semble que le numero de l'ordre des médecins existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]

    @api.one
    @api.depends('nom', 'prenoms', 'full_name')
    def _get_full_name(self):
        self.full_name = '%s %s' % (self.nom, self.prenoms)
        if bool(self.full_name):
            self.full_name = '%s %s' % (self.nom, self.prenoms)
            self.name = self.full_name
        else:
            self.full_name = '%s %s' % (self.nom, self.prenoms)
            self.name = '%s %s' % (self.nom, self.prenoms)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            nom = record.nom.strip()
            prenoms = record.prenoms.strip()
            result.append(
                (record.id,
                 u"%s %s" % (nom, prenoms)
                 ))
        return result


class Grade(models.Model):
    _name = 'proximas.grade.medecin'
    _description = 'Grades Medecins'

    sequence = fields.Integer(
        string="Sequence"
    )
    grade = fields.Char(
        string="Grade",
        size=32,
        required=True,
        help="Le grade concerné ou appelation."
    )
    name = fields.Char(
        string="Libellé",
        size=68,
        required=True,
        help="Libellé du grade concerné ou appelation."
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # CONTRAINTES
    _sql_constraints = [
        ('unique_grade',
         'UNIQUE (grade)',
         '''
         Proximas : Risque de doublon sur Localité/Zone!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]


class PoolMedical(models.Model):
    _name = 'proximas.pool.medical'
    _description = 'Pool Medical'

    # name = fields.Char()
    sequence = fields.Integer(
        string="Sequence"
    )
    medecin_id = fields.Many2one(
        comodel_name="proximas.medecin",
        string="Médecin",
    )
    prestataire_id = fields.Many2one(
        comodel_name="res.partner",
        string="Prestataire",
        domain=[
            ('is_prestataire', '=', True)
        ],
    )
    num_ordre = fields.Char(
        string="N°OM",
        related="medecin_id.num_ordre",
        readonly=True,
    )
    grade = fields.Char(
        related='medecin_id.grade_id.name',
        string="Grade",
        readonly=True,
        help='Indique le grade de la personne dans le corps médical',
    )
    name = fields.Char(
        string="Nom et Prénoms",
        related='medecin_id.name',
        readonly=True,
    )
    specialite = fields.Char(
        string="Spécialité",
        related="medecin_id.specialite_id.name",
        readonly=True,
    )
    is_conseil = fields.Boolean(
        string="Médecin Conseil?",
        related='medecin_id.is_conseil',
        readonly=True,
    )
    mobile = fields.Char(
        string="N°Mobile",
        related="medecin_id.mobile",
        readonly=True,
    )
    email = fields.Char(
        string="Email",
        related="medecin_id.email",
        readonly=True,
    )
    note = fields.Text(
        string="Notes et Observations",
        required=False,
    )
    # CONTRAINTES
    _sql_constraints = [
        ('name_medecin_uniq',
         'UNIQUE (medecin_id, prestataire_id)',
         '''
         Risque de doublons Pool Médical!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]


class PoolMedicalWizard(models.TransientModel):
    _name = 'pool.medical.wizard'
    _description = 'pool medical wizard'

    sequence = fields.Integer(
        string="Sequence"
    )
    prestataire_id = fields.Many2one(
        comodel_name="res.partner",
        string="Prestataire",
        domain=[
            ('is_prestataire', '=', True)
        ],
        required=True,
    )
    medecin_ids = fields.Many2many(
        comodel_name="proximas.medecin",
        string="Pool Médical du Prestataire",
    )
    note = fields.Text(
        string="Notes et Observations",
        required=False
    )

    @api.multi
    def record_pool(self):
        for wizard in self:
            prestataire = wizard.prestataire_id
            medecins = wizard.medecin_ids
            pool = self.env['proximas.pool.medical']
            for medecin in medecins:
                pool.create({'prestataire_id': prestataire.id,
                              'medecin_id': medecin.id})



class Prestation(models.Model):
    _name = 'proximas.prestation'
    _description = 'Offres Prestations'

    sequence = fields.Integer(
        string="Sequence"
    )
    code_prestation_id = fields.Many2one(
        comodel_name="proximas.code.prestation",
        string="Prestation",
    )

    prestataire_id = fields.Many2one(
        comodel_name="res.partner",
        string="Prestataire",
        domain=[
            ('is_prestataire', '=', True)
        ],
    )
    is_prestataire = fields.Boolean(
        string="Est Prestataire?",
        related='prestataire_id.is_prestataire',
        readonly=True,
        help="Indiquer si Oui le concerné est un prestataire conventionné!"
    )
    # Champs relztifs Code Prestation
    name = fields.Char(
        string='Prestation',
        related='code_prestation_id.name',
        # store=True,
        readyonly=True,
    )
    code = fields.Char(
        string='Code Prestation',
        related='code_prestation_id.code',
        readyonly=True,
    )
    delai_attente = fields.Integer(
        string="Délai Attente",
        related='code_prestation_id.delai_attente',
        readonly=True,
    )
    mt_cout_unit = fields.Float(
        string="Coût Unitaire",
        digits=(6,0),
        default=0,
        help="Indiquer le coût unitaire pris en compte dans le calcul en fonction du coefficient et/ou la quantité.",
    )
    # forfait_general = fields.Float(
    #     string="Coût Forfaitaire",
    #     digits=(6, 0),
    #     default=0,
    #     help='Montant forfaitaire général (sans tenir compte du coeficient et du coût unitaire.',
    # )
    forfait_sam = fields.Float(
        string="Forfait SAM",
        digits=(6, 0),
        default=0,
        help='Montant du forfait de la part SAM',
    )
    forfait_ticket = fields.Float(
        string="Forfait ticket",
        digits=(6, 0),
        default=0,
        help='Montant du forfait ticket modérateur',
    )
    code_non_controle = fields.Boolean(
        string="Code médical non contrôlé?",
        default=False,
        help="Prestation non soumis au contrôle du code médical de la police de couverture?"
    )
    mt_rabais = fields.Float(
        string="Rabais",
        digits=(6, 0),
        default=0,
    )
    taux_couvert_prestation = fields.Integer(
        string="Taux couverture (%)",
        default=0,
        help='Taux de couverture à appliquer sur la prestation exprimé en pourcentage (%)',

    )
    remise = fields.Integer(
        string="Taux Remise (%)",
        default=0,
        help='Taux de la remise à appliquer sur la prestation exprimé en pourcentage (%)',

    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # Champs Reliés Code Prestation
    rubrique_id = fields.Many2one(
        string="Rubrique",
        related='code_prestation_id.rubrique_id',
        store=True,
    )
    rubrique = fields.Char(
        string="Rubrique Médicale",
        related='rubrique_id.name',
        store=True,
    )
    code_medical_id = fields.Many2one(
        string="Code Médical",
        related='code_prestation_id.code_medical_id',
    )
    coefficient = fields.Integer(
        string="Coefficient",
        related='code_prestation_id.coefficient',
        readonly=True,

    )
    accord_prealable = fields.Boolean(
        string="Soumise à accord?",
        related='code_prestation_id.accord_prealable',
        readonly=True,
    )
    cout_modifiable = fields.Boolean(
        string="Coût Modifiable?",
        related='code_prestation_id.cout_modifiable',
        readonly=True,
    )
    quantite_exige = fields.Boolean(
        string="Quantité exigée?",
        related='code_prestation_id.quantite_exige',
        readonly=True,
    )
    arret_prestation = fields.Boolean(
        string="Arrêt de la prestation?",
        help='Cocher pour indiquer que la prestation est en arrêt. Cette prestation ne figurera plus dans la liste des \
            prestations du prestataire concerné.',
    )
    active = fields.Boolean(default=True)

    @api.depends('mt_cout_unit', 'forfait_sam', 'forfait_ticket')
    @api.constrains ('mt_cout_unit', 'forfait_sam', 'forfait_ticket')
    def check_and_validate_prestation(self):
        for rec in self:
            if rec.forfait_sam > 0 or rec.forfait_ticket > 0:
                forfait = int(rec.forfait_sam + rec.forfait_ticket)
                if forfait != int(rec.forfait_sam + rec.forfait_ticket):
                    raise ValidationError (_ (
                        "Proximaas : Contrôle de Règles de Gestion.\n\
                        Le montant du coût unitaire doit être egal à la somme du forfait SAM et du forfait assure.\
                        Par conséquent, veuillez modifier les montants concernés pour que la règle soit respectée. \
                        Veuiller contactez l'administrateur en cas de besoin."
                    )
                    )



    # CONTRAINTES
    _sql_constraints = [
        ('prestation_prestataire_uniq',
         'UNIQUE (prestataire_id, code_prestation_id)',
         '''
         Risque de doublons Prestation Médicale!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]



class PoolPrestationWizard(models.TransientModel):
    _name = 'pool.prestation.wizard'
    _description = 'pool prestation wizard'

    sequence = fields.Integer(
        string="Sequence"
    )
    prestataire_id = fields.Many2one(
        comodel_name="res.partner",
        string="Prestataire",
        domain=[
            ('is_prestataire', '=', True)
        ]
    )
    prestation_ids = fields.Many2many(
        comodel_name="proximas.code.prestation",
        string="Offre Prestations",
    )
    note = fields.Text(
        string="Notes et Observations",
        required=False
    )

    @api.multi
    def record_pool(self):
        for wizard in self:
            prestataire = wizard.prestataire_id
            prestations = wizard.prestation_ids
            pool = self.env['proximas.prestation']
            for prestation in prestations:
                pool.create({'prestataire_id': prestataire.id,
                            'code_prestation_id': prestation.id})


class SmsUser(models.Model):
    _name = 'proximas.sms.user'
    _description = 'Utilisateur SMS'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Nom et Prénoms",
        required=True,
        size=64
    )
    mobile = fields.Char(
        string="Num. Mobile",
        size=11,
        required=True,
        help="Numéro de téléphone mobile pour l'envoi et la réception de SMS. format international:- Ex.(:22501010101).",
    )
    prestataire_id = fields.Many2one(
        comodel_name="res.partner",
        string="Prestataire Médical - CRO",
        domain=[('is_prestataire', '=', True)],
        required=True,
    )
    pool_medical_id = fields.Many2one(
        comodel_name="proximas.pool.medical",
        string="Médecin (Pool médical)",
        required=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    @api.constrains('mobile')
    def _validate_mobile_number(self):
        for rec in self:
            mobile_number = self.search_count([
                ('mobile', '=', rec.mobile),
            ])
            if bool(mobile_number) > 1:
                raise ValidationError(_(
                    "Proximaas : Contrôle de Règles de Gestion.\n\
                    Il semble que le numéro de mobile: (%s) ait déjà été inscrit dans la liste des utilisateurs SMS.\
                    Par conséquent, il ne peut y avoir plus d'une fois un même numéro pour 2 utilisateurs. \
                    Veuiller contactez l'administrateur." % rec.mobile
                    )
                )

    # CONTRAINTES
    _sql_constraints = [
        ('name_localite_zone',
         'UNIQUE (mobile)',
         '''
         Risque de doublon sur Localité/Zone!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]
