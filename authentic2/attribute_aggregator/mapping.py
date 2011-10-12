'''
    VERIDIC Project - Towards a centralized access control system

    Copyright (C) 2011  Mikael Ates

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from django.utils.translation import ugettext as _


ATTRIBUTE_NAMESPACES = \
    ("http://schemas.xmlsoap.org/ws/2005/05/identity/claims",)

ATTRIBUTE_MAPPING = {

#Extracted from openldap system schema
"top": {
    "oid": "2.5.6.0",
    "display_name": _("top"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"extensibleObject": {
    "oid": "1.3.6.1.4.1.1466.101.120.111",
    "display_name": _("extensibleObject"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"alias": {
    "oid": "2.5.6.1",
    "display_name": _("alias"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"referral": {
    "oid": "2.16.840.1.113730.3.2.6",
    "display_name": _("referral"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"OpenLDAProotDSE": {
    "oid": "1.3.6.1.4.1.4203.1.4.1",
    "display_name": _("OpenLDAProotDSE LDAProotDSE"),
    "alias": ['LDAProotDSE'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"subentry": {
    "oid": "2.5.17.0",
    "display_name": _("subentry"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"subschema": {
    "oid": "2.5.20.1",
    "display_name": _("subschema"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"collectiveAttributeSubentry": {
    "oid": "2.5.17.2",
    "display_name": _("collectiveAttributeSubentry"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"dynamicObject": {
    "oid": "1.3.6.1.4.1.1466.101.119.2",
    "display_name": _("dynamicObject"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"glue": {
    "oid": "1.3.6.1.4.1.4203.666.3.4",
    "display_name": _("glue"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"syncConsumerSubentry": {
    "oid": "1.3.6.1.4.1.4203.666.3.5",
    "display_name": _("syncConsumerSubentry"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"syncProviderSubentry": {
    "oid": "1.3.6.1.4.1.4203.666.3.6",
    "display_name": _("syncProviderSubentry"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"objectClass": {
    "oid": "2.5.4.0",
    "display_name": _("objectClass"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.38",
},

#Extracted from openldap system schema
"structuralObjectClass": {
    "oid": "2.5.21.9",
    "display_name": _("structuralObjectClass"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.38",
},

#Extracted from openldap system schema
"createTimestamp": {
    "oid": "2.5.18.1",
    "display_name": _("createTimestamp"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.24",
},

#Extracted from openldap system schema
"modifyTimestamp": {
    "oid": "2.5.18.2",
    "display_name": _("modifyTimestamp"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.24",
},

#Extracted from openldap system schema
"creatorsName": {
    "oid": "2.5.18.3",
    "display_name": _("creatorsName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"modifiersName": {
    "oid": "2.5.18.4",
    "display_name": _("modifiersName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"hasSubordinates": {
    "oid": "2.5.18.9",
    "display_name": _("hasSubordinates"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.7",
},

#Extracted from openldap system schema
"subschemaSubentry": {
    "oid": "2.5.18.10",
    "display_name": _("subschemaSubentry"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"collectiveAttributeSubentries": {
    "oid": "2.5.18.12",
    "display_name": _("collectiveAttributeSubentries"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"collectiveExclusions": {
    "oid": "2.5.18.7",
    "display_name": _("collectiveExclusions"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.38",
},

#Extracted from openldap system schema
"entryDN": {
    "oid": "1.3.6.1.1.20",
    "display_name": _("entryDN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"entryUUID": {
    "oid": "1.3.6.1.1.16.4",
    "display_name": _("entryUUID"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.1.16.1",
},

#Extracted from openldap system schema
"entryCSN": {
    "oid": "1.3.6.1.4.1.4203.666.1.7",
    "display_name": _("entryCSN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.4203.666.11.2.1{64}",
},

#Extracted from openldap system schema
"namingCSN": {
    "oid": "1.3.6.1.4.1.4203.666.1.13",
    "display_name": _("namingCSN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.4203.666.11.2.1{64}",
},

#Extracted from openldap system schema
"superiorUUID": {
    "oid": "1.3.6.1.4.1.4203.666.1.11",
    "display_name": _("superiorUUID"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.1.16.1",
},

#Extracted from openldap system schema
"syncreplCookie": {
    "oid": "1.3.6.1.4.1.4203.666.1.23",
    "display_name": _("syncreplCookie"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.40",
},

#Extracted from openldap system schema
"contextCSN": {
    "oid": "1.3.6.1.4.1.4203.666.1.25",
    "display_name": _("contextCSN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.4203.666.11.2.1{64}",
},

#Extracted from openldap system schema
"syncTimestamp": {
    "oid": "1.3.6.1.4.1.4203.666.1.26",
    "display_name": _("syncTimestamp"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.24",
},

#Extracted from openldap system schema
"altServer": {
    "oid": "1.3.6.1.4.1.1466.101.120.6",
    "display_name": _("altServer"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26",
},

#Extracted from openldap system schema
"namingContexts": {
    "oid": "1.3.6.1.4.1.1466.101.120.5",
    "display_name": _("namingContexts"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"supportedControl": {
    "oid": "1.3.6.1.4.1.1466.101.120.13",
    "display_name": _("supportedControl"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.38",
},

#Extracted from openldap system schema
"supportedExtension": {
    "oid": "1.3.6.1.4.1.1466.101.120.7",
    "display_name": _("supportedExtension"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.38",
},

#Extracted from openldap system schema
"supportedLDAPVersion": {
    "oid": "1.3.6.1.4.1.1466.101.120.15",
    "display_name": _("supportedLDAPVersion"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap system schema
"supportedSASLMechanisms": {
    "oid": "1.3.6.1.4.1.1466.101.120.14",
    "display_name": _("supportedSASLMechanisms"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from openldap system schema
"supportedFeatures": {
    "oid": "1.3.6.1.4.1.4203.1.3.5",
    "display_name": _("supportedFeatures"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.38",
},

#Extracted from openldap system schema
"monitorContext": {
    "oid": "1.3.6.1.4.1.4203.666.1.10",
    "display_name": _("monitorContext"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"configContext": {
    "oid": "1.3.6.1.4.1.4203.1.12.2.1",
    "display_name": _("configContext"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"vendorName": {
    "oid": "1.3.6.1.1.4",
    "display_name": _("vendorName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from openldap system schema
"vendorVersion": {
    "oid": "1.3.6.1.1.5",
    "display_name": _("vendorVersion"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from openldap system schema
"administrativeRole": {
    "oid": "2.5.18.5",
    "display_name": _("administrativeRole"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.38",
},

#Extracted from openldap system schema
"subtreeSpecification": {
    "oid": "2.5.18.6",
    "display_name": _("subtreeSpecification"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.45",
},

#Extracted from openldap system schema
"dITStructureRules": {
    "oid": "2.5.21.1",
    "display_name": _("dITStructureRules"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.17",
},

#Extracted from openldap system schema
"dITContentRules": {
    "oid": "2.5.21.2",
    "display_name": _("dITContentRules"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.16",
},

#Extracted from openldap system schema
"matchingRules": {
    "oid": "2.5.21.4",
    "display_name": _("matchingRules"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.30",
},

#Extracted from openldap system schema
"attributeTypes": {
    "oid": "2.5.21.5",
    "display_name": _("attributeTypes"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.3",
},

#Extracted from openldap system schema
"objectClasses": {
    "oid": "2.5.21.6",
    "display_name": _("objectClasses"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.37",
},

#Extracted from openldap system schema
"nameForms": {
    "oid": "2.5.21.7",
    "display_name": _("nameForms"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.35",
},

#Extracted from openldap system schema
"matchingRuleUse": {
    "oid": "2.5.21.8",
    "display_name": _("matchingRuleUse"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.31",
},

#Extracted from openldap system schema
"ldapSyntaxes": {
    "oid": "1.3.6.1.4.1.1466.101.120.16",
    "display_name": _("ldapSyntaxes"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.54",
},

#Extracted from openldap system schema
"aliasedObjectName": {
    "oid": "2.5.4.1",
    "display_name": _("aliasedObjectName aliasedEntryName"),
    "alias": ['aliasedEntryName'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"ref": {
    "oid": "2.16.840.1.113730.3.1.34",
    "display_name": _("ref"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from openldap system schema
"entry": {
    "oid": "1.3.6.1.4.1.4203.1.3.1",
    "display_name": _("entry"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.4203.1.1.1",
},

#Extracted from openldap system schema
"children": {
    "oid": "1.3.6.1.4.1.4203.1.3.2",
    "display_name": _("children"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.4203.1.1.1",
},

#Extracted from openldap system schema
"authzTo": {
    "oid": "1.3.6.1.4.1.4203.666.1.8",
    "display_name": _("authzTo saslAuthzTo"),
    "alias": ['saslAuthzTo'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.4203.666.2.7",
},

#Extracted from openldap system schema
"authzFrom": {
    "oid": "1.3.6.1.4.1.4203.666.1.9",
    "display_name": _("authzFrom saslAuthzFrom"),
    "alias": ['saslAuthzFrom'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.4203.666.2.7",
},

#Extracted from openldap system schema
"entryTtl": {
    "oid": "1.3.6.1.4.1.1466.101.119.3",
    "display_name": _("entryTtl"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap system schema
"dynamicSubtrees": {
    "oid": "1.3.6.1.4.1.1466.101.119.4",
    "display_name": _("dynamicSubtrees"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"distinguishedName": {
    "oid": "2.5.4.49",
    "display_name": _("distinguishedName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from openldap system schema
"name": {
    "oid": "2.5.4.41",
    "display_name": _("name"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{32768}",
},

#Extracted from openldap system schema
"cn": {
    "oid": "2.5.4.3",
    "display_name": _("cn commonName"),
    "alias": ['commonName'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap system schema
"uid": {
    "oid": "0.9.2342.19200300.100.1.1",
    "display_name": _("uid userid"),
    "alias": ['userid'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256}",
},

#Extracted from openldap system schema
"uidNumber": {
    "oid": "1.3.6.1.1.1.1.0",
    "display_name": _("uidNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap system schema
"gidNumber": {
    "oid": "1.3.6.1.1.1.1.1",
    "display_name": _("gidNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap system schema
"userPassword": {
    "oid": "2.5.4.35",
    "display_name": _("userPassword"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.40{128}",
},

#Extracted from openldap system schema
"labeledURI": {
    "oid": "1.3.6.1.4.1.250.1.57",
    "display_name": _("labeledURI"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from openldap system schema
"authPassword": {
    "oid": "1.3.6.1.4.1.4203.1.3.4",
    "display_name": _("authPassword"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.4203.1.1.2",
},

#Extracted from openldap system schema
"supportedAuthPasswordSchemes": {
    "oid": "1.3.6.1.4.1.4203.1.3.3",
    "display_name": _("supportedAuthPasswordSchemes"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{32}",
},

#Extracted from openldap system schema
"description": {
    "oid": "2.5.4.13",
    "display_name": _("description"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{1024}",
},

#Extracted from openldap system schema
"seeAlso": {
    "oid": "2.5.4.34",
    "display_name": _("seeAlso"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/inetorgperson.ldif
"carLicense": {
    "oid": "2.16.840.1.113730.3.1.1",
    "display_name": _("carLicense"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15)",
},

#Extracted from openldap schema /etc/ldap/schema/inetorgperson.ldif
"departmentNumber": {
    "oid": "2.16.840.1.113730.3.1.2",
    "display_name": _("departmentNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15)",
},

#Extracted from openldap schema /etc/ldap/schema/inetorgperson.ldif
"displayName": {
    "oid": "2.16.840.1.113730.3.1.241",
    "display_name": _("displayName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from openldap schema /etc/ldap/schema/inetorgperson.ldif
"employeeNumber": {
    "oid": "2.16.840.1.113730.3.1.3",
    "display_name": _("employeeNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from openldap schema /etc/ldap/schema/inetorgperson.ldif
"employeeType": {
    "oid": "2.16.840.1.113730.3.1.4",
    "display_name": _("employeeType"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15)",
},

#Extracted from openldap schema /etc/ldap/schema/inetorgperson.ldif
"jpegPhoto": {
    "oid": "0.9.2342.19200300.100.1.60",
    "display_name": _("jpegPhoto"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.28)",
},

#Extracted from openldap schema /etc/ldap/schema/inetorgperson.ldif
"preferredLanguage": {
    "oid": "2.16.840.1.113730.3.1.39",
    "display_name": _("preferredLanguage"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from openldap schema /etc/ldap/schema/inetorgperson.ldif
"userSMIMECertificate": {
    "oid": "2.16.840.1.113730.3.1.40",
    "display_name": _("userSMIMECertificate"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.5)",
},

#Extracted from openldap schema /etc/ldap/schema/inetorgperson.ldif
"userPKCS12": {
    "oid": "2.16.840.1.113730.3.1.216",
    "display_name": _("userPKCS12"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.5)",
},


#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"gecos": {
    "oid": "1.3.6.1.1.1.1.2",
    "display_name": _("gecos"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"homeDirectory": {
    "oid": "1.3.6.1.1.1.1.3",
    "display_name": _("homeDirectory"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"loginShell": {
    "oid": "1.3.6.1.1.1.1.4",
    "display_name": _("loginShell"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"shadowLastChange": {
    "oid": "1.3.6.1.1.1.1.5",
    "display_name": _("shadowLastChange"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"shadowMin": {
    "oid": "1.3.6.1.1.1.1.6",
    "display_name": _("shadowMin"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"shadowMax": {
    "oid": "1.3.6.1.1.1.1.7",
    "display_name": _("shadowMax"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"shadowWarning": {
    "oid": "1.3.6.1.1.1.1.8",
    "display_name": _("shadowWarning"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"shadowInactive": {
    "oid": "1.3.6.1.1.1.1.9",
    "display_name": _("shadowInactive"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"shadowExpire": {
    "oid": "1.3.6.1.1.1.1.10",
    "display_name": _("shadowExpire"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"shadowFlag": {
    "oid": "1.3.6.1.1.1.1.11",
    "display_name": _("shadowFlag"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"memberUid": {
    "oid": "1.3.6.1.1.1.1.12",
    "display_name": _("memberUid"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"memberNisNetgroup": {
    "oid": "1.3.6.1.1.1.1.13",
    "display_name": _("memberNisNetgroup"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"nisNetgroupTriple": {
    "oid": "1.3.6.1.1.1.1.14",
    "display_name": _("nisNetgroupTriple"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.1.1.0.0)",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"ipServicePort": {
    "oid": "1.3.6.1.1.1.1.15",
    "display_name": _("ipServicePort"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"ipServiceProtocolSUPname": {
    "oid": "1.3.6.1.1.1.1.16",
    "display_name": _("ipServiceProtocolSUPname"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"ipProtocolNumber": {
    "oid": "1.3.6.1.1.1.1.17",
    "display_name": _("ipProtocolNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"oncRpcNumber": {
    "oid": "1.3.6.1.1.1.1.18",
    "display_name": _("oncRpcNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"ipHostNumber": {
    "oid": "1.3.6.1.1.1.1.19",
    "display_name": _("ipHostNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{128})",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"ipNetworkNumber": {
    "oid": "1.3.6.1.1.1.1.20",
    "display_name": _("ipNetworkNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{128}",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"ipNetmaskNumber": {
    "oid": "1.3.6.1.1.1.1.21",
    "display_name": _("ipNetmaskNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{128}",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"macAddress": {
    "oid": "1.3.6.1.1.1.1.22",
    "display_name": _("macAddress"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{128})",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"bootParameter": {
    "oid": "1.3.6.1.1.1.1.23",
    "display_name": _("bootParameter"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.1.1.0.1)",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"bootFile": {
    "oid": "1.3.6.1.1.1.1.24",
    "display_name": _("bootFile"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"nisMapNameSUPname": {
    "oid": "1.3.6.1.1.1.1.26",
    "display_name": _("nisMapNameSUPname"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/nis.ldif
"nisMapEntry": {
    "oid": "1.3.6.1.1.1.1.27",
    "display_name": _("nisMapEntry"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{1024}",
},


#Extracted from openldap schema /etc/ldap/schema/core.ldif
"knowledgeInformation": {
    "oid": "2.5.4.2",
    "display_name": _("knowledgeInformation"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{32768})",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"sn": {
    "oid": "2.5.4.4",
    "display_name": _("sn surname"),
    "alias": ['surname'],
    "profile_field_name": 'last_name',
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
                ],
            "friendly_names":
                [
            "Last Name",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"serialNumber": {
    "oid": "2.5.4.5",
    "display_name": _("serialNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.44{64})",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"c": {
    "oid": "2.5.4.6",
    "display_name": _("c countryName"),
    "alias": ['countryName'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"l": {
    "oid": "2.5.4.7",
    "display_name": _("l localityName"),
    "alias": ['localityName'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/locality",
                ],
            "friendly_names":
                [
            "Locality Name or City",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"st": {
    "oid": "2.5.4.8",
    "display_name": _("st stateOrProvinceName"),
    "alias": ['stateOrProvinceName'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/stateorprovince",
                ],
            "friendly_names":
                [
            "State or Province",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"street": {
    "oid": "2.5.4.9",
    "display_name": _("street streetAddress"),
    "alias": ['streetAddress'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/streetaddress",
                ],
            "friendly_names":
                [
            "Street Address",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"o": {
    "oid": "2.5.4.10",
    "display_name": _("o organizationName"),
    "alias": ['organizationName'],
    "profile_field_name": 'company',
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"ou": {
    "oid": "2.5.4.11",
    "display_name": _("ou organizationalUnitName"),
    "alias": ['organizationalUnitName'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"title": {
    "oid": "2.5.4.12",
    "display_name": _("title"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"searchGuide": {
    "oid": "2.5.4.14",
    "display_name": _("searchGuide"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.25)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"businessCategory": {
    "oid": "2.5.4.15",
    "display_name": _("businessCategory"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128})",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"postalAddress": {
    "oid": "2.5.4.16",
    "display_name": _("postalAddress"),
    "profile_field_name": 'postal_address',
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.41)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"postalCode": {
    "oid": "2.5.4.17",
    "display_name": _("postalCode"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{40})",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/postalcode",
                ],
            "friendly_names":
                [
            "Postal Code",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"postOfficeBox": {
    "oid": "2.5.4.18",
    "display_name": _("postOfficeBox"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{40})",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"physicalDeliveryOfficeName": {
    "oid": "2.5.4.19",
    "display_name": _("physicalDeliveryOfficeName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128})",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"telephoneNumber": {
    "oid": "2.5.4.20",
    "display_name": _("telephoneNumber"),
    "profile_field_name": 'phone',
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.50{32})",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/otherphone",
                ],
            "friendly_names":
                [
            "Secondary or Work Telephone Number",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"telexNumber": {
    "oid": "2.5.4.21",
    "display_name": _("telexNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.52)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"teletexTerminalIdentifier": {
    "oid": "2.5.4.22",
    "display_name": _("teletexTerminalIdentifier"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.51)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"fax": {
    "oid": "2.5.4.23",
    "display_name": _("fax facsimileTelephoneNumber"),
    "alias": ['facsimileTelephoneNumber'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"x121Address": {
    "oid": "2.5.4.24",
    "display_name": _("x121Address"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.36{15})",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"internationaliSDNNumber": {
    "oid": "2.5.4.25",
    "display_name": _("internationaliSDNNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.36{16})",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"registeredAddress": {
    "oid": "2.5.4.26",
    "display_name": _("registeredAddress"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.41)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"destinationIndicator": {
    "oid": "2.5.4.27",
    "display_name": _("destinationIndicator"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.44{128})",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"preferredDeliveryMethod": {
    "oid": "2.5.4.28",
    "display_name": _("preferredDeliveryMethod"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.14",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"presentationAddress": {
    "oid": "2.5.4.29",
    "display_name": _("presentationAddress"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.43",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"supportedApplicationContext": {
    "oid": "2.5.4.30",
    "display_name": _("supportedApplicationContext"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.38)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"member": {
    "oid": "2.5.4.31",
    "display_name": _("member"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"owner": {
    "oid": "2.5.4.32",
    "display_name": _("owner"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"roleOccupant": {
    "oid": "2.5.4.33",
    "display_name": _("roleOccupant"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"userCertificate": {
    "oid": "2.5.4.36",
    "display_name": _("userCertificate"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.8)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"cACertificate": {
    "oid": "2.5.4.37",
    "display_name": _("cACertificate"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.8)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"authorityRevocationList": {
    "oid": "2.5.4.38",
    "display_name": _("authorityRevocationList"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.9)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"certificateRevocationList": {
    "oid": "2.5.4.39",
    "display_name": _("certificateRevocationList"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.9)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"crossCertificatePair": {
    "oid": "2.5.4.40",
    "display_name": _("crossCertificatePair"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.10)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"gn": {
    "oid": "2.5.4.42",
    "display_name": _("gn givenName"),
    "alias": ['givenName'],
    "profile_field_name": 'first_name',
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
                ],
            "friendly_names":
                [
            "First Name",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"initials": {
    "oid": "2.5.4.43",
    "display_name": _("initials"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"generationQualifier": {
    "oid": "2.5.4.44",
    "display_name": _("generationQualifier"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"x500UniqueIdentifier": {
    "oid": "2.5.4.45",
    "display_name": _("x500UniqueIdentifier"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.6)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"dnQualifier": {
    "oid": "2.5.4.46",
    "display_name": _("dnQualifier"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.44)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"enhancedSearchGuide": {
    "oid": "2.5.4.47",
    "display_name": _("enhancedSearchGuide"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.21)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"protocolInformation": {
    "oid": "2.5.4.48",
    "display_name": _("protocolInformation"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.42)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"uniqueMember": {
    "oid": "2.5.4.50",
    "display_name": _("uniqueMember"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.34)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"houseIdentifier": {
    "oid": "2.5.4.51",
    "display_name": _("houseIdentifier"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{32768})",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"supportedAlgorithms": {
    "oid": "2.5.4.52",
    "display_name": _("supportedAlgorithms"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.49)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"deltaRevocationList": {
    "oid": "2.5.4.53",
    "display_name": _("deltaRevocationList"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.9)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"dmdName": {
    "oid": "2.5.4.54",
    "display_name": _("dmdName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"pseudonym": {
    "oid": "2.5.4.65",
    "display_name": _("pseudonym"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"mail": {
    "oid": "0.9.2342.19200300.100.1.3",
    "display_name": _("mail rfc822Mailbox"),
    "alias": ['rfc822Mailbox'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"dc": {
    "oid": "0.9.2342.19200300.100.1.25",
    "display_name": _("dc domainComponent"),
    "alias": ['domainComponent'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"associatedDomain": {
    "oid": "0.9.2342.19200300.100.1.37",
    "display_name": _("associatedDomain"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/core.ldif
"email": {
    "oid": "1.2.840.113549.1.9.1",
    "display_name": _("email pkcs9email emailAddress"),
    "alias": ['pkcs9email', 'emailAddress'],
    "profile_field_name": 'email',
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                ],
            "friendly_names":
                [
            "Email Address",
                ],
        }
    }
},


#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"textEncodedORAddress": {
    "oid": "0.9.2342.19200300.100.1.2",
    "display_name": _("textEncodedORAddress"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"info": {
    "oid": "0.9.2342.19200300.100.1.4",
    "display_name": _("info"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{2048})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"drink": {
    "oid": "0.9.2342.19200300.100.1.5",
    "display_name": _("drink favouriteDrink"),
    "alias": ['favouriteDrink'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"roomNumber": {
    "oid": "0.9.2342.19200300.100.1.6",
    "display_name": _("roomNumber"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"photo": {
    "oid": "0.9.2342.19200300.100.1.7",
    "display_name": _("photo"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.23{25000})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"userClass": {
    "oid": "0.9.2342.19200300.100.1.8",
    "display_name": _("userClass"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"host": {
    "oid": "0.9.2342.19200300.100.1.9",
    "display_name": _("host"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"manager": {
    "oid": "0.9.2342.19200300.100.1.10",
    "display_name": _("manager"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"documentIdentifier": {
    "oid": "0.9.2342.19200300.100.1.11",
    "display_name": _("documentIdentifier"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"documentTitle": {
    "oid": "0.9.2342.19200300.100.1.12",
    "display_name": _("documentTitle"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"documentVersion": {
    "oid": "0.9.2342.19200300.100.1.13",
    "display_name": _("documentVersion"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"documentAuthor": {
    "oid": "0.9.2342.19200300.100.1.14",
    "display_name": _("documentAuthor"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"documentLocation": {
    "oid": "0.9.2342.19200300.100.1.15",
    "display_name": _("documentLocation"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"homePhone": {
    "oid": "0.9.2342.19200300.100.1.20",
    "display_name": _("homePhone homeTelephoneNumber"),
    "alias": ['homeTelephoneNumber'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/homephone",
                ],
            "friendly_names":
                [
            "Primary or Home Telephone Number",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"secretary": {
    "oid": "0.9.2342.19200300.100.1.21",
    "display_name": _("secretary"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"otherMailbox": {
    "oid": "0.9.2342.19200300.100.1.22",
    "display_name": _("otherMailbox"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"aRecord": {
    "oid": "0.9.2342.19200300.100.1.26",
    "display_name": _("aRecord"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"mDRecord": {
    "oid": "0.9.2342.19200300.100.1.27",
    "display_name": _("mDRecord"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"mXRecord": {
    "oid": "0.9.2342.19200300.100.1.28",
    "display_name": _("mXRecord"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"nSRecord": {
    "oid": "0.9.2342.19200300.100.1.29",
    "display_name": _("nSRecord"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"sOARecord": {
    "oid": "0.9.2342.19200300.100.1.30",
    "display_name": _("sOARecord"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"cNAMERecord": {
    "oid": "0.9.2342.19200300.100.1.31",
    "display_name": _("cNAMERecord"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"associatedName": {
    "oid": "0.9.2342.19200300.100.1.38",
    "display_name": _("associatedName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"homePostalAddress": {
    "oid": "0.9.2342.19200300.100.1.39",
    "display_name": _("homePostalAddress"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.41)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"personalTitle": {
    "oid": "0.9.2342.19200300.100.1.40",
    "display_name": _("personalTitle"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"mobile": {
    "oid": "0.9.2342.19200300.100.1.41",
    "display_name": _("mobile mobileTelephoneNumber"),
    "alias": ['mobileTelephoneNumber'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/mobilephone",
                ],
            "friendly_names":
                [
            "Mobile Telephone Number",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"pager": {
    "oid": "0.9.2342.19200300.100.1.42",
    "display_name": _("pager pagerTelephoneNumber"),
    "alias": ['pagerTelephoneNumber'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"co": {
    "oid": "0.9.2342.19200300.100.1.43",
    "display_name": _("co friendlyCountryName"),
    "alias": ['friendlyCountryName'],
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "namespaces": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
            "identifiers":
                [
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/country",
                ],
            "friendly_names":
                [
            "Country",
                ],
        }
    }
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"uniqueIdentifier": {
    "oid": "0.9.2342.19200300.100.1.44",
    "display_name": _("uniqueIdentifier"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"organizationalStatus": {
    "oid": "0.9.2342.19200300.100.1.45",
    "display_name": _("organizationalStatus"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"janetMailbox": {
    "oid": "0.9.2342.19200300.100.1.46",
    "display_name": _("janetMailbox"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"mailPreferenceOption": {
    "oid": "0.9.2342.19200300.100.1.47",
    "display_name": _("mailPreferenceOption"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.27)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"buildingName": {
    "oid": "0.9.2342.19200300.100.1.48",
    "display_name": _("buildingName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"dSAQuality": {
    "oid": "0.9.2342.19200300.100.1.49",
    "display_name": _("dSAQuality"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.19",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"singleLevelQuality": {
    "oid": "0.9.2342.19200300.100.1.50",
    "display_name": _("singleLevelQuality"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.13",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"subtreeMinimumQuality": {
    "oid": "0.9.2342.19200300.100.1.51",
    "display_name": _("subtreeMinimumQuality"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.13",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"subtreeMaximumQuality": {
    "oid": "0.9.2342.19200300.100.1.52",
    "display_name": _("subtreeMaximumQuality"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.13",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"personalSignature": {
    "oid": "0.9.2342.19200300.100.1.53",
    "display_name": _("personalSignature"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"dITRedirect": {
    "oid": "0.9.2342.19200300.100.1.54",
    "display_name": _("dITRedirect"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12)",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"audio": {
    "oid": "0.9.2342.19200300.100.1.55",
    "display_name": _("audio"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.4{25000})",
},

#Extracted from openldap schema /etc/ldap/schema/cosine.ldif
"documentPublisher": {
    "oid": "0.9.2342.19200300.100.1.56",
    "display_name": _("documentPublisher"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15)",
},


#Extracted from openldap schema /etc/ldap/schema/misc.ldif
"mailLocalAddress": {
    "oid": "2.16.840.1.113730.3.1.13",
    "display_name": _("mailLocalAddress"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{256})",
},

#Extracted from openldap schema /etc/ldap/schema/misc.ldif
"mailHost": {
    "oid": "2.16.840.1.113730.3.1.18",
    "display_name": _("mailHost"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{256}",
},

#Extracted from openldap schema /etc/ldap/schema/misc.ldif
"mailRoutingAddress": {
    "oid": "2.16.840.1.113730.3.1.47",
    "display_name": _("mailRoutingAddress"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{256}",
},

#Extracted from openldap schema /etc/ldap/schema/misc.ldif
"rfc822MailMember": {
    "oid": "1.3.6.1.4.1.42.2.27.2.1.15",
    "display_name": _("rfc822MailMember"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonAffiliation": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.1",
    "display_name": _("eduPersonAffiliation"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonNickname": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.2",
    "display_name": _("eduPersonNickname"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonOrgDN": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.3",
    "display_name": _("eduPersonOrgDN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonOrgUnitDN": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.4",
    "display_name": _("eduPersonOrgUnitDN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonPrimaryAffiliation": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.5",
    "display_name": _("eduPersonPrimaryAffiliation"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonPrincipalName": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.6",
    "display_name": _("eduPersonPrincipalName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonEntitlement": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.7",
    "display_name": _("eduPersonEntitlement"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonPrimaryOrgUnitDN": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.8",
    "display_name": _("eduPersonPrimaryOrgUnitDN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonScopedAffiliation": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.9",
    "display_name": _("eduPersonScopedAffiliation"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonTargetedID": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.10",
    "display_name": _("eduPersonTargetedID"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduPerson schema in ldif format for OpenLDAP
#last edited by Etan E. Weintraub on May 27, 2009
"eduPersonAssurance": {
    "oid": "1.3.6.1.4.1.5923.1.1.1.11",
    "display_name": _("eduPersonAssurance"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduOrg schema in ldif format
#eduOrg Objectclass version 1.1 (2002-10-23)
"eduOrgHomePageURI": {
    "oid": ":1.3.6.1.4.1.5923.1.2.1.2",
    "display_name": _("eduOrgHomePageURI"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduOrg schema in ldif format
#eduOrg Objectclass version 1.1 (2002-10-23)
"eduOrgIdentityAuthNPolicyURI": {
    "oid": ":1.3.6.1.4.1.5923.1.2.1.3",
    "display_name": _("eduOrgIdentityAuthNPolicyURI"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduOrg schema in ldif format
#eduOrg Objectclass version 1.1 (2002-10-23)
"eduOrgLegalName": {
    "oid": ":1.3.6.1.4.1.5923.1.2.1.4",
    "display_name": _("eduOrgLegalName"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduOrg schema in ldif format
#eduOrg Objectclass version 1.1 (2002-10-23)
"eduOrgSuperiorURI": {
    "oid": ":1.3.6.1.4.1.5923.1.2.1.5",
    "display_name": _("eduOrgSuperiorURI"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from eduOrg schema in ldif format
#eduOrg Objectclass version 1.1 (2002-10-23)
"eduOrgWhitePagesURI": {
    "oid": ":1.3.6.1.4.1.5923.1.2.1.6",
    "display_name": _("eduOrgWhitePagesURI"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannListeRouge": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.1",
    "display_name": _("supannListeRouge"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.7",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannActivite": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.2",
    "display_name": _("supannActivite"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannOrganisme": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.3",
    "display_name": _("supannOrganisme"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannCivilite": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.4",
    "display_name": _("supannCivilite"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.44{32}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannAffectation": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.5",
    "display_name": _("supannAffectation"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannCodeEntite": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.6",
    "display_name": _("supannCodeEntite"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannCodeEntiteParent": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.7",
    "display_name": _("supannCodeEntiteParent"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEntiteAffectation": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.8",
    "display_name": _("supannEntiteAffectation"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannCodeINE": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.9",
    "display_name": _("supannCodeINE"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.44{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuId": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.10",
    "display_name": _("supannEtuId"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEmpId": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.11",
    "display_name": _("supannEmpId"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannAutreTelephone": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.12",
    "display_name": _("supannAutreTelephone"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.50",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEntiteAffectationPrincipale": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.13",
    "display_name": _("supannEntiteAffectationPrincipale"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtablissement": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.14",
    "display_name": _("supannEtablissement"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannMailPerso": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.15",
    "display_name": _("supannMailPerso"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{256}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannTypeEntite": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.16",
    "display_name": _("supannTypeEntite"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannParrainDN": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.17",
    "display_name": _("supannParrainDN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannGroupeDateFin": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.18",
    "display_name": _("supannGroupeDateFin"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.24",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannGroupeAdminDN": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.19",
    "display_name": _("supannGroupeAdminDN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannAliasLogin": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.20",
    "display_name": _("supannAliasLogin"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannRole": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.21",
    "display_name": _("supannRole"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannGroupeLecteurDN": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.22",
    "display_name": _("supannGroupeLecteurDN"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.12",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannRoleGenerique": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.23",
    "display_name": _("supannRoleGenerique"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{256}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannRoleEntite": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.24",
    "display_name": _("supannRoleEntite"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{512}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuAnneeInscription": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.25",
    "display_name": _("supannEtuAnneeInscription"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.36{4}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuCursusAnnee": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.26",
    "display_name": _("supannEtuCursusAnnee"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuDiplome": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.27",
    "display_name": _("supannEtuDiplome"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuElementPedagogique": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.28",
    "display_name": _("supannEtuElementPedagogique"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuEtape": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.29",
    "display_name": _("supannEtuEtape"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuInscription": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.30",
    "display_name": _("supannEtuInscription"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{4096}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuRegimeInscription": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.31",
    "display_name": _("supannEtuRegimeInscription"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuSecteurDisciplinaire": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.32",
    "display_name": _("supannEtuSecteurDisciplinaire"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEtuTypeDiplome": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.33",
    "display_name": _("supannEtuTypeDiplome"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannAutreMail": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.34",
    "display_name": _("supannAutreMail"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.26{256}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannEmpCorps": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.35",
    "display_name": _("supannEmpCorps"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannTypeEntiteAffectation": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.36",
    "display_name": _("supannTypeEntiteAffectation"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

#Extracted from version 389 Directory Server du schema
#SupAnn version 2009.6
#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt
"supannRefId": {
    "oid": "1.3.6.1.4.1.7135.1.2.1.37",
    "display_name": _("supannRefId"),
    "type": "http://www.w3.org/2001/XMLSchema#string",
    "syntax": "1.3.6.1.4.1.1466.115.121.1.15{128}",
},

}
