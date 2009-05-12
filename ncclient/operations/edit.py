# Copyright 2009 Shikhar Bhushan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ncclient import content

from rpc import RPC

import util

"Operations related to configuration editing"

class EditConfig(RPC):
    
    # tested: no
    # combed: yes
    
    SPEC = {'tag': 'edit-config', 'subtree': []}
    
    def request(self, target=None, config=None, default_operation=None,
                test_option=None, error_option=None):
        util.one_of(target, config)
        spec = EditConfig.SPEC.copy()
        subtree = spec['subtree']
        subtree.append(util.store_or_url('target', target, self._assert))
        subtree.append(content.validated_root(config, 'config'))
        if default_operation is not None:
            subtree.append({
                'tag': 'default-operation',
                'text': default_operation
                })
        if test_option is not None:
            self._assert(':validate')
            subtree.append({
                'tag': 'test-option',
                'text': test_option
                })
        if error_option is not None:
            if error_option == 'rollback-on-error':
                self._assert(':rollback-on-error')
            subtree.append({
                'tag': 'error-option',
                'text': error_option
                })


class DeleteConfig(RPC):
    
    # tested: no
    # combed: yes
    
    SPEC = {'tag': 'delete-config', 'subtree': []}
    
    def request(self, target):
        spec = DeleteConfig.SPEC.copy()
        spec['subtree'].append(util.store_or_url('source', source, self._assert))
        return self._request(spec)


class CopyConfig(RPC):
    
    # tested: no
    # combed: yes
    
    SPEC = {'tag': 'copy-config', 'subtree': []}
    
    def request(self, source, target):
        spec = CopyConfig.SPEC.copy()
        spec['subtree'].append(util.store_or_url('source', source, self._assert))
        spec['subtree'].append(util.store_or_url('target', source, self._assert))
        return self._request(spec)


class Validate(RPC):
    
    # tested: no
    # combed: yes
    
    'config attr shd not include <config> root'
    
    DEPENDS = [':validate']
    
    SPEC = {'tag': 'validate', 'subtree': []}
    
    def request(self, source=None, config=None):
        util.one_of(source, config)
        spec = Validate.SPEC.copy()
        if config is None:
            spec['subtree'].append(util.store_or_url('source', source, self._assert))
        else:
            spec['subtree'].append(content.validated_root(config, 'config'))
        return self._request(spec)


class Commit(RPC):
    
    # tested: no
    # combed: yes
    
    DEPENDS = [':candidate']
    
    SPEC = {'tag': 'commit', 'subtree': []}
    
    def _parse_hook(self):
        pass
    
    def request(self, confirmed=False, timeout=None):
        spec = SPEC.copy()
        if confirmed:
            self._assert(':confirmed-commit')
            spec['subtree'].append({'tag': 'confirmed'})
            if timeout is not None:
                spec['subtree'].append({
                    'tag': 'confirm-timeout',
                    'text': timeout
                })
        return self._request(Commit.SPEC)


class DiscardChanges(RPC):
    
    # tested: no
    # combed: yes
    
    DEPENDS = [':candidate']
    
    SPEC = {'tag': 'discard-changes'}


class ConfirmedCommit(Commit):
    "psuedo-op"
    
    # tested: no
    # combed: yes
    
    DEPENDS = [':candidate', ':confirmed-commit']
    
    def request(self, timeout=None):
        "Commit changes; requireing that a confirming commit follow"
        return Commit.request(self, confirmed=True, timeout=timeout)
    
    def confirm(self):
        "Make the confirming commit"
        return Commit.request(self, confirmed=True)
    
    def discard(self):
        return DiscardChanges(self.session, self.async, self.timeout).request()