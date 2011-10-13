'''
    VERIDIC - Towards a centralized access control system

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

'''
    (Core - 3958) For the sake of improved interoperability, it is RECOMMENDED
    that all time references be in UTC time.
    (Core - 3960) For doubles, XACML SHALL use the conversions described in
    [IEEE754]
'''

#RENAME me to XACML constants!

from django.utils.translation import ugettext as _


ACS_XACML_DATATYPE_STRING = "http://www.w3.org/2001/XMLSchema#string"
ACS_XACML_DATATYPE_BOOLEAN = "http://www.w3.org/2001/XMLSchema#boolean"
ACS_XACML_DATATYPE_INTEGER = "http://www.w3.org/2001/XMLSchema#integer"
ACS_XACML_DATATYPE_DOUBLE = "http://www.w3.org/2001/XMLSchema#double"
ACS_XACML_DATATYPE_TIME = "http://www.w3.org/2001/XMLSchema#time"
ACS_XACML_DATATYPE_DATE = "http://www.w3.org/2001/XMLSchema#date"
ACS_XACML_DATATYPE_DATETIME = "http://www.w3.org/2001/XMLSchema#dateTime"
#ACS_XACML_DATATYPE_ANYURI = "http://www.w3.org/2001/XMLSchema#anyURI"
#ACS_XACML_DATATYPE_HEXBINARY = "http://www.w3.org/2001/XMLSchema#hexBinary"
#ACS_XACML_DATATYPE_BASE64BINARY = \
#    "http://www.w3.org/2001/XMLSchema#base64Binary"
#ACS_XACML_DATATYPE_DAYTIMEDURATION = \
#    "http://www.w3.org/2001/XMLSchema#dayTimeDuration"
#ACS_XACML_DATATYPE_YEARMONTHDURATION = \
#    "http://www.w3.org/2001/XMLSchema#yearMonthDuration"


'''
An ITU-T Rec.X.520 Distinguished Name.
The valid syntax for such a name is described in IETF RFC 2253
"Lightweight Directory Access Protocol (v3): UTF-8 String Representation of
Distinguished Names".
'''
ACS_XACML_DATATYPE_X500NAME = \
    "urn:oasis:names:tc:xacml:1.0:data-type:x500Name"
'''
An electronic mail address. The valid syntax for such a name is described
in IETF RFC 2821, Section 4.1.2,
Command Argument Syntax, under the term "Mailbox".
'''
ACS_XACML_DATATYPE_RFC822NAME = \
    "urn:oasis:names:tc:xacml:1.0:data-type:rfc822Name"
'''
The syntax SHALL be:
ipAddress = address [ "/" mask ] [ ":" [ portrange ] ]
For an IPv4 address, the address and mask are formatted in accordance with the syntax for a
"host" in IETF RFC 2396 "Uniform Resource Identifiers (URI): Generic Syntax", section 3.2.
For an IPv6 address, the address and mask are formatted in accordance with the syntax for an
"ipv6reference" in IETF RFC 2732 "Format for Literal IPv6 Addresses in URL's". (Note that an
IPv6 address or mask, in this syntax, is enclosed in literal "[" "]" brackets.)
'''
ACS_XACML_DATATYPE_IPADDRESS = \
    "urn:oasis:names:tc:xacml:2.0:data-type:ipAddress"
'''
The syntax SHALL be:
dnsName = hostname [ ":" portrange ]
The hostname is formatted in accordance with IETF RFC 2396 "Uniform Resource Identifiers
(URI): Generic Syntax", section 3.2, except that a wildcard "*" may be used in the left-most
component of the hostname to indicate "any subdomain" under the domain specified to its right.
For both the "urn:oasis:names:tc:xacml:2.0:data-type:ipAddress" and
"urn:oasis:names:tc:xacml:2.0:data-type:dnsName" data-types, the port or port range syntax
SHALL be
portrange = portnumber | "-"portnumber | portnumber"-"[portnumber]
where "portnumber" is a decimal port number. If the port number is of the form "-x", where "x" is
a port number, then the range is all ports numbered "x" and below. If the port number is of the
form "x-", then the range is all ports numbered "x" and above. [This syntax is taken from the Java
SocketPermission.]
'''
ACS_XACML_DATATYPE_DNSNAME = \
    "urn:oasis:names:tc:xacml:2.0:data-type:dnsName"
ACS_XACML_DATATYPE_XPATHEXPRESSION = \
    "urn:oasis:names:tc:xacml:3.0:data-type:xpathExpression"

XACML_DATA_TYPE = (
    (ACS_XACML_DATATYPE_STRING, _('String')),
    (ACS_XACML_DATATYPE_BOOLEAN, _('Boolean')),
    (ACS_XACML_DATATYPE_INTEGER, _('Integer')),
    (ACS_XACML_DATATYPE_DOUBLE, _('Double')),
    (ACS_XACML_DATATYPE_TIME, _('Time')),
    (ACS_XACML_DATATYPE_DATE, _('Date')),
    (ACS_XACML_DATATYPE_DATETIME, _('Date and Time')),
#    (ACS_XACML_DATATYPE_ANYURI, _('Any URI')),
#    (ACS_XACML_DATATYPE_HEXBINARY, _('Hex Binary')),
#    (ACS_XACML_DATATYPE_BASE64BINARY, _('Base64 Binary')),
#    (ACS_XACML_DATATYPE_DAYTIMEDURATION, _('Day Time Duration')),
#    (ACS_XACML_DATATYPE_YEARMONTHDURATION, _('Year Month Duration')),
#    (ACS_XACML_DATATYPE_X500NAME, _('X500 name')),
    (ACS_XACML_DATATYPE_RFC822NAME, _('email address')),
    (ACS_XACML_DATATYPE_IPADDRESS, _('IP address')),
#    (ACS_XACML_DATATYPE_DNSNAME, _('DNS name')),
#    (ACS_XACML_DATATYPE_XPATHEXPRESSION, _('XPATH expression')),
)

ACS_XACML_COMPARISON_EQUALITY_STRING = \
    "urn:oasis:names:tc:xacml:1.0:function:string-equal"
ACS_XACML_COMPARISON_EQUALITY_STRING_IGN_CASE = \
    "urn:oasis:names:tc:xacml:3.0:function:string-equal-ignore-case"
ACS_XACML_COMPARISON_EQUALITY_BOOLEAN = \
    "urn:oasis:names:tc:xacml:1.0:function:boolean-equal"
ACS_XACML_COMPARISON_EQUALITY_INTEGER = \
    "urn:oasis:names:tc:xacml:1.0:function:integer-equal"
ACS_XACML_COMPARISON_EQUALITY_DOUBLE = \
    "urn:oasis:names:tc:xacml:1.0:function:double-equal"
ACS_XACML_COMPARISON_EQUALITY_DATE = \
    "urn:oasis:names:tc:xacml:1.0:function:date-equal"
ACS_XACML_COMPARISON_EQUALITY_TIME = \
    "urn:oasis:names:tc:xacml:1.0:function:time-equal"
ACS_XACML_COMPARISON_EQUALITY_DATETIME = \
    "urn:oasis:names:tc:xacml:1.0:function:dateTime-equal"
ACS_XACML_COMPARISON_EQUALITY_DAYTIMEDURATION = \
    "urn:oasis:names:tc:xacml:3.0:function:dayTimeDuration-equal"
ACS_XACML_COMPARISON_EQUALITY_YEARMONTHDURATION = \
    "urn:oasis:names:tc:xacml:3.0:function:yearMonthDuration-equal"
ACS_XACML_COMPARISON_EQUALITY_ANYURI = \
    "urn:oasis:names:tc:xacml:1.0:function:anyURI-equal"
ACS_XACML_COMPARISON_EQUALITY_X500NAME = \
    "urn:oasis:names:tc:xacml:1.0:function:x500Name-equal"
ACS_XACML_COMPARISON_EQUALITY_RFC822NAME = \
    "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-equal"
ACS_XACML_COMPARISON_EQUALITY_IPADDRESS = \
    "urn:oasis:names:tc:xacml:1.0:function:ipAddress-equal"
ACS_XACML_COMPARISON_EQUALITY_HEXBINARY = \
    "urn:oasis:names:tc:xacml:1.0:function:hexBinary-equal"
ACS_XACML_COMPARISON_EQUALITY_BASE64BINARY = \
    "urn:oasis:names:tc:xacml:1.0:function:base64Binary-equal"

XACML_COMPARISON_EQUALITY = (
    ACS_XACML_COMPARISON_EQUALITY_STRING,
    ACS_XACML_COMPARISON_EQUALITY_STRING_IGN_CASE,
    ACS_XACML_COMPARISON_EQUALITY_BOOLEAN,
    ACS_XACML_COMPARISON_EQUALITY_INTEGER,
    ACS_XACML_COMPARISON_EQUALITY_DOUBLE,
    ACS_XACML_COMPARISON_EQUALITY_DATE,
    ACS_XACML_COMPARISON_EQUALITY_TIME,
    ACS_XACML_COMPARISON_EQUALITY_DATETIME,
#    ACS_XACML_COMPARISON_EQUALITY_DAYTIMEDURATION, _('Day Time Duration equality')),
#    ACS_XACML_COMPARISON_EQUALITY_YEARMONTHDURATION, _('Year Month Duration equality')),
#    ACS_XACML_COMPARISON_EQUALITY_ANYURI, _('Any URI equality')),
#    ACS_XACML_COMPARISON_EQUALITY_X500NAME, _('X500 name equality')),
    ACS_XACML_COMPARISON_EQUALITY_RFC822NAME,
    ACS_XACML_COMPARISON_EQUALITY_IPADDRESS,
#    ACS_XACML_COMPARISON_EQUALITY_HEXBINARY, _('Hex binary equality')),
#    ACS_XACML_COMPARISON_EQUALITY_BASE64BINARY, _('base 64 binary equality')),
)

XACML_COMPARISON_EQUALITY_TYPE = (
    (ACS_XACML_COMPARISON_EQUALITY_STRING, _('String equality')),
    (ACS_XACML_COMPARISON_EQUALITY_STRING_IGN_CASE, _('String equality ignoring case')),
    (ACS_XACML_COMPARISON_EQUALITY_BOOLEAN, _('Boolean equality')),
    (ACS_XACML_COMPARISON_EQUALITY_INTEGER, _('Integer equality')),
    (ACS_XACML_COMPARISON_EQUALITY_DOUBLE, _('Double equality')),
    (ACS_XACML_COMPARISON_EQUALITY_DATE, _('Date equality')),
    (ACS_XACML_COMPARISON_EQUALITY_TIME, _('Time equality')),
    (ACS_XACML_COMPARISON_EQUALITY_DATETIME, _('DateTime equality')),
#    (ACS_XACML_COMPARISON_EQUALITY_DAYTIMEDURATION, _('Day Time Duration equality')),
#    (ACS_XACML_COMPARISON_EQUALITY_YEARMONTHDURATION, _('Year Month Duration equality')),
#    (ACS_XACML_COMPARISON_EQUALITY_ANYURI, _('Any URI equality')),
#    (ACS_XACML_COMPARISON_EQUALITY_X500NAME, _('X500 name equality')),
    (ACS_XACML_COMPARISON_EQUALITY_RFC822NAME, _('email equality')),
    (ACS_XACML_COMPARISON_EQUALITY_IPADDRESS, _('IP address equality')),
#    (ACS_XACML_COMPARISON_EQUALITY_HEXBINARY, _('Hex binary equality')),
#    (ACS_XACML_COMPARISON_EQUALITY_BASE64BINARY, _('base 64 binary equality')),
)

XACML_COMPARISON_EQUALITY_TYPE_DIC = {
    ACS_XACML_COMPARISON_EQUALITY_STRING: _('String equality'),
    ACS_XACML_COMPARISON_EQUALITY_STRING_IGN_CASE: _('String equality ignoring case'),
    ACS_XACML_COMPARISON_EQUALITY_BOOLEAN: _('Boolean equality'),
    ACS_XACML_COMPARISON_EQUALITY_INTEGER: _('Integer equality'),
    ACS_XACML_COMPARISON_EQUALITY_DOUBLE: _('Double equality'),
    ACS_XACML_COMPARISON_EQUALITY_DATE: _('Date equality'),
    ACS_XACML_COMPARISON_EQUALITY_TIME: _('Time equality'),
    ACS_XACML_COMPARISON_EQUALITY_DATETIME: _('DateTime equality'),
#    ACS_XACML_COMPARISON_EQUALITY_DAYTIMEDURATION: _('Day Time Duration equality'),
#    ACS_XACML_COMPARISON_EQUALITY_YEARMONTHDURATION: _('Year Month Duration equality'),
#    ACS_XACML_COMPARISON_EQUALITY_ANYURI: _('Any URI equality'),
#    ACS_XACML_COMPARISON_EQUALITY_X500NAME: _('X500 name equality'),
    ACS_XACML_COMPARISON_EQUALITY_RFC822NAME: _('email equality'),
    ACS_XACML_COMPARISON_EQUALITY_IPADDRESS: _('IP address equality'),
#    ACS_XACML_COMPARISON_EQUALITY_HEXBINARY: _('Hex binary equality'),
#    ACS_XACML_COMPARISON_EQUALITY_BASE64BINARY: _('base 64 binary equality'),
}

ACS_XACML_COMPARISON_INTEGER_GRT = \
    "urn:oasis:names:tc:xacml:1.0:function:integer-greater-than"
ACS_XACML_COMPARISON_INTEGER_GRT_OE = \
    "urn:oasis:names:tc:xacml:1.0:function:integer-greater-than-or-equal"
ACS_XACML_COMPARISON_INTEGER_LT = \
    "urn:oasis:names:tc:xacml:1.0:function:integer-less-than"
ACS_XACML_COMPARISON_INTEGER_LT_OE = \
    "urn:oasis:names:tc:xacml:1.0:function:integer-less-than-or-equal"
ACS_XACML_COMPARISON_DOUBLE_GRT = \
    "urn:oasis:names:tc:xacml:1.0:function:double-greater-than"
ACS_XACML_COMPARISON_DOUBLE_GRT_OE = \
    "urn:oasis:names:tc:xacml:1.0:function:double-greater-than-or-equal"
ACS_XACML_COMPARISON_DOUBLE_LT = \
    "urn:oasis:names:tc:xacml:1.0:function:double-less-than"
ACS_XACML_COMPARISON_DOUBLE_LT_OE = \
    "urn:oasis:names:tc:xacml:1.0:function:double-less-than-or-equal"

ACS_XACML_COMPARISON_GRT = (
    ACS_XACML_COMPARISON_INTEGER_GRT,
    ACS_XACML_COMPARISON_DOUBLE_GRT,
)
ACS_XACML_COMPARISON_GRT_OE = (
    ACS_XACML_COMPARISON_INTEGER_GRT_OE,
    ACS_XACML_COMPARISON_DOUBLE_GRT_OE,
)
ACS_XACML_COMPARISON_LT = (
    ACS_XACML_COMPARISON_INTEGER_LT,
    ACS_XACML_COMPARISON_DOUBLE_LT,
)
ACS_XACML_COMPARISON_LT_OE = (
    ACS_XACML_COMPARISON_INTEGER_LT_OE,
    ACS_XACML_COMPARISON_DOUBLE_LT_OE,
)

ACS_XACML_COMPARISON = ACS_XACML_COMPARISON_GRT \
    + ACS_XACML_COMPARISON_GRT_OE \
    + ACS_XACML_COMPARISON_LT \
    + ACS_XACML_COMPARISON_LT_OE

XACML_COMPARISON_DIFF_TYPE = (
    (ACS_XACML_COMPARISON_INTEGER_GRT, _('Integer 1 greater than integer 2')),
    (ACS_XACML_COMPARISON_INTEGER_GRT_OE, _('Integer 1 greater than or equal integer 2')),
    (ACS_XACML_COMPARISON_INTEGER_LT, _('Integer 1 less than integer 2')),
    (ACS_XACML_COMPARISON_INTEGER_LT_OE, _('Integer 1 less than or equal integer 2')),
    (ACS_XACML_COMPARISON_DOUBLE_GRT, _('Double 1 greater than double 2')),
    (ACS_XACML_COMPARISON_DOUBLE_GRT_OE, _('Double 1 greater than or equal double 2')),
    (ACS_XACML_COMPARISON_DOUBLE_LT, _('Double 1 less than double 2')),
    (ACS_XACML_COMPARISON_DOUBLE_LT_OE, _('Double 1 less than or equal double 2')),
)

XACML_COMPARISON_DIFF_TYPE_DIC = {
    ACS_XACML_COMPARISON_INTEGER_GRT: _('Integer 1 greater than integer 2'),
    ACS_XACML_COMPARISON_INTEGER_GRT_OE: _('Integer 1 greater than or equal integer 2'),
    ACS_XACML_COMPARISON_INTEGER_LT: _('Integer 1 less than integer 2'),
    ACS_XACML_COMPARISON_INTEGER_LT_OE: _('Integer 1 less than or equal integer 2'),
    ACS_XACML_COMPARISON_DOUBLE_GRT: _('Double 1 greater than double 2'),
    ACS_XACML_COMPARISON_DOUBLE_GRT_OE: _('Double 1 greater than or equal double 2'),
    ACS_XACML_COMPARISON_DOUBLE_LT: _('Double 1 less than double 2'),
    ACS_XACML_COMPARISON_DOUBLE_LT_OE: _('Double 1 less than or equal double 2'),
}

XACML_COMPARISON_TYPE_DIC = dict(XACML_COMPARISON_EQUALITY_TYPE_DIC.items() \
    + XACML_COMPARISON_DIFF_TYPE_DIC.items())

XACML_COMPARISON_TYPE = XACML_COMPARISON_EQUALITY_TYPE + XACML_COMPARISON_DIFF_TYPE

ACS_COMP_TYPE = {
    ACS_XACML_COMPARISON_INTEGER_GRT: ACS_XACML_DATATYPE_INTEGER,
    ACS_XACML_COMPARISON_INTEGER_GRT_OE: ACS_XACML_DATATYPE_INTEGER,
    ACS_XACML_COMPARISON_INTEGER_LT: ACS_XACML_DATATYPE_INTEGER,
    ACS_XACML_COMPARISON_INTEGER_LT_OE: ACS_XACML_DATATYPE_INTEGER,
    ACS_XACML_COMPARISON_DOUBLE_GRT: ACS_XACML_DATATYPE_DOUBLE,
    ACS_XACML_COMPARISON_DOUBLE_GRT_OE: ACS_XACML_DATATYPE_DOUBLE,
    ACS_XACML_COMPARISON_DOUBLE_LT: ACS_XACML_DATATYPE_DOUBLE,
    ACS_XACML_COMPARISON_DOUBLE_LT_OE: ACS_XACML_DATATYPE_DOUBLE,
    ACS_XACML_COMPARISON_EQUALITY_STRING: ACS_XACML_DATATYPE_STRING,
    ACS_XACML_COMPARISON_EQUALITY_STRING_IGN_CASE: ACS_XACML_DATATYPE_STRING,
    ACS_XACML_COMPARISON_EQUALITY_BOOLEAN: ACS_XACML_DATATYPE_BOOLEAN,
    ACS_XACML_COMPARISON_EQUALITY_INTEGER: ACS_XACML_DATATYPE_INTEGER,
    ACS_XACML_COMPARISON_EQUALITY_DOUBLE: ACS_XACML_DATATYPE_DOUBLE,
    ACS_XACML_COMPARISON_EQUALITY_DATE: ACS_XACML_DATATYPE_DATE,
    ACS_XACML_COMPARISON_EQUALITY_TIME: ACS_XACML_DATATYPE_TIME,
    ACS_XACML_COMPARISON_EQUALITY_DATETIME: ACS_XACML_DATATYPE_DATETIME,
#    ACS_XACML_COMPARISON_EQUALITY_DAYTIMEDURATION: ACS_XACML_DATATYPE_DAYTIMEDURATION,
#    ACS_XACML_COMPARISON_EQUALITY_YEARMONTHDURATION: ACS_XACML_DATATYPE_YEARMONTHDURATION,
#    ACS_XACML_COMPARISON_EQUALITY_ANYURI: ACS_XACML_DATATYPE_ANYURI,
#    ACS_XACML_COMPARISON_EQUALITY_X500NAME: ACS_XACML_DATATYPE_X500NAME,
    ACS_XACML_COMPARISON_EQUALITY_RFC822NAME: ACS_XACML_DATATYPE_RFC822NAME,
    ACS_XACML_COMPARISON_EQUALITY_IPADDRESS: ACS_XACML_DATATYPE_IPADDRESS,
#    ACS_XACML_COMPARISON_EQUALITY_HEXBINARY: ACS_XACML_DATATYPE_HEXBINARY,
#    ACS_XACML_COMPARISON_EQUALITY_BASE64BINARY: ACS_XACML_DATATYPE_BASE64BINARY,
}
