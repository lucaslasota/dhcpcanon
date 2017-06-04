# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab 2
# Copyright 2016, 2017 juga (juga at riseup dot net), MIT license.
"""Class to Initialize and call external script."""
from __future__ import unicode_literals

import logging
import os
import subprocess

import attr
from dhcpcanon.constants import (LEASEATTRS2ENVKEYS,
                                 LEASEATTRS_SAMEAS_ENVKEYS, SCRIPT_ENV_KEYS,
                                 STATES2REASONS)

logger = logging.getLogger('dhcpcanon')


@attr.s
class ClientScript(object):
    """Simulates the behaviour of isc-dhcp client-script or nm-dhcp-helper."""

    scriptname = attr.ib(default=None)
    env = attr.ib(default=attr.Factory(dict))

    def __attrs_post_init__(self):
        """."""
        self.env = dict.fromkeys(SCRIPT_ENV_KEYS, '')

    def script_init(self, lease, state, prefix='', medium=''):
        """Initialize environment to pass to the external script."""
        if self.scriptname is not None:
            if isinstance(state, int):
                reason = STATES2REASONS[state]
            else:
                reason = state

            self.env['medium'] = medium
            self.env['client'] = 'dhcpcanon'
            self.env['pid'] = str(os.getpid())
            self.env['reason'] = reason

            for k in LEASEATTRS_SAMEAS_ENVKEYS:
                self.env[k] = lease.__getattribute__(k)

            for k, v in LEASEATTRS2ENVKEYS.items():
                self.env[k] = str(lease.__getattribute__(v))

    def script_go(self, scriptname=None, env=None):
        """Run the external script."""
        scriptname = self.scriptname or scriptname
        if scriptname is not None:
            env = self.env or env
            logger.debug('calling script %s with env %s', scriptname, env)
            sp = subprocess.Popen([scriptname], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=env,
                                  close_fds=True, shell=False)
            _, err = sp.communicate()
            if sp.returncode != 0:
                logger.debug('sp err %s', err)
            return sp.returncode
        return None
