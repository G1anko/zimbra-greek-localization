# Zimbra Greek Localization 🇬🇷

Unofficial Greek (`el`) localization for the **Zimbra Classic Web Client 10.1.x**.

This project provides Greek message bundles, keyboard-shortcut descriptions and a Greek localization for the bundled **Search Highlighter** Zimlet.

> Community project. Not affiliated with or endorsed by Zimbra/Synacor.

## Tested versions

- Zimbra 10.1.18
- Zimbra 10.1.20

The installer performs strict source checks before changing files. If the installed English bundles differ from the exact reference snapshot, it falls back to a key/placeholder compatibility check and stops if anything is unsafe or incompatible.

## Coverage

- Message bundle entries translated: **2,078**
- Keyboard shortcut descriptions: **214/214**
- Search Highlighter Zimlet strings: **4/4**
- Main bundles included: `ZmMsg`, `ZhMsg`, `AjxMsg`, `ZMsg`, `I18nMsg`
- Shortcut bundles included: `ZmKeys`, `AjxKeys`

This is a substantial but still evolving localization. Some Zimbra strings may remain in English and can be added in later releases.

## Install / upgrade

Download and extract the release on the Zimbra server, then run:

```bash
cd zimbra-greek-localization
sudo python3 install.py
```

The installer:

- verifies the installed English source bundles;
- checks MessageFormat placeholders;
- preserves existing Greek values instead of overwriting them;
- creates a timestamped backup under `/opt/zimbra/`;
- installs the Search Highlighter Greek resource bundle when that Zimlet is present;
- does **not** restart Zimbra automatically.

After a successful install:

```bash
sudo -iu zimbra zmmailboxdctl restart
sudo -iu zimbra zmmailboxdctl status
```

Then hard-refresh the browser (`Ctrl+Shift+R`).

## Rollback

The installer prints the exact backup path, for example:

```text
/opt/zimbra/greek-upgrade-backup-YYYYmmdd-HHMMSS
```

Rollback with:

```bash
sudo python3 restore.py /opt/zimbra/greek-upgrade-backup-YYYYmmdd-HHMMSS
```

Then restart `mailboxd`.

## Language selection

Set the user's Zimbra locale to Greek (`el`) from the web client preferences or through the normal Zimbra administration tools.

## Files

- `messages/` — Greek message bundles
- `keys/` — Greek keyboard-shortcut bundles
- `zimlets/` — Greek Search Highlighter Zimlet resources
- `install.py` — safe installer / upgrader
- `restore.py` — rollback from a backup created by the installer
- `coverage.json` — current translation coverage
- `source-sha256.json`, `keys-source-sha256.json` — reference hashes used for strict verification

## Licensing

The translated Zimbra resource files retain the upstream copyright and **GNU GPL version 2** notices contained in the corresponding source files.

The project-maintained installer and helper files are also distributed under **GPL-2.0-only** so the repository can be redistributed under a compatible license.

Zimbra names and trademarks belong to their respective owners.

## Contributing

If you find an English string while using the Greek locale, open an issue and include:

1. a screenshot;
2. where it appears in the interface;
3. the Zimbra version you are using.

Please do not include passwords, email contents or other sensitive data in screenshots.

---

## Ελληνικά

Ανεπίσημη ελληνική μετάφραση (`el`) για το **Zimbra Classic Web Client 10.1.x**.

Η έκδοση **v1.0.0** είναι η πρώτη δημόσια έκδοση του έργου και βασίζεται στη σωρευτική μετάφραση που δοκιμάστηκε σε πραγματική εγκατάσταση Zimbra 10.1.18 και 10.1.20.

Για εγκατάσταση:

```bash
sudo python3 install.py
```

Μετά την επιτυχημένη εγκατάσταση:

```bash
sudo -iu zimbra zmmailboxdctl restart
```

Αν εντοπίσετε αγγλικό κείμενο ενώ είναι επιλεγμένα τα Ελληνικά, ανοίξτε issue με screenshot και το σημείο όπου εμφανίζεται.
