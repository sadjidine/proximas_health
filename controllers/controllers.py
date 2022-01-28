# -*- coding: utf-8 -*-
# Copyright 2017 Cabinet SIGEM
# Auteur : Salifou OMBOTIMBE
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


import openerp.http as http
from openerp.http import request
import logging
from openerp import api, fields
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
import json
import sys
from datetime import datetime
from twilio.twiml.messaging_response import MessagingResponse


_logger = logging.getLogger(__name__)


class Controller(http.Controller):
    """
        SMS - API - Proximaas
        Traitement & exécution des requêtes envoyé par SMS via la passerelle (gateway)
        1. Récuprer le contenu du message sms reçu par le gateway et rédirigé à cette URL,
        2. Découpage du contenu de sms pour en extraire les variables,
        3. Elaborer les requêtes à rediriger vers la base de données ,
        4. Renvoyer la réponse par SMS après traitement...
    """

    @http.route('/api/sms', type='http', auth="public", methods=['GET', 'POST'], csrf=False, website=True)
    def incoming_sms(self, **kwargs):
        values = dict(kwargs)
        # Start our TwiML response
        response = MessagingResponse()
        
        if bool(values):
            """ 2-way-sms Parameters"""
            # SmsSid = values['SmsSid']
            sms_from = values['From']
            #from_list = sms_from.split()
            # sms_sender = from_list[0].strip()
            sms_sender = sms_from[1:]
            # To = values['To']
            # FromCountry = values['FromCountry']
            # ToCountry = values['ToCountry']
            sms_body = values['Body'].strip() or ''
            """Respond to incoming calls with a simple text message."""
            sms_body_list = sms_body.split('*')

            # Vérifier le contenu de SMS : Récupérer la syntaxe envoyée
            if len(sms_body_list) == 1:
                """ Si le la syntaxe est composée d'un seul (1) élément, 
                alors vérification de l'identifiant de l'assuré """
                sms_code_id = sms_body_list[0].strip().upper()
                assure = request.env['proximas.assure'].sudo().search(
                    [
                        '|',
                        ('code_id', '=', sms_code_id),
                        ('code_id_externe', '=', sms_code_id),
                    ])
                if bool(assure):
                    """ Si l'assuré existe en BD, alors renvoyé ses identifiants en réponse. """
                    # values['assure'] = assure
                    date_naissance = assure.date_naissance
                    date_naiss_list = date_naissance.split()
                    date_naiss_list_date_part = date_naiss_list[0]
                    date_day = date_naiss_list_date_part[8:]
                    date_month = date_naiss_list_date_part[5:7]
                    date_year = date_naiss_list_date_part[:4]
                    date_naiss_format = date_day + '-' + date_month + '-' + date_year
                    # Add a message
                    resp_body = _(u"Proximaas : Consultation Dossier Assuré:\nSAM: %s,\nCode ID: %s.\nI\
                    dentité: %s.\nNé(e) le: %s.\nGenre: %s.\nParenté: %s.\nStatut: %s.\n\
                    Infoline: +22522428282 - SIGEM." % (assure.structure_id.name, assure.code_id, assure.name,
                                                        date_naiss_format, assure.genre, assure.statut_familial, 
                                                        assure.state))
                    
                    response.message(resp_body)
                    # return str(response)
                else:
                    """ Dans le cas contraire, renvoyer un message """
                    # Add a message
                    resp_body = _(u"Proximaas: Echec ! Problème d'identification de l'assuré dans le système.\n\
                    Veuillez vérifier si vous avez fourni un code ID. valide.")
                    response.message(resp_body)
                    # return str (resp)
                #return str(response)
            # elif 1 < len(sms_body_list) < 4:
            #     """ Si le nombre d'éléments envoyé est supérieur à 1 et inférieur à 4, dans ce cas il y a erreur
            #     de syntaxe"""
            #     resp_body = _(u"Proximaas: Syntaxe incorrecte.\n\
            #     Veuillez vous référer au guide SMS.")
            #     response.message(resp_body)
                #return str(resp)
            elif len(sms_body_list) == 4:
                """ Si le nombre d'éléments envoyés est égal à 4, la syntaxe est juste, alors, traiter la requête. """
                values_length = len(sms_body_list)
                code_sms = sms_body_list[0].strip().upper()
                code_prestation = sms_body_list[1].strip().upper()
                code_affection = sms_body_list[2].strip().upper()
                code_workflow = sms_body_list[3].strip().upper()
                #code_prestation = ''
                # 1. Vérification de l'émetteur de la requête
                # response.message(u"Proximaas : %s - %s - %s - %s - %s" % (code_sms, prestation, affection, workflow, from_sms))
                # return str(resp)
                sms_user = request.env['proximas.sms.user'].sudo().search([('mobile', '=', sms_sender)])
                # response.message(u"Proximaas : %s - %s = %s" % (sms_user.name, sms_user.mobile, sms_sender))
                # return str(resp)
                # if bool(prestation) and str(prestation) == 'C':
                #     code_prestation = 'CMED'
                # if bool(prestation) and str(prestation) == 'G':
                #     code_prestation = 'CGEN'
                # if bool(prestation) and str(prestation) == 'S':
                #     code_prestation = 'CSP'
                if bool(sms_user):

                    assure = request.env['proximas.assure'].sudo().search([
                                                                '|',
                                                                ('code_id', '=', code_sms),
                                                                ('code_id_externe', '=', code_sms)
                                                        ])
                    nbre_assure = len(assure)
                    code_affection = request.env['proximas.pathologie'].sudo().search([('name', '=', code_affection)])
                    nbre_affection = len(code_affection)
                    if not bool(assure) or nbre_assure > 1 or not bool(assure.police_id):
                        resp_body = _(u"Proximaas: Désolé ! Problème d'identification de l'assuré dans le système.\n\
                        Veuillez vérifier si vous avez fourni un code ID. valide.\nInfoline: +22522428282 - SIGEM.")
                        response.message(resp_body)
                        #return str(resp)
                    elif assure.state != 'actif':
                        resp_body = _(u"Proximaas: Désolé ! L'assuré(e) : %s - %s, est bel et bien identifié mais \
                        ne peut faire l'objet de prise en charge. Etat assuré : %s.\nInfoline: +22522428282 - SIGEM."
                                      % (code_sms, assure.name, assure.state))
                        response.message(resp_body)
                        #return str(resp)
                    elif str(code_prestation) not in ['G', 'C', 'S']:
                        resp_body = _(u"Proximaas: Désolé ! Le code fourni pour la Prestation est incorrect...!\n\
                        Le code doit être : G = Consultation Généraliste  - S = Consultation Spécialiste - \
                        C = Contrôle médical.\nInfoline: +22522428282 - SIGEM.")
                        response.message(resp_body)
                        #return str(resp)
                    elif not bool(code_affection) or nbre_affection > 1:
                        resp_body = _(u"Proximaas: Désolé ! Le code fourni pour l'Affection est incorrect.\n\
                        Infoline: +22522428282 - SIGEM.")
                        response.message(resp_body)
                        #return str(resp)
                    elif str(code_workflow) not in ['D', 'O', 'T']:
                        resp_body = _(u"Proximaas: Désolé ! Le code fourni pour le workflow est incorrect...!\n\
                        Le code exact est : D = Dispensation, O = Orientation ou T = Terminer.\n\
                        Infoline: +22522428282 - SIGEM.")
                        response.message(resp_body)
                        #return str(resp)
                    else:
                        """ Script de création de la prise en charge et la prestation offerte par le CRO """
                        try:
                            code_saisi = code_sms
                            code_id = assure.code_id
                            assure_id = assure.id
                            # contrat_id = assure.contrat_id
                            # sms_sender_id = request.env['proximas.sms.user'].sudo().search([('mobile', '=', sms_sender)])
                            prestataire = sms_user.prestataire_id
                            pool_medical = sms_user.pool_medical_id
                            prestation = request.env['proximas.prestation'].sudo ().search([
                                ('code', '=', code_prestation)])

                            if bool(prestataire) and bool(pool_medical) and bool(prestation):
                                # exercice = request.env['proximas.exercice'].sudo().search([
                                #     ('en_cours', '=', True),
                                #     ('cloture', '=', False),
                                # ])
                                # exercice_id = exercice[0].id
                                # CONDITION TRY
                                prestataire_id = prestataire.id
                                prestation_id = prestation.id
                                pool_medical_id = pool_medical.id
                                prise_charge = request.env['proximas.prise.charge']
                                details_pec = request.env['proximas.details.pec']
                                pec = prise_charge.sudo ().create({
                                    'code_saisi': code_saisi,
                                    'code_id': code_id,
                                    'assure_id': assure_id,
                                    # 'pathologie_ids': [code_affection.id,],
                                    'prestataire_id': prestataire_id,
                                    'pool_medical_id': pool_medical_id,
                                })
                                code_pec = pec.code_pec
                                # structure_id = pec.structure_id.id
                                ligne_pec = details_pec.sudo().create({
                                    'pec_id': pec.id,
                                    'date_execution': fields.Date.today(),
                                    'prestation_cro_id': prestation_id,
                                    'pool_medical_id': pool_medical_id,
                                })
                                pec_code = pec.code_pec
                                pec_date = pec.date_saisie
                                date_list = pec_date.split()
                                date_list_date_part = date_list[0]
                                date_list_hour_part = date_list[1]
                                date_day = date_list_date_part[8:]
                                date_month = date_list_date_part[5:7]
                                date_year = date_list_date_part[:4]
                                date_format = date_day + '-' + date_month + '-' + date_year + ' ' + date_list_hour_part
                                # pec_date_fr = date_format.strftime('%d-%m-%Y à: H:M:S')
                                pec_id = request.env['proximas.prise.charge'].sudo().search([
                                    ('id', '=', pec.id)])
                                pec_id.pathologie_ids = [code_affection.id, ]
                                pec_ticket_mod_cro = ligne_pec.ticket_moderateur
                                pec_totaux_cro = ligne_pec.total_pc
                                pec_id.mt_encaisse_cro = pec_ticket_mod_cro
                                if code_workflow == 'D':
                                    pec.state = 'dispense'
                                elif code_workflow == 'O':
                                    pec.state = 'oriente'
                                elif code_workflow == 'T':
                                    pec.state = 'termine'
                                else:
                                    pec.state = 'cours'
                            else:
                                resp_body = _(u"Proximaas: Echec ! Un problème lié soit au prestataire ou à la \
                                prestation a interrompu le processus de création de la prise en charge.\n\
                                Infoline: +22522428282 - SIGEM.")
                                response.message(resp_body)
                                #return str(resp)
                        except ValidationError as ValidErr:
                            resp_body = _(u"Proximaas: Echec ! Un problème lié soit a l'assuré et/ou à la prestation, \
                            a interrompu le processus de création del la prise en charge.\n\
                            Infoline: +22522428282 - SIGEM.")
                            response.message(resp_body)
                            #return str(resp)
                        else:
                            # Envoi des infos réponse - SMS
                            resp_body = _(u"Proximaas * PEC N°: %s.\nCode ID.: %s.\nAssuré: %s.\nDate: %s\nEts. \
                            CRO: %s.\nPrestation: %s.\nTotaux: %d Fcfa.\nTicket modérateur: %d Fcfa.\n\
                            Statut: PEC créée avec succès.\nInfoline: +22522428282 - SIGEM."
                                          % (code_pec, code_sms, assure.name, date_format, prestataire.name,
                                             prestation.name, pec_totaux_cro,
                                             pec_ticket_mod_cro))
                            response.message(resp_body)
                            #return str(resp)
            else:
                resp_body = _(u"Proximaas: Syntaxe incorrecte.\nVeuillez vous référer au guide SMS.")
                response.message(resp_body)
                return str(resp)
        else:
            pass
            # resp = MessagingResponse()
            # response.message(u"Proximaas: Bienvenue sur notre API 2-way-sms...!\n\
            # Infoline: +22522428282 - SIGEM.")
            # return str(resp)
        #############################################################################################################
        # """Respond to incoming messages with a friendly SMS."""
        # # Start our response
        # resp = MessagingResponse()
        # # body = values['Body'] or ''
        #
        # # Add a message
        # response.message("Proximaas: Thanks so much for your message.")
        #
        # return str(resp)
        # return "<h1> Proximaas / Greetings....</h1>"
        # return request.render('proximas_medical.twiml_template', values)


    # @http.route('/web/sms_api', type='http', auth='public', methods=['GET', 'POST'], website=True)
    # def sms_hook_reply(self):
    #     """Respond to incoming messages with a friendly SMS."""
    #     # Start our response
    #     resp = MessagingResponse()
    #
    #     # Add a message
    #     response.message("Proximaas: Thanks so much for your message.")
    #
    #     return str(resp)
    #
    #
    #
    # @http.route('/web/sms', type='http', auth="none", methods=['GET', 'POST'], website=True)
    # def sms_reply(self, **kwargs):
    #     # Your Account Sid and Auth Token from twilio.com/console
    #     account_sid = 'ACc52945a1e999f9e5b63eb05d483ba400'
    #     auth_token = '9f7a5b162136423471faac1fd6040f0c'
    #     client = Client(account_sid, auth_token)
    #
    #     values = dict(kwargs)
    #     if bool(values):
    #         """ 2-way-sms Parameters"""
    #         # SmsSid = values['SmsSid']
    #         From = values['From']
    #         To = values['To']
    #         # FromCountry = values['FromCountry']
    #         # ToCountry = values['ToCountry']
    #         Body = values['Body'].strip () or ''
    #         """Respond to incoming calls with a simple text message."""
    #         # Start our TwiML response
    #         resp = MessagingResponse()
    #         resp_body = ''
    #         sms_body_list = Body.split('*')
    #         if len(sms_body_list) == 1:
    #             code_sms = sms_body_list[0].strip().upper()
    #             assure = request.env['proximas.assure'].sudo().search(['|',
    #                                                                    ('code_id', '=', code_sms),
    #                                                                    ('code_id_externe', '=', code_sms)]
    #                                                                   )
    #             if bool(assure):
    #                 values['assure'] = assure
    #                 # Add a message
    #                 resp_body = _(u"Assuré : %s * Code ID: %s * Statut: %s - Etat: %s" % (assure.name, assure.code_id,
    #                                                                                       assure.statut_familial,
    #                                                                                       assure.state))
    #                 response.message(resp_body)
    #             else:
    #                 # Add a message
    #                 resp_body = _(u"Désolé ! L'assuré n'est pas identifié dans le système...!")
    #                 response.message(resp_body)
    #         elif len(sms_body_list) > 1:
    #             values_length = len(sms_body_list)
    #             code_sms = sms_body_list[0].strip().upper()
    #             prestation = sms_body_list[1].strip().upper()
    #             code_affection = sms_body_list[2].strip().upper()
    #             sms_sender = values['From'] or ''
    #
    #         client.messages.create(
    #             from_=To,
    #             body=resp_body,
    #             status_callback='https://proximaas.net/sms/',
    #             to='+' + From,
    #         )
    #
    #         return str(resp)
    #     else:
    #         resp = MessagingResponse()
    #         response.message(u"Proximaas: Bienvenue sur l'API 2-way-sms...!")
    #         return str(resp)

        # message = client.messages.create(
        #     from_='+17058053670',
        #     body='Proximaas - SMS : Ceci est un réponse de Test ',
        #     to='+22507828859'
        # )
        #
        # print(message.sid)


    # @http.route(['/sms_api/'], type='http', auth="none", methods=['GET', 'POST'], website=True)
    # def view(self, **kwargs):
    #     values = dict(kwargs)
    #     # object_ids = request.env['proximas.assure'].sudo().search([('code_id', '=', values['code_id'])])
    #     # values['object_ids'] = object_ids
    #     # values['assure'] = object_ids[0].name
    #     # return request.render('proximas_medical.assure_view_template', values)
    #     message = values['msg'].strip() or ''
    #     msg_values = message.split('*')
    #     if len(msg_values) == 1:
    #         code_id = msg_values[0].strip().upper()
    #         assure = request.env['proximas.assure'].sudo().search([('code_id', '=', code_id)])
    #         values['assure'] = assure
    #         # values['assure'] = assure[0].name
    #         return request.render('proximas_medical.assure_view_template', values)
    #     elif len(msg_values) > 1:
    #         values_length = len(msg_values)
    #         code_id = msg_values[0].strip().upper()
    #         prestation = msg_values[1].strip().upper()
    #         code_affection = msg_values[2].strip().upper()
    #         sms_sender = values['from'] or ''


    ###################################################################################################################
    # CLICKATELL - API HTTP Callback Parameters:
    #8-------------------------------------------------------
    # 1. integrationName :   Name of your integration
    # 2. messageId       :   ID of original message to which reply was sent
    # 3. replyMessageId  :   ID of the reply message
    # 4. fromNumber      :   The number from which we received the reply
    # 5. toNumber        :   The number to which reply was sent
    # 6. timestamp       :   Timestamp for when we received the reply message
    # 7. text            :   Content of the reply message
    # 8. charset         :   Character set of the reply message
    # 9. udh             :   UDH (User data header) content of the message
    # 10. network        :   Network ID keyword Keyword
    ###################################################################################################################
    # @http.route('/proximaas/assure', type='http', auth='none')
    # def assure(self):
    #     records = request.env['proximas.assure'].sudo().search([])
    #     result = '<html><body><table><tr><td>'
    #     result += '</td></tr><tr><td>'.join(
    #     records.mapped('name'))
    #     result += '</td></tr></table></body></html>'
    #     return result
    #
    # @http.route('/proximaas/details_assure', type='http', auth='none')
    # def details_assure(self, assure_id):
    #     record = request.env['proximas.assure'].sudo().search([('id', '=', int(assure_id))])
    #     return u'<html><body><h1>Assuré : %s</h1>Statut : %s' % (record.name, record.state)
    #
    # @http.route("/proximaas/details_assure/<model('proximas.assure'):assure>", type='http', auth='none')
    # def details_assure_in_path(self, assure):
    #     return self.details_assure(assure.id)






#####################################################################################################################
# class ProximasMedical(http.Controller):
#     @http.route('/proximas_medical/proximas_medical/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/proximas_medical/proximas_medical/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('proximas_medical.listing', {
#             'root': '/proximas_medical/proximas_medical',
#             'objects': http.request.env['proximas_medical.proximas_medical'].search([]),
#         })

#     @http.route('/proximas_medical/proximas_medical/objects/<model("proximas_medical.proximas_medical"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('proximas_medical.object', {
#             'object': obj
#         })