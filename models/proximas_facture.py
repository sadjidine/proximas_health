# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Sadjidine Salifou OMBOTIMBE
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import _, api, fields, models
from datetime import datetime
from openerp.exceptions import ValidationError, UserError
from openerp.tools import amount_to_text_fr
from random import randint

class Facture(models.Model):
    _name = 'proximas.facture'
    _description = 'Facture Prestataire'
    _inherit = ['mail.thread']
    _order = 'date_emission desc'

    name = fields.Char(
        string="V/Réf. Facture",
        required=True,
    )
    num_facture = fields.Char(
        string="Num. Facture",
        compute="_get_num_facture",
        require=False,
        store=True,
        help="Numéro automatique unique de la facture fourni par le système.!",
    )
    code_facture = fields.Char (
        string="Code Facture",
        compute="_get_code_facture",
        require=False,
        help="Code unique de la facture fourni par le système.!",
    )
    ref_interne = fields.Char(
        string="N/Réf. Facture",
        required=False,
        help='Référence interne de la facture'
    )
    state = fields.Selection(
        string="Etat",
        selection=[
            ('attente', 'En attente'),
            ('traite', 'Traitement'),
            ('cloture', 'Clôture'),
        ],
        default="attente",
    )
    date_emission = fields.Date(
        string="Date Emission",
        default=datetime.now(),
        required=True,
    )
    date_traitement = fields.Date(
        string="Date Traitement",
        default=datetime.now(),
        required=True,
    )
    date_reception = fields.Date(
        string="Date Reception (Dépôt)",
        required=False,
    )
    prestataire_id = fields.Many2one(
        comodel_name="res.partner",
        string="Prestataire de soins",
        domain=[
            ('is_prestataire', '=', True)
        ],
        # default=lambda self: self._get_current_user(),
    )
    prestataire = fields.Char(
        string="Prestataire",
        related='prestataire_id.name',
        store=True,
        required=False,
    )
    city = fields.Char(
        string="Ville",
        related='prestataire_id.city',
        required=False,
    )
    phone = fields.Char(
        string="Tél.",
        related='prestataire_id.phone',
        required=False,
    )
    mobile = fields.Char(
        string="Tél. mobile",
        related='prestataire_id.mobile',
        required=False,
    )
    fax = fields.Char(
        string="Fax",
        related='prestataire_id.fax',
        required=False,
    )
    details_pec_ids = fields.One2many(
        comodel_name="proximas.details.pec",
        inverse_name="facture_id",
        string="Prestation(s) fournie(s)",
    )
    mt_total_facture = fields.Float(
        string="Montant Total Facture",
        digits=(9, 0),
        compute='_compute_facture_details',
        default=0,
    )
    mt_total_exclusions = fields.Float(
        string="Montant Total Exclusions",
        digits=(9, 0),
        compute='_compute_facture_details',
        default=0,
    )
    nbre_prestations = fields.Integer(
        string="Nbre. Prestations",
        compute='_compute_facture_details',
        default=0,
        required=False,
    )
    doc_joint = fields.Binary(
        string="Facture pièce jointe",
        # attachment=True,
    )
    doc_filename = fields.Char(
        "Nom du fichier joint",
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # Champs calculés automatiquement pour les détails facture
    nbre_actes_facture = fields.Integer(
        string="Nbre. ligne(s)",
        compute='_compute_facture_details',
        default=0,
        required=False,
    )
    totaux_actes_facture = fields.Float(
        string="Totaux Facture",
        digits=(9, 0),
        compute='_compute_facture_details',
        default=0,
    )
    totaux_actes_pc_facture = fields.Float (
        string="Totaux PC",
        digits=(9, 0),
        compute='_compute_facture_details',
        default=0,
    )
    totaux_actes_npc_facture = fields.Float (
        string="Totaux NPC",
        digits=(9, 0),
        compute='_compute_facture_details',
        default=0,
    )
    totaux_part_sam_facture = fields.Float (
        string="Totaux SAM",
        digits=(9, 0),
        compute='_compute_facture_details',
        default=0,
    )
    totaux_ticket_moderateur_facture = fields.Float (
        string="Totaux Assuré",
        digits=(9, 0),
        compute='_compute_facture_details',
        default=0,
    )
    totaux_exclusions_facture = fields.Float (
        string="Totaux Exclusions",
        digits=(9, 0),
        compute='_compute_facture_details',
        default=0,
    )
    net_prestataire_facture = fields.Float (
        string="Totaux Prestataire",
        digits=(9, 0),
        compute='_compute_facture_details',
        default=0,
    )

    @api.multi
    def action_en_attente(self):
        self.state = 'attente'
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
    def action_traiter(self):
        self.state = 'traite'
        view_id = self.env.ref('proximas_medical.proximas_facture_view_tree', False).id
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
    def action_cloturer(self):
        self.state = 'cloture'
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

    # @api.one
    @api.depends('details_pec_ids')
    def _compute_facture_details(self):
        for rec in self:
            if bool(rec.details_pec_ids):
                # Calculs détails Actes médicaux et paramédicaux - Facture
                details_actes_facture = rec.details_pec_ids
                rec.nbre_actes_facture = len(details_actes_facture)
                rec.totaux_actes_facture = sum (item.cout_total for item in details_actes_facture) or 0
                rec.totaux_actes_pc_facture = sum (item.total_pc for item in details_actes_facture) or 0
                rec.totaux_actes_npc_facture = sum (item.total_npc for item in details_actes_facture) or 0
                rec.totaux_part_sam_facture = sum (item.net_tiers_payeur for item in details_actes_facture) or 0
                rec.totaux_ticket_moderateur_facture = sum (
                    item.ticket_moderateur for item in details_actes_facture) or 0
                rec.totaux_exclusions_facture = sum(item.mt_exclusion for item in details_actes_facture) or 0
                rec.net_prestataire_facture = int(rec.totaux_part_sam_facture - rec.totaux_exclusions_facture)
                rec.nbre_prestations = len(rec.details_pec_ids)

    @api.depends('mt_total_facture', 'num_facture')
    def montant_en_text(self):
        convert_lettre = amount_to_text_fr(self.net_prestataire_facture, 'Francs')
        # montant_lettre = str(convert_lettre).encode('utf-8')
        list_text = convert_lettre.split()
        montant_text = " ".join(list_text[0:-2])
        # montant_en_texte_1 = convert_lettre.replace(u"zéro", "")
        # montant_en_texte = convert_lettre.replace(u"cent", "")
        # convert_amount_in_words = amount_to_text_fr.amount_to_text(montant, lang='fr', currency='')
        # convert_amount_in_words = convert_amount_in_words.replace(' Zéro Cent', ' Only ')
        return montant_text.upper()

    @api.one
    @api.depends('date_emission')
    def _get_num_facture(self):
        """Généré un code unique pour la facture"""
        self.ensure_one()
        date_emission = fields.Datetime.from_string(self.date_emission)
        annee_format = datetime.strftime (date_emission, '%y')
        code_regenere = randint (1, 1e6)
        facture_id = u'F%s%06d' % (annee_format, code_regenere,)
        check_num_facture = self.search_count([('num_facture', '=', facture_id)])
        while check_num_facture >= 1:
            code_regenere = randint (1, 1e6)
            facture_id = u'F%s%06d' % (annee_format, code_regenere,)
            self.num_facture = facture_id
        self.num_facture = facture_id

    @api.one
    def _get_code_facture(self):
        self.ensure_one()
        self.code_facture = self.num_facture
        for pec in self.details_pec_ids:
            pec.facture_id = self.id

    # @api.one
    # @api.depends('details_pec_ids')
    # def _calcul_total_facture(self):
    #     # self.ensure_one()
    #     self.mt_total_facture = int(self.totaux_part_sam_facture - self.totaux_exclusions_facture)
    #     self.net_prestataire_facture = sum(item.net_prestataire for item in self.details_pec_ids)
    #     self.mt_total_exclusions = sum(item.mt_exclusion for item in self.details_pec_ids)
    #     self.nbre_prestations = len(self.details_pec_ids)
    #     for pec in self.details_pec_ids:
    #         pec.facture_id = self.id

    # @api.one
    # def _calcul_total_exclusions(self):
    #     self.mt_total_exclusions = sum(item.mt_exclusion for item in self.details_pec_ids)
    #     self.mt_total_facture = sum(item.net_prestataire for item in self.details_pec_ids)

    @api.constrains('num_facture')
    def validate_num_facture(self):
        check_num_facture = self.search_count([('num_facture', '=', self.num_facture)])
        if check_num_facture > 1:
            raise ValidationError(_(
                u"Proximaas : Contrôle Contrôle Règles de Gestion ; \n \
                Risque de doublon facture : %s. Le numéro généré par le système existe déjà pour une autre \
                facture. Cependant, Ce numéro doit être unique par facture.\n \
                Veuillez contactez les administrateurs pour plus détails..."
                ) % self.num_facture
            )


    _sql_constraints = [
        ('name_facture_prestataire_uniq',
         'UNIQUE (name, prestataire_id)',
         '''
         Risque de doublons Facture!
         Il semble que cette facture existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.
         ''')
    ]



class FactureWizard(models.TransientModel):
    _name = 'proximas.facture.wizard'
    _description = 'Facture wizard'


    name = fields.Char(
        string="V/Réf. Facture",
        size=64,
        required=True,
    )
    date_emission = fields.Date(
        string="Date Emission",
        required=True,
    )
    # date_reception = fields.Date(
    #     string="Date Reception",
    #     required=True,
    # )
    prestataire_id = fields.Many2one(
        comodel_name="res.partner",
        string="Prestataire de soins",
        domain=[
            ('is_prestataire', '=', True)
        ],
    )
    prestataire = fields.Char(
        string="Prestataire",
        related='prestataire_id.name',
        required=False,
    )
    is_prestataire = fields.Boolean(
        string="Est un prestataire?",
        related='prestataire_id.is_prestataire',
    )
    # prestataire_id = fields.Many2one(
    #     comodel_name="res.partner",
    #     string="Prestataire de soins",
    #     compute='_get_current_user',
    # )
    user_id = fields.Many2one (
        comodel_name="res.users",
        string="Créee Par",
        required=False,
    )
    current_user = fields.Many2one(
        comodel_name="res.users",
        string="Utilisateur en cours",
        compute='_get_current_user',
        required=False,
    )
    current_prestataire = fields.Char(
        string="Prestataire(User)",
        compute='_get_current_user',
        required=False,
    )

    @api.multi
    @api.depends('current_user')
    def _get_current_user(self):
        # for rec in self:
        self.ensure_one()
        user_id = self.env.context.get('uid')
        group_id = self.env.context.get('gid')
        user = self.env['res.users'].search([('id', '=', user_id)])
        prestataire_id = self.env['res.partner'].search([('id', '=', user.partner_id.id)])
        self.current_user = user_id
        self.current_prestataire = prestataire_id.name
        self.prestataire_id = prestataire_id.id

    @api.multi
    def record_facture_details(self):
        # Création Facture Prestataire
        action = {
            'name': 'Création Nouvelle Facture Prestataire',
            'view_type': 'form',
            'view_mode': 'form',
            # 'target': 'current',
            # 'views': [(view_id, 'form')],
            'res_model': 'proximas.facture',
            # 'view_id': view_id,
            # 'res_id': facture_id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_name': self.name,
                'default_date_emission': self.date_emission,
                # 'default_date_reception': wizard.date_reception,
                'default_prestataire_id': self.prestataire_id.id,
            },
        }
        return action

    # @api.multi
    # def record_facture_details(self):
    #     for wizard in self:
    #         # prestataire = wizard.prestataire_id
    #         # pec_facture = wizard.details_pec_ids
    #         facture = self.env['proximas.facture']
    #         # details_pec = self.env['proximas.details.pec']
    #         # for pec in pec_facture:
    #         #     pec.facture_id = wizard.name.strip()
    #             #details_pec.write({'facture_id': wizard.name.strip()})
    #         # contrat = self.env['proximas.contrat']
    #         facture.create({
    #             'name': wizard.name,
    #             'date_emission': wizard.date_emission,
    #             # 'date_reception': wizard.date_reception,
    #             'prestataire_id': wizard.prestataire_id.id,
    #             # 'details_pec_ids': wizard.details_pec_ids,
    #             # 'mt_total_facture': wizard.mt_total_facture
    #         }
    #         )
    #         current_facture = self.env['proximas.facture'].search(
    #             [
    #                 ('name', 'ilike', wizard.name),
    #                 ('date_emission', '=', wizard.date_emission),
    #             ]
    #         )
    #         # facture_id = current_facture.id
    #         # view_id = self.env.ref('proximas_medical.proximas_facture_view_form', False).id
    #         action = {
    #             'name': 'Création Nouvelle Facture Prestataire',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             # 'target': 'current',
    #             # 'views': [(view_id, 'form')],
    #             'res_model': 'proximas.facture',
    #             # 'view_id': view_id,
    #             # 'res_id': facture_id,
    #             'type': 'ir.actions.act_window',
    #             'context': {
    #                 'default_name': wizard.name,
    #                 'default_date_emission': wizard.date_emission,
    #                 # 'default_date_reception': wizard.date_reception,
    #                 'default_prestataire_id': wizard.prestataire_id.id,
    #             },
    #         }
    #         return action

