
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

