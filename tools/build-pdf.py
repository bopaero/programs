#!/usr/bin/env python3
"""Render the cross-program documents on programs.bopaero.com to their PDFs.

    python3 tools/build-pdf.py                 # build + check, write the PDFs into the repo root
    python3 tools/build-pdf.py --check         # build + check only, write nothing
    python3 tools/build-pdf.py --out DIR       # write the PDFs into DIR (the publish workflow)
    add --archive to also copy each PDF into versions/ when that version is not archived yet

These documents cover more than one program, so they read every source from the live sites:
the SF50 costing (and, for now, the comparison data) from sf50program.bopaero.com and the
SR22T costing from sr22tprogram.bopaero.com. The pages are served over HTTP for the render
(Chrome refuses fetch() from file://). Runs on macOS and on the GitHub Actions Ubuntu runner.

Nothing is written unless every document renders exactly its page count, every page carries
its version stamp, all documents were built from the same source versions, and no
JavaScript values or the page's error message leaked into the text.
"""
import functools
import http.server
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = r'(v[\d.-]+)'
# (page, PDF file, exact pages, stamp regex, archive name from the stamp's groups)
DOCS = [
    # Customer comparison (built 2026-10-16 in the SF50 repo, moved here 2026-10-21)
    ('comparison.html', 'bop-Aero-Aircraft-Ownership-Comparison.pdf', 2,
     r'Comparison %s · SF50 %s · SR22T %s' % (V, V, V), ('comparison', 'sf50', 'sr22t'),
     lambda v: '%s-comparison-sf50-%s-sr22t-%s.pdf' % (v['comparison'], v['sf50'], v['sr22t'])),
    # Founder's Circle Insert + Detail Sheet (built 2026-10-16, moved here 2026-10-21)
    ('founders-insert.html', 'bop-Aero-Founders-Circle-Insert.pdf', 2,
     r'(?<!· )SF50 %s · SR22T %s' % (V, V), ('sf50', 'sr22t'),
     lambda v: '%s-founders-insert-sr22t-%s.pdf' % (v['sf50'], v['sr22t'])),
    ('founders-detail.html', 'bop-Aero-Founders-Circle-Detail-Sheet.pdf', 2,
     r'(?<!· )SF50 %s · SR22T %s' % (V, V), ('sf50', 'sr22t'),
     lambda v: '%s-founders-detail-sr22t-%s.pdf' % (v['sf50'], v['sr22t'])),
    # Letter of Intent (added 2026-10-21): wording version LOI_VERSION in the page + both costings
    ('loi.html', 'bop-Aero-Letter-of-Intent.pdf', 6,
     r'LOI %s · SR22T %s · SF50 %s' % (V, V, V), ('loi', 'sr22t', 'sf50'),
     lambda v: '%s-loi-sf50-%s-sr22t-%s.pdf' % (v['loi'], v['sf50'], v['sr22t'])),
]
MAC_CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def chrome_binary():
    for c in (os.environ.get('CHROME'), MAC_CHROME, shutil.which('google-chrome'), shutil.which('chromium')):
        if c and os.path.exists(c):
            return c
    sys.exit('Chrome not found (set CHROME=/path/to/chrome)')


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def render(out_pdf, page):
    handler = functools.partial(QuietHandler, directory=REPO)
    httpd = socketserver.TCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        url = 'http://127.0.0.1:%d/%s' % (httpd.server_address[1], page)
        args = [chrome_binary(), '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                '--virtual-time-budget=10000', '--run-all-compositor-stages-before-draw',
                '--print-to-pdf=' + out_pdf, url]
        if os.environ.get('CI'):
            args.insert(1, '--no-sandbox')
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        httpd.shutdown()


def page_count(pdf):
    info = subprocess.run(['pdfinfo', pdf], check=True, capture_output=True, text=True).stdout
    return int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))


def main():
    args = sys.argv[1:]
    check_only = '--check' in args
    archive = '--archive' in args
    out_dir = args[args.index('--out') + 1] if '--out' in args else None

    built, problems, versions = [], [], {}
    for page, name, expected, pattern, keys, archive_name in DOCS:
        tmp = os.path.join(tempfile.mkdtemp(), name)
        render(tmp, page)
        pages = page_count(tmp)
        text = subprocess.run(['pdftotext', '-layout', tmp, '-'], check=True, capture_output=True, text=True).stdout
        bad = []
        if pages != expected:
            bad.append('rendered %d pages, expected %d' % (pages, expected))
        stamps = re.findall(pattern, text)
        if len(stamps) != expected:
            bad.append('version stamp appears on %d pages, expected %d' % (len(stamps), expected))
        if len(set(stamps)) > 1:
            bad.append('pages name different versions: %s' % sorted(set(stamps)))
        v = dict(zip(keys, stamps[0])) if stamps else {}
        for k, x in v.items():
            if versions.setdefault(k, x) != x:
                bad.append('built from %s %s while another document used %s' % (k, x, versions[k]))
        # The Insert carries the program, never its figures (Raymond 2026-10-16): those are on the Detail Sheet
        if page == 'founders-insert.html' and re.search(r'\$\s*\d|\d\s*%', text):
            bad.append('the Insert shows a financial figure: ' + re.search(r'.{0,40}(\$\s*\d|\d\s*%).{0,20}', text).group(0).strip())
        if 'could not be displayed' in text:
            bad.append('the page reported an error: ' + text.strip().splitlines()[0][:200])
        leaks = sorted(set(re.findall(r'undefined|NaN|Infinity|\[object Object\]|native code|function\s*\w*\(', text)))
        if leaks:
            bad.append('rendering errors in text: ' + ', '.join(leaks))
        problems += ['%s: %s (render kept at %s)' % (page, b, tmp) for b in bad]
        built.append((name, tmp, pages, archive_name(v) if not bad else None))
    if problems:
        sys.exit('NOT WRITTEN — ' + '; '.join(problems))

    for name, tmp, pages, arch in built:
        print('OK  %s  %d pages  %s bytes  (%s)' % (name, pages, format(os.path.getsize(tmp), ','), arch))
    if check_only:
        print('    --check: nothing written')
        return
    dest = out_dir or REPO
    # What this build was made from; .github/workflows/refresh.yml compares it with the live sources
    os.makedirs(os.path.join(dest, 'data'), exist_ok=True)
    with open(os.path.join(dest, 'data', 'build.json'), 'w') as fh:
        json.dump(versions, fh)
    for name, tmp, pages, arch in built:
        shutil.copyfile(tmp, os.path.join(dest, name))
        print('    wrote ' + os.path.join(dest, name))
        a = os.path.join(REPO, 'versions', arch)
        if archive and not os.path.exists(a):
            shutil.copyfile(tmp, a)
            print('ARCHIVED versions/' + arch)

if __name__ == '__main__':
    main()
