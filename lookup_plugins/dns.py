# Copyright 2013 Dale Sedivec
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import socket

from ansible import utils, errors

try:
    # ansible-2.x
    from ansible.plugins.lookup import LookupBase
except ImportError:
    # ansible-1.x
    class LookupBase(object):
        def __init__(self, basedir=None, runner=None, **kwargs):
            self.runner = runner
            self.basedir = basedir or (self.runner.basedir
                                       if self.runner
                                       else None)

        def get_basedir(self, variables):
            return self.basedir


class LookupModule(LookupBase):

    # "variables" in ansible 2.x, "inject" in 1.x
    def run(self, terms, inject=None, variables=None, **kwargs):
        basedir = self.get_basedir(variables)

        # ansible-1.x
        if hasattr(utils, 'listify_lookup_plugin_terms'):
            terms = utils.listify_lookup_plugin_terms(terms, basedir, inject)

        if isinstance(terms, basestring):
            terms = [terms]
        ret = []
        for term in terms:
            try:
                ret.append(socket.gethostbyname(term))
            except socket.error, ex:
                raise errors.AnsibleError("exception resolving %r" % (term,),
                                          ex)
        return ret
