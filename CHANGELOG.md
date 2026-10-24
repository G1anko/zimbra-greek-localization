# Changelog

## Unreleased

## v1.1.0 — 2026-10-25

Comprehensive Greek Classic Web Client localization release.

Highlights:
- Expanded the five main message bundles to **6,092 localized entries**.
- Coverage by bundle: ZmMsg 3,879/3,981; ZhMsg 1,844/1,863; AjxMsg 183/247; ZMsg 124/124; I18nMsg 62/73.
- Completed the audited Classic translation pass: 3,978/3,982 rows classified `Translate` are present in the Greek bundles.
- Kept four deliberate source fallbacks: `vCard`, `MO_AB_email`, `MO_AB_email2`, `MO_AB_email3`.
- Preserved the complete 214/214 keyboard-shortcut descriptions and Search Highlighter Zimlet localization.
- Added Greek locale technical overrides for EUR, Monday-first week layout, and Greek decimal/grouping separators.
- Validation passed with 0 duplicate keys, 0 placeholder mismatches, 0 HTML/markup mismatches, 0 malformed Unicode escapes, 0 malformed property lines, and 0 translated keys missing from the pinned upstream source snapshots.
- Includes the post-v1.0.0 error-report, compose validation, folder sync/notification, external-image, and reviewed Core Mail / Compose additions.

## v1.0.0 — 2026-10-04

First public release.

Highlights:
- Greek localization for the Zimbra Classic Web Client 10.1.x.
- 2,078 translated message-bundle entries.
- 214/214 translated keyboard-shortcut descriptions.
- Greek Search Highlighter Zimlet localization.
- Safe install/upgrade with exact-hash verification and compatible-source fallback.
- Timestamped backup and rollback support.
- Tested on Zimbra 10.1.18 and 10.1.20.