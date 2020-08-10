# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE - Sadjidine
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp.tools.translate import _
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Specialite(models.Model):
    _name = 'proximas.specialite'
    _description = 'specialite medicale'

    name = fields.Char(
        string="Spécialité",
        compute='_check_name',
    )
    note = fields.Text(
        string="Notes et Observations",
        required=False
    )
    libelle = fields.Char(
        string="Spécialité",
        required=True,
        size=32,
    )

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            label = record.libelle
            if bool(label):
                result.append(
                    (record.id,
                     u"%s" % label.strip().upper()
                     ))
            record.name = label
        return result

    @api.one
    @api.depends('libelle')
    def _check_name(self):
        """
        Dépend du  texte du libellé fourni
        :return: texte en majuscule
        """
        libelle = self.libelle.upper()
        self.name = libelle

    # CONTRAINTES
    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         '''
         Risque de doublons sur spécialité !
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.
         
         ''')
    ]


class RubriqueMedicale(models.Model):
    _name = 'proximas.rubrique.medicale'
    _description = 'Rubrique Medicale'

    name = fields.Char(
        string="Libellé Rubrique",
        size=32,
        required=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )


    @api.multi
    @api.onchange('name')
    def _check_name(self):
        """
        Renvoi le texte saisi en majuscule
        :return: name en majuscule
        """
        for rec in self:
            if rec.name:
                label = str(rec.name)
                rec.name = u"%s" % label.strip().upper()
            # else:
            #     return {'value': {},
            #             'warning': {'title': 'warning', 'message': 'Your message' + str(rec.note)}
            #             }

    # CONTRAINTES
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)',
         '''
         Proximas : Contrôle de Règles de Gestion : Risque de doublons sur Rubrique !
         Il semble que ce libellé existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]


class CodeMedical(models.Model):
    _name = 'proximas.code.medical'
    _description = 'code medical'

    name = fields.Char(
        string="Code médical",
        size=64,
        required=True,
    )
    libelle = fields.Char(
        string="Libellé",
        size=128,
        hemp='Libellé Texte explicatif du code médical.',
    )
    rubrique_id = fields.Many2one(
        comodel_name="proximas.rubrique.medicale",
        string="Rubrique",
        required=False,
    )
    active = fields.Boolean(default=True)
    note = fields.Text(
        string="Notes et Observations",
    )

    @api.multi
    @api.onchange('name')
    def _check_name(self):
        """
        Renvoi le texte saisi en majuscule
        :return: name en majuscule
        """
        for rec in self:
            if rec.name:
                label = str(rec.name)
                rec.name = u"%s" % label.strip()

    # CONTRAINTES
    _sql_constraints = [
        ('name_rubrique_uniq', 'UNIQUE(name, rubrique_id)',
         '''
         Proximas : Contrôle de Règles de Gestion : Risque de doublons sur code médical !
         Il semble que ce libellé existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]


class Pathologie(models.Model):
    _name = 'proximas.pathologie'
    _description = 'pathotologies'

    name = fields.Char(
        string="Code Affection",
        required=True,
    )
    libelle = fields.Char(
        string="Pathologie",
        required=True,
    )
    specialite_id = fields.Many2one(
        comodel_name="proximas.specialite",
        string="Specialité",
    )
    est_risque = fields.Boolean(
        string="Pathologie à risque?",
        help="Cochez si la pathologie est à risque",
    )
    active = fields.Boolean (default=True)
    note = fields.Text(
        string="Notes et Observations",
    )
    # CONTRAINTES
    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         '''
         Risque de doublons sur Affection (Pathologie) !
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         '''),
        ('libelle_uniq',
         'UNIQUE (libelle)',
         '''
         Risque de doublons sur Affection (Pathologie) !
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]


class CodePrestation(models.Model):
    _name = 'proximas.code.prestation'
    _description = 'Code prestation'

    name = fields.Char(
        string="Prestation",
        required=True,
    )
    code = fields.Char(
        string="Code Prestation",
        size=4,
        required=False,
        help='Indiquez s\'il y lieu, le code de la prestation médicale / paramédicale. '
    )
    code_medical_id = fields.Many2one(
        comodel_name="proximas.code.medical",
        string="Code Médical",
        required=True,
    )
    coefficient = fields.Integer(
        string="Coefficient",
        required=True,
        default=1,
    )
    accord_prealable = fields.Boolean(
        string="Soumise à accord?",
        help='Cocher pour indiquer que la prestation est soumise à accord préalable.',
    )
    cout_modifiable = fields.Boolean(
        string="Coût Modifiable?",
        help='Cocher pour indiquer que le coût de la prestation est modifiable.',
    )
    quantite_exige = fields.Boolean(
        string="Quantité exigée?",
        help='Cocher pour indiquer que la quantité doit être fournie lors de la prestation.',
    )
    rubrique_id = fields.Many2one(
        comodel_name="proximas.rubrique.medicale",
        string="Rubrique",
        related='code_medical_id.rubrique_id',
        readonly=True,
    )
    rubrique = fields.Char(
        string="Rubrique",
        related='rubrique_id.name',
        readonly=True,
    )
    # Gestion de délai à observer avant de bénéficier de la même prestation médicale
    delai_attente = fields.Integer(
        string="Délai d'attente (Nbre. jours)",
        required=True,
        default=0,
        help="délai d'attente ==> Nombre de jours à observer pour bénéficier une seconde fois de cette prestation."
    )
    age_minimum = fields.Integer(
        string="Age Minimum.(années)",
        required=True,
        default=0,
        help="L'âge minimum autorisé pour l'accès à cette prestation."
    )
    age_maximum = fields.Integer(
        string="Age Maxi.(années)",
        required=True,
        default=0,
        help="L'âge maximum autorisé pour l'accès à cette prestation."
    )
    # active = fields.Boolean(default=True)
    note = fields.Text(
        string="Notes et Observations",
    )

    # CONTRAINTES
    _sql_constraints = [
        ('name_code_uniq',
         'UNIQUE (name, code, code_medical_id)',
         '''
         Risque de doublons sur Prestation médicale !
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]


# Gestion des Médicaments

class ClasseTherapeutiqe(models.Model):
    _name = 'proximas.classe.therapeutique'
    _description = 'Groupe Therapeutique'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Groupe Thérapeutique",
        size=128,
        required=True,
    )
    parent_id = fields.Many2one(
        comodel_name="proximas.classe.therapeutique",
        string="Classe Parente",
        ondelete='restrict',
    )
    child_ids = fields.One2many(
        comodel_name="proximas.classe.therapeutique",
        inverse_name="parent_id",
        string="Sous/Classes",
    )
    _parent_store = True

    parent_left = fields.Integer(
        index=True,
    )
    parent_right = fields.Integer(
        index=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    # CONTRAINTES
    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         '''
         Risque de doublons sur Classe thérapeutique !
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise ValidationError(
                'Erreur! Vous ne pouvez pas créer de catégories recursives...!'
            )




class Molecule(models.Model):
    _name = 'proximas.molecule'
    _description = 'Principes Actifs - DCI'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Molécule",
        required=True,
    )
    note = fields.Text (
        string="Notes et Observations",
    )

    # CONTRAINTES
    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         '''
         Risque de doublons sur Molécule !
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         ''')
    ]



class FormeGalenique(models.Model):
    _name = 'proximas.forme.galenique'
    _description = 'Forme Galenique'

    sequence = fields.Integer (
        string="Sequence"
    )
    name = fields.Char(
        string="Forme Galénique",
        size=64,
        required=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         '''
         Risque de doublons Forme Galénique!
         Il semble que cette Forme Galénique existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.
         ''')
    ]


class VoieTherapeutique(models.Model):
    _name = 'proximas.voie.therapeutique'
    _description = 'Voie therapeutique'


    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Voie thérapeutique",
        size=64,
        required=True,
    )
    note = fields.Text(
        string="Notes et Observations",
        required=False
    )

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         '''
         Risque de doublons Voie Thérapeutique!
         Il semble que ce libellé pour la voie thérapeutique existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.
         ''')
    ]


class ProduitPharmacie(models.Model):
    _name = 'proximas.produit.pharmacie'
    _description = 'Produit Pharmaceutique'

    name = fields.Char(
        string="Nom Commercial - Désignation",
        size=128,
        required=True
    )
    code_produit = fields.Char(
        string="Code Produit",
        size=64,
    )
    classe_therapeutique_ids = fields.Many2many(
        comodel_name="proximas.classe.therapeutique",
        string="Groupe(s) Thérapeutique(s)",
    )
    dosage = fields.Char(
        string="Dosage",
        size=64,
    )
    molecule_ids = fields.Many2many(
        comodel_name="proximas.molecule",
        string="Principe(s) Actif(s) (Molecules)",
    )
    voie_therapeutique_id = fields.Many2one(
        comodel_name="proximas.voie.therapeutique",
        string="Voie Thérapeutique",
    )
    forme_galenique_id = fields.Many2one(
        comodel_name="proximas.forme.galenique",
        string="Forme Galénique",
    )
    # rubrique_id = fields.Many2one(
    #     comodel_name="proximas.rubrique.medicale",
    #     string="Rubrique Médicale",
    #     default='PHARMACIE',
    # )
    prix_indicatif = fields.Float(
        string="Prix indicatif",
        digits=(6, 0),
        default=0,
    )
    # # Gestion de Taux de couverture à appliquer sur le médicament exprimé en pourcentage (%)
    # taux_couvert_produit = fields.Integer(
    #     string="Taux couverture (%)",
    #     default=0,
    #     help='Taux de couverture à appliquer sur le médicament exprimé en pourcentage (%)',
    #
    # )
    arret_medicament = fields.Boolean(
        string="Arrêter le produit?",
        help='Cocher pour indiquer l\'arrêt de la dispensation du produit. Ce produit ne figurera plus dans la liste des \
            médicaments dispensés.',
    )
    marge_medicament = fields.Float(
        string='Marge/Produit Phcie.',
        help="Marge tolérée sur le coût du produit pharmaceutique",
        digits=(6, 0),
        default=0,
    )
    # Gestion de délai à observer pour dispenser le même médicament
    delai_attente = fields.Integer(
        string="Délai d'attente (nbre. jours)",
        default=0,
        help="Nombre de jours à observer avant de dispenser le même médicament"
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
                 u"%s - %s %s"
                 % (record.name, record.forme_galenique_id.name or '', record.dosage or '')
                 ))
        return result

    # CONTRAINTES
    _sql_constraints = [
        ('name_voie_therapeutique_uniq',
         'UNIQUE (name, voie_therapeutique_id, molecule_id)',
         '''
         Risque de doublons Produit Pharmaceutique!
         Il semble que ce nom avec la même voie thérapeutique existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.
         
         ''')
    ]
