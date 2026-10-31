"""Generates web/king-animated-desktop/{index,privacy-policy,terms-of-service}.html (self-contained, no external requests).
Copy the whole folder into your TeamExyKings GitHub Pages repo.  Run: python tools/make_web.py"""
import os, sys, html, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from king_pets import about_info as AI, config as C
OUT = os.path.join(ROOT, "web", "king-animated-desktop")
os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
for f in ("gallery.png", "settings.png", "settings_white.png", "settings_text.png", "demo.gif"):
    src = os.path.join(ROOT, "docs", f)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(OUT, "img", f))
NAME, VER, DATE = C.APP_NAME, C.VERSION, "31 October 2026"
RELEASES = AI.REPO_URL + "/releases"

CSS = """
:root{--bg:#000;--panel:#0b0b0d;--panel2:#15161a;--line:#2a2b32;--text:#ececf1;--muted:#9a9ca8;--accent:#00ffd0;--accent-ink:#000}
@media (prefers-color-scheme:light){:root:not([data-theme=dark]){--bg:#fff;--panel:#f4f5f8;--panel2:#e9ebf1;--line:#cfd3dc;--text:#14151a;--muted:#5d6170;--accent:#00846b;--accent-ink:#fff}}
:root[data-theme=light]{--bg:#fff;--panel:#f4f5f8;--panel2:#e9ebf1;--line:#cfd3dc;--text:#14151a;--muted:#5d6170;--accent:#00846b;--accent-ink:#fff}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
a{color:var(--accent)}a:hover{text-decoration:none}
.wrap{max-width:980px;margin:0 auto;padding:0 20px}
nav{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
nav .wrap{display:flex;gap:18px;align-items:center;min-height:56px;flex-wrap:wrap}
nav .brand{font-weight:800;letter-spacing:.3px;color:var(--text);text-decoration:none}nav .brand b{color:var(--accent)}
nav .sp{flex:1}nav a.l{color:var(--muted);text-decoration:none;font-size:14px}nav a.l:hover{color:var(--accent)}
button.theme{background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:8px;padding:5px 10px;cursor:pointer}
h1{font-size:clamp(30px,5.5vw,52px);line-height:1.1;margin:.2em 0 .3em}h2{font-size:26px;margin:2em 0 .5em}h3{font-size:18px;margin:1.6em 0 .3em;color:var(--accent)}
.hero{padding:56px 0 24px}.hero p.lead{font-size:19px;color:var(--muted);max-width:680px}
.btn{display:inline-block;background:var(--accent);color:var(--accent-ink);padding:11px 20px;border-radius:10px;font-weight:700;text-decoration:none;margin:6px 8px 6px 0}
.btn.ghost{background:transparent;color:var(--text);border:1px solid var(--line)}.btn.ghost:hover{border-color:var(--accent);color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}.card h3{margin-top:0}
img.shot{width:100%;height:auto;border-radius:12px;border:1px solid var(--line);display:block}
.pill{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:2px 12px;color:var(--muted);font-size:13px;margin:2px}
code,kbd{background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:1px 6px;font-size:.92em}
table{border-collapse:collapse;width:100%;margin:12px 0}td,th{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}th{background:var(--panel)}
.note{border-left:3px solid var(--accent);background:var(--panel);padding:10px 14px;border-radius:0 10px 10px 0;margin:16px 0;color:var(--muted)}
footer{border-top:1px solid var(--line);margin-top:60px;padding:30px 0 50px;color:var(--muted);font-size:14px}
footer a{color:var(--muted)}footer a:hover{color:var(--accent)}
.toc a{display:inline-block;margin-right:14px}
@media(max-width:560px){body{font-size:15px}.hero{padding-top:36px}}
"""
JS = """<script>(function(){try{var t=localStorage.getItem('kad-theme');if(t)document.documentElement.setAttribute('data-theme',t)}catch(e){}
document.addEventListener('click',function(e){var b=e.target.closest('button.theme');if(!b)return;var r=document.documentElement,cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:light)').matches?'light':'dark');var n=cur==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('kad-theme',n)}catch(e){}})})();</script>"""


def page(title, desc, body, active):
    nav = "".join(f'<a class="l" href="{h}">{t}</a>' for h, t in
                  (("index.html", "Home"), ("privacy-policy.html", "Privacy Policy"), ("terms-of-service.html", "Terms of Use")))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<meta name="color-scheme" content="dark light"><meta name="theme-color" content="#000000">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect x='4' y='4' width='56' height='56' rx='14' fill='%2308080c' stroke='%2300ffd0' stroke-width='4'/%3E%3Ctext x='32' y='45' font-size='36' font-weight='700' text-anchor='middle' fill='%2300ffd0' font-family='Arial'%3EK%3C/text%3E%3C/svg%3E">
<style>{CSS}</style></head><body>
<nav><div class="wrap"><a class="brand" href="index.html">King <b>Animated Desktop</b></a><span class="sp"></span>{nav}
<a class="l" href="{AI.REPO_URL}">Source</a><button class="theme" type="button" aria-label="Toggle light/dark theme">&#9788;</button></div></nav>
{body}
<footer><div class="wrap"><p><b>{NAME}</b> v{VER} &middot; {AI.LICENSE_NAME} &middot; &copy; 2026 {AI.BRAND}</p>
<p><a href="index.html">Home</a> &middot; <a href="privacy-policy.html">Privacy Policy</a> &middot; <a href="terms-of-service.html">Terms of Use</a> &middot;
<a href="{AI.REPO_URL}">Source code</a> &middot; <a href="mailto:{AI.EMAIL}">{AI.EMAIL}</a></p>
<p>Built by {AI.DEV_NAME} &middot; {AI.BRAND}, {AI.LOCATION}. {AI.PLEDGE}</p></div></footer>{JS}</body></html>"""


# ───────────────────────── index ─────────────────────────
n_obj = 61
index_body = f"""
<header class="hero"><div class="wrap">
<span class="pill">Windows 10 / 11</span><span class="pill">Free &amp; open source</span><span class="pill">No ads &middot; no tracking</span>
<h1>King Animated Desktop</h1>
<p class="lead">Little animated friends and your own custom text, floating over every app on your screen: a web-swinging hero, a trotting Labrador,
a neon badge, {n_obj} objects to mix and match &mdash; and your own text with any position, animation or swing.</p>
<p><a class="btn" href="{RELEASES}">Download for Windows</a><a class="btn ghost" href="{AI.REPO_URL}">View source on GitHub</a></p>
</div></header>
<main class="wrap">
<img class="shot" src="img/demo.gif" alt="Animated objects floating over the desktop" onerror="this.style.display='none'">
<h2>What you get</h2>
<div class="grid">
<div class="card"><h3>{n_obj} animated objects</h3><p>Animals, birds, characters, flyers, floaters, fallers, sports balls and corner decor. Tick the ones you like or use a preset.</p></div>
<div class="card"><h3>Custom text</h3><p>Write anything: pick a font, colour and box style, put it in any corner or exact spot, animate it (16 animations) or hang it from a thread and let it <b>swing</b>.</p></div>
<div class="card"><h3>Over all your apps</h3><p>Click-through, always-on-top overlays that stay above your windows without stealing focus or blocking your mouse. Multi-monitor aware.</p></div>
<div class="card"><h3>{len(C.SCHEMA)} global + per-object settings</h3><p>Size, speed, colours, hue, rainbow, swing physics, quiet hours, battery &amp; full-screen rules, autostart and more. Live preview.</p></div>
<div class="card"><h3>Pitch-black &amp; white themes</h3><p>A tidy settings window in pitch black (default), white or system theme, with your own accent colour.</p></div>
<div class="card"><h3>Private by design</h3><p>No accounts, no telemetry, no network connections. Settings stay on your PC. <a href="privacy-policy.html">Read the privacy policy</a>.</p></div>
</div>
<h2>Screenshots</h2>
<div class="grid"><img class="shot" src="img/gallery.png" alt="Gallery of all objects" onerror="this.style.display='none'">
<img class="shot" src="img/settings.png" alt="Settings window, pitch-black theme" onerror="this.style.display='none'">
<img class="shot" src="img/settings_text.png" alt="Custom text editor" onerror="this.style.display='none'">
<img class="shot" src="img/settings_white.png" alt="Settings window, white theme" onerror="this.style.display='none'"></div>
<h2>Install</h2>
<ol><li>Download <code>KingAnimatedDesktop_Setup_{VER}.exe</code> from the <a href="{RELEASES}">Releases page</a>.</li>
<li>Accept the licence, choose the options (desktop shortcut, start with Windows) and finish. It installs to <code>C:\\Program Files\\King Animated Desktop</code>.</li>
<li>Right-click the tray icon (near the clock) for Settings, Pause and Quit.</li></ol>
<div class="note">Windows may show a SmartScreen warning for new, unsigned open-source programs. Choose <b>More info &rarr; Run anyway</b> only if you downloaded it from the official Releases page above.
Exclusive full-screen games (DirectX/Vulkan exclusive mode) cannot be drawn over by any normal window; borderless/windowed games work.</div>
<h2>Support the project</h2>
<div class="card"><p><b>King Animated Desktop is free forever.</b> If it makes your desktop smile, a voluntary donation helps keep it ad-free and maintained. Donations unlock nothing &mdash; every feature is already free.</p>
<p><a class="btn" href="{AI.PAYPAL_URL}" rel="noopener">Donate with PayPal</a><a class="btn" href="{AI.RAZORPAY_URL}" rel="noopener">Donate with Razorpay (UPI / cards)</a></p>
<p style="color:var(--muted);font-size:14px">Payments are handled by PayPal or Razorpay on their own sites. See the <a href="privacy-policy.html#donations">Privacy Policy</a> and <a href="terms-of-service.html#donations">Terms</a>.</p></div>
<h2>Questions</h2>
<h3>Does it slow my PC down?</h3><p>A handful of objects use very little CPU. You can lower the frame rate, cap the number of objects, hide on battery or hide during full-screen apps.</p>
<h3>How do I remove it?</h3><p>Windows Settings &rarr; Apps &rarr; King Animated Desktop &rarr; Uninstall. You will be asked whether to delete your settings too.</p>
<h3>Can I add my own objects?</h3><p>Yes &mdash; it is open source. See <a href="{AI.REPO_URL}/blob/main/CONTRIBUTING.md">CONTRIBUTING.md</a>.</p>
<h3>Contact</h3><p><a href="mailto:{AI.EMAIL}">{AI.EMAIL}</a></p>
</main>"""

# ───────────────────────── privacy ─────────────────────────
def sec(i, title, inner):
    return f'<h2 id="s{i}">{i}. {title}</h2>{inner}'

privacy_body = f"""<main class="wrap"><div class="hero"><h1>Privacy Policy</h1>
<p class="lead">{NAME} &middot; Last updated {DATE} &middot; applies to version {VER[:3]}.x &middot; GDPR (Regulation (EU) 2016/679) &amp; ePrivacy information</p></div>
<div class="note"><b>In short:</b> the app itself collects, sends, sells or shares <b>no personal data</b>. It has no accounts, analytics, telemetry, advertising or cookies and makes no internet connections. Everything stays on your computer. The only time any personal data reaches us is if <em>you choose</em> to donate or email us (sections 6 and 7).</div>
{sec(1, "Who is responsible", f"<p>{AI.BRAND}, {AI.LOCATION} (the &ldquo;Publisher&rdquo;). Privacy contact: <a href=\"mailto:{AI.EMAIL}\">{AI.EMAIL}</a>. Because the program sends nothing to the Publisher, there is no processing of your data by the Publisher through the app; this policy is provided for transparency and for the optional contacts below.</p>")}
{sec(2, "What the app stores on your computer (only on your device)", """<table><tr><th>Item</th><th>Where</th><th>Why</th></tr>
<tr><td>Your settings: chosen objects, custom texts you write, colours, sizes, badge text</td><td><code>%APPDATA%\\KingAnimatedDesktop\\config.json</code></td><td>So your setup is remembered. Anything you type as text stays in this file only.</td></tr>
<tr><td>Start-up entry (only if &ldquo;Start with Windows&rdquo; is on)</td><td>Registry: <code>HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run</code></td><td>To start the program when you sign in.</td></tr>
<tr><td>Lock file <code>kingdesktop.lock</code></td><td>Windows temp folder</td><td>Prevents two copies running at once.</td></tr>
<tr><td>Settings files you export yourself</td><td>Where you save them</td><td>Backup / moving to another PC.</td></tr></table><p>None of this is transmitted anywhere.</p>""")}
{sec(3, "What the app reads locally (never stored or sent)", """<ul><li>Size and window class of the foreground window &mdash; only to hide the objects during full-screen apps if you turn on that option.</li>
<li>Power status (battery / mains) &mdash; only if you turn on &ldquo;Hide when running on battery&rdquo;.</li>
<li>The system clock &mdash; only if you turn on quiet hours.</li><li>Your monitor layout &mdash; to place objects on screen.</li></ul>
<p>The program does not read your files, keystrokes, clipboard, other programs&rsquo; contents or screen contents. It draws small transparent windows above your screen, nothing more.</p>""")}
{sec(4, "Legal basis, recipients and transfers", """<p>No personal data is processed through the app, so no consent is needed (Art. 6(1)(a)) and no cookies or similar technologies are used (ePrivacy Directive 2002/58/EC, Art. 5(3)). There are no recipients, processors or transfers outside the EU/EEA for the app itself. For the optional contacts below the legal bases are stated in each section.</p>""")}
{sec(5, "Links that open your browser", f"""<p>The Info tab has buttons (website, source code, policies, donate, e-mail support). They only do something when you click them, and then your own browser or e-mail program opens the page. The app itself makes no connection. What those sites do with your visit is governed by their own policies: GitHub (code &amp; downloads), {AI.WEBSITE.replace("https://", "")}, PayPal, Razorpay.</p>
<p>These policy pages are bundled with the installer and open offline from your PC.</p>""")}
<h2 id="donations">6. Donations (optional)</h2>
<p>Donating is entirely voluntary and unlocks nothing. Clicking a donate button opens a payment page run by <b>PayPal</b> (PayPal (Europe) S.&agrave; r.l. et Cie, S.C.A., Luxembourg, and PayPal Inc.) or <b>Razorpay</b> (Razorpay Software Private Limited, India). <b>We never see or store your card, bank or UPI details.</b></p>
<ul><li><b>What we receive:</b> from the payment provider we receive the amount, date, transaction reference and the name and e-mail address you gave them (if shown to us). We use it only to confirm and acknowledge the donation, keep accounting records and meet legal obligations.</li>
<li><b>Legal basis:</b> legitimate interest in handling donations you chose to make (Art. 6(1)(f)) and legal obligation for accounting (Art. 6(1)(c)).</li>
<li><b>Retention:</b> as long as accounting / tax rules in India require (generally several years), then deleted.</li>
<li><b>Transfers:</b> the providers may process data outside the EU/EEA (for example in India or the USA) under their own safeguards. See <a href="https://www.paypal.com/legalhub/privacy-full">PayPal&rsquo;s</a> and <a href="https://razorpay.com/privacy/">Razorpay&rsquo;s</a> privacy policies.</li></ul>
<h2 id="s7">7. If you contact us</h2>
<p>If you e-mail <a href="mailto:{AI.EMAIL}">{AI.EMAIL}</a> (for example via &ldquo;Email support&rdquo;), we receive your address and message and use them only to answer you (Art. 6(1)(f)). We keep it while the conversation is open and a reasonable time after, then delete it. Your mail provider also processes it under its own policy.</p>
{sec(8, "Websites &amp; downloads", f"<p>These pages and the downloads are hosted by GitHub (GitHub Pages / Releases). GitHub may log technical visitor data such as your IP address under its own policy. These pages use <b>no cookies, no analytics, no external fonts or scripts</b>; the only thing stored in your browser is your light/dark choice (local storage), which never leaves your device.</p>")}
{sec(9, "Retention and erasure (right to be forgotten)", """<p>Your app data lives only on your PC. Delete it any time: uninstall and answer <b>Yes</b> to &ldquo;Also delete my settings?&rdquo;, or delete the folder <code>%APPDATA%\\KingAnimatedDesktop</code>. Turning off &ldquo;Start with Windows&rdquo; in Settings removes the start-up entry.</p>""")}
{sec(10, "Your rights", f"<p>Under the GDPR you have the rights of access, rectification, erasure, restriction, portability and objection, and the right to complain to your national data-protection authority (list: <a href=\"https://edpb.europa.eu/about-edpb/about-edpb/members_en\">edpb.europa.eu</a>). For app data you exercise these directly on your own device as described above; for donation or e-mail records, write to <a href=\"mailto:{AI.EMAIL}\">{AI.EMAIL}</a>. There is no automated decision-making or profiling.</p>")}
{sec(11, "Children", "<p>The app collects no data from anyone, including children. Donating is intended for adults.</p>")}
{sec(12, "Security", "<p>The program has no network functionality and no server component and does not need administrator rights after installation. Download it only from the official Releases page and check the file hash if provided.</p>")}
{sec(13, "Changes", f"<p>If a future version changes how data is handled, this page and CHANGELOG.md will be updated before release. Current version of this policy: {DATE}.</p>")}
<p style="color:var(--muted)"><i>This policy is provided in good faith for an open-source hobby project; it is not legal advice.</i></p></main>"""

# ───────────────────────── terms ─────────────────────────
terms_body = f"""<main class="wrap"><div class="hero"><h1>Terms of Use</h1>
<p class="lead">{NAME} &middot; Last updated {DATE} &middot; version {VER[:3]}.x</p></div>
<p>By installing or using {NAME} you agree to these terms. If you do not agree, do not install or use it.</p>
{sec(1, "Who we are", f"<p>{AI.BRAND}, {AI.LOCATION}. Contact: <a href=\"mailto:{AI.EMAIL}\">{AI.EMAIL}</a>. Source code: <a href=\"{AI.REPO_URL}\">{AI.REPO_URL.replace('https://','')}</a>.</p>")}
{sec(2, "Free and open source", "<p>The program is free of charge and licensed under the <b>MIT License</b>, reproduced below. You may use, copy, modify and redistribute it under that licence.</p>")}
<div class="card"><p><b>MIT License</b><br>Copyright (c) 2026 TeamExyKings</p>
<p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the &ldquo;Software&rdquo;), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>
<p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>
<p>THE SOFTWARE IS PROVIDED &ldquo;AS IS&rdquo;, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p></div>
{sec(3, "Your statutory rights", "<p>Nothing in these terms excludes or limits any right or liability that cannot be excluded or limited by law &mdash; including mandatory consumer rights where you live (EU/EEA/UK), liability for intent or gross negligence, death or personal injury, or mandatory product-liability rules. Those rules take priority over the disclaimer above.</p>")}
{sec(4, "What the program does on your PC", """<p>It copies files to the folder you choose (default <code>C:\\Program Files\\King Animated Desktop</code>); optionally creates a desktop shortcut and a start-up entry for your Windows account; and shows small always-on-top, click-through windows above your screen. It does not read or change your files, other programs or the contents of other windows. You can change or remove all of this in Settings or by uninstalling.</p>""")}
{sec(5, "Using custom text", "<p>You are responsible for the text you display. The program only shows it on your own screen; it does not upload or publish it.</p>")}
{sec(6, "Third-party components", f"<p>The program includes the Qt framework and PySide6 (GNU LGPL v3), the Python runtime (PSF License) and other components under their own licences. They are not covered by the MIT licence above. Full notices and licence texts are installed with the program (<code>THIRD_PARTY_NOTICES.txt</code>, <code>licenses</code> folder). As the LGPL allows, you may replace the Qt/PySide6 libraries with your own build &mdash; see the notice file.</p>")}
<h2 id="donations">7. Donations</h2>
<ul><li>Donations through the PayPal and Razorpay buttons are <b>voluntary gifts</b> to support development. They are not a purchase and do not buy goods, services, a licence, support or any feature &mdash; the software stays free for everyone.</li>
<li>Payments are processed by PayPal or Razorpay under their own terms. We never receive your card or bank details. Any refund or dispute is handled with the provider; where mandatory law gives you rights, those are unaffected.</li>
<li>Donations are generally not tax-deductible and no invoice or receipt is issued unless the payment provider provides one.</li>
<li>See the <a href="privacy-policy.html#donations">Privacy Policy</a> for how donation data is handled.</li></ul>
{sec(8, "Trademarks and characters", "<p>All characters are original, simple drawings and are not affiliated with or endorsed by any film, comic or game franchise. The names &ldquo;King Animated Desktop&rdquo; and &ldquo;TeamExyKings&rdquo; identify this project. Other names mentioned by users belong to their owners. Windows is a trademark of Microsoft Corporation; this project is independent of Microsoft.</p>")}
{sec(9, "Support", f"<p>Support is best-effort and voluntary, by e-mail at <a href=\"mailto:{AI.EMAIL}\">{AI.EMAIL}</a> or through <a href=\"{AI.REPO_URL}/issues\">GitHub issues</a>.</p>")}
{sec(10, "Ending use", "<p>You may stop using and uninstall the program at any time. The MIT licence continues for as long as you comply with its conditions.</p>")}
{sec(11, "Governing law", "<p>Subject to section 3 and to any mandatory consumer-protection law of your country of residence (which you keep), these terms are governed by the laws of India. If you are a consumer in the EU/EEA you may also bring proceedings in the courts of your country of residence.</p>")}
{sec(12, "Changes and language", f"<p>We may update these terms for new versions; the date above shows the current text. The English text is authoritative.</p><p style=\"color:var(--muted)\"><i>Provided in good faith for an open-source hobby project; not legal advice.</i></p>")}</main>"""

for name, title, desc, body in (
    ("index.html", f"{NAME} - animated desktop companions for Windows", "Free, open-source animated objects and custom text that float over every app on your Windows desktop.", index_body),
    ("privacy-policy.html", f"Privacy Policy - {NAME}", "How King Animated Desktop handles data: it collects none.", privacy_body),
    ("terms-of-service.html", f"Terms of Use - {NAME}", "Terms of use and MIT licence for King Animated Desktop.", terms_body)):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(page(title, desc, body, name))
print("wrote", os.listdir(OUT))
