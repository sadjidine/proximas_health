# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE - Sadjidine
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import _, fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'create_date desc'

    relationship = fields.Char(
        size=25,
    )
    relative_id = fields.Many2one(
        string='Contact',
        comodel_name='res.partner',
    )
    is_public = fields.Boolean(
        string="Statut Public?",
        help="Cocher pour définir le statut public du prestataire",
    )
    alias = fields.Char(
        string='Dénomination',
        required=False,
        help='Dénomination Juridique',
    )
    activation_date = fields.Date(
        string='Activation Date',
        default=fields.Date.today(),
        help="Date d'activation",

    )
    ref = fields.Char(
        size=64,
        string='Sigle',
        help='Sigle ou Enseigne',
    )
    # Gestion de type de partenaire
    # Prestataire / fournisseur de soins médicaux de paramédicaux
    is_prestataire = fields.Boolean(
        string="Est Prestataire?",
        help="Indiquer si Oui le concerné est un prestataire conventionné!"
    )
    is_groupe = fields.Boolean(
        string="Ets Non Conventionné?",
        help="Cocher pour indiquer le groupe Ets. non conventinné (remboursement)."
    )
    # Médecin / fournisseur de soins médicaux de paramédicaux
    is_medecin = fields.Boolean(
        string="Est Médecin?",
        help="Indiquer si Oui le concerné est un membre du corp médical!"
    )
    # Assuré / Adhérent / Ayant-droit
    is_ayant_droit = fields.Boolean(
        string="Est Assuré(e)?",
        help="Indiquer si Oui le concerné est un assuré (Ayant-droit)!"
    )
    is_adherent = fields.Boolean(
        string="Est Adhérent(e)?",
        help="Indiquer si Oui le concerné est un Adhérent)!"
    )
    is_membre_organe = fields.Boolean(
        string="Est Assuré(e)?",
        help="Indiquer si Oui le concerné est un assuré (Adhérent/Conjoint/Enfant)!"
    )
    categorie_id = fields.Many2one(
        comodel_name="proximas.categorie.prestataire",
        string="Catégorie",
        index=True,
    )
    standing_id = fields.Many2one(
        comodel_name="proximas.standing",
        string="Standing",
    )
    pool_medical_ids = fields.One2many(
        comodel_name="proximas.pool.medical",
        inverse_name="prestataire_id",
        string="Pool médical",
    )
    prestation_ids = fields.One2many(
        comodel_name="proximas.prestation",
        inverse_name="prestataire_id",
        string="Offre Prestation",
    )
    # statut_id = fields.Many2one(
    #     comodel_name="proximas.statut.reseau",
    #     string="Statut Réseau",
    # )
    date_convention = fields.Date(
        string="Date convention",
    )
    mt_caution = fields.Float(
        string="Montant Caution",
        digits=(9, 0),
        default=0,
    )
    mt_prefinancement = fields.Float(
        string="Montant Préfinancement",
        digits=(9, 0),
        default=0,
    )
    mt_seuil_prefinancement = fields.Float(
        string="Seuil Préfinancement",
        digits=(9, 0),
        default=0,
    )
    mt_rabais_pc = fields.Integer(
        string="Montant Rabais/PC",
        digits=(9, 0),
        default=0,
    )
    mt_rabais_facture = fields.Float(
        string="Mt. Rabais/Facture",
        digits=(9, 0),
        default=0,
    )
    remise_pc = fields.Integer(
        string="Taux Remise/PC (%)",
        default=0,
    )
    tx_remise_facture = fields.Integer(
        string="Taux Remise/Facture (%)",
        default=0,
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    # @api.multi
    # @api.depends('ref', 'name')
    # def _get_full_name(self):
    #     # self.ensure_one()
    #     for rec in self:
    #         rec.display_name = u"%s - %s" % (rec.ref, rec.name)
        # ref = str(self.ref).strip()
        # # alias = str(self.alias).strip()
        # if bool(self.ref) and bool(self.alias):
        #     self.display_name = ref
        # else:
        #     self.alias = self.name
        #     self.display_name = ref
        # self.display_name = ref


    # @api.multi
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         result.append(
    #             (record.id,
    #              u"%s - %s" % (record.ref, record.name)
    #              ))
    #     return result


# class ResUsers(models.Model):
#     _inherit = 'res.users'
#
#     name_user = fields.Char(
#         string="Catégorie",
#         size=32,
#         help='nom de référence de la catégorie',
#         required=True,
#     )
#     alias = fields.Char(
#         string="Libellé",
#         help="Libellé de la catégorie s\'il ya lieu.",
#         required=False,
#     )


# class ResPartner(models.Model):
#     _inherit = 'res.partner'
#
#     relationship = fields.Char(
#         size=25,
#     )
#     relative_id = fields.Many2one(
#         string='Contact',
#         comodel_name='res.partner',
#     )
#     alias = fields.Char(
#         string='Alias',
#         size=256,
#         help='Common name the partner is referred to as',
#     )
#     activation_date = fields.Date(
#         string='Activation Date',
#         help='Date the partner was activated',
#     )
#     ref = fields.Char(
#         size=256,
#         string='ID/SSN',
#         help='Patient Social Security Number or equivalent',
#     )
#     # Gestion de type de partenaire
#     # Prestataire / fournisseur de soins médicaux de paramédicaux
#     is_prestataire = fields.Boolean(
#         string="Est Prestataire?",
#         help="Indiquer si Oui le concerné est un prestataire conventionné!"
#     )
#     # Médecin / fournisseur de soins médicaux de paramédicaux
#     is_medecin = fields.Boolean(
#         string="Est Médecin?",
#         help="Indiquer si Oui le concerné est un membre du corp médical!"
#     )
#     # Assuré / Adhérent / Ayant-droit
#     is_assure = fields.Boolean(
#         string="Est Assuré(e)?",
#         help="Indiquer si Oui le concerné est un assuré (Adhérent/Conjoint/Enfant)!"
#     )
#     is_adherent = fields.Boolean(
#         string="Est Adhérent(e)?",
#         help="Indiquer si Oui le concerné est un Adhérent)!"
#     )
#     is_membre_organe = fields.Boolean(
#         string="Est Assuré(e)?",
#         help="Indiquer si Oui le concerné est un assuré (Adhérent/Conjoint/Enfant)!"
#     )
