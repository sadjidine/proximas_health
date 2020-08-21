# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE - Sadjidine
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp.tools.translate import _
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class Police(models.Model):
    _name = 'proximas.police'
    _description = 'police assurance'
    _short_name = 'libelle'

    sequence = fields.Integer(
        string="Sequence"
    )
    color = fields.Integer (
        string="Color index",
        required=False,
    )
    name = fields.Char(
        string="Code Police",
        size=32,
    )
    libelle = fields.Char(
        string="Libellé",
    )
    structure_id = fields.Many2one(
        comodel_name="res.company",
        string="Organisation",
        required=False,
    )
    validite_contrat = fields.Integer(
        string="Délai Validité contrat (jours)",
        required=True,
        default=0,
        help='Délai de validité du contrat (en nombre de jours).',
    )
    date_echeance = fields.Date(
        string="Date Echéance",
        help="Date d'échéance prévue pour la police de couverture.",
    )
    mt_droit_adhesion = fields.Float(
        string="Droit Adhésion",
        digits=(9, 0),
        required=True,
    )
    # PARAMETRES DE CONTROLES POLICE ('CODE MEDICAL, RUBRIQUEs, ANTECEDENTS)
    controle_medical_ids = fields.One2many(
        comodel_name="proximas.code.medical.police",
        inverse_name="police_id",
        string="Contrôle code médical",
        required=False,
    )
    controle_rubrique_ids = fields.One2many(
        comodel_name="proximas.controle.rubrique",
        inverse_name="police_id",
        string="Contrôle Rubrique médicale",
        required=False,
    )
    controle_antecedent_ids = fields.One2many(
        comodel_name="proximas.controle.antecedent",
        inverse_name="police_id",
        string="Contrôle Antécedent médical",
        required=False,
    )
    prime_police_ids = fields.One2many(
        comodel_name="proximas.prime",
        inverse_name="police_id",
        string="Primes Police",
        required=False,
    )
    droit_adhesion_individu = fields.Boolean(
        string="Droit Adhésion/Individu?",
        help="Cocher pour indiquer que le droit d'adhésion est applicable à chaque individu (Adhérent et ayants droit",
    )
    standing_id = fields.Many2one(
        comodel_name="proximas.standing",
        string="Standing Réseau",
    )
    mt_prime_police = fields.Float(
        string="Montant Prime Couverture",
        digits=(9, 0),
        required=True,
        help="Montant de la prime (cotisation) annuelle pour la police de couverture concernée.",
    )
    retard_cotisation = fields.Float(
        string="Mt. Retard Toléré",
        digits=(9, 0),
        required=True,
        default=0
    )
    controle_retard_cotisation = fields.Boolean(
        string="Contrôle bloquant sur retard cotisation?",
        help="Cocher pour indiquer le facteur bloquant du contrôle!",
        default=False,
    )
    controle_genre = fields.Boolean(
        string="Contrôle Genre?",
        help="Cochez pour activer le contôle du genre.",
        default=False,
    )
    delai_carence = fields.Integer(
        string="Délai Carence",
        required=True,
        default=0,
    )
    plafond_individu = fields.Float(
        string="Plafond individu",
        digits=(9, 0),
        required=True,
        default=0,
    )
    plafond_famille = fields.Float(
        string="Plafond famille",
        digits=(9, 0),
        required=True,
        default=0,
    )
    tx_couv_public_couvert = fields.Integer(
        string="Taux Remb. Public/Couvert (%)",
        required=True,
        default=0,
        help="Taux de Remboursement dans un établissement public dans la zone de couverture du réseau "
    )
    tx_couv_public = fields.Integer(
        string="Taux Couvert. Public(%)",
        required=True,
        default=0,
        help="Taux de couverture dans un établissement public dans le réseau de soins ou dans une zone non couverte."
    )
    tx_couv_prive_couvert = fields.Integer(
        string="Taux Remb. Privé/Couvert (%)",
        required=True,
        default=0,
        help="Taux de Remboursement dans un établissement privé dans la zone de couverture du réseau "
    )
    tx_couv_prive = fields.Integer(
        string="Taux Couvert. Privé(%)",
        required=True,
        default=0,
        hrlp="Taux de couverture dans un établissement privé dans le réseau de soins ou dans une zone non couverte."
    )
    # Ajout de fonctionnalités sur options Remboursement de frais médicaux
    mode_controle_plafond = fields.Selection(
        string="Mode Contrôle Plafond",
        selection=[
            ('exercice', 'Exercice'),
            ('contrat', 'Contrat'),
            ('assure', 'Assuré'),
        ],
        default='exercice',
        help="Indiquer le mode d'application pour le contrôle des plafonds paramétrés.",
    )
    validite_demande_remb = fields.Integer (
        string="Délai Validité Remb. (jours)",
        required=True,
        default=0,
        help='Délai de validité pour le remboursement de l\'acte médical(en nombre de jours).',
    )
    nbre_maxi_demande = fields.Integer(
        string="Nbre. maxi de demandes de remboursement",
        default=0,
    )
    mt_plafond_remb_demande = fields.Float (
        string="Montant Plafond/Demande (remboursement)",
        digits=(6, 0),
        default=0,
    )
    mt_plafond_remb_individu = fields.Float(
        string="Montant Plafond/Individu (remboursement)",
        digits=(6,0),
        default=0,
    )
    mt_plafond_remb_famille = fields.Float(
        string="Montant Plafond/Famille (remboursement)",
        digits=(6, 0),
        default=0,
    )
    # Contrôles sue les limites d'âge (adhérent  et ayant-droits)
    age_limite_adherent = fields.Integer(
        string="Age limite Adhérent",
        required=True,
        default=0
    )
    age_limite_conjoint = fields.Integer(
        string="Age limite Conjoint(e)",
        required=True,
        default=0,
    )
    age_limite_enfant = fields.Integer(
        string="Age limite Enfant",
        required=True,
        default=0,
    )
    age_limite_ascendant = fields.Integer(
        string="Age limite Ascendant",
        required=True,
        default=0,
    )
    age_limite_parent = fields.Integer(
        string="Age limite Parent",
        required=True,
        default=0,
    )
    nbre_limite_ascendant = fields.Integer(
        string="Nbre. limite Ascendant(s)",
        required=True,
        default=0,
    )
    supplement_ascendant = fields.Integer(
        string="Nbre. Ascendant(s) supp.",
        required=True,
        default=0,
        help='Nombre d\'ascendanrt(s) supplémentaire(s)',
    )
    nbre_maxi_ascendant = fields.Integer(
        string="Nbre. Maxi Ascendants",
        compute='nbre_maxi_ayant_droit',
        default=0,
        store=True,
        help='Nombre maxi d\'ascendant(s) autorisé(s)',
    )
    mt_supplement_ascendant = fields.Float (
        string="Montant Ascendant Supp.",
        digits=(9, 0),
        required=True,
        default=0,
        help='Montant à payer par ascendant supplémentaire',
    )
    nbre_limite_parent = fields.Integer(
        string="Nbre. limite Parent(s)",
        required=True,
        default=0,
    )
    supplement_parent = fields.Integer(
        string="Nbre. Parent(s) supp.",
        required=True,
        default=0,
        help='Nombre de parent(s) supplémentaire(s)',
    )
    nbre_maxi_parent = fields.Integer(
        string="Nbre. Maxi Parents",
        compute='nbre_maxi_ayant_droit',
        default=0,
        store=True,
        help='Nombre maxi de parennt(s) autorisé(s)',
    )
    mt_supplement_parent = fields.Float(
        string="Montant Parent Supp.",
        digits=(9, 0),
        required=True,
        default=0,
        help='Montant à payer par parent supplémentaire',
    )
    nbre_limite_conjoint = fields.Integer(
        string="Nbre. limite Conjoint(es)",
        required=True,
        default=0,
    )
    supplement_conjoint = fields.Integer(
        string="Nbre.Conjoint(es) supp.",
        required=True,
        default=0,
        help='Nombre de conjoint(es) supplémentaire(s)',
    )
    nbre_maxi_conjoint = fields.Integer(
        string="Nbre. Maxi Conjoints",
        compute='nbre_maxi_ayant_droit',
        default=0,
        store=True,
        help='Nombre maxi de conjoint(s) autorisé(s)',
    )
    mt_supplement_conjoint = fields.Float(
        string="Montant Supplémentaire/Conjoint(e)",
        digits=(9, 0),
        required=True,
        default=0,
    )
    age_majorite_enfant = fields.Integer(
        string="Age de majorité Enfant",
        required=True,
        default=0,
    )
    nbre_limite_enfant = fields.Integer(
        string="Nbre. limite Enfants",
        required=True,
        default=0,
    )
    supplement_enfant = fields.Integer (
        string="Nbre. Enfants supp.",
        required=True,
        default=0,
        help='Nombre d\'enfant(s) supplémentaire(s)',
    )
    nbre_maxi_enfant = fields.Integer(
        string="Nbre. Maxi. Enfants",
        compute='nbre_maxi_ayant_droit',
        default=0,
        store=True,
        help='Nombre maxi d\'enfant(s) autorisé(s)',
    )
    enfant_invalide = fields.Boolean(
        string="Enfant invalide?",
        help="Cochez si l'on doit tenit compte des cas d'invalidité chez l'enfant",
        default=False,
    )
    mt_supplement_enfant = fields.Float(
        string="Montant Supplémentaire/Enfant",
        digits=(9, 0),
        required=True,
        default=0,
    )
    nbre_prescription_maxi = fields.Integer(
        string="Nbre. maxi Prescriptions",
        required=True,
        default=0,
    )
    mt_plafond_prescription = fields.Float(
        string="Mt. Plafond/Prescription",
        digits=(9, 0),
        required=True,
        default=0,
    )
    mt_supplement_maladie = fields.Float(
        string="Mt. Supplément. maladie chronique",
        digits=(9, 0),
        required=True,
        default=0,
    )
    mt_forfait_accouchement = fields.Float(
        tring="Mt. Forfait Accouchement",
        digits=(9, 0),
        required=True,
        default=0,
     )
    seuil_alerte = fields.Integer(
        string="Seuil d'alerte(%)sur Plafonds",
        required=True,
        help='Seuil d\'alerte applicable sur le plafond individu et famille',
        default=0,
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
    note = fields.Text(
        string="Notes et Observations",
    )
    # CAPITAL DECES ET FRAIS FUNERAIRES
    mt_capital_deces = fields.Float(
        string="Montant Capital Décès",
        digits=(9, 0),
        required=True,
        default=0,
    )
    mt_frais_funeraire = fields.Float(
        string="Montant Frais Funéraires",
        digits=(9, 0),
        required=True,
        default=0,
    )

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                 u"%s" % record.name
                 ))
        return result

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['active'] = True
        if not vals.get('name'):
            sequence = self.env['ir.sequence'].next_by_code('proximas.police')
            vals['name'] = sequence
        return super(Police, self).create(vals)
    
    
    @api.multi
    @api.depends('nbre_limite_conjoint', 'nbre_limite_enfant', 'nbre_limite_ascendant', 'nbre_limite_parent',
                 'supplement_conjoint', 'supplement_enfant', 'supplement_ascendant', 'supplement_parent')
    def nbre_maxi_ayant_droit(self):
        for rec in self:
            rec.nbre_maxi_conjoint = int(rec.nbre_limite_conjoint) + int(rec.supplement_conjoint) or 0
            rec.nbre_maxi_enfant = int(rec.nbre_limite_enfant) + int(rec.supplement_enfant) or 0
            rec.nbre_maxi_ascendant = int(rec.nbre_limite_ascendant) + int(rec.supplement_ascendant) or 0
            rec.nbre_maxi_parent = int(rec.nbre_limite_parent) + int(rec.supplement_parent) or 0

    # CONTRAINTES
    @api.constrains('seuil_alerte', 'tx_couv_public_couvert', 'tx_couv_public', 'tx_couv_prive_couvert' \
                    'tx_couv_prive')
    def _check_taux(self):
        if 0 < self.seuil_alerte > 100:
            raise ValidationError(_ (
                "Proximas : Violation de Règles de Gestion\n " +
                "Contrôle Seuil d'alerte Police:\n Le seuil d'alerte est un taux compris entre 0 et 100 maximmum."
                )
            )
        if 0 < self.tx_couv_public_couvert > 100:
            raise ValidationError(_(

                "Proximas : Violation de Règles de Gestion\n " +
                "Contrôle Taux de Remboursement Public en zone Couverte:\n \
                Le taux doit obligatoirement être compris entre 0 et 100 maximmum."
                )
            )
        if 0 < self.tx_couv_public > 100:
            raise ValidationError(_(

                "Proximas : Violation de Règles de Gestion\n " +
                "Contrôle Taux de Remboursement Public en zone non Couverte:\n \
                 Le taux doit obligatoirement être compris entre 0 et 100 maximmum."
                )
            )
        if 0 < self.tx_couv_prive_couvert > 100:
            raise ValidationError(_(

                "Proximas : Violation de Règles de Gestion\n " +
                "Contrôle Taux de Remboursement Privé en zone Couverte:\n \
                 Le taux doit obligatoirement être compris entre 0 et 100 maximmum."
                )
            )
        if 0 < self.tx_couv_prive > 100:
            raise ValidationError(_(

                "Proximas : Violation de Règles de Gestion\n " +
                "Contrôle Taux de Remboursement Privé en zone non Couverte:\n \
                 Le taux doit obligatoirement être compris entre 0 et 100 maximmum."
                )
            )

    _sql_constraints = [
        ('name_structure_uniq',
         'UNIQUE (name, structure_id)',
         '''
         Risque de doublons Police Couverture!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

         '''),
    ]


class Prime(models.Model):
    _name = 'proximas.prime'
    _description = 'Primes'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Libellé",
    )
    police_id = fields.Many2one(
        comodel_name="proximas.police",
        string="Police",
        required=True,
    )
    applicable = fields.Selection(
        string="Applicable par",
        selection=[
            ('adherent', 'Adhérent'),
            ('ayant-droit', 'Ayant-droit'),
            ('tous', 'Tous')
        ],
        default='adherent',
        help="Sélection du champ d'application de la prime de couverture."
    )
    periodicite = fields.Selection(
        string="Périodicité",
        selection=[
            ('jour', 'Journalière'),
            ('semaine', 'Hebdomadaire'),
            # ('quinze', 'Quinzaine'),
            ('mois', 'Mensuelle'),
            ('trimestre', 'Trimestrielle'),
            # ('semestre', 'Sémestrielle'),
            ('annee', 'Annuelle'),
            ('unique', 'Unique'),
        ],
        default='mois',
        help="Sélectionner la périodicité de versement de la prime."
    )
    date_debut = fields.Date(
        string="Date Début",
    )
    date_fin = fields.Date(
        string="Date Fin",
    )
    # validite_prime = fields.Integer(
    #     string="Délai Validité (jours)",
    #     default=0,
    #     help='Délai de validité de la prime concernée (en nombre de jours).',
    # )
    mt_prime = fields.Float(
        string="Mt. Prime",
        digits=(9, 0),
        required=True,
        help='Montant de la prime à verser.',
    )
    # renouvelable = fields.Boolean(
    #     string="Renouvelable?",
    #     default=False,
    # )
    # date_fin_prime = fields.Date(
    #     string="Date fin Prime",
    #
    # )
    note = fields.Text(
        string="Notes et Observations",
    )

    @api.onchange('date_debut', 'date_fin')
    def _check_prime_dates(self):
        date_debut = fields.Datetime.from_string(self.date_debut)
        date_fin = fields.Datetime.from_string(self.date_fin)
        if bool(date_debut) and bool(date_fin):
            if date_debut > date_fin:
                # date_debut_format = datetime.strptime(self.date_debut, '%Y-%m-%d')
                # date_fin_format = datetime.strptime(self.date_fin, '%Y-%m-%d')
                date_debut_format = date_debut.strftime('%d-%m-%Y')
                date_fin_format = date_fin.strftime('%d-%m-%Y')
                return {'value': {},
                        'warning': {
                            'title': "Proximaas : Contrôle de Règles de Gestion.",
                            'message': "La date début: %s doit obligatoirement être antérieure à la date de fin: %s. \
                             Veuillez rectifier vos données. Pour plus d'informations, contactez l'administrateur..."
                            % (date_debut_format, date_fin_format)
                            }
                        }

    @api.constrains('date_debut', 'date_fin')
    def _validate_prime_dates(self):
        date_debut = fields.Datetime.from_string(self.date_debut)
        date_fin = fields.Datetime.from_string (self.date_fin)
        if bool(date_debut) and bool(date_fin):
            if date_debut > date_fin:
                date_debut_format = datetime.strftime(date_debut, '%d-%m-%Y')
                date_fin_format = datetime.strftime(date_fin, '%d-%m-%Y')
                raise ValidationError(_(
                    "Proximaas : Contrôle de Règles de Gestion.\n \
                    La date début: %s doit obligatoirement être antérieure à la date de fin: %s. Veuillez rectifier \
                    vos données. Pour plus d'informations, contactez l'administrateur..."
                    ) % (date_debut_format, date_fin_format)
                )


class PrimeContrat(models.Model):
    _name = 'proximas.prime.contrat'
    _description = 'Primes sur Contrat'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Libellé",
    )
    contrat_id = fields.Many2one(
        comodel_name="proximas.contrat",
        string="Contrat",
        required=True,
    )
    applicable = fields.Selection(
        string="Applicable par",
        selection=[
            ('adherent', 'Adhérent'),
            ('ayant-droit', 'Ayant-droit'),
            ('tous', 'Tous')
        ],
        default='adherent',
        help="Sélection du champ d'application de la prime sur contrat."
    )
    periodicite = fields.Selection(
        string="Périodicité",
        selection=[
            ('jour', 'Journalière'),
            ('semaine', 'Hebdomadaire'),
            # ('quinze', 'Quinzaine'),
            ('mois', 'Mensuelle'),
            ('trimestre', 'Trimestrielle'),
            # ('semestre', 'Sémestrielle'),
            ('annee', 'Annuelle'),
            ('unique', 'Unique'),
        ],
        default='mois',
        help="Sélectionner la périodicité de versement de la prime."
    )
    date_debut = fields.Date(
        string="Date Début",
    )
    date_fin = fields.Date(
        string="Date Fin",
    )
    mt_prime = fields.Float(
        string="Mt. Prime",
        digits=(9, 0),
        required=True,
        help='Montant de la prime sur contrat à verser.',
    )
    note = fields.Text(
        string="Notes et Observations",
    )

    @api.onchange('date_debut', 'date_fin')
    def _check_prime_dates(self):
        date_debut = fields.Datetime.from_string (self.date_debut)
        date_fin = fields.Datetime.from_string (self.date_fin)
        if bool (date_debut) and bool (date_fin):
            if date_debut > date_fin:
                # date_debut_format = datetime.strptime(self.date_debut, '%Y-%m-%d')
                # date_fin_format = datetime.strptime(self.date_fin, '%Y-%m-%d')
                date_debut_format = date_debut.strftime('%d-%m-%Y')
                date_fin_format = date_fin.strftime('%d-%m-%Y')
                return {'value': {},
                        'warning': {
                            'title': "Proximaas : Contrôle de Règles de Gestion.",
                            'message': "La date début: %s doit obligatoirement être antérieure à la date de fin: %s. \
                             Veuillez rectifier vos données. Pour plus d'informations, contactez l'administrateur..."
                            % (date_debut_format, date_fin_format)
                        }
                        }

    @api.constrains ('date_debut', 'date_fin')
    def _validate_prime_dates(self):
        date_debut = fields.Datetime.from_string (self.date_debut)
        date_fin = fields.Datetime.from_string (self.date_fin)
        if bool (date_debut) and bool (date_fin):
            if date_debut > date_fin:
                date_debut_format = datetime.strftime (date_debut, '%d-%m-%Y')
                date_fin_format = datetime.strftime (date_fin, '%d-%m-%Y')
                raise ValidationError (_ (
                    "Proximaas : Contrôle de Règles de Gestion.\n \
                    La date début: %s doit obligatoirement être antérieure à la date de fin: %s. Veuillez rectifier \
                    vos données. Pour plus d'informations, contactez l'administrateur..."
                    ) % (date_debut_format, date_fin_format)
                )


class Contrat(models.Model):
    _name = 'proximas.contrat'
    _description = 'Contrats'

    sequence = fields.Integer(
        string="Sequence"
    )
    color = fields.Integer (
        string="Color index",
        required=False,
    )
    name = fields.Char(
        string="Contrat",
    )
    num_contrat = fields.Char(
        string="N° Contrat",
        compute='_get_contrat_info',
        store=True,
    )
    adherent_id = fields.Many2one(
        comodel_name="proximas.adherent",
        string="Adhérent",
        required=True,
    )
    police_id = fields.Many2one(
        comodel_name="proximas.police",
        string="Police Couverture",
        required=True,
    )
    ayant_droit_ids = fields.One2many(
        comodel_name="proximas.ayant.droit",
        inverse_name="contrat_id",
        string="Ayant-droit",
    )
    prime_contrat_ids = fields.One2many(
        comodel_name="proximas.prime.contrat",
        inverse_name="contrat_id",
        string="Primes Contrat",
    )
    cotisation_ids = fields.One2many(
        comodel_name="proximas.cotisation",
        inverse_name="contrat_id",
        string="Règlement Cotisation",
    )
    
    # CONTRAT PERSONNALISE POUR L'ADHERENT PRINCIPAL

    mt_annuel = fields.Float(
        string="Prime Annuelle",
        digits=(9, 0),
        help="Montant total annuel à verser pour le contrat",
        default=0,
        compute='_compute_prime_contrat',
        store=True,
        # Montant vannuel global calculé
    )
    # periodicite = fields.Selection(
    #     string="Périodicité",
    #     selection=[
    #         ('mois', 'Mensuelle'),
    #         ('trimestre', 'Trimestrielle'),
    #         ('semestre', 'Sémestrielle'),
    #         ('annuel', 'Annuelle'),
    #     ],
    #     default='mois',
    #     help="Sélectionner la périodicité pour le versement de la prime!"
    # )
    retard_cotisation = fields.Float(
        string="Mt. Retard Toléré",
        digits=(9, 0),
        # compute='_get_retard_cotisation',
        defzault=1,
        # default=lambda self: self._get_retard_cotisation(),
    )
    # date_activation = fields.Date(
    #     string="Date Prise Effet",
    #     required=True,
    #     default=fields.Date.today(),
    #     help="Date de prise effet la police de couverture",
    # )
    date_resiliation = fields.Date(
        string="Date Résiliation",
        help="Date de résiliation du contrat de couverture"
    )
    date_fin_prevue = fields.Date(
        string="Date Fin Contrat",
        compute='_compute_debut_fin_contrat',
        help="Date de fin prévue du contrat de couverture en rapport avec le délai de validité de la police."
    )
    date_debut_contrat = fields.Date(
        string="Date Début Contrat",
        compute='_compute_debut_fin_contrat',
        help="Date de début du contrat de couverture par rapport avec le délai de validité de la police."
    )
    delai_carence = fields.Integer(
        string="Délai de carence",
        help="La période (nbre. de jours) de carence à observer avant de bénéficier de la couverture!",
        # default=lambda self: self._get_delai_carence(),
    )
    validite_contrat = fields.Integer(
        string="Délai Validité contrat (jours)",
        help='Délai de validité du contrat (en nombre de jours).',
        default=1,
    )
    nbre_renouvellement_contrat = fields.Integer(
        string="Nbre. réconduite(s) contrat",
        compute='_compute_debut_fin_contrat',
        help='Nombre de renouvellement du contrat.',
    )
    actif = fields.Boolean(
        string="Activé?",
        default=False,
        help="Indique l'état du contrat (actif ou non actif).",
    )
    # Date d'ACTIVATUION ASSURE
    date_activation = fields.Date(
        string="Date Prise Effet",
        default=lambda self: self.adherent_id.date_activation,
        help='Date à laquelle le contrat est activé (date de prise d\'effet).'
    )
    note = fields.Text(
        string="Notes et Observations",
        required=False
    )
    # POLICE DETAILS & ADHERENT
    structure_id = fields.Many2one(
        comodel_name="res.company",
        string="Organisation",
        related='police_id.structure_id',
    )
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
    validite_contrat_police = fields.Integer(
        string="Délai Validité contrat (jours)",
        related='police_id.validite_contrat',
        readonly=True,
    )
    date_echeance_police = fields.Date (
        string="Date Echéance Police",
        related='police_id.date_echeance',
        readonly=True,
        help="Date d'échéance prévue pour la police de couverture.",
    )
    controle_retard_cotisation = fields.Boolean(
        string="Contrôle Retard Cotisation?",
        related='police_id.controle_retard_cotisation',
        readonly=True,
    )
    controle_genre = fields.Boolean(
        string="Contrôle Genre?",
        related='police_id.controle_genre',
        readonly=True,
    )
    delai_carence_police = fields.Integer(
        string="Delai carence police",
        related='police_id.delai_carence',
        readonly=True,
    )
    age_limite_adherent = fields.Integer(
        string="Age Limite Adhérent",
        related='police_id.age_limite_adherent',
        readonly=True,
    )
    age_limite_conjoint = fields.Integer(
        string="Age Limite Conjoint(e)",
        related='police_id.age_limite_conjoint',
        readonly=True,
    )
    age_limite_enfant = fields.Integer(
        string="Age Limite Enfant",
        related='police_id.age_limite_enfant',
        readonly=True,
    )
    age_limite_ascendant = fields.Integer(
        string="Age Limite Enfant",
        related='police_id.age_limite_ascendant',
        readonly=True,
    )
    age_limite_parent = fields.Integer(
        string="Age Limite Enfant",
        related='police_id.age_limite_parent',
        readonly=True,
    )
    age_majorite_enfant = fields.Integer(
        string="Age Limite Enfant",
        related='police_id.age_majorite_enfant',
        readonly=True,
    )
    mode_controle_plafond = fields.Selection(
        string="Mode Contrôle Plafond",
        related='police_id.mode_controle_plafond',
        readonly=True,
    )
    # Champs relatifs Adherent
    code_id = fields.Char(
        string="Code ID.",
        related='adherent_id.code_id',
        readonly=True,
    )
    code_id_externe = fields.Char(
        size=32,
        string='Code ID. Externe',
        related='adherent_id.code_id_externe',
        help="Code ID. obtenu à partir d'un système exterieur."
    )
    date_naissance = fields.Date(
        string="Date Naissance",
        related='adherent_id.date_naissance',
    )
    matricule = fields.Char(
        size=32,
        string='N° Matricule',
        related='adherent_id.matricule',
    )
    localite_id = fields.Many2one(
        # comodel_name="proximas.localite",
        string="Localité",
        related="adherent_id.localite_id",
        help="Indiquez la localité de rattachement de l'assuré",
    )
    groupe_id = fields.Many2one(
        # comodel_name="proximas.groupe",
        string="Groupe",
        related="adherent_id.groupe_id",
        required=False,
    )
    groupe_suspendu = fields.Boolean(
        string="Groupe Actif?",
        related='groupe_id.est_suspendu',
        readonly=True,
        help="Indique si le groupe concerné est actif ou non."
    )
    photo = fields.Binary(
        string="Photo",
        attachment=True,
        related="adherent_id.image",
        required=False,
    )
    assure_id = fields.Many2one(
        comodel_name="proximas.assure",
        string="Assuré",
        compute='_get_assure',
        required=False,
    )
    image_medium = fields.Binary(
        attachment=True,
        related='adherent_id.image_medium',
    )
    # image_small = fields.Binary(
    #     attachment=True,
    #     related='adherent_id.image_small',
    # )
    nom = fields.Char(
        string="Nom",
        related='adherent_id.nom',
    )
    prenoms = fields.Char(
        string="Prénom(s)",
        related='adherent_id.prenoms',
    )
    name_adherent = fields.Char(
        string="Nom & Prénoms",
        related='adherent_id.name',
    )
    age = fields.Char(
        string="Age",
        related='adherent_id.age',
        readonly=True,
    )
    tranche_age = fields.Selection (
        string="Tranche d'âge",
        related='adherent_id.tranche_age',
        store=True,
    )
    statut_familial = fields.Selection(
        string="Statut Familial",
        related='adherent_id.statut_familial',
        readonly=True,
    )
    genre = fields.Selection(
        string="Genre",
        related='adherent_id.genre',
    )
    groupe_sanguin = fields.Selection (
        string="Groupe Sanguin",
        related='adherent_id.groupe_sanguin',
        help="Sélectionner un groupe sanguin dans la liste.",
    )
    quartier = fields.Char(
        size=64,
        string='Quartier/Secteur',
        related='adherent_id.quartier',
        help='Indiquer le secteur ou le quartier de résidence',
    )
    date_inscription = fields.Date(
        string="Date Inscription",
        related='adherent_id.date_inscription',
        readonly=True,
    )
    date_activation_adherent = fields.Date(
        string="Date Activation",
        related='adherent_id.date_activation',
        help="Date d'activation de l'adhérent."
    )
    cas_chronique = fields.Boolean(
        string="Malade Chronique?",
        related='adherent_id.cas_chronique',
        readonly=True,
    )
    ref = fields.Char(
        string='Pièce N°',
        related='adherent_id.ref',
        readonly=True,
        help='Type, N° et Date validité de la CNI, Passport ou autre pièce fournie, s\'il y a lieu',
    )
    # localite = fields.Many2one(
    #     string="Localité",
    #     related='adherent_id.localite_id',
    # )

    # parent_id = fields.Many2one(
    #     string="Assure Parent",
    #     related='adherent_id.groupe_id',
    # )
    state = fields.Selection(
        string="Etat",
        related='adherent_id.state',
        readonly=True,
    )
    is_assure = fields.Boolean(
        string="Est Assure?",
        related='adherent_id.is_assure',
    )
    is_company = fields.Boolean(
        string="Est Assure?",
        related='adherent_id.is_company',
    )
    type = fields.Selection(
        string="Type",
        related='adherent_id.type',
    )
    # CONTACTS ADHERENT
    street = fields.Char(
        string="Street",
        related='adherent_id.street',
    )
    street2 = fields.Char(
        string="Street 2",
        related='adherent_id.street2',
    )
    city = fields.Char(
        string="City",
        related='adherent_id.city',
    )
    zip = fields.Char(
        string="Zip)",
        related='adherent_id.zip',
    )
    country_id = fields.Many2one(
        string="Country",
        related='adherent_id.country_id',
    )
    phone = fields.Char(
        string="Phone",
        related='adherent_id.phone',
    )
    mobile = fields.Char(
        string="Mobile",
        related='adherent_id.mobile',
    )
    mobile_2 = fields.Char(
        string="Mobile #2",
        related='adherent_id.mobile_2',
    )
    email = fields.Char(
        string="Mobile",
        related='adherent_id.email',
    )

    # Champs relatifs Police
    mt_capital_deces = fields.Float(
        string="Montant Capital Décès",
        digits=(9, 0),
        related='police_id.mt_capital_deces',
        readonly=True,
    )
    mt_frais_funeraire = fields.Float (
        string="Montant Frais Funéraires",
        digits=(9, 0),
        related='police_id.mt_frais_funeraire',
        readonly=True,
    )
    validite_pec = fields.Integer(
        string="Validité PEC (Heures)",
        related='police_id.validite_pec',
        readonly=True,
    )
    marge_medicament = fields.Float(
        string='Marge/Produit Phcie.',
        related='police_id.marge_medicament',
        readonly=True,
    )
    # CHAMPS CALCULES
    nbre_cas_chronique = fields.Integer(
        string="Nbre. Cas Chronique(s)",
        compute='_compute_prime_contrat',
        default=0,
    )

    nbre_versmt_cotisation = fields.Integer(
        string="Nbre. Versements Effectués",
        compute='_get_nbre_versement',
        default=0,
        help="Nombre de versements effectués"
    )
    mt_totaux_versmt_cotisation = fields.Integer(
        string="Totaux Versements",
        compute='_get_totaux_versement',
        default=0,
        help="Montant totaux de versements effectués"
    )
    nbre_conjoint = fields.Integer(
        string="Nbre. Conjoint(s)",
        compute='_get_nbre_ayant_droit',
        default=0,
        help="Nombre de conjoint(es)"
    )
    nbre_enfant = fields.Integer(
        string="Nbre. Enfant(s)",
        compute='_get_nbre_ayant_droit',
        default=0,
        help="Nombre d'enfant(s)"
    )
    nbre_ascendant = fields.Integer(
        string="Nbre. Ascendant(s)",
        compute='_get_nbre_ayant_droit',
        default=0,
        help="Nombre d'ascendant(s)"
    )
    nbre_parent = fields.Integer(
        string="Nbre. Parent(s)",
        compute='_get_nbre_ayant_droit',
        default=0,
        help="Nombre de parent(s)"
    )
    nbre_conjoint_supp = fields.Integer(
        string="Nbre. conjoint(s) Supp.",
        compute='_get_nbre_conjoint_supp',
        default=0,
        help="Nombre de conjoint(es) supplémentaire(s)"
    )
    nbre_maxi_conjoint = fields.Integer(
        string="Nbre. Maxi Conjoints",
        related='police_id.nbre_maxi_conjoint',
        default=0,
        help='Nombre maxi de conjoint(s) autorisé(s)',
    )
    nbre_limite_conjoint = fields.Integer(
        string="Nbre. limite Conjoints",
        related='police_id.nbre_limite_conjoint',
        default=0,
    )
    supplement_conjoint = fields.Integer(
        string="Nbre. Conjoint(s Supp)",
        related='police_id.supplement_conjoint',
        readonly=True,
        help='Nombre de conjoint(s) supplémentaire(s) autorisé(s)',
    )
    nbre_enfant_supp = fields.Integer(
        string="Nbre. enfant(s) Supp.",
        compute='_get_nbre_enfant_supp',
        default=0,
        help="Nombre d'enfant(s) supplémentaire(s)"
    )
    nbre_limite_enfant = fields.Integer(
        string="Nbre. limite Enfants",
        related='police_id.nbre_limite_enfant',
        default=0,
    )
    supplement_enfant = fields.Integer(
        string="Nbre. Enfant(s) supp/",
        related='police_id.supplement_enfant',
        readonly=True,
        help='Nombre d\'enfant(s) supplémentaire(s) autorisé(s)',
    )
    nbre_maxi_enfant = fields.Integer(
        string="Nbre. Maxi enfants",
        related='police_id.nbre_maxi_enfant',
        default=0,
        help='Nombre maxi d\'enfant(s) supplémentaire(s) autorisé(s)',
    )
    supplement_ascendant = fields.Integer(
        string="Nbre. Ascendantt(s) supp.",
        related='police_id.supplement_ascendant',
        readonly=True,
        help='Nombre d\'ascendant(s) supplémentaire(s) autorisé(s)',
    )
    nbre_limite_ascendant = fields.Integer (
        string="Nbre. limite Ascendants",
        related='police_id.nbre_limite_ascendant',
        default=0,
    )
    nbre_maxi_ascendant = fields.Integer(
        string="Nbre. Maxi ascendants",
        related='police_id.nbre_maxi_ascendant',
        default=0,
        help='Nombre maxi d\'ascendant(s) supplémentaire(s) autorisé(s)',
    )
    supplement_parent = fields.Integer(
        string="Nbre. parent(s Supp)",
        related='police_id.supplement_parent',
        readonly=True,
        help='Nombre de parent(s) supplémentaire(s) autorisé(s)',
    )
    nbre_limite_parent = fields.Integer (
        string="Nbre. limite Parents",
        related='police_id.nbre_limite_parent',
        default=0,
    )
    nbre_maxi_parent = fields.Integer (
        string="Nbre. Maxi Parents",
        related='police_id.nbre_maxi_parent',
        default=0,
        help='Nombre maxi de parent(s) autorisé(s)',
    )
    jours_contrat = fields.Integer(
        string="Nbre. jours Contrat",
        compute='_get_etat_contrat',
        readonly=True,
    )
    effectif_contrat = fields.Integer(
        string="Effectif/ Contrat",
        compute='_compute_prime_contrat',
        store=True,
        readonly=True,
    )
    prise_charge_ids = fields.One2many(
        comodel_name="proximas.prise.charge",
        inverse_name="contrat_id",
        string="Prises en charge",
    )
    rfm_ids = fields.One2many(
        comodel_name="proximas.remboursement.pec",
        inverse_name="contrat_id",
        string="Remb. Frais Médicaux",
    )
    details_pec_ids = fields.One2many(
        comodel_name="proximas.details.pec",
        inverse_name="contrat_id",
        string="Détails PEC",
        domain=[
            ('date_execution', '!=', None),
        ]
    )
    details_actes_ids = fields.One2many (
        comodel_name="proximas.details.pec",
        inverse_name="contrat_id",
        string="Détails PEC",
        domain=[
            ('date_execution', '!=', None),
            ('produit_phcie_id', '=', None),
        ]
    )
    details_phcie_ids = fields.One2many (
        comodel_name="proximas.details.pec",
        inverse_name="contrat_id",
        string="Détails PEC",
        domain=[
            ('date_execution', '!=', None),
            ('produit_phcie_id', '!=', None),
        ]
    )
    # Champs calculés pour Prime de Couverture
    totaux_net_payable_police = fields.Float(
        string='Net Payable Prime Police',
        digits=(9, 0),
        compute='_compute_prime_contrat',
        store=True,
        help='Totaux à devoir pour les primes liées à la police.',
    )
    totaux_prime_police = fields.Float (
        string='S/Totaux Prime Police',
        digits=(9, 0),
        compute='_compute_prime_contrat',
        store=True,
        help='Totaux dues pour la prime police.',
    )
    totaux_net_payable_contrat = fields.Float(
        string='Net Payable Prime Contrat',
        digits=(9, 0),
        compute='_compute_prime_contrat',
        store=True,
        help='Totaux à devoir pour les primes liées au contrat.',
    )
    totaux_prime_contrat = fields.Float (
        string='S/Totaux Primes Contrat',
        digits=(9, 0),
        compute='_compute_prime_contrat',
        store=True,
        help='Totaux dues pour les primes.',
    )
    totaux_prime = fields.Float(
        string='S/Totaux Généraux Primes',
        digits=(9, 0),
        compute='_compute_prime_contrat',
        store=True,
        help='Totaux dues pour les l\'ensemble des primes.',
    )
    totaux_net_payable = fields.Float(
        string='Net Payable Prime',
        digits=(9, 0),
        compute='_compute_prime_contrat',
        store=True,
        help='Totaux payable pour l\'ensemble des primes.',
    )
    mt_reste_payable = fields.Float(
        string='Reste Payable (Prime)',
        digits=(9, 0),
        compute='_compute_prime_contrat',
        store=True,
        help='Totaux à devoir pour la prime de couverture.',
    )
    # Compte contrat pour le controle consommation famille
    # sous_totaux_contrat = fields.Float(
    #     string="S/Totaux Contrat",
    #     digits=(9, 0),
    #     compute='_check_details_pec',
    #     default=0,
    #     # related='assure_id.sous_totaux_pec',
    # )
    # nbre_actes_contrat = fields.Integer(
    #     string="Nbre. Actes Contrat",
    #     compute='_check_details_pec',
    #     default=0,
    #     # related='assure_id.nbre_actes_pec',
    # )
    # CHAMPS CALCULES - CONTROLES DE PLAFONDS
    nbre_pec_contrat_encours = fields.Integer(
        string="Nbre. PEC/Famille",
        compute='_compute_sinistres_contrat',
        default=0,
        help="Nombre de prises en charge (PEC) pour l'exercice en cours..."
    )
    nbre_rfm_contrat_encours = fields.Integer(
        string="Nbre. Remb./Famille",
        compute='_compute_sinistres_contrat',
        default=0,
        help="Nombre de Remboursemenr(s)/Contrat pour l'exercice en cours..."
    )
    mt_sinistres_contrat_encours = fields.Float(
        string="Totaux Sinistres Famille",
        digits=(9, 0),
        compute='_compute_sinistres_contrat',
        default=0,
        help="Totaux Sinistres /Contrat pour l'exercice en cours..."
    )
    nbre_actes_contrat_encours = fields.Integer(
        string="Nbre. Actes/Famille",
        compute='_compute_sinistres_contrat',
        default=0,
        help="Nombre d'actes médicaux pour l'exercice en cours..."
    )
    mt_sinistres_actes_contrat_encours = fields.Float(
        string="Totaux Actes Famille",
        digits=(9, 0),
        compute='_compute_sinistres_contrat',
        default=0,
    )
    nbre_phcie_contrat_encours = fields.Integer(
        string="Nbre. Prescription(s)/Famille",
        compute='_compute_sinistres_contrat',
        default=0,
        help="Nombre de prescription(s) pour l'exercice en cours..."
    )
    mt_sinistres_phcie_contrat_encours = fields.Float (
        string="Totaux Phcie. Famille",
        digits=(9, 0),
        compute='_compute_sinistres_contrat',
        default=0,
    )
    taux_sinistre_plafond_famille = fields.Float(
        string="Taux Sinistre/Plafond",
        digits=(9, 0),
        compute='_compute_sinistres_contrat',
        default=0,
    )
    duree_activation = fields.Char(
        string="Durée Activation (Details)",
        compute='_get_duree_activation',
    )

    @api.one
    @api.depends('date_activation', 'date_resiliation',  'validite_contrat', 'validite_contrat_police', 'jours_contrat',
                 'mode_controle_plafond')
    def _compute_debut_fin_contrat(self):
        now = fields.Datetime.from_string (fields.Date.today ())
        activation_contrat = fields.Date.from_string(self.date_activation)
        date_resiliation = fields.Date.from_string(self.date_resiliation)
        validite_contrat = int (self.validite_contrat)
        validite_police = int (self.validite_contrat_police)
        if validite_contrat:
            nbre_renouvellement = self.jours_contrat / validite_contrat
            self.nbre_renouvellement_contrat = nbre_renouvellement
        elif validite_police:
            nbre_renouvellement = self.jours_contrat / validite_police
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
                if date_resiliation:
                    self.date_debut_contrat = activation_contrat
                    self.date_fin_prevue = date_resiliation
                elif activation_contrat > date_debut:
                    self.date_debut_contrat = activation_contrat
                    self.date_fin_prevue = date_fin
                else:
                    self.date_debut_contrat = date_debut
                    self.date_fin_prevue = date_fin
            else:
                raise UserError (
                    '''
                         Proximaas - Contrôle des règles de Gestion :\n
                         Le mode de contrôle défini pour le plafond famille (contrat)\
                         est l'Exercice. Cependant, le système n'a détecté aucun ou plus d'un exercice\
                         en cours. Pour plus d'informations, veuillez contactez l'administrateur...
                     '''
                )
        # 2. MODE DE CONTROLE PAR CONTRAT
        elif self.mode_controle_plafond in ['contrat']:
            if date_resiliation:
                self.date_debut_contrat = activation_contrat
                self.date_fin_prevue = date_resiliation
            elif self.nbre_renouvellement_contrat >= 1:
                if validite_contrat:
                    self.date_debut_contrat = activation_contrat + timedelta (days=int (self.validite_contrat))
                    date_debut = fields.Date.from_string(self.date_debut_contrat)
                    self.date_fin_prevue = date_debut + timedelta (days=int (self.validite_contrat))
                elif validite_police:
                    self.date_debut_contrat = activation_contrat + timedelta (days=int (self.validite_police))
                    date_debut = fields.Date.from_string (self.date_debut_contrat)
                    self.date_fin_prevue = date_debut + timedelta (days=int (self.validite_police))
            else:
                if validite_contrat:
                    self.date_debut_contrat = activation_contrat
                    date_debut = fields.Date.from_string (self.date_debut_contrat)
                    self.date_fin_prevue = date_debut + timedelta (days=int (self.validite_contrat))
                elif validite_police:
                    self.date_debut_contrat = activation_contrat
                    date_debut = fields.Date.from_string (self.date_debut_contrat)
                    self.date_fin_prevue = date_debut + timedelta(days=int (self.validite_police))

    @api.one
    @api.depends('prise_charge_ids', 'rfm_ids', 'details_pec_ids', 'details_phcie_ids')
    def _compute_sinistres_contrat(self):
        # for rec in self:
        if self.details_pec_ids:
            date_debut = fields.Date.from_string(self.date_debut_contrat)
            date_fin = fields.Date.from_string(self.date_fin_prevue)
            prise_en_charge_encours = []
            rfm_encours = []
            details_pec_encours = []
            details_actes_encours = []
            details_phcie_encours = []
            for detail in self.prise_charge_ids:
                date_saisie = fields.Date.from_string(detail.date_saisie)
                if date_debut <= date_saisie <= date_fin:
                    prise_en_charge_encours.append(detail)
            for detail in self.rfm_ids:
                date_saisie = fields.Date.from_string(detail.date_saisie)
                if date_debut <= date_saisie <= date_fin:
                    rfm_encours.append(detail)
            for detail in self.details_pec_ids:
                date_execution = fields.Date.from_string (detail.date_execution)
                if date_debut <= date_execution <= date_fin:
                    details_pec_encours.append (detail)
            for detail in self.details_actes_ids:
                date_execution = fields.Date.from_string (detail.date_execution)
                if date_debut <= date_execution <= date_fin:
                    details_actes_encours.append (detail)
            for detail in self.details_phcie_ids:
                date_execution = fields.Date.from_string (detail.date_execution)
                if date_debut <= date_execution <= date_fin:
                    details_phcie_encours.append (detail)
            self.nbre_pec_contrat_encours = len(prise_en_charge_encours)
            self.nbre_rfm_contrat_encours = len(rfm_encours)
            self.nbre_actes_contrat_encours = len(details_actes_encours)
            self.mt_sinistres_contrat_encours = sum(item.total_pc for item in details_pec_encours)
            self.mt_sinistres_actes_contrat_encours = sum(item.total_pc for item in details_actes_encours)
            self.nbre_phcie_contrat_encours = len(details_phcie_encours)
            self.mt_sinistres_phcie_contrat_encours = sum(item.total_pc for item in details_phcie_encours)
        if self.plafond_famille:
            self.taux_sinistre_plafond_famille = self.mt_sinistres_contrat_encours * 100 / self.plafond_famille
        

    # NIVEAU CONSO COURANT
    # @api.multi
    @api.depends('adherent_id', 'mode_controle_plafond')
    def _sinistre_details_pec(self):
        for rec in self:
            # CALCULS DE DETAILS SINISTRES
            # 1. MODE DE CONTROLE PAR EXERCICE
            contrat_id = rec.id
            plafond_famille = rec.plafond_famille
            if bool (rec.mode_controle_plafond == 'exercice'):
                exo = self.env['proximas.exercice'].search([
                    ('res_company_id', '=', rec.structure_id.id),
                    ('en_cours', '=', True),
                ])
                if bool (exo) and len (exo) != 1:
                    return {'value': {},
                            'warning': {
                                'title': u'Proximas : Contrôle Règles de gestion => Plafond Exercice ',
                                'message': u"Le mode de contrôle défini pour le plafond famille (contrat)\
                                 est l'Exercice. Cependant, le système a détecté plus d'un exercice\
                                 en cours. Pour plus d'informations, veuillez contactez l'administrateur..."
                            }
                            }
                elif bool (exo) and len (exo) == 1:
                    details_pec_exo_encours = self.env['proximas.details.pec'].search (
                        [
                            ('contrat_id', '=', contrat_id),
                            ('date_execution', '!=', None),
                            ('exo_name', '=', exo.name)
                        ]
                    )
                    actes_exo_encours = self.env['proximas.details.pec'].search_count (
                        [
                            ('contrat_id', '=', contrat_id),
                            ('date_execution', '!=', None),
                            ('produit_phcie_id', '=', None),
                            ('exo_name', '=', exo.name)
                        ]
                    )
                    phcie_exo_encours = self.env['proximas.details.pec'].search_count (
                        [
                            ('contrat_id', '=', contrat_id),
                            ('date_execution', '!=', None),
                            ('produit_phcie_id', '!=', None),
                            ('exo_name', '=', exo.name)
                        ]
                    )
                    if bool (details_pec_exo_encours):
                        rec.mt_sinistre_encours = sum (item.total_pc for item in details_pec_exo_encours) or 0
                        if bool (actes_exo_encours):
                            rec.nbre_acte_encours = int (actes_exo_encours)
                        if bool (phcie_exo_encours):
                            rec.nbre_phcie_encours = int (phcie_exo_encours)
                        if bool (rec.plafond_famille):
                            rec.taux_sinistre_plafond_famille = rec.mt_sinistre_encours * 100 / plafond_famille
                else:
                    return {'value': {},
                            'warning': {
                                'title': u'Proximas : Contrôle Règles de gestion => Plafond Exercice ',
                                'message': u"Le mode de contrôle défini pour le plafond famille (contrat)\
                                 est l'Exercice. Cependant, le système n'a pu obtenir aucun exercice\
                                 en cours. Pour plus d'informations, veuillez contactez l'administrateur..."
                            }
                            }
            # 2. MODE DE CONTROLE PAR CONTRAT
            elif bool (rec.mode_controle_plafond == 'contrat'):
                pass

    @api.multi
    def _get_assure(self):
        for rec in self:
            assure = self.env['proximas.assure'].search([('code_id', 'ilike', self.code_id)])
            rec.assure_id = assure.id

    @api.depends('date_activation', 'date_inscription')
    def _get_duree_activation(self):
        now = datetime.now()
        if bool(self.date_activation):
            activation = fields.Datetime.from_string (self.date_activation)
            delta = relativedelta (now, activation)
            annees_mois_jours = '%s %s - %s %s - %s %s' % (
                delta.years, _ ('an(s)'),
                delta.months, _ ('mois'),
                delta.days, _ ('jours')
            )
            self.duree_activation = annees_mois_jours

    # @api.one
    # @api.depends('date_resiliation', 'date_activation', 'validite_contrat', 'validite_contrat_police', 'jours_contrat',
    #              'police_id', 'ayant_droit_ids', 'cotisation_ids', 'prime_contrat_ids', 'retard_cotisation')
    # def auto_compute_date_fin_prevue(self):
    #     now = fields.Datetime.from_string (fields.Date.today ())
    #     activation_contrat = fields.Datetime.from_string (self.date_activation)
    #     date_resiliation = fields.Datetime.from_string (self.date_resiliation)
    #     date_echeance_police = fields.Datetime.from_string (self.date_echeance_police)
    #     nbre_jours_validite_police = int (self.validite_contrat_police)
    #     # Calcul de la date de fin prévue du contrat Adherent
    #     # datetime.now () + timedelta (days=2, hours=4, minutes=3, seconds=12)
    #     if bool (date_resiliation):
    #         self.date_fin_prevue = date_resiliation
    #     elif not bool (date_resiliation):
    #         self.date_fin_prevue = activation_contrat + timedelta (days=int (self.validite_contrat))
    #     date_fin_prevue = fields.Datetime.from_string (self.date_fin_prevue)
    #     if date_fin_prevue <= now:
    #         self.date_fin_prevue = date_fin_prevue + timedelta (days=int (self.validite_contrat))
    #     else:
    #         self.date_fin_prevue = now
    #
    # @api.one
    # @api.depends('date_activation', 'date_fin_prevue', 'validite_contrat', 'validite_contrat_police', 'jours_contrat',
    #              'nbre_renouvellement_contrat', )
    # def auto_compute_date_debut(self):
    #     # Calcul de la date de fin prévue du contrat Adherent
    #     # datetime.now () + timedelta (days=2, hours=4, minutes=3, seconds=12)
    #     now = fields.Datetime.from_string (fields.Date.today())
    #     activation_contrat = fields.Datetime.from_string(self.date_activation)
    #     date_fin_prevue = fields.Datetime.from_string(self.date_fin_prevue) or now
    #     nbre_jours_validite_police = int(self.validite_contrat_police)
    #     if bool (nbre_jours_validite_police):
    #         self.nbre_renouvellement_contrat = self.jours_contrat / nbre_jours_validite_police
    #     nbre_renouvellement = self.nbre_renouvellement_contrat
    #     if bool (nbre_renouvellement) and nbre_renouvellement <= 0:
    #         self.date_debut_contrat = activation_contrat
    #     elif bool (nbre_renouvellement) and nbre_renouvellement > 0:
    #         self.date_debut_contrat = date_fin_prevue - timedelta(days=int(self.validite_contrat))
    #

    # CALCULS DE PRIMES DE COUVERTURE PAAR CONTRAT
    # @api.one
    @api.depends('police_id', 'ayant_droit_ids', 'cotisation_ids', 'prime_contrat_ids', 'date_activation',
                 'date_resiliation', 'delai_carence', 'retard_cotisation', 'date_fin_prevue', 'validite_contrat_police')
    def _compute_prime_contrat(self):
        for rec in self:
            now = fields.Datetime.from_string (fields.Date.today ())
            activation_contrat = fields.Datetime.from_string(rec.date_activation) or now
            date_resiliation = fields.Datetime.from_string(rec.date_resiliation) or now
            date_fin_prevue = fields.Datetime.from_string(rec.date_fin_prevue) or now
            nbre_jours_validite_police = int(rec.validite_contrat_police)
            nbre_jours_contrat = int(rec.jours_contrat)
            mt_retard_cotisation = int(rec.retard_cotisation)
            controle_retard = bool(rec.controle_retard_cotisation)
            totaux_versements = int(rec.mt_totaux_versmt_cotisation)
            mt_supp_enfant = int(rec.police_id.mt_supplement_enfant)
            mt_supp_conjoint = int(rec.police_id.mt_supplement_conjoint)
            mt_supp_parent = int(rec.police_id.mt_supplement_parent)
            mt_supp_ascendant = int(rec.police_id.mt_supplement_ascendant)
            mt_supp_malade_chronique = int(rec.police_id.mt_supplement_maladie)
            mt_supp_global = mt_supp_conjoint + mt_supp_enfant + mt_supp_ascendant + mt_supp_parent + mt_supp_malade_chronique
            rec.effectif_contrat = len(rec.ayant_droit_ids) + 1
            effectif_famille = int(rec.effectif_contrat)

            # Si le contrôle de Retard Cotisation est activé?
            if bool(controle_retard):
                # Si Oui, alors vérifier s'il y a un montant de retard toleré et que le net payable est superieur au
                # montant de retard toleré?
                if 0 < mt_retard_cotisation <= rec.mt_reste_payable:
                    # Si Oui, Désactivé le contrat
                    rec.actif = False

            if bool(nbre_jours_validite_police):
                nbre_renouvellement = int (nbre_jours_contrat / nbre_jours_validite_police) + 1
            if date_fin_prevue >= now:
                primes_police = self.env['proximas.prime'].search ([('police_id', '=', rec.police_id.id)])
                primes_contrat = self.env['proximas.prime.contrat'].search ([('contrat_id', '=', rec.id)])
                # 1. Calcul de la Prime Totale Police
                if bool(primes_police):
                    # Verifier s'il y a des primes enregistrées pour la police concernée du contrat.
                    prime_payable_police = 0
                    prime_globale_police = 0
                    for item in primes_police:
                        # Pour chaque prime définie pour la police concernée :
                        # date_resiliation = fields.Datetime.from_string(rec.date_resiliation) or now
                        applicable = item.applicable
                        periodicite = item.periodicite
                        mt_prime = int(item.mt_prime)
                        date_debut = fields.Datetime.from_string (item.date_debut)
                        date_fin = fields.Datetime.from_string (item.date_fin)
                        nbre_jours_contrat = int(rec.jours_contrat)
                        nbre_jours_total = 0
                        nbre_jours_payable = 0

                        # Si le champ d'application de la prime est le contrat (famille)
                        if applicable == 'tous':
                            # Vérification de la présence d'ayant-droit dans le contrat
                            if bool(rec.ayant_droit_ids):
                                ayant_droit = self.env['proximas.ayant.droit'].search ([('contrat_id', '=', rec.id)])
                                total_prime_police_ayant_droit = 0
                                # Ajout de la prime de l'adhérent
                                if bool (date_fin) and (date_fin > date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                elif bool (date_fin) and not bool (date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                elif not bool (date_fin) and bool (date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                else:
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (now - date_debut).days
                                        nbre_jours_payable = nbre_jours_total
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (now - activation_contrat).days
                                        nbre_jours_payable = nbre_jours_total
                                # Vérification de la périodicité de la prime
                                if periodicite == 'jour':
                                    qte_prime = int (nbre_jours_payable)
                                    qte_valide = int (nbre_jours_total)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'semaine':
                                    qte_prime = round (nbre_jours_payable / 7) + 1
                                    qte_valide = round (nbre_jours_total / 7)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'mois':
                                    qte_prime = round (nbre_jours_contrat / 30) + 1
                                    qte_valide = round (nbre_jours_total / 30)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'trimestre':
                                    qte_prime = round (nbre_jours_payable / 90) + 1
                                    qte_valide = round (nbre_jours_total / 90)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'annee':
                                    qte_prime = round (nbre_jours_payable / 365) + 1
                                    qte_valide = round (nbre_jours_total / 365)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'unique':
                                    prime_payable_police += int (mt_prime)
                                    prime_globale_police += int (mt_prime)
                                # Calcul de la prime pour les ayant-droits
                                for item in ayant_droit:
                                    date_activation = fields.Datetime.from_string(item.date_activation)
                                    # Vérification de la date de fin d'application de la prime et calcul du nbre de jours
                                    # écoulés selon la date d'activation de l'ayant-droit, la date début et fin de la prime
                                    if bool (date_fin) and (date_fin > date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    elif bool (date_fin) and not bool (date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    elif not bool (date_fin) and bool (date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    else:
                                        if date_debut > date_activation:
                                            nbre_jours_total = (now - date_debut).days
                                            nbre_jours_payable = nbre_jours_total
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (now - date_activation).days
                                            nbre_jours_payable = nbre_jours_total
                                    # Vérification de la périodicité de la prime
                                    if periodicite == 'jour':
                                        qte_prime = int (nbre_jours_payable)
                                        qte_valide = int (nbre_jours_total)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'semaine':
                                        qte_prime = round (nbre_jours_payable / 7) + 1
                                        qte_valide = round (nbre_jours_total / 7)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'mois':
                                        qte_prime = round (nbre_jours_payable / 30) + 1
                                        qte_valide = round (nbre_jours_total / 30)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'trimestre':
                                        qte_prime = round (nbre_jours_payable / 90) + 1
                                        qte_valide = round (nbre_jours_total / 90)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'annee':
                                        qte_prime = round (nbre_jours_payable / 365) + 1
                                        qte_valide = round (nbre_jours_total / 365)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'unique':
                                        prime_payable_police += int (mt_prime)
                                        prime_globale_police += int (mt_prime)
                            else:
                                # Ajout de la prime de l'adhérent
                                if bool (date_fin) and (date_fin > date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                elif bool (date_fin) and not bool (date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                elif not bool (date_fin) and bool (date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                else:
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (now - date_debut).days
                                        nbre_jours_payable = nbre_jours_total
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (now - activation_contrat).days
                                        nbre_jours_payable = nbre_jours_total

                                # Vérification de la périodicité de la prime
                                if periodicite == 'jour':
                                    qte_prime = int (nbre_jours_payable)
                                    qte_valide = int (nbre_jours_total)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'semaine':
                                    qte_prime = round (nbre_jours_payable / 7) + 1
                                    qte_valide = round (nbre_jours_total / 7)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'mois':
                                    qte_prime = round (nbre_jours_payable / 30) + 1
                                    qte_valide = round (nbre_jours_total / 30)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'trimestre':
                                    qte_prime = round (nbre_jours_payable / 90) + 1
                                    qte_valide = round (nbre_jours_total / 90)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'annee':
                                    qte_prime = round (nbre_jours_payable / 365) + 1
                                    qte_valide = round (nbre_jours_total / 365)
                                    prime_payable_police += int (qte_prime * mt_prime)
                                    prime_globale_police += int (qte_valide * mt_prime)
                                elif periodicite == 'unique':
                                    prime_payable_police += int (mt_prime)
                                    prime_globale_police += int (mt_prime)
                        # Vérification du champ d'application de la prime police
                        elif applicable == 'ayant-droit':
                            # Vérification de la présence d'ayant-droit dans le contrat
                            if bool(rec.ayant_droit_ids):
                                ayant_droit = self.env['proximas.ayant.droit'].search([('contrat_id', '=', rec.id)])
                                # total_prime_police_ayant_droit = 0
                                # Calcul de la prime pour les ayant-droits
                                for item in ayant_droit:
                                    date_activation = fields.Datetime.from_string (item.date_activation)
                                    # Vérification de la date de fin d'application de la prime et calcul du nbre de jours
                                    # écoulés selon la date d'activation de l'ayant-droit, la date début et fin de la prime
                                    if bool (date_fin) and (date_fin > date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    elif bool (date_fin) and not bool (date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    elif not bool (date_fin) and bool (date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    else:
                                        if date_debut > date_activation:
                                            nbre_jours_total = (now - date_debut).days
                                            nbre_jours_payable = nbre_jours_total
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (now - date_activation).days
                                            nbre_jours_payable = nbre_jours_total
                                    # Vérification de la périodicité de la prime
                                    if periodicite == 'jour':
                                        qte_prime = int (nbre_jours_payable)
                                        qte_valide = int (nbre_jours_total)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'semaine':
                                        qte_prime = round (nbre_jours_payable / 7) + 1
                                        qte_valide = round (nbre_jours_total / 7)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'mois':
                                        qte_prime = round (nbre_jours_payable / 30) + 1
                                        qte_valide = round (nbre_jours_total / 30)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'trimestre':
                                        qte_prime = round (nbre_jours_payable / 90) + 1
                                        qte_valide = round (nbre_jours_total / 90)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'annee':
                                        qte_prime = round (nbre_jours_payable / 365) + 1
                                        qte_valide = round (nbre_jours_total / 365)
                                        prime_payable_police += int (qte_prime * mt_prime)
                                        prime_globale_police += int (qte_valide * mt_prime)
                                    elif periodicite == 'unique':
                                        prime_payable_police += int (mt_prime)
                                        prime_globale_police += int (mt_prime)
                        # Si le champ d'application de la prime est l'adherent
                        elif applicable == 'adherent':
                            # Ajout de la prime de l'adhérent
                            if bool (date_fin) and (date_fin > date_fin_prevue):
                                if date_debut > activation_contrat:
                                    nbre_jours_total = (date_fin_prevue - date_debut).days
                                    nbre_jours_payable = (now - date_debut).days
                                elif date_debut <= activation_contrat:
                                    nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                    nbre_jours_payable = (now - activation_contrat).days
                            elif bool (date_fin) and not bool (date_fin_prevue):
                                if date_debut > activation_contrat:
                                    nbre_jours_total = (date_fin - date_debut).days
                                    nbre_jours_payable = (now - date_debut).days
                                elif date_debut <= activation_contrat:
                                    nbre_jours_total = (date_fin - activation_contrat).days
                                    nbre_jours_payable = (now - activation_contrat).days
                            elif not bool (date_fin) and bool (date_fin_prevue):
                                if date_debut > activation_contrat:
                                    nbre_jours_total = (date_fin_prevue - date_debut).days
                                    nbre_jours_payable = (now - date_debut).days
                                elif date_debut <= activation_contrat:
                                    nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                    nbre_jours_payable = (now - activation_contrat).days
                            else:
                                if date_debut > activation_contrat:
                                    nbre_jours_total = (now - date_debut).days
                                    nbre_jours_payable = nbre_jours_total
                                elif date_debut <= activation_contrat:
                                    nbre_jours_total = (now - activation_contrat).days
                                    nbre_jours_payable = nbre_jours_total
                            # Vérification de la périodicité de la prime
                            if periodicite == 'jour':
                                qte_prime = int (nbre_jours_payable)
                                qte_valide = int (nbre_jours_total)
                                prime_payable_police += int (qte_prime * mt_prime)
                                prime_globale_police += int (qte_valide * mt_prime)
                            elif periodicite == 'semaine':
                                qte_prime = round(nbre_jours_payable / 7) + 1
                                qte_valide = round(nbre_jours_total / 7)
                                prime_payable_police += int (qte_prime * mt_prime)
                                prime_globale_police += int (qte_valide * mt_prime)
                            elif periodicite == 'mois':
                                qte_prime = round (nbre_jours_payable / 30) + 1
                                qte_valide = round (nbre_jours_total / 30)
                                prime_payable_police += int (qte_prime * mt_prime)
                                prime_globale_police += int (qte_valide * mt_prime)
                            elif periodicite == 'trimestre':
                                qte_prime = round (nbre_jours_payable / 90) + 1
                                qte_valide = round (nbre_jours_total / 90)
                                prime_payable_police += int (qte_prime * mt_prime)
                                prime_globale_police += int (qte_valide * mt_prime)
                            elif periodicite == 'annee':
                                qte_prime = round (nbre_jours_payable / 365) + 1
                                qte_valide = round (nbre_jours_total / 365)
                                prime_payable_police += int (qte_prime * mt_prime)
                                prime_globale_police += int (qte_valide * mt_prime)
                            elif periodicite == 'unique':
                                prime_payable_police += int (mt_prime)
                                prime_globale_police += int (mt_prime)
                    # on obtinet les totaux primes pour la police
                    rec.totaux_net_payable_police = prime_payable_police
                    rec.totaux_prime_police = prime_globale_police

                # 2. Calcul de la Prime Totale Contrat
                if bool(primes_contrat):
                    # Verifier s'il y a des primes enregistrées pour la police concernée du contrat.
                    prime_payable_contrat = 0
                    prime_globale_contrat = 0
                    for item in primes_contrat:
                        # Pour chaque prime définie pour la police concernée :
                        # date_resiliation = fields.Datetime.from_string(rec.date_resiliation) or now
                        applicable = item.applicable
                        periodicite = item.periodicite
                        mt_prime = int (item.mt_prime)
                        date_debut = fields.Datetime.from_string (item.date_debut)
                        date_fin = fields.Datetime.from_string (item.date_fin)
                        nbre_jours_contrat = int(rec.jours_contrat)
                        nbre_jours_total = 0
                        nbre_jours_payable = 0
                        # Vérification du champ d'application de la prime contrat
                        if applicable == 'ayant-droit':
                            # Vérification de la présence d'ayant-droit dans le contrat
                            if bool(rec.ayant_droit_ids):
                                ayant_droit = self.env['proximas.ayant.droit'].search(
                                    [('contrat_id', '=', rec.id)])
                                # total_prime_police_ayant_droit = 0

                                for item in ayant_droit:
                                    date_activation = fields.Datetime.from_string (item.date_activation)
                                    # Vérification de la date de fin d'application de la prime et calcul du nbre de jours
                                    # écoulés selon la date d'activation de l'ayant-droit, la date début et fin de la prime
                                    if bool (date_fin) and (date_fin > date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    elif bool (date_fin) and not bool (date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    elif not bool (date_fin) and bool (date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    else:
                                        if date_debut > date_activation:
                                            nbre_jours_total = (now - date_debut).days
                                            nbre_jours_payable = nbre_jours_total
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (now - date_activation).days
                                            nbre_jours_payable = nbre_jours_total
                                    # Vérification de la périodicité de la prime
                                    if periodicite == 'jour':
                                        qte_prime = int (nbre_jours_payable)
                                        qte_valide = int (nbre_jours_total)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'semaine':
                                        qte_prime = round (nbre_jours_payable / 7) + 1
                                        qte_valide = round (nbre_jours_total / 7)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'mois':
                                        qte_prime = round (nbre_jours_payable / 30) + 1
                                        qte_valide = round (nbre_jours_total / 30)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'trimestre':
                                        qte_prime = round (nbre_jours_payable / 90) + 1
                                        qte_valide = round (nbre_jours_total / 90)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'annee':
                                        qte_prime = round (nbre_jours_payable / 365) + 1
                                        qte_valide = round (nbre_jours_total / 365)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'unique':
                                        prime_payable_contrat += int (mt_prime)
                                        prime_globale_contrat += int (mt_prime)
                        # Si le champ d'application de la prime est le contrat (famille)
                        elif applicable == 'tous':
                            # Vérification de la présence d'ayant-droit dans le contrat
                            if bool (rec.ayant_droit_ids):
                                ayant_droit = self.env['proximas.ayant.droit'].search (
                                    [('contrat_id', '=', rec.id)])
                                total_prime_police_ayant_droit = 0
                                # Ajout de la prime de l'adhérent
                                if bool (date_fin) and (date_fin > date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                elif bool (date_fin) and not bool (date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                elif not bool (date_fin) and bool (date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                else:
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (now - date_debut).days
                                        nbre_jours_payable = nbre_jours_total
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (now - activation_contrat).days
                                        nbre_jours_payable = nbre_jours_total
                                # Vérification de la périodicité de la prime
                                if periodicite == 'jour':
                                    qte_prime = int (nbre_jours_payable)
                                    qte_valide = int (nbre_jours_total)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'semaine':
                                    qte_prime = round (nbre_jours_payable / 7) + 1
                                    qte_valide = round (nbre_jours_total / 7)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'mois':
                                    qte_prime = round (nbre_jours_contrat / 30) + 1
                                    qte_valide = round (nbre_jours_total / 30)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'trimestre':
                                    qte_prime = round (nbre_jours_payable / 90) + 1
                                    qte_valide = round (nbre_jours_total / 90)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'annee':
                                    qte_prime = round (nbre_jours_payable / 365) + 1
                                    qte_valide = round (nbre_jours_total / 365)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'unique':
                                    prime_payable_contrat += int (mt_prime)
                                    prime_globale_contrat += int (mt_prime)
                                # Calcul de la prime contrat pour les ayants-droit
                                for item in ayant_droit:
                                    date_activation = fields.Datetime.from_string (item.date_activation)
                                    # Vérification de la date de fin d'application de la prime et calcul du nbre de jours
                                    # écoulés selon la date d'activation de l'ayant-droit, la date début et fin de la prime
                                    if bool (date_fin) and (date_fin > date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    elif bool (date_fin) and not bool (date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    elif not bool (date_fin) and bool (date_fin_prevue):
                                        if date_debut > date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_debut).days
                                            nbre_jours_payable = (now - date_debut).days
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (date_fin_prevue - date_activation).days
                                            nbre_jours_payable = (now - date_activation).days
                                    else:
                                        if date_debut > date_activation:
                                            nbre_jours_total = (now - date_debut).days
                                            nbre_jours_payable = nbre_jours_total
                                        elif date_debut <= date_activation:
                                            nbre_jours_total = (now - date_activation).days
                                            nbre_jours_payable = nbre_jours_total
                                    # Vérification de la périodicité de la prime
                                    if periodicite == 'jour':
                                        qte_prime = int (nbre_jours_payable)
                                        qte_valide = int (nbre_jours_total)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'semaine':
                                        qte_prime = round (nbre_jours_payable / 7) + 1
                                        qte_valide = round (nbre_jours_total / 7)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'mois':
                                        qte_prime = round (nbre_jours_payable / 30) + 1
                                        qte_valide = round (nbre_jours_total / 30)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'trimestre':
                                        qte_prime = round (nbre_jours_payable / 90) + 1
                                        qte_valide = round (nbre_jours_total / 90)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'annee':
                                        qte_prime = round (nbre_jours_payable / 365) + 1
                                        qte_valide = round (nbre_jours_total / 365)
                                        prime_payable_contrat += int (qte_prime * mt_prime)
                                        prime_globale_contrat += int (qte_valide * mt_prime)
                                    elif periodicite == 'unique':
                                        prime_payable_contrat += int (mt_prime)
                                        prime_globale_contrat += int (mt_prime)
                            else:
                                # Ajout de la prime de l'adhérent
                                if bool (date_fin) and (date_fin > date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                elif bool (date_fin) and not bool (date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                elif not bool (date_fin) and bool (date_fin_prevue):
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - date_debut).days
                                        nbre_jours_payable = (now - date_debut).days
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                        nbre_jours_payable = (now - activation_contrat).days
                                else:
                                    if date_debut > activation_contrat:
                                        nbre_jours_total = (now - date_debut).days
                                        nbre_jours_payable = nbre_jours_total
                                    elif date_debut <= activation_contrat:
                                        nbre_jours_total = (now - activation_contrat).days
                                        nbre_jours_payable = nbre_jours_total
                                # Vérification de la périodicité de la prime
                                if periodicite == 'jour':
                                    qte_prime = int (nbre_jours_payable)
                                    qte_valide = int (nbre_jours_total)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'semaine':
                                    qte_prime = round (nbre_jours_payable / 7) + 1
                                    qte_valide = round (nbre_jours_total / 7)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'mois':
                                    qte_prime = round (nbre_jours_payable / 30) + 1
                                    qte_valide = round (nbre_jours_total / 30)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'trimestre':
                                    qte_prime = round (nbre_jours_payable / 90) + 1
                                    qte_valide = round (nbre_jours_total / 90)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'annee':
                                    qte_prime = round (nbre_jours_payable / 365) + 1
                                    qte_valide = round (nbre_jours_total / 365)
                                    prime_payable_contrat += int (qte_prime * mt_prime)
                                    prime_globale_contrat += int (qte_valide * mt_prime)
                                elif periodicite == 'unique':
                                    prime_payable_contrat += int (mt_prime)
                                    prime_globale_contrat += int (mt_prime)
                        # Si le champ d'application de la prime est l'adherent
                        elif applicable == 'adherent':
                            # Ajout de la prime de l'adhérent
                            if bool (date_fin) and (date_fin > date_fin_prevue):
                                if date_debut > activation_contrat:
                                    nbre_jours_total = (date_fin_prevue - date_debut).days
                                    nbre_jours_payable = (now - date_debut).days
                                elif date_debut <= activation_contrat:
                                    nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                    nbre_jours_payable = (now - activation_contrat).days
                            elif bool (date_fin) and not bool (date_fin_prevue):
                                if date_debut > activation_contrat:
                                    nbre_jours_total = (date_fin - date_debut).days
                                    nbre_jours_payable = (now - date_debut).days
                                elif date_debut <= activation_contrat:
                                    nbre_jours_total = (date_fin - activation_contrat).days
                                    nbre_jours_payable = (now - activation_contrat).days
                            elif not bool (date_fin) and bool (date_fin_prevue):
                                if date_debut > activation_contrat:
                                    nbre_jours_total = (date_fin_prevue - date_debut).days
                                    nbre_jours_payable = (now - date_debut).days
                                elif date_debut <= activation_contrat:
                                    nbre_jours_total = (date_fin_prevue - activation_contrat).days
                                    nbre_jours_payable = (now - activation_contrat).days
                            else:
                                if date_debut > activation_contrat:
                                    nbre_jours_total = (now - date_debut).days
                                    nbre_jours_payable = nbre_jours_total
                                elif date_debut <= activation_contrat:
                                    nbre_jours_total = (now - activation_contrat).days
                                    nbre_jours_payable = nbre_jours_total
                            # Vérification de la périodicité de la prime
                            if periodicite == 'jour':
                                qte_prime = int (nbre_jours_payable)
                                qte_valide = int (nbre_jours_total)
                                prime_payable_contrat += int (qte_prime * mt_prime)
                                prime_globale_contrat += int (qte_valide * mt_prime)
                            elif periodicite == 'semaine':
                                qte_prime = round (nbre_jours_payable / 7) + 1
                                qte_valide = round (nbre_jours_total / 7)
                                prime_payable_contrat += int (qte_prime * mt_prime)
                                prime_globale_contrat += int (qte_valide * mt_prime)
                            elif periodicite == 'mois':
                                qte_prime = round (nbre_jours_payable / 30) + 1
                                qte_valide = round (nbre_jours_total / 30)
                                prime_payable_contrat += int (qte_prime * mt_prime)
                                prime_globale_contrat += int (qte_valide * mt_prime)
                            elif periodicite == 'trimestre':
                                qte_prime = round (nbre_jours_payable / 90) + 1
                                qte_valide = round (nbre_jours_total / 90)
                                prime_payable_contrat += int (qte_prime * mt_prime)
                                prime_globale_contrat += int (qte_valide * mt_prime)
                            elif periodicite == 'annee':
                                qte_prime = round (nbre_jours_payable / 365) + 1
                                qte_valide = round (nbre_jours_total / 365)
                                prime_payable_contrat += int (qte_prime * mt_prime)
                                prime_globale_contrat += int (qte_valide * mt_prime)
                            elif periodicite == 'unique':
                                prime_payable_contrat += int (mt_prime)
                                prime_globale_contrat += int (mt_prime)
                    # on obtinet les totaux primes pour le contrat
                    rec.totaux_net_payable_contrat = prime_payable_contrat
                    rec.totaux_prime_contrat = prime_globale_contrat
                # On obtient les totaux des primes à devoir
                rec.totaux_net_payable = rec.totaux_net_payable_police + rec.totaux_net_payable_contrat
                rec.totaux_prime = rec.totaux_prime_police + rec.totaux_prime_contrat
                rec.mt_reste_payable = rec.totaux_net_payable - totaux_versements
            else:
                pass

    # DETAILS CONTROLES POLICE
    # @api.multi
    # @api.depends('adherent_id')
    # def _check_details_pec(self):
    #     for rec in self:
    #         contrat_id = rec.id
    #         details_pec_contrat = self.env['proximas.details.pec'].search(
    #             [('contrat_id', '=', contrat_id)]
    #         )
    #         nbre_details_pec_contrat = self.env['proximas.details.pec'].search_count(
    #             [
    #                 ('contrat_id', '=', contrat_id),
    #                 ('pool_medical_id', '!=', None),
    #             ]
    #         )
    #         if details_pec_contrat:
    #             rec.nbre_actes_contrat = int(nbre_details_pec_contrat) or 0
    #             rec.sous_totaux_contrat = sum(item.total_pc for item in details_pec_contrat) or 0

    @api.multi
    def toggle_actif(self):
        self.actif = not self.actif

    #@api.multi
    # @api.depends('date_activation', 'date_resiliation', 'delai_carence', 'date_resiliation', 'retard_cotisation',
    #              'groupe_suspendu', 'mt_reste_payable')
    @api.one
    def _get_etat_contrat(self):
        """
        Vérifie l'état du contrat Actif ou non en fonction du délai de carence, date de résiliation ou plafond/famille.
        Return True or False
        """
        now = datetime.now()
        debut = fields.Datetime.from_string(self.date_activation) or \
                fields.Datetime.from_string(fields.Date.today ())
        # 1. Verifier si la date de résiliation est renseignée (contrat résilié)
        if bool(self.date_resiliation):
            resiliation = fields.Datetime.from_string(self.date_resiliation)
            jours = (resiliation - debut).days
            self.jours_contrat = int(jours)
        else:
            jours = (now - debut).days
            self.jours_contrat = int(jours)
        delai = int(self.delai_carence)
        retard_cotisation = int(self.retard_cotisation)
        reste_payable = int(self.mt_reste_payable)
        # Verifie la validité de la date de résiliation
        if 0 < retard_cotisation <= reste_payable:
            self.actif = False
        elif bool(self.date_resiliation) and (self.date_resiliation < now):
            self.actif = False
        # Verifie le délai de carence
        elif delai >= self.jours_contrat:
            self.actif = False
        # Verifie le groupe
        elif bool(self.groupe_id) and bool(self.groupe_suspendu):
            self.is_active = False
        # Verifie le niveau de consommation (Plafond/Famille)
        else:
            self.actif = True

    @api.one
    @api.depends('ayant_droit_ids')
    def _get_nbre_ayant_droit(self):
        compte_conjoint = 0
        compte_enfant = 0
        compte_ascendant = 0
        compte_parent = 0
        if bool(self.ayant_droit_ids):
            for element in self.ayant_droit_ids:
                if element.statut == 'conjoint':
                    compte_conjoint += 1
                elif element.statut == 'enfant':
                    compte_enfant += 1
                elif element.statut == 'ascendant':
                    compte_ascendant += 1
                elif element.statut == 'parent':
                    compte_parent += 1
            self.nbre_conjoint = compte_conjoint
            self.nbre_enfant = compte_enfant
            self.nbre_ascendant = compte_ascendant
            self.nbre_parent = compte_parent

    @api.one
    @api.depends('cotisation_ids')
    def _get_nbre_versement(self):
        # self.ensure_one()
        self.nbre_versmt_cotisation = len(self.cotisation_ids)

    @api.one
    @api.depends('cotisation_ids')
    def _get_totaux_versement(self):
        # self.ensure_one()
        if bool(self.cotisation_ids):
            for cotisation in self.cotisation_ids:
                self.mt_totaux_versmt_cotisation += cotisation.mt_versement
        else:
            self.mt_totaux_versmt_cotisation = 0


    @api.one
    @api.depends('ayant_droit_ids')
    def _get_nbre_conjoint_supp(self):
        # self.ensure_one()
        if self.nbre_conjoint > self.nbre_limite_conjoint > 0:
            self.nbre_conjoint_supp = self.nbre_conjoint - self.nbre_limite_conjoint
        else:
            self.nbre_conjoint_supp = 0

    @api.one
    @api.depends('ayant_droit_ids')
    def _get_nbre_enfant_supp(self):
        # self.ensure_one()
        if self.nbre_enfant > self.nbre_limite_enfant > 0:
            self.nbre_enfant_supp = self.nbre_enfant - self.nbre_limite_enfant
        else:
            self.nbre_enfant_supp = 0

    @api.one
    @api.depends('is_assure', 'adherent_id')# 'police_id'
    def _get_contrat_info(self):
        """Généré un nom  pour contrat"""
        # if bool(self.police_id) and bool(self.id):
        cid = self.id
        pid = self.police_id.id
        if bool(cid) and isinstance(cid, int):
            self.num_contrat = '%02d%04d' % (pid, cid)
        else:
            self.num_contrat = ''

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                 u"%s - %s %s" % (record.num_contrat, record.adherent_id.nom, record.adherent_id.prenoms)
                 ))
        return result

    @api.constrains('ayant_droit_ids')
    def _check_genre(self):
        for record in self:
            if bool(record.controle_genre):
                for conjoint in record.ayant_droit_ids:
                    if conjoint.statut == 'conjoint' and conjoint.genre == record.genre:
                        raise ValidationError(
                            '''
                                 Proximaas - Contrôle des règles de Gestion : Contrôle sur Genre\n
                                 L'adhérent et le Conjoint ne peuvent être du même genre.\n
                                 Vérifiez s'il n'y a pas d'erreur sur le genre ?
                             '''
                        )

    @api.multi
    @api.onchange('adherent_id')
    def _check_adherent_age_limite(self):
        for rec in self:
            age = rec.adherent_id.age
            if int(age) > int(rec.age_limite_adherent) > 0:
                raise ValidationError(_(
                    '''
                         PROXIMAS : VIOLATION DE REGLE DE GESTION:
                         Contrôle des règles de Gestion: Age limite Adhérent.
                    ''' + 'L\'âge de cet adhérent est supérieur à la limite autorisée' + ': ' + age
                    )
                )
                #   self.env["proximas.adherent"].search([('id', '=', rec.adherent_id.id)]).unlink()

    # @api.one
    @api.onchange('ayant_droit_ids')
    def _check_genre_warning(self):
        # self.ensure_one()
        if not bool(self.controle_genre):
            for conjoint in self.ayant_droit_ids:
                if conjoint.statut == 'conjoint' and conjoint.genre == self.genre:
                    raise UserError(_(
                        u"Proximaas: Contrôle de Règle de Gestion.\n \
                        Contrôle du Genre Adhérent(e) et Conjoint(e). L'adhérent et le Conjoint sont du même genre.\
                        Vérifiez bien si c'est cela que vous voulez réellement.Pour plus d'informations,veuillez \
                        contactez l'administrateur..."
                    ))

    @api.constrains('adherent_id')
    def _check_adherent_age_limite(self):
        for rec in self:
            age = int(rec.adherent_id.age)
            if int(age) > int(rec.age_limite_adherent) > 0:
                raise ValidationError(_(
                    u"Proximaas: Contrôle de Règle de Gestion.\n \
                     Contrôle des règles de Gestion: Age limite Adhérent. \
                     L'âge de cet adhérent est supérieur à la limite autorisée, c-à-d: %d an(s).\
                     Pour plus d'informations,veuillez contactez l'administrateur..."
                    ) % age
                )

    @api.constrains('ayant_droit_ids')
    def _check_nbre_conjoint_supp(self):
        for rec in self:
            maxi_conjoint = int(rec.nbre_maxi_conjoint)
            maxi_ascendant = int(rec.nbre_maxi_ascendant)
            maxi_parent = int(rec.nbre_maxi_parent)
            if rec.nbre_conjoint > maxi_conjoint > 0:
                raise ValidationError(_(
                         u"Proximaas: Contrôle de Règle de Gestion.\n \
                          Contrôle Nombre Maxi Conjoint:\n Le nombre maximum de conjoints autorisés est de : %d \
                          alors que le contrat de l\'adhérent en comporte : %d. Pour plus d'informations,\
                          veuillez contactez l'administrateur..."
                    ) % (maxi_conjoint, rec.nbre_conjoint)
                )
            elif rec.nbre_ascendant > maxi_ascendant > 0:
                raise ValidationError(_(
                         u"Proximaas: Contrôle de Règle de Gestion.\n \
                          Contrôle Nombre Maxi Ascendant:\n Le nombre maximum de d'ascendants autorisés est de : %d \
                          alors que le contrat de l\'adhérent en comporte : %d. Pour plus d'informations,\
                          veuillez contactez l'administrateur..."
                    ) % (maxi_ascendant, rec.nbre_ascendant)
                )
            elif rec.nbre_parent > maxi_parent > 0:
                raise ValidationError(_(
                         u"Proximaas: Contrôle de Règle de Gestion.\n \
                          Contrôle Nombre Maxi Parents:\n Le nombre maximum de de parents autorisés est de : %d \
                          alors que le contrat de l\'adhérent en comporte : %d. Pour plus d'informations,\
                          veuillez contactez l'administrateur..."
                    ) % (maxi_parent, rec.nbre_parent)
                )

    @api.constrains('ayant_droit_ids')
    def _check_nbre_enfant_supp(self):
        for rec in self:
            maxi_enfant = rec.nbre_maxi_enfant
            if rec.nbre_enfant > maxi_enfant > 0:
                raise ValidationError(_(

                    u"Proximaas: Contrôle de Règle de Gestion. \n \
                    Contrôle Nombre Maxi Enfant: Le nombre maximum d'enfants autorisé par cette police est de : %d \
                    alors que le contrat de l\'adhérent en comporte : %d. Pour plus d'informations,\
                    veuillez contactez l'administrateur..."
                    ) % (maxi_enfant, rec.nbre_enfant)
                )

    # CONTRAINTES
    _sql_constraints = [
                ('police_adherent_uniq',
                    'UNIQUE (police_id, adherent_id)',
                     '''
                     Risque de doublons Contrat!
                     Il semble que cet enregistrement existe déjà dans la base de données...
                     Vérifiez s'il n'y pas de doublon ou contacter l'administrateur système.

                     ''')
                ]


class ContratWizard(models.TransientModel):
    _name = 'proximas.contrat.wizard'
    _description = 'contrat wizard'

    #name = fields.Char()
    police_id = fields.Many2one(
        comodel_name="proximas.police",
        string="Police Couverture",
        required=True,
    )
    date_activation = fields.Date(
        string="Date Activation Contrat",
        required=True,
    )
    localite_id = fields.Many2one(
        comodel_name="proximas.localite",
        string="Localité",
        required=False,
    )
    groupe_id = fields.Many2one(
        comodel_name="proximas.groupe",
        string="Groupe",
        required=False,
    )
    name = fields.Char(
        string="Nom Complet",
        compute='_get_full_name',
        store=True,
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
    matricule = fields.Char(
        size=32,
        string='N° Matricule',
        help='Numero matricule s\'il y a lieu',
    )
    date_naissance = fields.Date(
        string="Date Naissance",
        required=True,
    )
    age = fields.Char(
        compute='_compute_age',
        default=0,
        readonly=True,
    )
    genre = fields.Selection(
        [
            ('masculin', 'Masculin'),
            ('feminin', 'Feminin'),
        ],
        required=True,
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
    quartier = fields.Char(
        size=64,
        string='Quartier/Secteur',
        help='Indiquer le secteur ou le quartier de résidence',
    )
    age_limite_adherent = fields.Integer(
        string="Age limite police",
        related="police_id.age_limite_adherent",
        readonly=True,
    )

    # @api.multi
    @api.depends('nom', 'prenoms')
    def _get_full_name(self):
        # self.ensure_one()
        self.name = '%s %s' % (self.nom, self.prenoms)

    # @api.multi
    @api.depends('date_naissance')
    @api.onchange('date_naissance')
    def _compute_age(self):
        # self.ensure_one()
        now = fields.Datetime.from_string(fields.Date.today())
        naissance = fields.Datetime.from_string(self.date_naissance) or datetime.now()
        delta = relativedelta(now, naissance)
        self.age = delta.years

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['is_assure'] = True
        if not vals.get('police_id'):
            sequence = self.env['ir.sequence'].next_by_code('proximas.contrat.wizard')
            vals['police_id'] = sequence
        return super(ContratWizard, self).create(vals)

    @api.multi
    def open_contrat_popup(self):
        # the best thing you can calculate the default values
        # however you like then pass them to the context
        #self.ensure_one()
        age_limite = int(self.age_limite_adherent)
        age = int(self.age)

        check_adherent = self.env['proximas.adherent'].search(
            [
                ('nom', 'like', self.nom),
                ('prenoms', 'like', self.prenoms),
                ('matricule', '=', self.matricule),
                ('date_naissance', '=', self.date_naissance)
            ]
        )
        # Prévention de doublon lors de la création de contrat adhérent
        if bool(check_adherent):
            raise UserError(_(
                u"Proximaas: Contrôle de Règle de Gestion: Doublon Adhérent \n \
                 L'adhérent concerné : %s a déjà souscrit pour cette police de couverture : %s an(s). Cependant, \
                 il y a risque de doublon dans le système. Pour plus de détails, veuillez contactez l'administrateur."
                ) % (self.name, self.police_id.name)
            )
        # Vérification de limite d'âge pour la police concernée.
        elif age > age_limite and age_limite != 0:
            raise ValidationError(_(
                u"Proximaas: Contrôle de Règle de Gestion: Age limite Adhérent \n \
                 L'âge limite autorisé par cette police de couverture, est de : %02d an(s). Cependant, Cet(tte) \
                 adhérent(e) en a: %02d. Pour plus de détails, veuillez contactez l'administrateur."
                ) % (age_limite, age)
            )
        else:
            adherent = self.env['proximas.adherent']  # .search([])
            # contrat = self.env['proximas.contrat']
            adherent.create({
                'nom': self.nom,
                'prenoms': self.prenoms,
                'name': '%s %s' % (self.nom, self.prenoms),
                'date_naissance': self.date_naissance,
                'matricule': self.matricule,
                'genre': self.genre,
                'localite_id': self.localite_id.id,
                'groupe_id': self.groupe_id.id,
                'date_activation': self.date_activation,
            }
            )
            # name = '%s %s' % (self.nom, self.prenoms)
            current_adherent = self.env['proximas.adherent'].search(
                [
                    ('nom', 'like', self.nom),
                    ('prenoms', 'like', self.prenoms),
                    ('matricule', '=', self.matricule),
                    ('date_naissance', '=', self.date_naissance)
                ]
            )
            adherent_id = current_adherent.id
            # adherent_id =
            action = {
                'name': 'Création Contrat Adhérent',
                'view_type': 'form',
                'view_mode': 'form',
                # 'target': 'new',
                'res_model': 'proximas.contrat',
                'type': 'ir.actions.act_window',
                # 'domain' : [('id', '=', member_ids)],
                'context': {
                    'default_police_id': self.police_id.id,
                    'default_adherent_id': adherent_id,
                    'default_delai_carence': self.police_id.delai_carence,
                    'default_validite_contrat': self.police_id.validite_contrat,
                    'default_retard_cotisation': self.police_id.retard_cotisation,
                    'default_date_activation': self.date_activation,
                }
            }
            return action


class PoolContratWizard(models.TransientModel):
    _name = 'proximas.pool.contrat.wizard'
    _description = 'pool adherents contrat wizard'

    police_id = fields.Many2one(
        comodel_name="proximas.police",
        string="Police Couverture",
        required=True,
    )
    adherent_ids = fields.Many2many(
        comodel_name="proximas.adherent",
        string="Pool Adhérents",
        required=True,
    )

    @api.multi
    def record_pool(self):
        for wizard in self:
            police = wizard.police_id
            adherents = wizard.adherent_ids
            pool = self.env['proximas.contrat']
            for adherent in adherents:
                pool.create({
                    'police_id': police.id,
                    'adherent_id': adherent.id,
                    'delai_carence': police.delai_carence,
                    'validite_contrat': police.validite_contrat,
                    'retard_cotisation': police.retard_cotisation,
                    'date_activation': adherent.date_activation,
                })


class Cotisation(models.Model):
    _name = 'proximas.cotisation'
    _description = 'cotisation'
    _order = 'date_versement'

    contrat_id = fields.Many2one(
        comodel_name="proximas.contrat",
        string="Contrat",
        ondelete='cascade',
        required=True,
    )
    mt_versement = fields.Float(
        string="Montant Paiement",
        digits=(9,0),
        default=0
    )
    date_versement = fields.Date(
        string="Date Paiement",
        required=True,
    )
    mode_paiement = fields.Selection(
        string="",
        selection=[
            ('espece', 'Espèces'),
            ('cheque', 'Chèque'),
            ('virement', 'Virement'),
            ('autre', 'Autre'),
        ],
        default='espece',
        required=False,
    )
    ref_cheque = fields.Char(
        size=32,
        string='Réf. Chèque /Virement',
        help='Indiquez les références du chèque ou du virement bancaire',
    )
    note = fields.Text(
        string="Notes et Observations",
    )
    # CONTRAINTES
    _sql_constraints = [
        ('contrat__date_versement_unique',
         'UNIQUE (contrat_id, date_versement)',
         '''
         Risque de doublon sur Versement à la même date!
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]


class CodeMedicalPolice(models.Model):
    _name = 'proximas.code.medical.police'
    _description = 'code medical police'

    sequence = fields.Integer(
        string="Sequence"
    )
    police_id = fields.Many2one(
        comodel_name="proximas.police",
        string="Police",
        required=True,
    )
    code_medical_id = fields.Many2one(
        comodel_name="proximas.code.medical",
        string="Code Médical",
        required=True,
    )
    tx_public = fields.Integer(
        string="Taux Public (%)",
        required=True,
        default=0,
    )
    tx_prive = fields.Integer(
        string="Taux Privé (%)",
        required=True,
        default=0,
    )
    tx_remb_couvert = fields.Integer(
        string="Taux Remb. Zone Couverte (%)",
        required=True,
        default=0,
    )
    plafond_individu = fields.Float(
        string="Plafond/individu",
        digits=(9, 0),
        required=True,
        default=0,
    )
    plafond_famille = fields.Float(
        string="Plafond/famille",
        digits=(9, 0),
        required=True,
        default=0,
    )
    mt_plafond = fields.Float(
        string="Mt. Plafond",
        digits=(9, 0),
        required=True,
        default=0,
    )
    # Champs relatif code Medical
    code_medical = fields.Char(
        string="Libellé Code médical",
        related='code_medical_id.libelle',
        readonly=True,
    )
    # Gestion du facteur bloquant du contrôle
    controle_strict = fields.Boolean(
        string="Contrôle Bloquant?",
        help="Cocher pour indiquer le facteur bloquant du contrôle!",
        default=False,
    )
    # Gestion de délai à observer pour bénéficier de la même prestation médicale
    delai_attente = fields.Integer(
        string="Délai d'attente (Nbre. jours)",
        required=True,
        default=0,
        help="Nombre de jours à observer avant de bénéficier du même acte médical"
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
                 u"%s - %s" % (record.police_id.name, record.code_medical_id.name)
                 ))
        return result

    # CONTRAINTES
    @api.constrains('tx_public', 'tx_prive', 'tx_remb_couvert')
    def _check_taux(self):
        if 0 > self.tx_public > 100:
            raise ValidationError(_(
                u"Proximaas : Contrôle de Règles de Gestion.\n \
                Contrôle Taux Couvertue Public:\n \
                Le taux doit obligatoirement être compris entre 0 et 100 maximmum. \
                Pour plus d'informations, veuillez contactez l'administrateur..."
                ))
        if 0 > self.tx_prive > 100:
            raise ValidationError(_(
                u"Proximaas : Contrôle de Règles de Gestion.\n \
                Contrôle Taux Couvertue Privé:\n \
                Le taux doit obligatoirement être compris entre 0 et 100 maximmum. \
                Pour plus d'informations, veuillez contactez l'administrateur..."
                )
            )
        if 0 > self.tx_remb_couvert > 100:
            raise ValidationError(_(

                u"Proximaas : Contrôle de Règles de Gestion.\n \
                Contrôle Taux de Remboursement en Zone Couverte:\n \
                Le taux doit obligatoirement être compris entre 0 et 100 maximmum. \
                Pour plus d'informations, veuillez contactez l'administrateur..."
                )
            )

    _sql_constraints = [
        ('police_code_medical_unique',
         'UNIQUE (police_id, code_medical_id)',
         '''
         Risque de doublon sur Code médical pour la police !
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]


class ControleRubrique(models.Model):
    _name = 'proximas.controle.rubrique'
    _description = 'controle rubrique'

    sequence = fields.Integer(
        string="Sequence"
    )
    police_id = fields.Many2one(
        comodel_name="proximas.police",
        string="Police",
        required=True,
    )
    rubrique_id = fields.Many2one(
        comodel_name="proximas.rubrique.medicale",
        string="Rubrique",
        required=True,
    )
    genre = fields.Selection(
        string="Genre",
        selection=[
            ('masculin', 'Masculin'),
            ('feminin', 'Feminin'),
            ('tous', 'Tous'),
        ],
        required=True,
        default='tous'
    )
    statut_familial = fields.Selection(
        string="Statut Familial",
        selection=[
            ('adherent', 'Adhérent'),
            ('conjoint', 'Conjoint(e)'),
            ('enfant', 'Enfant'),
            ('adherent_conjoint', 'Adhérent/Conjoint'),
            ('aderent_enfant', 'Adhérent/Enfant'),
            ('conjoint_enfant', 'Conjoint/Enfant'),
            ('tous', 'Tous')
        ],
        required=True,
    )
    ticket_exigible = fields.Boolean(
        string="Ticket Exigible?",
        help='Cochez si le ticket modérateur est exigible !',
    )
    nbre_actes_maxi_individu = fields.Integer(
        string="Nbre. Actes maxi/individu",
        required=True,
        default=0,
    )
    nbre_actes_maxi_famille = fields.Integer(
        string="Nbre. Actes maxi/famille",
        required=True,
        default=0,
    )
    plafond_individu = fields.Float(
        string="Plafond/individu",
        digits=(9, 0),
        required=True,
        default=0,
    )
    plafond_famille = fields.Float(
        string="Plafond/famille",
        digits=(9, 0),
        required=True,
        default=0,
    )
    age_limite = fields.Integer(
        string="Age limite",
        required=True,
        default=0,
    )
    delai_carence = fields.Integer(
        string="Délai carence",
        required=True,
        default=0,
    )
    # Gestion de délai à observer pour bénéficier de la même prestation médicale
    delai_attente = fields.Integer(
        string="Délai d'attente (Nbre. jours)",
        required=True,
        default=0,
        help="délai d'attente ==> Nombre de jours à observer entre 2 prestations de la même rubrique médicale"
    )
    controle_strict = fields.Boolean(
        string="Contrôle Bloquant?",
        help="Cocher pour indiquer le facteur bloquant du contrôle!",
        default=False,
    )
    # exclusivite_adherent = fields.Boolean(string="exclusivité Adhérent?",
    # help='Cochez si la rubrique est exclusivement reservé à l'adhérent!' )
    note = fields.Text(
        string="Notes et Observations",
    )
    # Champs relatifs
    rubrique_name = fields.Char(
        string="Libelle Rubrique",
        related='rubrique_id.name',
        readonly=True,
    )
    police_name = fields.Char(
        string="Libelle Police",
        related='police_id.name',
        readonly=True,
    )


    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                 u"%s - %s" % (record.police_name, record.rubrique_name)
                 ))
        return result
    # CONTRAINTES
    _sql_constraints = [
        ('police_rubrique_unique',
         'UNIQUE (police_id, rubrique_id)',
         '''
         Risque de doublon sur Rubrique médicale pour la police !
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]


class ControleAntecedent(models.Model):
    _name = 'proximas.controle.antecedent'
    _description = 'controle antecedent'

    sequence = fields.Integer(
        string="Sequence"
    )
    police_id = fields.Many2one(
        comodel_name="proximas.police",
        string="Police",
        required=True,
    )
    pathologie_id = fields.Many2one(
        comodel_name="proximas.pathologie",
        string="Code Affection",
        required=True,
    )
    pathologie = fields.Char(
        string="Affection",
        related='pathologie_id.libelle',
        readonly=True,
    )
    controle_strict = fields.Boolean(
        string="Contrôle Bloquant?",
        help="Cocher pour indiquer le facteur bloquant du contrôle!",
        default=False,
    )
    plafond_individu = fields.Float(
        string="Mt. Plafond/individu",
        digits=(9, 0),
        required=True,
        default=0
    )
    plafond_famille = fields.Float(
        string="Mt. Plafond/Famille",
        digits=(9, 0),
        required=True,
        default=0
    )
    nbre_pec = fields.Integer(
        string="Nbre. Limite PEC",
        required=True,
        default=0,
        help="Nombre limite de prise en charge autorisées"
    )
    # Gestion de délai à observer avant de bénéficier d'une prestation médicale pour une même pathologie
    delai_attente = fields.Integer(
        string="Délai d'attente (Nbre. jours)",
        required=True,
        default=0,
        help="Nombre de jours à observer avant de faire l'objet d'une prise en charge concernant la pathologie."
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
                 u"%s - %s" % (record.police_id.name, record.pathologie_id.libelle)
                 ))
        return result

    # CONTRAINTES
    _sql_constraints = [
        ('police_code_pathologie_unique',
         'UNIQUE(police_id, pathologie_id)',
         '''
         Risque de doublon sur Pathologie (Affection) pour la police !
         Il semble que cet enregistrement existe déjà dans la base de données...
         Vérifiez s'il n'y pas de doublon ou contactez l'administrateur.
         '''
         )
    ]