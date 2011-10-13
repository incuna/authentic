import sys, re

#f = open("./eduperson.ldif", 'rb')
#try:
#    while(True):
#        r = f.next()
#        if r.find('#') == 0:
#            pass
##            print "Comment: " + r
#        else:
#            a, b, val = r.partition('attributeType')
#            if val:
#                oid = val
#                for it in [' ', '\(', '\n']:
#                    oid = re.sub(it, '', oid)
#                a, b, name = f.next().partition('NAME')
#                for it in [' ', '\'', '\n']:
#                    name = re.sub(it, '', name)
#                a, b, syntax = f.next().partition('SYNTAX')
#                while not syntax:
#                    a, b, syntax = f.next().partition('SYNTAX')
#                for it in [' ', '\'', '\n', '\)']:
#                    syntax = re.sub(it, '', syntax)
#                print '#Extracted from eduPerson schema in ldif format for OpenLDAP'
#                print '#last edited by Etan E. Weintraub on May 27, 2009'
#                print '"' + name + '": {'
#                print '    "oid": "' + oid + '",'
#                print '    "display_name": _("' + name + '"),'
#                print '    "type": "http://www.w3.org/2001/XMLSchema#string",'
#                print '    "syntax": "' + syntax + '",'
#    #            print '    "namespaces": {'
#    #            print '        "eduPerson": {'
#    #            print '            "identifiers":'
##                print '    }'
#                print '},\n'
#except Exception, err:
#    print err

#f = open("./eduorg.ldif", 'rb')
#try:
#    while(True):
#        r = f.next()
#        if r.find('#') == 0:
#            pass
##            print "Comment: " + r
#        else:
#            a, b, val = r.partition('attributetypes')
#            if val:
#                oid = val
#                for it in [' ', '\(', '\n']:
#                    oid = re.sub(it, '', oid)
#                a, b, name = f.next().partition('NAME')
#                for it in [' ', '\'', '\n']:
#                    name = re.sub(it, '', name)
#                a, b, syntax = f.next().partition('SYNTAX')
#                while not syntax:
#                    a, b, syntax = f.next().partition('SYNTAX')
#                for it in [' ', '\'', '\n', '\)']:
#                    syntax = re.sub(it, '', syntax)
#                print '#Extracted from eduOrg schema in ldif format'
#                print '#eduOrg Objectclass version 1.1 (2002-10-23)'
#                print '"' + name + '": {'
#                print '    "oid": "' + oid + '",'
#                print '    "display_name": _("' + name + '"),'
#                print '    "type": "http://www.w3.org/2001/XMLSchema#string",'
#                print '    "syntax": "' + syntax + '",'
#    #            print '    "namespaces": {'
#    #            print '        "eduPerson": {'
#    #            print '            "identifiers":'
##                print '    }'
#                print '},\n'
#except Exception, err:
#    print err

#f = open("./60supann.ldif.txt", 'rb')
#try:
#    while(True):
#        r = f.next()
#        if r.find('#') == 0:
#            pass
##            print "Comment: " + r
#        else:
#            a, b, val = r.partition('attributeTypes')
#            if val:
#                oid = f.next()
#                for it in [' ', '\n']:
#                    oid = re.sub(it, '', oid)
#                a, b, name = f.next().partition('NAME')
#                for it in [' ', '\'', '\n']:
#                    name = re.sub(it, '', name)
#                a, b, syntax = f.next().partition('SYNTAX')
#                while not syntax:
#                    a, b, syntax = f.next().partition('SYNTAX')
#                for it in [' ', '\'', '\n', '\)']:
#                    syntax = re.sub(it, '', syntax)
#                print '#Extracted from version 389 Directory Server du schema'
#                print '#SupAnn version 2009.6'
#                print '#http://www.cru.fr/_media/documentation/supann/supann_2009.schema.txt'
#                print '"' + name + '": {'
#                print '    "oid": "' + oid + '",'
#                print '    "display_name": _("' + name + '"),'
#                print '    "type": "http://www.w3.org/2001/XMLSchema#string",'
#                print '    "syntax": "' + syntax + '",'
#    #            print '    "namespaces": {'
#    #            print '        "eduPerson": {'
#    #            print '            "identifiers":'
##                print '    }'
#                print '},\n'
#except Exception, err:
#    print err

#import os
#PATH = '/etc/ldap/schema/'
#l = [f for f in os.listdir(PATH) if f.rfind('.ldif') > 0]
#for f_n in l:
#    f = open(PATH + f_n, 'rb')
#    try:
#        while(True):
#            r = f.next()
#            if r.find('#') == 0:
#                pass
##                print "Comment: " + r
#            else:
#                a, b, val = r.partition('olcAttributeTypes:')
#                if val:
#                    exit = False
#                    if val.rfind(')') > 0:
#                        exit = True
#                    for it in [' ', '\n']:
##                    for it in [' ', '\'', '\n', '\(', '\)']:
#                        val = re.sub(it, '', val)
#                    s = val

#                    if not exit:
#                        found = False
#                        while not found:
#                            ligne = f.next()
#                            if ligne.rfind(')') > 0:
#                                found = True
#                            for it in [' ', '\n']:
##                            for it in [' ', '\'', '\n', '\(', '\)']:
#                                ligne = re.sub(it, '', ligne)
#                            s += ligne

#                    oid, b, s = s.partition('NAME')
#                    name, b, s2 = s.partition('DESC')
#                    if name == s:
#                        name, b, s2 = s.partition('EQUALITY')
#                    if name == s:
#                        name, b, s2 = s.partition('SYNTAX')
#                    names = None
#                    if name.find('(') == 0:
#                        for it in ['\(', '\)']:
#                            name = re.sub(it, '', name)
#                        names = [re.sub('\'', '', n) for n in name.split("'") if n]
#                        names.sort(key=lambda x: len(x))
#                    a, b, syntax = s2.partition('SYNTAX')
#                    syntax, a, b = syntax.partition('SINGLE-VALUE')

#                    for it in ['\'', '\(', '\)']:
#                        oid = re.sub(it, '', oid)

#                    if names:
#                        print '#Extracted from openldap schema ' +PATH + f_n
#                        print '"' + names[0] + '": {'
#                        display_name = ' '.join(names)
#                        names.pop(0)
#                        print '    "oid": "' + oid + '",'
#                        print '    "display_name": _("' + display_name + '"),'
#                        print '    "alias": ' + str(names) + ','
#                        print '    "type": "http://www.w3.org/2001/XMLSchema#string",'
#                        if syntax:
#                            print '    "syntax": "' + syntax + '",'
#                        print '},\n'
#                    else:
#                        for it in ['\'', '\(', '\)']:
#                            name = re.sub(it, '', name)
#                        print '#Extracted from openldap schema ' +PATH + f_n
#                        print '"' + name + '": {'
#                        print '    "oid": "' + oid + '",'
#                        print '    "display_name": _("' + name + '"),'
#                        print '    "type": "http://www.w3.org/2001/XMLSchema#string",'
#                        if syntax:
#                            print '    "syntax": "' + syntax + '",'
#                        print '},\n'
#    except Exception, err:
#        print err
#    f.close()

f = open("./openldap_system_schema", 'rb')
try:
    s = ''
    while(True):
        r = f.next()

        for it in [' ', '\n', '\t']:
            r = re.sub(it, '', r)

        s += r


#        if r.find('#') == 0:
#            pass
##                print "Comment: " + r
#        else:
#            a, b, val = r.partition('olcAttributeTypes:')
#            if val:
#                exit = False
#                if val.rfind(')') > 0:
#                    exit = True
#                for it in [' ', '\n']:
##                    for it in [' ', '\'', '\n', '\(', '\)']:
#                    val = re.sub(it, '', val)
#                s = val

#                if not exit:
#                    found = False
#                    while not found:
#                        ligne = f.next()
#                        if ligne.rfind(')') > 0:
#                            found = True
#                        for it in [' ', '\n']:
##                            for it in [' ', '\'', '\n', '\(', '\)']:
#                            ligne = re.sub(it, '', ligne)
#                        s += ligne

#                oid, b, s = s.partition('NAME')
#                name, b, s2 = s.partition('DESC')
#                if name == s:
#                    name, b, s2 = s.partition('EQUALITY')
#                if name == s:
#                    name, b, s2 = s.partition('SYNTAX')
#                names = None
#                if name.find('(') == 0:
#                    for it in ['\(', '\)']:
#                        name = re.sub(it, '', name)
#                    names = [re.sub('\'', '', n) for n in name.split("'") if n]
#                    names.sort(key=lambda x: len(x))
#                a, b, syntax = s2.partition('SYNTAX')
#                syntax, a, b = syntax.partition('SINGLE-VALUE')

#                for it in ['\'', '\(', '\)']:
#                    oid = re.sub(it, '', oid)

#                if names:
#                    print '#Extracted from openldap schema ' +PATH + f_n
#                    print '"' + names[0] + '": {'
#                    display_name = ' '.join(names)
#                    names.pop(0)
#                    print '    "oid": "' + oid + '",'
#                    print '    "display_name": _("' + display_name + '"),'
#                    print '    "alias": ' + str(names) + ','
#                    print '    "type": "http://www.w3.org/2001/XMLSchema#string",'
#                    if syntax:
#                        print '    "syntax": "' + syntax + '",'
#                    print '},\n'
#                else:
#                    for it in ['\'', '\(', '\)']:
#                        name = re.sub(it, '', name)
#                    print '#Extracted from openldap schema ' +PATH + f_n
#                    print '"' + name + '": {'
#                    print '    "oid": "' + oid + '",'
#                    print '    "display_name": _("' + name + '"),'
#                    print '    "type": "http://www.w3.org/2001/XMLSchema#string",'
#                    if syntax:
#                        print '    "syntax": "' + syntax + '",'
#                    print '},\n'
except Exception, err:
    print err

s = s.split('{"')
dic = []
for entry in s:
    d = [it for it in entry.split('"') if it and it !=',' and it !='{' and it !=',}']
    if d:
        dic.append(d)

for attr in dic:
    name = attr[0]
    oid = None
    names = None
    syntax = None
    for a in attr:
        if a.find('NAME') != -1:
            oid, xxx, n = a.partition('NAME')
            if not oid:
                oid = attr[1]
            for it in ['\(']:
                oid = re.sub(it, '', oid)
            if n.find('(') != -1 and n.find(')') != -1:
                names = [v for v in n.split("'") if v != '(' and v != ')' and v != '']
        elif a.find('SYNTAX') != -1:
            y, z, syntax = a.partition('SYNTAX')
            if syntax:
                syntax, a, b = syntax.partition('SINGLE-VALUE')
                syntax, a, b = syntax.partition('NO-USER-MODIFICATION')
                syntax, a, b = syntax.partition('USAGEdirectoryOperation')
                syntax, a, b = syntax.partition('USAGEdSAOperation')
                for it in ['\)']:
                    syntax = re.sub(it, '', syntax)

    if names:
        print '#Extracted from openldap system schema'
        print '"' + names[0] + '": {'
        display_name = ' '.join(names)
        names.pop(0)
        print '    "oid": "' + oid + '",'
        print '    "display_name": _("' + display_name + '"),'
        print '    "alias": ' + str(names) + ','
        print '    "type": "http://www.w3.org/2001/XMLSchema#string",'
        if syntax:
            print '    "syntax": "' + syntax + '",'
        print '},\n'
    else:
        for it in ['\'', '\(', '\)']:
            name = re.sub(it, '', name)
        print '#Extracted from openldap system schema'
        print '"' + name + '": {'
        print '    "oid": "' + oid + '",'
        print '    "display_name": _("' + name + '"),'
        print '    "type": "http://www.w3.org/2001/XMLSchema#string",'
        if syntax:
            print '    "syntax": "' + syntax + '",'
        print '},\n'

#"commonName": {
#    "oid": "2.5.4.3",
#    "friendly_name": _("Common Name"),
#    "type": "http://www.w3.org/2001/XMLSchema#string",
#    "namespaces": {
#        "LDAP": {
#            "identifiers":
#                [
#                "cn",
#                ]
#        },
#    }
#},

