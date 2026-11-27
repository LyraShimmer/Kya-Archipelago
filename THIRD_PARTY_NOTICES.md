# Third-party notices - Kya Archipelago Launcher

## certifi (python-certifi)

- Project: https://github.com/certifi/python-certifi
- Python package: https://pypi.org/project/certifi/
- Original author: Kenneth Reitz; maintained by the certifi contributors.
- License: Mozilla Public License 2.0 (MPL-2.0).
- Mozilla full license: https://www.mozilla.org/en-US/MPL/2.0/
- Source code and CA certificate bundle: https://github.com/certifi/python-certifi

The Launcher uses certifi's Mozilla CA certificate bundle to verify TLS certificates
when connecting to hosted Archipelago rooms. Certificate verification remains enabled.

The following files are included with this Launcher distribution:
- `THIRD_PARTY_LICENSES/certifi_LICENSE.txt` - certifi's original upstream LICENSE notice
- `THIRD_PARTY_LICENSES/MPL-2.0.txt` - the full Mozilla Public License 2.0 text

certifi is distributed under its original terms, not under the project's own license.
For the source code of certifi and the bundled CA certificate data, see the upstream
repository above. The certificate bundle originates from Mozilla's CA root store.

## Additional software components

The packaged executable and its build rely on other independently licensed projects.
This section identifies major components, but does not claim to be a complete
software bill of materials or a comprehensive license audit of all transitive modules.

- Python runtime: Python Software Foundation License, Version 2;
  https://docs.python.org/3/license.html
- PyInstaller bootloader (used to package the Windows EXEs):
  GPL-2.0-or-later with the PyInstaller bootloader exception;
  https://pyinstaller.org/en/stable/license.html
- Pillow (used by the optional Color Studio and image handling): HPND;
  https://github.com/python-pillow/Pillow/blob/main/LICENSE
- websocket-client (a Python build dependency): Apache-2.0;
  https://github.com/websocket-client/websocket-client/blob/master/LICENSE

The components named above are governed by their respective original license terms.
Where applicable, consult the bundled application and source distributions for their
full license text, notices and other third-party components.

## Contributor attribution

The secure WSS certificate-handling patch was developed and tested by eNigma
([eBigma](https://github.com/eBigma)), submitted in pull request #1:
https://github.com/LyraShimmer/Kya-Archipelago/pull/1

This community contribution is also acknowledged in `CONTRIBUTORS.md` and `CREDITS.md`.
