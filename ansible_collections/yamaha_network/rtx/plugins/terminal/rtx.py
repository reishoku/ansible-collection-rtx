# Copyright (C) Yamaha Corporation.
#
# (c) 2016 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <https://www.gnu.org/licenses/gpl-3.0.txt>.
#
import json
import re

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.common.text.converters import to_text, to_bytes
from ansible.plugins.terminal import TerminalBase
from ansible.utils.display import Display

display = Display()


class TerminalModule(TerminalBase):
  terminal_stdout_re = [re.compile(rb"[>#]|Password: ")]

  terminal_stderr_re = [
    re.compile(rb"Error:", re.I),
  ]

  def on_open_shell(self):
    pass

  def on_become(self, passwd=None):
    if self._get_prompt().endswith(b'#'):
      return

    cmd = {'command': 'administrator'}
    if passwd:
      cmd['prompt'] = to_text(r"[\r\n]?Password: $", errors='surrogate_or_strict')
      cmd['answer'] = passwd
    try:
      self._exec_cli_command(to_bytes(json.dumps(cmd), errors='surrogate_or_strict'))
    except AnsibleConnectionFailure:
      raise AnsibleConnectionFailure('unable to elevate privilege to administrator mode')

  def on_unbecome(self):
    prompt = self._get_prompt()
    if prompt is None:
      # if prompt is None most likely the terminal is hung up at a prompt
      return

    if prompt.endswith(b'#'):
      self._exec_cli_command(b'exit')
