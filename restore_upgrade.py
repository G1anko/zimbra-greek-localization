#!/usr/bin/env python3
"""Restore files from a backup created by the Greek localization upgrade script."""
from pathlib import Path
import json, os, shutil, sys
if os.geteuid()!=0:
    raise SystemExit('Run with sudo python3 restore_upgrade.py /opt/zimbra/greek-upgrade-backup-YYYYmmdd-HHMMSS')
if len(sys.argv)!=2:
    raise SystemExit('Usage: sudo python3 restore_upgrade.py /opt/zimbra/greek-upgrade-backup-YYYYmmdd-HHMMSS')

backup=Path(sys.argv[1]).resolve()
sf=backup/'upgrade-state.json'
if not sf.is_file():
    raise SystemExit('STOP: upgrade-state.json not found in '+str(backup))
state=json.loads(sf.read_text())
base=Path(state.get('base',''))
if str(base)!='/opt/zimbra/jetty/webapps/zimbra/WEB-INF/classes':
    raise SystemExit('STOP: unexpected base in backup state')

for e in state.get('files',[]):
    if e['subdir'] not in ('messages','keys'):
        raise SystemExit('STOP: unexpected subdir in backup state')
    dest=base/e['subdir']/e['name']
    src=backup/e['subdir']/e['name']
    if dest.is_symlink():
        raise SystemExit('STOP: refusing symlink: '+str(dest))
    if e['existed']:
        if not src.is_file():
            raise SystemExit('STOP: missing backup file: '+str(src))
        shutil.copy2(src,dest)
        print('Restored '+str(dest))
    elif dest.exists():
        if not dest.is_file():
            raise SystemExit('STOP: not a regular file: '+str(dest))
        dest.unlink()
        print('Removed newly created '+str(dest))

for e in state.get('zimlets',[]):
    dest=Path(e['dest'])
    expected_prefix='/opt/zimbra/zimlets-deployed/'
    if not str(dest).startswith(expected_prefix):
        raise SystemExit('STOP: unexpected Zimlet destination: '+str(dest))
    src=backup/'zimlets'/e['zimlet']/e['name']
    if dest.is_symlink():
        raise SystemExit('STOP: refusing Zimlet symlink: '+str(dest))
    if e['existed']:
        if not src.is_file():
            raise SystemExit('STOP: missing Zimlet backup file: '+str(src))
        shutil.copy2(src,dest)
        print('Restored '+str(dest))
    elif dest.exists():
        if not dest.is_file():
            raise SystemExit('STOP: not a regular Zimlet file: '+str(dest))
        dest.unlink()
        print('Removed newly created '+str(dest))

print('Rollback completed. No service restart or account changes performed.')
