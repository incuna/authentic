import datetime, time
import logging

import lasso

from django.conf import settings
from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import *
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth import get_user
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from authentic2.saml.common import *
from authentic2.saml.models import *
from authentic2.authsaml2.utils import *
from authentic2.authsaml2 import signals
from authentic2.authsaml2.models import *
from backends import AuthSAML2PersistentBackend, \
        AuthSAML2TransientBackend
from authentic2.utils import cache_and_validate

__logout_redirection_timeout = getattr(settings, 'IDP_LOGOUT_TIMEOUT', 600)

'''SAMLv2 SP implementation'''

logger = logging.getLogger('authentic2.authsaml2')

metadata_map = (
    ('AssertionConsumerService',
            lasso.SAML2_METADATA_BINDING_ARTIFACT ,
            '/singleSignOnArtifact'),
    ('AssertionConsumerService',
            lasso.SAML2_METADATA_BINDING_POST ,
            '/singleSignOnPost'),
    ('SingleLogoutService',
            lasso.SAML2_METADATA_BINDING_REDIRECT ,
            '/singleLogout', '/singleLogoutReturn'),
    ('SingleLogoutService',
            lasso.SAML2_METADATA_BINDING_SOAP ,
            '/singleLogoutSOAP'),
    ('ManageNameIDService',
            lasso.SAML2_METADATA_BINDING_SOAP ,
            '/manageNameIdSOAP'),
    ('ManageNameIDService',
            lasso.SAML2_METADATA_BINDING_REDIRECT ,
            '/manageNameId', '/manageNameIdReturn'),
)
metadata_options = { 'key': settings.SAML_SIGNATURE_PUBLIC_KEY }

@cache_and_validate(settings.LOCAL_METADATA_CACHE_TIMEOUT)
def metadata(request):
    '''Endpoint to retrieve the metadata file'''
    logger.info('metadata: return metadata')
    return HttpResponse(get_metadata(request, request.path),
            mimetype='text/xml')

###
 # sso
 # @request
 # @entity_id: Provider ID to request
 #
 # Single SignOn request initiated from SP UI
 # Binding supported: Redirect
 ###
def sso(request, is_passive=None, force_authn=None, http_method=None):
    '''Django view initiating an AuthnRequesst toward an identity provider.

       Keyword arguments:
       entity_id -- the SAMLv2 entity id identifier targeted by the
       AuthnRequest, it should be resolvable to a metadata document.
       is_passive -- whether to let the identity provider passively, i.e.
       without user interaction, authenticate the user.
       force_authn -- whether to ask the identity provider to authenticate the
       user even if it is already authenticated.
    '''
    entity_id = request.REQUEST.get('entity_id')
    s = get_service_provider_settings()
    if not s:
        return error_page(request,
            _('sso: Service provider not configured'), logger=logger)
    # 1. Save the target page
    logger.info('sso: save next url in session %s' \
        % request.session.session_key)
    register_next_target(request)

    # 2. Init the server object
    server = build_service_provider(request)
    if not server:
        return error_page(request,
            _('sso: Service provider not configured'), logger=logger)
    # 3. Define the provider or ask the user
    if not entity_id:
        providers_list = get_idp_list()
        if not providers_list:
            return error_page(request,
                 _('sso: Service provider not configured'), logger=logger)
        if providers_list.count() == 1:
            p = providers_list[0]
        else:
            logger.debug('sso: \
                No SAML2 identity provider selected')
            context['message'] = _('No SAML2 identity provider selected')
            context['redir_timeout'] = __logout_redirection_timeout
            template = 'auth/saml2/logout.html'
            if not s.back_url:
                context[REDIRECT_FIELD_NAME] = '/'
            else:
                context[REDIRECT_FIELD_NAME] = s.back_url
            return render_to_response(template, context_instance = context)
    else:
        logger.info('sso: sso with provider %s' % entity_id)
        p = load_provider(request, entity_id, server=server, sp_or_idp='idp',
                autoload=True)
        if not p:
            return error_page(request,
                _('sso: The provider does not exist'), logger=logger)
    # 4. Build authn request
    login = lasso.Login(server)
    if not login:
        return error_page(request,
            _('sso: Unable to create Login object'), logger=logger)
    # Only redirect is necessary for the authnrequest
    if not http_method:
        http_method = server.getFirstHttpMethod(server.providers[p.entity_id],
                lasso.MD_PROTOCOL_TYPE_SINGLE_SIGN_ON)
        logger.debug('sso: \
            No http method given. Method infered: %s' % http_method)
    if http_method == lasso.HTTP_METHOD_NONE:
        return error_page(request,
            _('sso: %s does not have any supported SingleSignOn endpoint') \
            %entity_id, logger=logger)
    try:
        login.initAuthnRequest(p.entity_id, http_method)
    except lasso.Error, error:
        return error_page(request,
            _('sso: initAuthnRequest %s') %lasso.strError(error[0]),
            logger=logger)

    # 5. Request setting
    setAuthnrequestOptions(p, login, force_authn, is_passive)
    try:
        login.buildAuthnRequestMsg()
    except lasso.Error, error:
        return error_page(request,
            _('SSO: buildAuthnRequestMsg %s') %lasso.strError(error[0]),
            logger=logger)

    # 6. Save the request ID (association with the target page)
    logger.debug('sso: Authnrequest ID: %s' % login.request.iD)
    logger.debug('sso: Save request id in the session %s' \
        % request.session.session_key)
    register_request_id(request, login.request.iD)

    # 7. Redirect the user
    logger.debug('sso: user redirection')
    return return_saml2_request(request, login,
            title=('AuthnRequest for %s' % entity_id))

###
 # singleSignOnArtifact, singleSignOnPostOrRedirect
 # @request
 #
 # Single SignOn Response
 # Binding supported: Artifact, POST
 ###
def singleSignOnArtifact(request):
    logger.info('singleSignOnArtifact: Binding Artifact processing begins...')
    server = build_service_provider(request)
    if not server:
        return error_page(request,
            _('singleSignOnArtifact: Service provider not configured'), logger=logger)

    # Load the provider metadata using the artifact
    if request.method == 'GET':
        logger.debug('singleSignOnArtifact: GET')
        artifact = request.REQUEST.get('SAMLart')
    else:
        logger.debug('singleSignOnArtifact: POST')
        artifact = request.POST.get('SAMLart')
    logger.debug('singleSignOnArtifact: artifact %s' % artifact)
    p = LibertyProvider.get_provider_by_samlv2_artifact(artifact)
    p = load_provider(request, p.entity_id, server=server, sp_or_idp='idp')
    logger.info('singleSignOnArtifact: provider %s loaded' % p.entity_id)

    login = lasso.Login(server)
    if not login:
        return error_page(request,
            _('singleSignOnArtifact: Unable to create Login object'), logger=logger)

    message = get_saml2_request_message(request)
    if not message:
        return error_page(request,
            _('singleSignOnArtifact: No message given.'), logger=logger)
    #logger.debug('singleSignOnArtifact: message %s' % message)

    while True:
        logger.debug('singleSignOnArtifact: Authnresponse processing')
        try:
            if request.method == 'GET':
                login.initRequest(get_saml2_query_request(request),
                        lasso.HTTP_METHOD_ARTIFACT_GET)
            else:
                login.initRequest(artifact, lasso.HTTP_METHOD_ARTIFACT_POST)
            break
        except (lasso.ServerProviderNotFoundError,
                lasso.ProfileUnknownProviderError):
            logger.debug('singleSignOnArtifact: Unable to process Authnresponse - \
                load another provider')
            provider_id = login.remoteProviderId
            provider_loaded = load_provider(request, provider_id,
                    server=server, sp_or_idp='idp')

            if not provider_loaded:
                message = _('singleSignOnArtifact: provider %r unknown') % provider_id
                return error_page(request, message, logger=logger)
            else:
                logger.info('singleSignOnArtifact: \
                    provider %s loaded' % provider_id)
                continue
        except lasso.Error, error:
            return error_page(request,
                _('singleSignOnArtifact: initRequest %s') %lasso.strError(error[0]),
                logger=logger)

    try:
        login.buildRequestMsg()
    except lasso.Error, error:
        return error_page(request,
            _('singleSignOnArtifact: buildRequestMsg %s') %lasso.strError(error[0]),
            logger=logger)

    # TODO: Client certificate
    client_cert = None
    try:
        logger.info('singleSignOnArtifact: soap call to %s' % login.msgUrl)
        logger.debug('singleSignOnArtifact: soap message %s' % login.msgBody)
        soap_answer = soap_call(login.msgUrl,
            login.msgBody, client_cert = client_cert)
    except Exception, e:
        return error_page(request,
            _('singleSignOnArtifact: Failure to communicate \
            with artifact resolver %r') % login.msgUrl,
            logger=logger)
    if not soap_answer:
        return error_page(request,
            _('singleSignOnArtifact: Artifact resolver at %r returned \
            an empty response') % login.msgUrl,
            logger=logger)

    logger.debug('singleSignOnArtifact: soap answer %s' % soap_answer)

    # If connexion over HTTPS, do not check signature?!
    if login.msgUrl.startswith('https'):
        logger.debug('singleSignOnArtifact: \
            artifact solved over HTTPS - Signature Hint forbidden')
        login.setSignatureVerifyHint(lasso.PROFILE_SIGNATURE_HINT_FORBID)

    try:
        login.processResponseMsg(soap_answer)
    except lasso.Error, error:
        return error_page(request,
            _('singleSignOnArtifact: processResponseMsg raised %s') \
            %lasso.strError(error[0]), logger=logger)

    # TODO: Relay State

    logger.info('singleSignOnArtifact: Binding artifact treatment terminated')
    return sso_after_response(request, login, provider=p)

@csrf_exempt
def singleSignOnPost(request):
    logger.info('singleSignOnPost: Binding POST processing begins...')
    server = build_service_provider(request)
    if not server:
        return error_page(request,
            _('singleSignOnPost: Service provider not configured'),
            logger=logger)

    login = lasso.Login(server)
    if not login:
        return error_page(request,
            _('singleSignOnPost: Unable to create Login object'),
            logger=logger)

    # TODO: check messages = get_saml2_request_message(request)

    # Binding POST
    message = get_saml2_post_response(request)
    if not message:
        return error_page(request,
            _('singleSignOnPost: No message given.'), logger=logger)
    logger.debug('singleSignOnPost: message %s' % message)

    ''' Binding REDIRECT

        According to: saml-profiles-2.0-os
        The HTTP Redirect binding MUST NOT be used,
        as the response will typically exceed the
        URL length permitted by most user agents.
    '''
    # if not message:
    #    message = request.META.get('QUERY_STRING', '')

    while True:
        logger.debug('singleSignOnPost: Authnresponse processing')
        try:
            login.processAuthnResponseMsg(message)
            break
        except (lasso.ServerProviderNotFoundError,
                lasso.ProfileUnknownProviderError):
            logger.debug('singleSignOnPost: \
                Unable to process Authnresponse - load another provider')
            provider_id = login.remoteProviderId
            provider_loaded = load_provider(request, provider_id,
                    server=server, sp_or_idp='idp', autoload=True)

            if not provider_loaded:
                message = _('singleSignOnPost: provider %r unknown' \
                    %provider_id)
                return error_page(request, message, logger=logger)
            else:
                logger.info('singleSignOnPost: \
                    provider %s loaded' % provider_id)
                continue
        except lasso.Error, error:
            logger.debug('singleSignOnPost: lasso error, login dump is %s' \
                % login.dump())
            return error_page(request,
                _('singleSignOnPost: %s') %lasso.strError(error[0]),
                logger=logger)

    logger.info('singleSignOnPost: Binding POST treatment terminated')
    return sso_after_response(request, login, provider=provider_loaded)

###
 # sso_after_response
 # @request
 # @login
 # @relay_state
 #
 # Post-authnrequest processing
 ###
def sso_after_response(request, login, relay_state = None, provider=None):

    logger.info('sso_after_response: Authnresponse processing begins...')
    s = get_service_provider_settings()
    if not s:
        return error_page(request,
            _('sso_after_response: Service provider not configured'),
            logger=logger)

    # If there is no inResponseTo: IDP initiated
    # else, check that the response id is the same
    irt = None
    try:
        irt = login.response.assertion[0].subject. \
            subjectConfirmation.subjectConfirmationData.inResponseTo
    except:
        return error_page(request,
            _('sso_after_response: No Response ID'), logger=logger)
    logger.debug('sso_after_response: inResponseTo: %s' %irt)

    if irt and not check_response_id(request, login):
        return error_page(request,
            _('sso_after_response: Request and Response ID do not match'),
            logger=logger)
    logger.debug('sso_after_response: ID checked')

    logger.info('sso_after_response: Authnresponse processing terminated')
    logger.info('sso_after_response: Assertion processing begins...')

    #TODO: Register assertion and check for replay
    # Add LibertyAssertion()
    assertion = login.response.assertion[0]
    if not assertion:
        return error_page(request,
            _('sso_after_response: Assertion missing'), logger=logger)
    logger.debug('sso_after_response: assertion %s' % assertion.dump())

    # Check: Check that the url is the same as in the assertion
    try:
        if assertion.subject. \
                subjectConfirmation.subjectConfirmationData.recipient != \
                request.build_absolute_uri().partition('?')[0]:
            return error_page(request,
                _('sso_after_response: SubjectConfirmation \
                Recipient Mismatch'),
                logger=logger)
    except:
        return error_page(request,
            _('sso_after_response: Errot checking \
            SubjectConfirmation Recipient'),
            logger=logger)
    logger.debug('sso_after_response: \
        the url is the same as in the assertion')

    # Check: SubjectConfirmation
    try:
        if assertion.subject.subjectConfirmation.method != \
                'urn:oasis:names:tc:SAML:2.0:cm:bearer':
            return error_page(request,
                _('sso_after_response: Unknown \
                SubjectConfirmation Method'),
                logger=logger)
    except:
        return error_page(request,
            _('sso_after_response: Error checking \
            SubjectConfirmation Method'),
            logger=logger)
    logger.debug('sso_after_response: subjectConfirmation method known')


    # Check: AudienceRestriction
    try:
        audience_ok = False
        for audience_restriction in assertion.conditions.audienceRestriction:
            if audience_restriction.audience != login.server.providerId:
                return error_page(request,
                    _('sso_after_response: \
                    Incorrect AudienceRestriction'),
                    logger=logger)
            audience_ok = True
        if not audience_ok:
            return error_page(request,
                _('sso_after_response: \
                Incorrect AudienceRestriction'),
                logger=logger)
    except:
        return error_page(request,
            _('sso_after_response: Error checking AudienceRestriction'),
            logger=logger)
    logger.debug('sso_after_response: audience restriction repected')

    # Check: notBefore, notOnOrAfter
    now = datetime.datetime.utcnow()
    try:
        not_before = assertion.subject. \
            subjectConfirmation.subjectConfirmationData.notBefore
    except:
        return error_page(request,
            _('sso_after_response: missing subjectConfirmationData'),
            logger=logger)

    not_on_or_after = assertion.subject.subjectConfirmation. \
        subjectConfirmationData.notOnOrAfter

    if irt:
        if not_before is not None:
            return error_page(request,
                _('sso_after_response: \
                assertion in response to an AuthnRequest, \
                notBefore MUST not be present in SubjectConfirmationData'),
                logger=logger)
    elif not_before is not None and not not_before.endswith('Z'):
        return error_page(request,
            _('sso_after_response: \
            invalid notBefore value ' + not_before), logger=logger)
    if not_on_or_after is None or not not_on_or_after.endswith('Z'):
        return error_page(request,
            _('sso_after_response: invalid notOnOrAfter value'),
            logger=logger)
    try:
        if not_before and now < iso8601_to_datetime(not_before):
            return error_page(request,
                _('sso_after_response: Assertion received too early'),
                logger=logger)
    except:
        return error_page(request,
            _('sso_after_response: invalid notBefore value ' + not_before),
            logger=logger)
    try:
        if not_on_or_after and now > iso8601_to_datetime(not_on_or_after):
            return error_page(request,
            _('sso_after_response: Assertion expired'), logger=logger)
    except:
        return error_page(request,
            _('sso_after_response: invalid notOnOrAfter value'),
            logger=logger)

    logger.debug('sso_after_response: assertion validity timeslice respected : \
        %s <= %s < %s ' % (not_before, str(now), not_on_or_after))


    try:
        login.acceptSso()
    except lasso.Error, error:
        return error_page(request,
            _('sso_after_response: acceptSso raised %s') \
                %lasso.strError(error[0]), logger=logger)

    logger.info('sso_after_response: \
        Assertion processing terminated with success')

    attributes = {}

    for att_statement in login.assertion.attributeStatement:
        for attribute in att_statement.attribute:
            try:
                name, format, nickname = \
                    attribute.name.decode('ascii'), \
                    attribute.nameFormat.decode('ascii'), \
                    attribute.friendlyName
            except UnicodeDecodeError:
                message = 'sso_after_response: name or \
                    format of an attribute failed to decode as ascii: %r %r'
                logger.warning(message % (attribute.name, attribute.format))
                continue
            try:
                values = attribute.attributeValue
                if values:
                    attributes[(name, format)] = []
                    if nickname:
                        attributes[nickname] = attributes[(name, format)]
                for value in values:
                    content = []
                    for any in value.any:
                        content.append(any.exportToXml())
                    content = ''.join(content)
                    attributes[(name, format)].append(content.decode('utf8'))
            except UnicodeDecodeError:
                message = 'sso_after_response: \
                attribute value is not utf8 encoded %r'
                logger.warning(message % value)
                continue
    # Keep the issuer
    attributes['__issuer'] = login.assertion.issuer.content
    attributes['__nameid'] = login.assertion.subject.nameID.content

    # Register attributes in session for other applications
    request.session['attributes'] = attributes

    #logger.debug('sso_after_response: \
    #    attributes in assertion %s' % str(attributes))

    '''Access control processing'''

    decisions = signals.authz_decision.send(sender=None,
         request=request, attributes=attributes, provider=provider)
    if not decisions:
        logger.debug('sso_after_response: No authorization function \
            connected')

    access_granted = True
    one_message = False
    for decision in decisions:
        logger.debug('sso_after_response: authorization function %s' \
            %decision[0].__name__)
        dic = decision[1]
        logger.debug('sso_after_response: decision is %s' %dic['authz'])
        if dic.has_key('message'):
            logger.debug('sso_after_response: with message %s' %dic['message'])
        if not dic['authz']:
            access_granted = False
            if dic.has_key('message'):
                one_message = True
                messages.add_message(request, messages.ERROR, dic['message'])

    if not access_granted:
        if not one_message:
            p = get_authorization_policy(provider)
            messages.add_message(request, messages.ERROR,
                p.default_denial_message)
        return error_page(request,
            logger=logger, default_message=False, timer=True)

    '''Access granted, now we deal with session management'''


    url = get_registered_url(request)
    if not request.session.has_key('saml_request_id'):
        #IdP initiated
        url = '/'

    #XXX: Allow external login of user

    user = request.user

    policy = get_idp_options_policy(provider)
    if login.nameIdentifier.format == \
        lasso.SAML2_NAME_IDENTIFIER_FORMAT_TRANSIENT \
        and (policy is None \
             or not policy.transient_is_persistent):
        logger.info('sso_after_response: Transient nameID')
        if s.handle_transient == 'AUTHSAML2_UNAUTH_TRANSIENT_ASK_AUTH':
            return error_page(request,
                _('sso_after_response: \
                Transient access policy not yet implemented'),
                logger=logger)
        if s.handle_transient == 'AUTHSAML2_UNAUTH_TRANSIENT_OPEN_SESSION':
            logger.info('sso_after_response: \
                Opening session for transient with nameID')
            logger.debug('sso_after_response: \
                nameID %s' %login.nameIdentifier.dump())
            user = authenticate(name_id=login.nameIdentifier)
            if not user:
                return error_page(request,
                    _('sso_after_response: \
                    No backend for temporary federation is configured'),
                    logger=logger)
            auth_login(request, user)
            logger.debug('sso_after_response: django session opened')
            signals.auth_login.send(sender=None,
                request=request, attributes=attributes)
            logger.debug('sso_after_response: successful login signal sent')
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            save_session(request, login, kind=LIBERTY_SESSION_DUMP_KIND_SP)
            logger.info('sso_after_response: \
                login processing ended with success - redirect to target')
            return HttpResponseRedirect(url)
        return error_page(request, _('sso_after_response: \
            Transient access policy: Configuration error'),
            logger=logger)

    if login.nameIdentifier.format == \
        lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT \
        or (login.nameIdentifier.format == \
            lasso.SAML2_NAME_IDENTIFIER_FORMAT_TRANSIENT \
                and policy is not None and policy.transient_is_persistent):
        logger.info('sso_after_response: Persistent nameID')
        if policy is not None and policy.transient_is_persistent:
            logger.info('sso_after_response: \
                Transient nameID %s treated as persistent' % \
                login.nameIdentifier.dump())
        user = AuthSAML2PersistentBackend(). \
            authenticate(name_id=login.nameIdentifier,
                provider_id=login.remoteProviderId)
        if not user and \
                s.handle_persistent == \
                    'AUTHSAML2_UNAUTH_PERSISTENT_CREATE_USER_PSEUDONYMOUS':
            # Auto-create an user then do the authentication again
            logger.info('sso_after_response: Account creation')
            AuthSAML2PersistentBackend(). \
                create_user(name_id=login.nameIdentifier,
                    provider_id=provider.entity_id)
            user = AuthSAML2PersistentBackend(). \
                authenticate(name_id=login.nameIdentifier,
                    provider_id=login.remoteProviderId)
        if user:
            auth_login(request, user)
            logger.debug('sso_after_response: session opened')
            signals.auth_login.send(sender=None,
                request=request, attributes=attributes)
            logger.debug('sso_after_response: \
                signal sent that the session is opened')
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            save_session(request, login, kind=LIBERTY_SESSION_DUMP_KIND_SP)
            #save_federation(request, login)
            maintain_liberty_session_on_service_provider(request, login)
            logger.info('sso_after_response: \
                Login processing ended with success - redirect to target')
            return HttpResponseRedirect(url)
        elif s.handle_persistent == \
                'AUTHSAML2_UNAUTH_PERSISTENT_ACCOUNT_LINKING_BY_AUTH':
            if request.user.is_authenticated():
                logger.info('sso_after_response: Add federation')
                add_federation(request.user, name_id=login.nameIdentifier,
                    provider_id=login.remoteProviderId)
                return HttpResponseRedirect(url)
            logger.info('sso_after_response: Account linking required')
            save_session(request, login, kind=LIBERTY_SESSION_DUMP_KIND_SP)
            logger.debug('sso_after_response: \
                Register identity dump in session')
            save_federation_temp(request, login, attributes=attributes)
            maintain_liberty_session_on_service_provider(request, login)
            return render_to_response('auth/saml2/account_linking.html',
                    context_instance=RequestContext(request))
        return error_page(request,
            _('sso_after_response: \
            Persistent Account policy: Configuration error'), logger=logger)

    return error_page(request,
        _('sso_after_response: \
        Transient access policy: NameId format not supported'), logger=logger)
        #TODO: Relay state

###
 # finish_federation
 # @request
 #
 # Called after an account linking.
 # TODO: add checkbox, create new account (settings option, user can choose)
 # Create pseudonymous or user choose or only account linking
 ###
@csrf_exempt
def finish_federation(request):
    logger.info('finish_federation: Return after account linking form filled')
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            logger.info('finish_federation: form valid')
            server = build_service_provider(request)
            if not server:
                return error_page(request,
                    _('finish_federation: \
                    Service provider not configured'), logger=logger)

            login = lasso.Login(server)
            if not login:
                return error_page(request,
                    _('finish_federation: \
                    Unable to create Login object'), logger=logger)

            s = load_session(request, login, kind=LIBERTY_SESSION_DUMP_KIND_SP)
            load_federation_temp(request, login)
            if not login.session:
                return error_page(request,
                    _('finish_federation: Error loading session.'),
                    logger=logger)

            login.nameIdentifier = \
                login.session.getAssertions()[0].subject.nameID

            logger.debug('finish_federation: nameID %s' % \
                login.nameIdentifier.dump())

            provider_id = None
            if request.session.has_key('remoteProviderId'):
                provider_id = request.session['remoteProviderId']
            fed = add_federation(form.get_user(),
                name_id=login.nameIdentifier,
                provider_id=provider_id)
            if not fed:
                return error_page(request,
                    _('SSO/finish_federation: \
                    Error adding new federation for this user'),
                    logger=logger)

            logger.info('finish_federation: federation added')

            url = get_registered_url(request)
            auth_login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            logger.debug('finish_federation: session opened')

            attributes = []
            if request.session.has_key('attributes'):
                attributes = request.session['attributes']
            signals.auth_login.send(sender=None,
                request=request, attributes=attributes)
            logger.debug('finish_federation: \
                signal sent that the session is opened')

            if s:
                s.delete()
            if login.session:
               login.session.isDirty = True
            if login.identity:
                login.identity.isDirty = True
            save_session(request, login, kind=LIBERTY_SESSION_DUMP_KIND_SP)
            #save_federation(request, login)
            maintain_liberty_session_on_service_provider(request, login)
            logger.info('finish_federation: \
                Login processing ended with success - redirect to target')
            return HttpResponseRedirect(url)
        else:
            # TODO: Error: login failed: message and count 3 attemps
            logger.warning('finish_federation: \
                form not valid - Try again! (Brute force?)')
            return render_to_response('auth/saml2/account_linking.html',
                    context_instance=RequestContext(request))
    else:
        return error_page(request,
            _('finish_federation: Unable to perform federation'),
            logger=logger)

'''We do not manage mutliple login.
 There is only one global logout possible.
 Then, remove the function "federate your identity"
 under a sso session.
 Multiple login should not be for a SSO purpose
 but to obtain "membership cred" or "attributes".
 Then, Idp sollicited for such creds should not maintain
 a session after the credential issuing.
 Multiple logout: Tell the user on which idps, the user is logged
 Propose local or global logout
 For global, break local session only when
 there is only idp logged remaining'''


###
 # sp_slo
 # @request
 # @provider_id
 #
 # slo request send from another application
 # Does not deal with the local session.
 ###
def ko_icon(request):
    return HttpResponseRedirect('%s/images/ko.png' % settings.MEDIA_URL)

def ok_icon(request):
    return HttpResponseRedirect('%s/images/ok.png' % settings.MEDIA_URL)

def sp_slo(request, provider_id):
    all = request.REQUEST.get('all')
    next = request.REQUEST.get('next')
    if not provider_id:
        return HttpResponseRedirect(next) or ko_icon(request)
    server = create_server(request)
    logout = lasso.Logout(server)
    logger.info('sp_slo: sp_slo for %s' % provider_id)
    load_session(request, logout, kind=LIBERTY_SESSION_DUMP_KIND_SP)
    provider = load_provider(request, provider_id,
        server=server, sp_or_idp='idp')
    if not provider:
        logger.error('sp_slo:  sp_slo failed to load provider')
        return HttpResponseRedirect(next) or ko_icon(request)
    policy =  get_idp_options_policy(provider)
    if policy and policy.enable_http_method_for_slo_request \
            and policy.http_method_for_slo_request:
        if policy.http_method_for_slo_request == lasso.HTTP_METHOD_SOAP:
            logger.info('sp_slo: sp_slo by SOAP')
            try:
               logout.initRequest(None, lasso.HTTP_METHOD_SOAP)
            except:
                logger.exception('sp_slo: sp_slo init error')
                return HttpResponseRedirect(next) or ko_icon(request)
            try:
                logout.buildRequestMsg()
            except:
                logger.exception('sp_slo: sp_slo build error')
                return HttpResponseRedirect(next) or ko_icon(request)
            try:
                soap_response = send_soap_request(request, logout)
            except:
                logger.exception('sp_slo: sp_slo SOAP failure')
                return HttpResponseRedirect(next) or ko_icon(request)
            return process_logout_response(request,
                logout, soap_response, next)
        else:
            try:
               logout.initRequest(None, lasso.HTTP_METHOD_REDIRECT)
            except:
                logger.exception('sp_slo: sp_slo init error')
                return HttpResponseRedirect(next) or ko_icon(request)
            try:
                logout.buildRequestMsg()
            except:
                logger.exception('sp_slo: sp_slo build error')
                return HttpResponseRedirect(next) or ko_icon(request)
            logger.info('sp_slo: sp_slo by redirect')
            save_key_values(logout.request.id,
                logout.dump(), provider_id, next)
            return HttpResponseRedirect(logout.msgUrl)
    try:
        logout.initRequest(provider_id)
    except lasso.ProfileMissingAssertionError:
        logger.error('sp_slo: \
            sp_slo failed because no sessions exists for %r' % provider_id)
        return HttpResponseRedirect(next) or ko_icon(request)
    logout.msgRelayState = logout.request.id
    try:
        logout.buildRequestMsg()
    except:
        logger.exception('sp_slo: sp_slo misc error')
        return HttpResponseRedirect(next) or ko_icon(request)
    if logout.msgBody: # SOAP case
        logger.info('sp_slo: sp_slo by SOAP')
        try:
            soap_response = send_soap_request(request, logout)
        except:
            logger.exception('sp_slo: sp_slo SOAP failure')
            return HttpResponseRedirect(next) or ko_icon(request)
        return process_logout_response(request, logout, soap_response, next)
    else:
        logger.info('sp_slo: sp_slo by redirect')
        save_key_values(logout.request.id, logout.dump(), provider_id, next)
        return HttpResponseRedirect(logout.msgUrl)

def process_logout_response(request, logout, soap_response, next):
    try:
        logout.processRequestMsg(soap_response)
    except:
        logger.exception('process_logout_response: \
            processRequestMsg raised an exception')
        return redirect_next(request, next) or ko_icon(request)
    else:
        delete_session(request)
        return redirect_next(request, next) or ok_icon(request)

###
 # logout
 # @request
 #
 # Single Logout Request from UI
 ###
def logout(request):
    if not is_sp_configured():
        return error_page(request,
            _('logout: Service provider not configured'),
            logger=logger)
    if request.user.is_anonymous():
        return error_page(request,
            _('logout: not a logged in user'),
            logger=logger)
    server = build_service_provider(request)
    if not server:
        return error_page(request,
            _('logout: Service provider not configured'),
            logger=logger)
    logout = lasso.Logout(server)
    if not logout:
        return error_page(request,
            _('logout: Unable to create Login object'),
            logger=logger)
    load_session(request, logout, kind=LIBERTY_SESSION_DUMP_KIND_SP)
    # Lookup for the Identity provider from session
    q = LibertySessionDump. \
        objects.filter(django_session_key = request.session.session_key)
    if not q:
        return error_page(request,
            _('logout: No session for global logout.'),
            logger=logger)
    try:
        pid = lasso.Session().newFromDump(q[0].session_dump). \
            get_assertions().keys()[0]
        p = LibertyProvider.objects.get(entity_id=pid)
    except:
        return error_page(request,
            _('logout: Session malformed.'),
            logger=logger)

    provider = load_provider(request, pid, server=server, sp_or_idp='idp')
    if not provider:
        return error_page(request,
            _('logout: Error loading provider.'),
            logger=logger)

    policy = get_idp_options_policy(provider)
    if policy and policy.enable_http_method_for_slo_request \
            and policy.http_method_for_slo_request:
        if policy.http_method_for_slo_request == lasso.HTTP_METHOD_SOAP:
            try:
               logout.initRequest(None, lasso.HTTP_METHOD_SOAP)
            except lasso.Error, error:
                return localLogout(request, error)
            try:
                logout.buildRequestMsg()
            except lasso.Error, error:
                return localLogout(request, error)
        # TODO: Client cert
            client_cert = None
            soap_answer = None
            try:
                soap_answer = soap_call(logout.msgUrl,
                    logout.msgBody, client_cert = client_cert)
            except SOAPException, error:
                return localLogout(request, error)
            if not soap_answer:
                remove_liberty_session_sp(request)
                signals.auth_logout.send(sender=None, user=request.user)
                auth_logout(request)
                return error_page(request,
                    _('logout: SOAP error - \
                    Only local logout performed.'),
                    logger=logger)
            return slo_return(request, logout, soap_answer)
        else:
            try:
                logout.initRequest(None, lasso.HTTP_METHOD_REDIRECT)
            except lasso.Error, error:
                return localLogout(request, error)
            session_index = get_session_index(request)
            if session_index:
                logout.request.sessionIndex = session_index
            try:
                logout.buildRequestMsg()
            except lasso.Error, error:
                return localLogout(request, error)
            return HttpResponseRedirect(logout.msgUrl)

    # If not defined in the metadata,
    # put ANY to let lasso do its job from metadata
    try:
       logout.initRequest(pid)
    except lasso.Error, error:
       localLogout(request, error)
    if not logout.msgBody:
        try:
            logout.buildRequestMsg()
        except lasso.Error, error:
            return localLogout(request, error)
        # TODO: Client cert
        client_cert = None
        try:
            soap_answer = soap_call(logout.msgUrl,
                logout.msgBody, client_cert = client_cert)
        except SOAPException:
            return localLogout(request, error)
        return slo_return(request, logout, soap_answer)
    else:
        session_index = get_session_index(request)
        if session_index:
            logout.request.sessionIndex = session_index
        try:
            logout.buildRequestMsg()
        except lasso.Error, error:
            return localLogout(request, error)
        return HttpResponseRedirect(logout.msgUrl)

    return error_page(request,
            _('logout:  Unknown HTTP method.'),
            logger=logger)

def localLogout(request, error):
    remove_liberty_session_sp(request)
    signals.auth_logout.send(sender=None, user=request.user)
    auth_logout(request)
    if error.url:
        return error_page(request,
            _('localLogout:  SOAP error \
            with %s -  Only local logout performed.') %error.url,
            logger=logger)
    return error_page(request,
        _('localLogout:  %s -  Only local \
        logout performed.') %lasso.strError(error[0]),
        logger=logger)

###
 # singleLogoutReturn
 # @request
 #
 # Response from Redirect
 # Single Logout SOAP SP initiated
 ###
def singleLogoutReturn(request):
    if not is_sp_configured():
        return error_page(request,
            _('singleLogoutReturn: Service provider not configured'),
            logger=logger)

    server = build_service_provider(request)
    if not server:
        return error_page(request,
            _('singleLogoutReturn: Service provider not configured'),
            logger=logger)

    query = get_saml2_query_request(request)
    if not query:
        return error_page(request,
            _('singleLogoutReturn: \
            Unable to handle Single Logout by Redirect without request'),
            logger=logger)

    logout = lasso.Logout(server)
    if not logout:
        return error_page(request,
            _('singleLogoutReturn: Unable to create Login object'),
            logger=logger)

    load_session(request, logout, kind=LIBERTY_SESSION_DUMP_KIND_SP)

    return slo_return(request, logout, query)

###
 # slo_return
 # @request
 # @logout
 # @message
 #
 # Post-response processing
 ###
def slo_return(request, logout, message):
    try:
        logout.processResponseMsg(message)
    except lasso.Error, error:
        # Silent local logout
        return local_logout(request)
    if logout.isSessionDirty:
        if logout.session:
            save_session(request, logout, kind=LIBERTY_SESSION_DUMP_KIND_SP)
        else:
            delete_session(request)
    remove_liberty_session_sp(request)
    return local_logout(request)

def local_logout(request):
        global __logout_redirection_timeout
        "Logs out the user and displays 'You are logged out' message."
        context = RequestContext(request)
        context['redir_timeout'] = __logout_redirection_timeout
        context['message'] = 'You are logged out'
        template = 'auth/saml2/logout.html'
        s = get_service_provider_settings()
        if not s or not s.back_url:
            context['next_page'] = '/'
        else:
            context['next_page'] = s.back_url
        signals.auth_logout.send(sender = None, user = request.user)
        auth_logout(request)
        return render_to_response(template, context_instance = context)

###
 # singleLogoutSOAP
 # @request
 #
 # Single Logout SOAP IdP initiated
 # TODO: Manage valid soap responses on error (else error 500)
 ###
@csrf_exempt
def singleLogoutSOAP(request):
    try:
        soap_message = get_soap_message(request)
    except:
        return http_response_bad_request('singleLogoutSOAP: Bad SOAP message')

    if not soap_message:
        return http_response_bad_request('singleLogoutSOAP: Bad SOAP message')

    request_type = lasso.getRequestTypeFromSoapMsg(soap_message)
    if request_type != lasso.REQUEST_TYPE_LOGOUT:
        return http_response_bad_request('singleLogoutSOAP: \
        SOAP message is not a slo message')

    if not is_sp_configured():
        return http_response_forbidden_request('singleLogoutSOAP: \
        Service provider not configured')

    server = build_service_provider(request)
    if not server:
        return http_response_forbidden_request('singleLogoutSOAP: \
        Service provider not configured')

    logout = lasso.Logout(server)
    if not logout:
        return http_response_forbidden_request('singleLogoutSOAP: \
        Unable to create Login object')

    while True:
        try:
            logout.processRequestMsg(soap_message)
            break
        except (lasso.ServerProviderNotFoundError,
                lasso.ProfileUnknownProviderError):
            provider_id = logout.remoteProviderId
            provider_loaded = load_provider(request, provider_id,
                    server=server, sp_or_idp='idp')

            if not provider_loaded:
                message = _('SLO/SOAP: provider %r unknown') % provider_id
                return error_page(request, message, logger=logger)
            else:
                continue
        except lasso.Error, error:
            message = 'singleLogoutSOAP \
            processRequestMsg: %s' %lasso.strError(error[0])
            return http_response_forbidden_request(message)

    # Look for a session index
    try:
        session_index = logout.request.sessionIndex
    except:
        pass

    fed = lookup_federation_by_name_identifier(profile=logout)
    if not fed:
        return http_response_forbidden_request('singleLogoutSOAP: \
        Unable to find user')

    session = None
    if session_index:
#        # Map session.id to session.index
#        for x in get_session_manager().values():
#            if logout.remoteProviderId is x.proxied_idp:
#                if x._proxy_session_index == session_index:
#                   session = x
#            else:
#                if x.get_session_index() == session_index:
#                    session = x
        # TODO: WARNING: A user can be logged without a federation!
        try:
            session = LibertySessionSP. \
                objects.get(federation=fed, session_index=session_index)
        except:
            pass
#    else:
#        # No session index take the last session
#        # with the same name identifier
#        name_identifier = logout.nameIdentifier.content
#        for session_candidate in get_session_manager().values():
#            if name_identifier in (session_candidate.name_identifiers or []):
#                session = session_candidate
        try:
            session = LibertySessionSP.objects.get(federation=fed)
        except:
            # no session, build straight failure answer
           pass
    if session:
        q = LibertySessionDump. \
            objects.filter(django_session_key = session.django_session_key)
        if not q:
            logger.warning('singleLogoutSOAP: No session dump for this session')
            finishSingleLogoutSOAP(logout)
        logger.info('singleLogoutSOAP from %s, \
            for session index %s and session %s' % \
            (logout.remoteProviderId, session_index, session.id))
        logout.setSessionFromDump(q[0].session_dump.encode('utf8'))
    else:
        logger.warning('singleLogoutSOAP: No Liberty session found')
        return finishSingleLogoutSOAP(logout)
#    authentic.identities.get_store().load_identities()
#    try:
#       identity = authentic.identities.get_store().get_identity(session.user)
#    except KeyError:
#        pass
#    else:
#        if identity.lasso_dump:
#            logout.setIdentityFromDump(identity.lasso_dump)
#    if session.proxied_idp:
#        self.proxy_slo_soap(session, identity)
#        logout.setSessionFromDump(session.lasso_session_dump)
    try:
        logout.validateRequest()
    except lasso.Error, error:
        message = 'singleLogoutSOAP validateRequest: %s' %lasso.strError(error[0])
        logger.info(message)
        # We continue the process
    django_session_key = session.django_session_key
    session.delete()
    q[0].delete()
    from django.contrib.sessions.models import Session
    try:
        ss = Session.objects.all()
        for s in ss:
            if s.session_key == django_session_key:
                session_django = s
    except:
        import sys
        logger.warning('singleLogoutSOAP: \
            Unable to grab user session: %s' %sys.exc_info()[0])
        return finishSingleLogoutSOAP(logout)
    try:
        session_django.delete()
    except:
        import sys
        logger.warning('singleLogoutSOAP: \
            Unable to delete user session: %s' %sys.exc_info()[0])
        return finishSingleLogoutSOAP(logout)

    return finishSingleLogoutSOAP(logout)

def finishSingleLogoutSOAP(logout):
    try:
        logout.buildResponseMsg()
    except:
        logger.warning('singleLogoutSOAP \
            buildResponseMsg: %s' %lasso.strError(error[0]))
        return http_response_forbidden_request(message)

    django_response = HttpResponse()
    django_response.status_code = 200
    django_response.content_type = 'text/xml'
    django_response.content = logout.msgBody
    return django_response

###
 # singleLogout
 # @request
 #
 # Single Logout Redirect IdP initiated
 ###
def singleLogout(request):
    if not is_sp_configured():
        return http_response_forbidden_request('singleLogout: \
            Service provider not configured')

    query = get_saml2_query_request(request)
    if not query:
        return http_response_forbidden_request('singleLogout: \
            Unable to handle Single Logout by Redirect without request')

    server = build_service_provider(request)
    if not server:
        return http_response_forbidden_request('singleLogout: \
            Service provider not configured')

    logout = lasso.Logout(server)
    while True:
        try:
            logout.processRequestMsg(query)
            break
        except (lasso.ServerProviderNotFoundError,
                lasso.ProfileUnknownProviderError):
            provider_id = logout.remoteProviderId
            provider_loaded = load_provider(request, provider_id,
                    server=server, sp_or_idp='idp')

            if not provider_loaded:
                message = _('singleLogout: provider %r unknown') % provider_id
                return error_page(request, message, logger=logger)
            else:
                continue
        except lasso.Error, error:
            logger.error('singleLogout: %s' %lasso.strError(error[0]))
            return slo_return_response(logout)

    logger.info('singleLogout: from %s' % logout.remoteProviderId)

    load_session(request, logout, kind=LIBERTY_SESSION_DUMP_KIND_SP)

    try:
        logout.validateRequest()
    except lasso.Error, error:
        logger.error('singleLogout: %s' %lasso.strError(error[0]))
        return slo_return_response(logout)

    if logout.isSessionDirty:
        if logout.session:
            save_session(request, logout, kind=LIBERTY_SESSION_DUMP_KIND_SP)
        else:
            delete_session(request)
    remove_liberty_session_sp(request)
    signals.auth_logout.send(sender=None, user=request.user)
    auth_logout(request)


    # TODO: we cannot call slo_return_response, 
    # else django raise an error due an httpresponse return missing
    try:
        logout.buildResponseMsg()
    except lasso.Error, error:
        logger.error('singleLogout: error building response %s' %lasso.strError(error[0]))
        return http_response_forbidden_request('singleLogout: %s') % \
            lasso.strError(error[0])
    else:
        logger.info('singleLogout: redirect to %s' %logout.msgUrl)
        return HttpResponseRedirect(logout.msgUrl)

def slo_return_response(logout):
    try:
        logout.buildResponseMsg()
    except lasso.Error, error:
        return http_response_forbidden_request('slo_return_response: %s') \
            %lasso.strError(error[0])
    else:
        return HttpResponseRedirect(logout.msgUrl)

###
 # federationTermination
 # @request
 # @method
 # @entity_id
 #
 # Name Identifier Management
 # Federation termination: request from user interface
 # Profile supported: Redirect, SOAP
 # For response, if the requester uses a (a)synchronous binding,
 # the responder uses the same.
 # Else, the grabs the preferred method from the metadata.
 # By default we do not break the session.
 # TODO: Define in admin a parameter to indicate if the
 # federation termination implies a local logout (IDP and SP initiated)
 # -> Should not logout.
 # TODO: Clean tables of all dumps about this user
 ###
def federationTermination(request):
    entity_id = request.REQUEST.get('entity_id')
    if not is_sp_configured():
        return error_page(request,
            _('fedTerm/SP UI: Service provider not configured'),
            logger=logger)

    if not entity_id:
        return error_page(request,
            _('fedTerm/SP UI: No provider for defederation'),
            logger=logger)

    if request.user.is_anonymous():
        return error_page(request,
            _('fedTerm/SP UI: Unable to defederate a not logged user!'),
            logger=logger)

    server = build_service_provider(request)
    if not server:
        error_page(request,
            _('fedTerm/SP UI: Service provider not configured'),
            logger=logger)

    # Lookup for the Identity provider
    p = load_provider(request, entity_id, server=server, sp_or_idp='idp')
    if not p:
        return error_page(request,
            _('fedTerm/SP UI: No such identity provider.'),
            logger=logger)

    manage = lasso.NameIdManagement(server)

    load_session(request, manage, kind=LIBERTY_SESSION_DUMP_KIND_SP)
    load_federation(request, manage)
    fed = lookup_federation_by_user(request.user, p.entity_id)
    if not fed:
        return error_page(request,
            _('fedTerm/SP UI: Not a valid federation'),
            logger=logger)

    # The user asks a defederation,
    # we perform without knowing if the IdP can handle
    fed.delete()

    # TODO: Deal with identity provider configuration in policies

    # If not defined in the metadata,
    # put ANY to let lasso do its job from metadata
    if not p.identity_provider.enable_http_method_for_defederation_request:
        try:
            manage.initRequest(entity_id, None, lasso.HTTP_METHOD_ANY)
        except lasso.Error, error:
            return error_page(request,
                _('fedTerm/SP UI: %s') %lasso.strError(error[0]),
                logger=logger)

        if manage.msgBody:
            try:
                manage.buildRequestMsg()
            except lasso.Error, error:
                return error_page(request,
                    _('fedTerm/SP SOAP: %s') %lasso.strError(error[0]),
                    logger=logger)
            # TODO: Client cert
            client_cert = None
            try:
                soap_answer = soap_call(manage.msgUrl,
                    manage.msgBody, client_cert = client_cert)
            except SOAPException:
                return error_page(request,
                    _('fedTerm/SP SOAP: \
                    Unable to perform SOAP defederation request'),
                    logger=logger)
            return manage_name_id_return(request, manage, soap_answer)
        else:
            try:
                manage.buildRequestMsg()
            except lasso.Error, error:
                return error_page(request,
                    _('fedTerm/SP Redirect: %s') % \
                    lasso.strError(error[0]), logger=logger)
            save_manage(request, manage)
            return HttpResponseRedirect(manage.msgUrl)

    # Else, taken from config
    if p.identity_provider.http_method_for_defederation_request == \
            lasso.HTTP_METHOD_SOAP:
        try:
            manage.initRequest(entity_id, None, lasso.HTTP_METHOD_SOAP)
            manage.buildRequestMsg()
        except lasso.Error, error:
            return error_page(request,
                _('fedTerm/SP SOAP: %s') %lasso.strError(error[0]),
                logger=logger)
        # TODO: Client cert
        client_cert = None
        try:
            soap_answer = soap_call(manage.msgUrl,
                manage.msgBody, client_cert = client_cert)
        except SOAPException:
            return error_page(request,
                _('fedTerm/SP SOAP: \
                Unable to perform SOAP defederation request'),
                logger=logger)
        return manage_name_id_return(request, manage, soap_answer)

    if p.identity_provider.http_method_for_defederation_request == \
            lasso.HTTP_METHOD_REDIRECT:
        try:
            manage.initRequest(entity_id, None, lasso.HTTP_METHOD_REDIRECT)
            manage.buildRequestMsg()
        except lasso.Error, error:
            return error_page(request,
                _('fedTerm/SP Redirect: %s') %lasso.strError(error[0]),
                logger=logger)
        save_manage(request, manage)
        return HttpResponseRedirect(manage.msgUrl)

    return error_page(request, _('Unknown HTTP method.'), logger=logger)

###
 # manageNameIdReturn
 # @request
 #
 # Federation termination: response from Redirect SP initiated
 ###
def manageNameIdReturn(request):
    server = build_service_provider(request)
    if not server:
        return error_page(request,
            _('fedTerm/SP Redirect: Service provider not configured'),\
            logger=logger)

    manage_dump = get_manage_dump(request)
    manage = None
    if manage_dump and manage_dump.count()>1:
        for md in manage_dump:
            md.delete()
        return error_page(request,
            _('fedTerm/SP Redirect: Error managing manage dump'),
            logger=logger)
    elif manage_dump:
        manage = \
            lasso.NameIdManagement.newFromDump(server,
            manage_dump[0].manage_dump)
        manage_dump.delete()
    else:
        manage = lasso.NameIdManagement(server)

    if not manage:
        return error_page(request,
            _('fedTerm/SP Redirect: Defederation failed'), logger=logger)

    load_federation(request, manage)
    message = get_saml2_request_message(request)
    return manage_name_id_return(request, manage, message)

###
 # manage_name_id_return
 # @request
 # @logout
 # @message
 #
 # Post-response processing
 ###
def manage_name_id_return(request, manage, message):
    while True:
        try:
            manage.processResponseMsg(message)
        except (lasso.ServerProviderNotFoundError,
                lasso.ProfileUnknownProviderError):
            provider_id = manage.remoteProviderId
            provider_loaded = load_provider(request, provider_id,
                    server=manage.server, sp_or_idp='idp')

            if not provider_loaded:
                message = _('fedTerm/Return: \
                    provider %r unknown') % provider_id
                return error_page(request, message, logger=logger)
            else:
                continue
        except lasso.Error, error:
            return error_page(request,
                _('fedTerm/manage_name_id_return: %s') % \
                lasso.strError(error[0]),
                logger=logger)
        else:
            '''if manage.isIdentityDirty:
                if manage.identity:
                    save_federation(request, manage)'''
            break
    return HttpResponseRedirect(get_registered_url(request))

###
 # manageNameIdSOAP
 # @request
 #
 # Federation termination: request from SOAP IdP initiated
 # TODO: Manage valid soap responses on error (else error 500)
 ###
@csrf_exempt
def manageNameIdSOAP(request):
    try:
        soap_message = get_soap_message(request)
    except:
        return http_response_bad_request('fedTerm/IdP SOAP: Bad SOAP message')
    if not soap_message:
        return http_response_bad_request('fedTerm/IdP SOAP: Bad SOAP message')

    request_type = lasso.getRequestTypeFromSoapMsg(soap_message)
    if request_type != lasso.REQUEST_TYPE_NAME_ID_MANAGEMENT:
        return http_response_bad_request('fedTerm/IdP SOAP: \
            SOAP message is not a slo message')

    if not is_sp_configured():
        return http_response_forbidden_request('fedTerm/IdP SOAP: \
            Service provider not configured')

    server = build_service_provider(request)
    if not server:
        return http_response_forbidden_request('fedTerm/IdP SOAP: \
            Service provider not configured')

    manage = lasso.NameIdManagement(server)
    if not manage:
        return http_response_forbidden_request('fedTerm/IdP SOAP: \
            Unable to create Login object')

    while True:
        try:
            manage.processRequestMsg(soap_message)
            break
        except (lasso.ServerProviderNotFoundError,
                lasso.ProfileUnknownProviderError):
            provider_id = manage.remoteProviderId
            provider_loaded = load_provider(request, provider_id,
                    server=server, sp_or_idp='idp')

            if not provider_loaded:
                message = _('fedTerm/SOAP: provider %r unknown') % provider_id
                return error_page(request, message, logger=logger)
            else:
                continue
        except lasso.Error, error:
            message = 'fedTerm/IdP SOAP: %s' %lasso.strError(error[0])
            return http_response_forbidden_request(message)

    fed = lookup_federation_by_name_identifier(profile=manage)
    load_federation(request, manage, fed.user)
    try:
        manage.validateRequest()
    except lasso.Error, error:
        message = 'fedTerm/IdP SOAP: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    fed.delete()

    try:
        manage.buildResponseMsg()
    except:
        message = 'fedTerm/IdP SOAP: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    django_response = HttpResponse()
    django_response.status_code = 200
    django_response.content_type = 'text/xml'
    django_response.content = manage.msgBody
    return django_response

###
 # manageNameId
 # @request
 #
 # Federation termination: request from Redirect IdP initiated
 ###
def manageNameId(request):
    if not is_sp_configured():
        return http_response_forbidden_request('fedTerm/IdP Redirect: \
            Service provider not configured')

    query = get_saml2_query_request(request)
    if not query:
        return http_response_forbidden_request('fedTerm/IdP Redirect: \
            Unable to handle Single Logout by Redirect without request')

    server = build_service_provider(request)
    if not server:
        return http_response_forbidden_request('fedTerm/IdP Redirect: \
            Service provider not configured')

    manage = lasso.NameIdManagement(server)
    if not manage:
        return http_response_forbidden_request('fedTerm/IdP Redirect: \
            Unable to create Login object')

    try:
        manage.processRequestMsg(query)
    except lasso.Error, error:
        message = 'fedTerm/IdP Redirect: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    fed = lookup_federation_by_name_identifier(profile=manage)
    load_federation(request, manage, fed.user)
    try:
        manage.validateRequest()
    except lasso.Error, error:
        logger.warning('fedTerm/IdP Redirect: Unable to validate request')
        return

    fed.delete()

    try:
        manage.buildResponseMsg()
    except:
        message = 'fedTerm/IdP Redirect: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    return HttpResponseRedirect(manage.msgUrl)

#############################################
# Helper functions 
#############################################

def get_provider_id_and_options(provider_id):
    if not provider_id:
        provider_id=reverse(metadata)
    options = metadata_options
    if getattr(settings, 'AUTHSAML2_METADATA_OPTIONS', None):
        options.update(settings.AUTHSAML2_METADATA_OPTIONS)
    return provider_id, options

def get_metadata(request, provider_id=None):
    provider_id, options = get_provider_id_and_options(provider_id)
    return get_saml2_metadata(request, provider_id, sp_map=metadata_map,
            options=options)

def create_server(request, provider_id=None):
    provider_id, options = get_provider_id_and_options(provider_id)
    return create_saml2_server(request, provider_id, sp_map=metadata_map,
            options=options)

def http_response_bad_request(message):
    logger.error(message)
    return HttpResponseBadRequest(_(message))

def http_response_forbidden_request(message):
    logger.error(message)
    return HttpResponseForbidden(_(message))

def build_service_provider(request):
    return create_server(request, reverse(metadata))

def setAuthnrequestOptions(provider, login, force_authn, is_passive):
    if not provider or not login:
        return False

    p = get_idp_options_policy(provider)
    if not p:
        return False

    if p.no_nameid_policy:
        login.request.nameIDPolicy = None
    else:
        login.request.nameIDPolicy.format = \
            NAME_ID_FORMATS[p.requested_name_id_format]['samlv2']
        login.request.nameIDPolicy.allowCreate = p.allow_create
        login.request.nameIDPolicy.spNameQualifier = None

    if p.enable_binding_for_sso_response:
        login.request.protocolBinding = p.binding_for_sso_response

    if force_authn is None:
        force_authn = p.binding_for_sso_response
    login.request.protocolBinding = force_authn

    if is_passive is None:
        is_passive = p.want_is_passive_authn_request
    login.request.isPassive = is_passive

    login.request.consent = p.user_consent
    return True

def view_profile(request, next='', template_name='profile.html'):
    if request.session.has_key('next'):
        next = request.session['next']
    else:
        next = next
    if request.user is None \
        or not request.user.is_authenticated() \
        or not hasattr(request.user, '_meta'):
        return HttpResponseRedirect(next)

    #Add creation date
    federations = []
    try:
        feds = LibertyFederation.objects.filter(user=request.user)
        for f in feds:
            if f.idp_id:
                p = LibertyProvider.objects.get(entity_id=f.idp_id)
                federations.append(p.name)
    except:
        pass

    from frontend import AuthSAML2Frontend
    form = AuthSAML2Frontend().form()()
    if not form.fields['provider_id'].choices:
        form = None
    context = { 'submit_name': 'submit-%s' % AuthSAML2Frontend().id(),
                REDIRECT_FIELD_NAME: '/profile',
                'form': form }

    return render_to_string(template_name,
            { 'next': next,
              'federations': federations,
              'base': '/authsaml2'},
            RequestContext(request,context))

@login_required
@csrf_exempt
def delete_federation(request):
    if request.POST.has_key('next'):
        next = request.POST['next']
    else:
        next = '/'
    logger.info('[authsaml2] Ask for federation deletion')
    if request.method == "POST":
        if request.POST.has_key('fed'):
            try:
                p = LibertyProvider.objects.get(name=request.POST['fed'])
                f = LibertyFederation.objects. \
                    get(user=request.user, idp_id=p.entity_id)
                f.delete()
                logger.info('[authsaml2]: federation with %s deleted' \
                    %request.POST['fed'])
                messages.add_message(request, messages.INFO,
                _('Successful federation deletion.'))
                return HttpResponseRedirect(next)
            except:
                pass

    logger.error('[authsaml2]: Failed to delete federation'\
        %request.POST.has_key('fed'))
    messages.add_message(request, messages.INFO,
        _('Federation deletion failure.'))
    return HttpResponseRedirect(next)
