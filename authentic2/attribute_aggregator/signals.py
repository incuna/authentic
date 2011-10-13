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


import ldap_sources
import user_profile

from django.dispatch import Signal


any_attributes_call = Signal(providing_args = ["user"])
listed_attributes_call = Signal(providing_args = ["user", "definitions"])
listed_attributes_with_source_call = Signal(providing_args = \
    ["user", "definitions", "source"])

any_attributes_call.connect(ldap_sources.get_attributes)
listed_attributes_call.connect(ldap_sources.get_attributes)
listed_attributes_with_source_call.connect(ldap_sources.get_attributes)

any_attributes_call.connect(user_profile.get_attributes)
listed_attributes_call.connect(user_profile.get_attributes)
listed_attributes_with_source_call.connect(user_profile.get_attributes)
