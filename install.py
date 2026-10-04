#!/usr/bin/env python3
"""Install or safely merge the Greek Zimbra localization.

Safety model:
1) Exact SHA-256 verification for the main English message/key bundles when they match the source snapshot.
2) Compatible-source fallback for later 10.1.x builds: every translated key must still exist in the
   installed English bundle and use the same MessageFormat placeholder indexes.
3) Search Highlighter Zimlet Greek bundle is verified against its installed English properties file.
4) Full backup before writing; existing Greek values are preserved; no service restart.
"""
from pathlib import Path
import datetime, hashlib, json, os, pwd, grp, re, shutil

ROOT=Path(__file__).resolve().parent
BASE=Path('/opt/zimbra/jetty/webapps/zimbra/WEB-INF/classes')
ZIMLET_DEPLOYED=Path('/opt/zimbra/zimlets-deployed')
if os.geteuid()!=0:
    raise SystemExit('Run with sudo python3 upgrade_existing.py')

def props(path):
    lines=path.read_text(encoding='ascii', errors='strict').splitlines()
    out={}; i=0
    while i<len(lines):
        line=lines[i]; i+=1
        if not line.strip() or line.lstrip().startswith(('#','!')):
            continue
        logical=line
        while (len(logical)-len(logical.rstrip('\\'))) % 2 == 1 and i<len(lines):
            logical=logical[:-1]+lines[i].lstrip(); i+=1
        m=re.match(r'^\s*([^#!\s:=]+)\s*[:=]\s*(.*)$',logical)
        if m:
            out[m.group(1)]=m.group(2)
    return out

def ph(value):
    return sorted(set(re.findall(r'\{(\d+)(?:,[^}]*)?\}', value)))

def hash_status(subdir, manifest_name):
    manifest=json.loads((ROOT/manifest_name).read_text())
    mismatches=[]
    for name,digest in manifest.items():
        p=BASE/subdir/name
        if not p.is_file() or p.is_symlink():
            mismatches.append(str(p)+' (missing/unsafe)')
            continue
        got=hashlib.sha256(p.read_bytes()).hexdigest()
        if got!=digest:
            mismatches.append(str(p))
    return mismatches

def compatible_verify(subdir):
    srcdir=ROOT/subdir
    checked=0
    for src in sorted(srcdir.glob('*_el.properties')):
        english_name=src.name.replace('_el.properties','.properties')
        english=BASE/subdir/english_name
        if english.is_symlink() or not english.is_file():
            raise SystemExit('STOP: missing/unsafe installed English bundle: '+str(english))
        ep=props(english)
        gp=props(src)
        for key,gval in gp.items():
            if key not in ep:
                raise SystemExit(f'STOP: compatibility check failed: {key} missing from {english}')
            if ph(gval)!=ph(ep[key]):
                raise SystemExit(
                    f'STOP: placeholder mismatch for {key} in {english}: '
                    f'Greek={ph(gval)} English={ph(ep[key])}'
                )
            checked+=1
    return checked

def verify_zimlet(src, english):
    if english.is_symlink() or not english.is_file():
        raise SystemExit('STOP: missing/unsafe Search Highlighter English properties: '+str(english))
    ep=props(english)
    gp=props(src)
    for key,gval in gp.items():
        if key not in ep:
            raise SystemExit(f'STOP: Zimlet compatibility check failed: {key} missing from {english}')
        if ph(gval)!=ph(ep[key]):
            raise SystemExit(
                f'STOP: Zimlet placeholder mismatch for {key}: Greek={ph(gval)} English={ph(ep[key])}'
            )
    return len(gp)

msg_bad=hash_status('messages','source-sha256.json')
key_bad=hash_status('keys','keys-source-sha256.json')
if not msg_bad and not key_bad:
    print('Source verification: exact SHA-256 match.')
else:
    print('NOTICE: installed English bundle hashes differ from the original source snapshot.')
    print('Running compatible-source key/placeholder verification for this Zimbra build...')
    checked=compatible_verify('messages')+compatible_verify('keys')
    print(f'Compatibility verification passed: {checked} translated keys checked.')

# Preflight optional bundled Zimlet localizations before creating backup or writing.
zimlet_jobs=[]
zimroot=ROOT/'zimlets'
if zimroot.is_dir():
    for src in sorted(zimroot.glob('*/*_el.properties')):
        zimlet_name=src.parent.name
        deployed_dir=ZIMLET_DEPLOYED/zimlet_name
        english=deployed_dir/(zimlet_name+'.properties')
        checked=verify_zimlet(src,english)
        zimlet_jobs.append((src,deployed_dir,checked))
        print(f'Zimlet verification passed: {zimlet_name} ({checked} keys).')

stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup=Path('/opt/zimbra')/('greek-upgrade-backup-'+stamp)
backup.mkdir(mode=0o700)
uid=pwd.getpwnam('zimbra').pw_uid
gid=grp.getgrnam('zimbra').gr_gid
state={'base':str(BASE),'files':[],'zimlets':[]}
total_added=0

try:
    # Main message / shortcut bundles.
    for subdir in ('messages','keys'):
        srcdir=ROOT/subdir
        if not srcdir.is_dir():
            continue
        for src in sorted(srcdir.glob('*_el.properties')):
            dest=BASE/subdir/src.name
            if dest.is_symlink():
                raise RuntimeError('Refusing symlink: '+str(dest))
            sp=props(src)
            existed=dest.exists()
            entry={'subdir':subdir,'name':src.name,'existed':existed}
            state['files'].append(entry)
            bakdir=backup/subdir
            bakdir.mkdir(exist_ok=True)

            if existed:
                if not dest.is_file():
                    raise RuntimeError('Not a regular file: '+str(dest))
                shutil.copy2(dest,bakdir/src.name)
                current=props(dest)
                missing=[(k,v) for k,v in sp.items() if k not in current]
                conflicts=[k for k,v in sp.items() if k in current and current[k]!=v]
                if missing:
                    original=dest.read_text(encoding='ascii')
                    block='\n\n# Zimbra Greek localization v1.0.0 - added missing keys\n'+''.join(
                        f'{k} = {v}\n' for k,v in missing
                    )
                    dest.write_text(original.rstrip()+block,encoding='ascii')
                print(
                    f'{subdir}/{src.name}: added {len(missing)}, kept existing {len(sp)-len(missing)}'
                    +(f' ({len(conflicts)} existing values differ and were preserved)' if conflicts else '')
                )
                total_added+=len(missing)
            else:
                dest.write_bytes(src.read_bytes())
                os.chown(dest,uid,gid)
                os.chmod(dest,0o644)
                print(f'{subdir}/{src.name}: created with {len(sp)} keys')
                total_added+=len(sp)

    # Zimlet resource bundles.
    for src,deployed_dir,_ in zimlet_jobs:
        if deployed_dir.is_symlink() or not deployed_dir.is_dir():
            raise RuntimeError('Missing/unsafe deployed Zimlet directory: '+str(deployed_dir))
        dest=deployed_dir/src.name
        if dest.is_symlink():
            raise RuntimeError('Refusing Zimlet symlink: '+str(dest))
        sp=props(src)
        existed=dest.exists()
        state['zimlets'].append({
            'zimlet':src.parent.name,
            'name':src.name,
            'existed':existed,
            'dest':str(dest)
        })
        bakdir=backup/'zimlets'/src.parent.name
        bakdir.mkdir(parents=True,exist_ok=True)

        if existed:
            if not dest.is_file():
                raise RuntimeError('Not a regular Zimlet file: '+str(dest))
            shutil.copy2(dest,bakdir/src.name)
            current=props(dest)
            missing=[(k,v) for k,v in sp.items() if k not in current]
            conflicts=[k for k,v in sp.items() if k in current and current[k]!=v]
            if missing:
                original=dest.read_text(encoding='ascii')
                block='\n\n# Zimbra Greek localization v1.0.0 - added missing Zimlet keys\n'+''.join(
                    f'{k} = {v}\n' for k,v in missing
                )
                dest.write_text(original.rstrip()+block,encoding='ascii')
            print(
                f'zimlet/{src.parent.name}/{src.name}: added {len(missing)}, kept existing {len(sp)-len(missing)}'
                +(f' ({len(conflicts)} existing values differ and were preserved)' if conflicts else '')
            )
            total_added+=len(missing)
        else:
            shutil.copy2(src,dest)
            os.chown(dest,uid,gid)
            os.chmod(dest,0o644)
            print(f'zimlet/{src.parent.name}/{src.name}: created with {len(sp)} keys')
            total_added+=len(sp)

    (backup/'upgrade-state.json').write_text(
        json.dumps(state,indent=2)+'\n',encoding='utf-8'
    )
except Exception:
    # Roll back main bundles.
    for e in state['files']:
        dest=BASE/e['subdir']/e['name']
        bak=backup/e['subdir']/e['name']
        if e['existed'] and bak.exists():
            shutil.copy2(bak,dest)
        elif not e['existed'] and dest.exists() and not dest.is_symlink():
            dest.unlink()
    # Roll back Zimlet bundles.
    for e in state['zimlets']:
        dest=Path(e['dest'])
        bak=backup/'zimlets'/e['zimlet']/e['name']
        if e['existed'] and bak.exists():
            shutil.copy2(bak,dest)
        elif not e['existed'] and dest.exists() and not dest.is_symlink():
            dest.unlink()
    raise

print('Upgrade completed. Added keys:',total_added)
print('Backup:',backup)
print('No service restart or account changes performed.')
print('To roll back, use: sudo python3 restore_upgrade.py '+str(backup))
