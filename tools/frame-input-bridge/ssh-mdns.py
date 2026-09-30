#!/usr/bin/env python3
"""Resolve a paired .local headset with Avahi while retaining its SSH host identity."""
import ipaddress
import os
import re
import subprocess
import sys

SSH = '/usr/bin/ssh'
RESOLVER = '/usr/bin/avahi-resolve-host-name'


def resolve_ipv4(host):
    result = subprocess.run([RESOLVER, '-4', host], capture_output=True,
                            text=True, timeout=5, check=True)
    fields = result.stdout.strip().split()
    if len(fields) != 2 or fields[0].lower().rstrip('.') != host.lower():
        raise ValueError('Invalid discovery response')
    address = ipaddress.IPv4Address(fields[1])
    if address.is_loopback or address.is_unspecified or address.is_multicast or address.is_reserved:
        raise ValueError('Invalid headset address')
    if not (address.is_private or address.is_link_local):
        raise ValueError('Headset address is outside local networks')
    return str(address)


def command(args, resolver=resolve_ipv4):
    # This transport is private to the bridge's fixed SSH invocation.
    if len(args) < 3 or args[-2] != 'python3':
        raise ValueError('Unexpected bridge invocation')
    target = args[-3]
    if '@' not in target:
        raise ValueError('Missing target user')
    user, host = target.rsplit('@', 1)
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]*', user):
        raise ValueError('Invalid target user')
    if not host.lower().endswith('.local'):
        return [SSH, *args]
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.local', host):
        raise ValueError('Invalid discovery name')
    host = host.lower()
    address = resolver(host)
    updated = list(args)
    updated[-3] = f'{user}@{address}'
    # StrictHostKeyChecking remains supplied by the capture client. The owner
    # must pre-verify this hostname's key; discovery never trusts or installs keys.
    return [SSH, '-o', f'HostKeyAlias={host}', *updated]


def main():
    try:
        argv = command(sys.argv[1:])
        os.execv(SSH, argv)
    except (ValueError, OSError, subprocess.SubprocessError):
        print('Frame discovery or SSH transport unavailable.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
