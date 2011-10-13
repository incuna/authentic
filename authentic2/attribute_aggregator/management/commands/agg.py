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


from django.core.management.base import BaseCommand

from attribute_aggregator.mapping import ATTRIBUTE_MAPPING
from attribute_aggregator.core import load_or_create_user_profile, \
    set_user_alias_in_source
from attribute_aggregator.models import *


class Command(BaseCommand):
    '''
        Script to make tests on ABAC
    '''

    can_import_django_settings = True
    output_transaction = True
    requires_model_validation = True
    option_list = BaseCommand.option_list
    args = None
    help = \
        'No help.'

    def handle(self, *args, **options):

        print '-------- Tests --------'

        user, c = User.objects.get_or_create(username='abcdef')

#        print '%s' %ATTRIBUTE_MAPPING

        now = datetime.datetime.now().isoformat()
        print now
        s1, c = AttributeSource.objects.get_or_create(name="S1")
        print s1
        s2, c = LdapSource.objects.get_or_create(name="LDAP1",
            server="127.0.0.1", base="dc=entrouvert,dc=lan")
        print s2
        l = [ AttributeData('surname', values=(str(i), str(i+1), str(i+2)),
            source=s1, expiration_date=now) for i in range(10) ]
        l2 = [ AttributeData('gn', values=(str(i), str(i+1), str(i+2)),
            source=s2) for i in range(10) ]
        l3 = [ AttributeData('2.5.4.2', values=(str(i), str(i+1), str(i+2)),
            source=s2) for i in range(10) ]
        print [d.__unicode__() for d in l]
        print [d.__unicode__() for d in l2]
        print [d.__unicode__() for d in l3]

        p = load_or_create_user_profile(user=user)
        res = [p.add_data(d) for d in l]
        print res
        res = [p.add_data(d) for d in l2]
        print res
        res = [p.add_data(d) for d in l3]
        print res
        print p
        p.remove_data(0)
        p.remove_data(0)
        print p
        print [d.__unicode__() for d in p.get_data_of_definition('surname')]
        print [d.__unicode__() for d in p.get_data_of_source(s1)]
        print [d.__unicode__() for d in p.get_data_of_source_by_name('LDAP1')]
        print [d.__unicode__() \
            for d in p.get_data_of_definition_and_source('surname', s1)]
        print [d.__unicode__() \
            for d in p.get_data_of_definition_and_source_by_name(\
            'surname', 'S1')]
        print [d.__unicode__() for d in p.get_data_of_definition('2.5.4.2')]
        p.cleanup()
        print p

        attributes = {}
        data = []
#        attr = {}
#        attr['name'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/dateofbirth'
#        attr['namespace'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims'
#        attr['values'] = ('22', )
#        exp = datetime.datetime.now() + datetime.timedelta(days=1)
#        attr['expiration_date'] = exp.isoformat()
#        data.append(attr)
        attr = {}
        attr['name'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname'
        attr['namespace'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims'
        attr['values'] = ('Ates',)
        exp = datetime.datetime.now() + datetime.timedelta(days=1)
        attr['expiration_date'] = exp.isoformat()
        data.append(attr)
#        attr = {}
#        attr['name'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname'
#        attr['namespace'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims'
#        attr['values'] = ('Mikael', 'Ersin',)
#        exp = datetime.datetime.now() + datetime.timedelta(days=1)
#        attr['expiration_date'] = exp.isoformat()
#        data.append(attr)
#        attr = {}
#        attr['name'] = 'Nationality'
#        attr['namespace'] = 'ISO7501-1'
#        attr['values'] = ('FRA',)
#        data.append(attr)
        attributes['S1'] = data

#        data = []
#        attr = {}
#        attr['name'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname'
#        attr['namespace'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims'
#        attr['values'] = ('Ates',)
#        data.append(attr)
#        attr = {}
#        attr['name'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname'
#        attr['namespace'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims'
#        attr['values'] = ('Mikael', 'Ersin',)
#        data.append(attr)
#        attr = {}
#        attr['name'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/privatepersonalidentifier'
#        attr['namespace'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims'
#        attr['values'] = ('31q3sdf1q3sdf213q2d1f5qs',)
#        data.append(attr)
#        attr = {}
#        attr['name'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/dateofbirth'
#        attr['namespace'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims'
#        attr['values'] = ('17', )
#        data.append(attr)
#        attributes['LDAP1'] = data

        p.load_by_dic(attributes)

#        attributes = {}
#        data = []
#        attr = {}
#        attr['name'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname'
#        attr['namespace'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims'
#        attr['values'] = ('Ates',)
#        exp = datetime.datetime.now() + datetime.timedelta(days=2)
#        attr['expiration_date'] = exp.isoformat()
#        data.append(attr)
#        attr = {}
#        attr['name'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname'
#        attr['namespace'] = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims'
#        attr['values'] = ('Mikael', 'Ersin', 'Bob')
#        exp = datetime.datetime.now() + datetime.timedelta(days=2)
#        attr['expiration_date'] = exp.isoformat()
#        data.append(attr)
#        attributes['S1'] = data

#        p.load_by_dic(attributes)
        print p

        p = load_or_create_user_profile(user=user)
        print p

        set_user_alias_in_source(user, s2, 'uid=mikael,ou=people,dc=entrouvert,dc=lan')
        p.load_greedy()
        print p

        p.load_listed_attributes(('rfc822Mailbox',))
        print p

#        print [a.__unicode__() for a in p.get_data_of_definition('email')]
#        print p.get_freshest_data_of_definition('email').__unicode__()

        print '\n-------- DONE --------'
