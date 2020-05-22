# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE - Sadjidine
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp.tools.translate import _
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ResCompany(models.Model):
    _inherit = 'res.company'

    sigle = fields.Char(
        string="Sigle",
        size=32,

    )
    exercice_ids = fields.One2many(
        comodel_name="proximas.exercice",
        inverse_name="res_company_id",
        string="Exercices",
        required=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    # CONTRAINTES
    _sql_constraints = [
        ('name_sigle_uniq',
         'UNIQUE (name, sigle)',
         '''
         Risque de doublon sur Structure/Organisation!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]

class Groupe(models.Model):
    _name = 'proximas.groupe'
    _description = 'Groupe assures'
    _inherits = {'res.partner': 'partner_id'}
    _short_name = 'name'

    sequence = fields.Integer(
        string="Sequence"
    )
    parent_id = fields.Many2one(
        comodel_name="proximas.groupe",
        string="Groupe Parent",
        ondelete='restrict',
        required=False,
    )
    child_ids = fields.One2many(
        comodel_name="proximas.groupe",
        inverse_name='parent_id',
        string="Children"
    )
    _parent_store = True
    parent_left = fields.Integer(
        'Left parent',
        select=True
    )
    parent_right = fields.Integer(
        'Right parent',
        select=True
    )
    partner_id = fields.Many2one(
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='cascade',
        # index=True,
    )
    is_groupe = fields.Boolean(
        string="Est Groupe?",
        default=True
    )
    general_info = fields.Text(
        string='Information General',
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    # @api.one
    @api.depends('parent_id', 'name')
    def _get_display_name(self):
        self.display_name = self.name_get()[0][1]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            names = []
            current = record
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((record.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args

        locs = self.search(args, limit=limit)
        if len(locs) == 1:
            child_dom = [('parent_left', '>', locs[0].parent_left), ('parent_left', '<', locs[0].parent_right)]
            child_locs = self.search(child_dom)
            locs = locs + child_locs

        return locs.name_get()


class Exercice(models.Model):
    _name = 'proximas.exercice'
    _description = 'exercices paramatres'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Libellé",
        required=True,
        size=64
    )
    res_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Structure",
        required=True,
    )

    date_debut = fields.Date(
        string="Date début Exo.",
        required=True,
    )
    date_fin = fields.Date(
        string="Date fin Exo.",
        required=True,
    )
    validite_pec = fields.Integer(
        string="Validité PEC (Heures)",
        required=True,
        help='Délai de validité d\'une prise en charge exprimé en heures',
        default=0,
    )
    marge_medicament = fields.Float(
        string='Marge/Produit Phcie.',
        help="Marge tolérée sur le coût des produits pharmaceutiques",
        digits=(5, 0),
        required=True,
        default=0,
    )
    cloture = fields.Boolean(
        string="Cloturé?",
        help="Cochez pour clôturer l'exercice concerné",
    )
    en_cours = fields.Boolean(
        string="En Cours?",
        help="Cochez pour activer l'exercice en cours. N.B.: Plus d'un exercice ne peuvent être en cours",
    )
    note = fields.Text(
        string="Notes et Observations",
    )


    @api.onchange('en_cours')
    def _check_en_cours(self):
        nbre_encours = self.search_count([('en_cours', '=', True)])
        if nbre_encours >= 1:
            raise UserError(_(
                "Proximaas: Contrôle Règles de Gestion - Exercice en cours:\n Il ne peut y avoir plus d'un exercice \
                 en cours. Vérifiez si vous n'avez pas fixé plus d'un exercice en cours. Pour plus d'informations, \
                veuillez contacter l'administrateur.."
                )
            )

    @api.constrains('en_cours')
    def _validate_en_cours(self):
        nbre_encours = self.search_count([('en_cours', '=', True)])
        if nbre_encours > 1:
            raise ValidationError(_(
                "Proximaas: Contrôle Règles de Gestion - Exercice en cours:\n Il ne peut y avoir plus d'un exercice \
                en cours. Vérifiez si vous n'avez pas fixé plus d'un exercice en cours. Pour plus d'informations, \
                veuillez contacter l'administrateur.."
            )
            )

    # CONTRAINTES
    _sql_constraints = [
        ('name_organisation',
         'UNIQUE (name, res_company_id)',
         '''
         Risque de doublon sur Exercice/Organisation!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         ),
        ('check_dates',
         'CHECK (date_debut < date_fin)',
         '''
         Erreurs sur les date début et date fin!
         La date début doit obligatoirement être inférieure (antérieure) à la date de fin...
         Vérifiez s'il n'y pas d'erreur de saisies sur les dates ou contactez l'administrateur.
         '''
         )
    ]

class District(models.Model):
    _name = 'proximas.district'
    _description = 'District geographique'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="District Géographique",
        help="indiquer le libellé du district selon le découpage administratif en vigeur",
        required=True,
        size=64,
    )
    chef_lieu = fields.Char(
        string="Chef lieu District",
        help="indiquer le chef-lieu de la région selon le découpage administratif en vigeur",
        size=64,
    )
    country_id = fields.Many2one (
        comodel_name="res.country",
        string="Pays de Rattachement",
        required=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # CONTRAINTES
    _sql_constraints = [
        ('name_district',
         'UNIQUE (name, country_id)',
         '''
         Risque de doublon sur le nom de district/pays!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]

class Region(models.Model):
    _name = 'proximas.region'
    _description = 'Region geographique'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Région Géographique",
        help="indiquer le libellé de la région selon le découpage géographique en vigeur",
        required=True,
        size=64,
    )
    chef_lieu = fields.Char(
        string="Chef lieu Région",
        help="indiquer le chef-lieu de la région selon le découpage géographique en vigeur",
        size=64,
    )
    district_id = fields.Many2one(
        comodel_name="proximas.district",
        string="District de Rattachement",
        required=True,
    )
    country_id = fields.Many2one (
        related='district_id.country_id',
        string="Pays de Rattachement",
        readonly=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # CONTRAINTES
    _sql_constraints = [
        ('name_region_district',
         'UNIQUE (name, district_id)',
         '''
         Risque de doublon sur Region/District!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]

class Zone(models.Model):
    _name = 'proximas.zone'
    _description = 'zone geographique'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Zone Géographique",
        help="indiquer le libellé de la Zone selon le découpage géographique en vigeur",
        required=True,
        size=64,
    )
    region_id = fields.Many2one (
        comodel_name="proximas.region",
        string="Région de Rattachement",
        required=True,
    )
    country_id = fields.Many2one (
        related='region_id.country_id',
        string="Pays de Rattachement",
        readonly=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # CONTRAINTES
    _sql_constraints = [
        ('name_zone_region',
         'UNIQUE (name, region_id)',
         '''
         Risque de doublon sur Zone/Pays!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]


class Localite(models.Model):
    _name = 'proximas.localite'
    _description = 'Localite'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Localité",
        required=True,
        size=64
    )
    zone_id = fields.Many2one(
        comodel_name="proximas.zone",
        string="Zone de rattachement",
        required=True,
    )
    region_id = fields.Many2one(
        related='zone_id.region_id',
        string="Région de Rattachement",
        readonly=True,
    )
    district_id = fields.Many2one(
        related='region_id.district_id',
        string="District de Rattachement",
        readonly=True,
    )
    country_id = fields.Many2one(
        related='district_id.country_id',
        string="Pays de Rattachement",
        readonly=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # CONTRAINTES
    _sql_constraints = [
        ('name_localite_zone',
         'UNIQUE (name, zone_id)',
         '''
         Risque de doublon sur Localité/Zone!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]


class Organe(models.Model):
    _name = 'proximas.organe'
    _description = 'Organe de gestion'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Organe",
        size=32,
        required=True,
        help="Nom ou dénomination de l'organe de gestion"
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # CONTRAINTES
    _sql_constraints = [
        ('unique_name',
         'UNIQUE (name)',
         '''
         Risque de doublon sur Localité/Zone!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]


class OrganeExercice(models.Model):
    _name = 'proximas.organe.exercice'
    _description = 'Organe Exercice'

    sequence = fields.Integer(
        string="Sequence"
    )
    # name = fields.Char()
    organe_id = fields.Many2one(
        comodel_name="proximas.organe",
        string="Organe de Gestion",
        required=True,
    )
    exercice_id = fields.Many2one(
        comodel_name="proximas.exercice",
        string="Exercice",
        required=True,
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    organe = fields.Char(
        string="Organe",
        related='organe_id.name',
        readonly=True,
    )


class Membre(models.Model):
    _name = 'proximas.membre'
    _description = 'Membres'
    _inherits = {'res.partner': 'partner_id'}
    _short_name = 'name'

    sequence = fields.Integer(
        string="Sequence"
    )
    partner_id = fields.Many2one(
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='cascade',
        #index=True,
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
    genre = fields.Selection(
        [
            ('m', 'Masculin'),
            ('f', 'Feminin'),
        ],
        default="m",
        required=True,
    )
    mobile_1 = fields.Char(
        string="Tél. mobile 1",
        size=8
    )
    mobile_2 = fields.Char(
        string="Tél. mobile 2",
        size=8
    )
    email = fields.Char(
        string="Email",
    )
    general_info = fields.Text(
        string='Information General',
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
                 u"%s %s" % (record.nom, record.prenoms)
                 ))
        return result

    @api.multi
    @api.onchange('nom', 'prenoms')
    def _get_full_name(self):
        self.ensure_one()
        if bool(self.nom) and bool(self.prenoms):
            self.name = '%s %s' % (self.nom, self.prenoms)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['est_membre_organe'] = True
        if not vals.get('name'):
            sequence = self.env['ir.sequence'].next_by_code('proximas.membre')
            vals['name'] = sequence
        return super(Membre, self).create(vals)


class MembreOrgane(models.Model):
    _name = 'proximas.membre.organe'
    _description = 'Membres Organe'

    sequence = fields.Integer(
        string="Sequence"
    )
    # name = fields.Char()
    membre_id = fields.Many2one(
        comodel_name="proximas.membre",
        string="Membre",
        required=True,
    )
    organe_id = fields.Many2one(
        comodel_name="proximas.organe.exercice",
        string="Organe",
        required=True,
    )
    fonction = fields.Char(
        string="Fonction",
        size=32,
    )
    note = fields.Text(
        string="Notes et Observations",
    )