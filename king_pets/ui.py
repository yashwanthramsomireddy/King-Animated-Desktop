"""Settings window. All option pages are generated from config.SCHEMA / PET_SCHEMA."""
import copy, json, random
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon
from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QLineEdit,
                               QComboBox, QListWidget, QListWidgetItem, QPushButton, QCheckBox, QSlider,
                               QSpinBox, QDoubleSpinBox, QFormLayout, QScrollArea, QGroupBox, QColorDialog,
                               QFileDialog, QMessageBox, QListView, QFrame, QSplitter)

from . import config as C
from .sprites import REGISTRY, CATEGORIES
from .render import Ctx
from .actors import paint_sprite
from . import platform_utils as PU
from . import theme as TH
from . import about_info as AI

PRESETS = {
    "Starter (Web Swinger + Labrador)": ["spiderman", "lab_yellow"],
    "Zoo": ["cat", "fox", "bunny", "bear", "pig", "panda", "cow", "sheep", "husky", "duck", "chick", "penguin"],
    "Space": ["ufo", "rocket", "alien", "astronaut", "moon", "hangstar", "fallstar", "robot"],
    "Cricket & Sports": ["cricket", "soccer", "basketball", "beachball", "lab_yellow"],
    "Spooky": ["bat", "ghost", "pumpkin", "cat_black", "spider", "moon", "lantern"],
    "Winter": ["snowflake", "penguin", "husky", "campfire", "cloud", "lab_black"],
    "Garden": ["butterfly", "bee", "petal", "leaf", "frog", "snail", "sun", "turtle", "bird"],
    "Party": ["balloon", "discoball", "heart", "kite", "lantern", "monkey", "beachball"],
    "Ocean": ["fish", "jellyfish", "crab", "turtle", "duck", "cloud", "sun"],
    "Everything (chaos!)": list(REGISTRY.keys()),
}


TILE = {"color": "#12131a"}


def preview_pixmap(spec, size=84):
    pm = QPixmap(size, size); pm.fill(QColor(TILE["color"]))
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    if spec.custom and spec.kind == "swing":
        W, H, rope, ang = 130, 130, 70, 0.35
    elif spec.kind == "swing":
        W, H, rope, ang = 100, 100, 0, 0.0
    else:
        W, H, rope, ang = spec.w, spec.h, 0, 0.0
    sc = (size - 8) / max(W, H)
    p.translate((size - W * sc) / 2, (size - H * sc) / 2)
    p.scale(sc, sc)
    ctx = Ctx(t=0.8, W=W, H=H, rope=rope, ang=ang, gait=0.4, shadow=False)
    paint_sprite(p, spec, ctx)
    p.end()
    return pm


class SliderSpin(QWidget):
    """Slider + spinbox pair for int / float settings."""
    def __init__(self, spec, value, on_change):
        super().__init__()
        self.flt = spec["type"] == "float"
        lo, hi = spec["min"], spec["max"]
        self.mul = 100 if self.flt else 1
        lay = QHBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        self.sl = QSlider(Qt.Horizontal); self.sl.setRange(int(lo * self.mul), int(hi * self.mul))
        if self.flt:
            self.sp = QDoubleSpinBox(); self.sp.setDecimals(2); self.sp.setSingleStep(0.05)
        else:
            self.sp = QSpinBox()
        self.sp.setRange(lo, hi); self.sp.setFixedWidth(78)
        self.sp.setValue(value); self.sl.setValue(int(round(value * self.mul)))
        lay.addWidget(self.sl, 1); lay.addWidget(self.sp)
        self.sl.valueChanged.connect(lambda v: self._from_slider(v, on_change))
        self.sp.valueChanged.connect(lambda v: self._from_spin(v, on_change))

    def _from_slider(self, v, cb):
        val = v / self.mul if self.flt else v
        self.sp.blockSignals(True); self.sp.setValue(val); self.sp.blockSignals(False); cb(val)

    def _from_spin(self, v, cb):
        self.sl.blockSignals(True); self.sl.setValue(int(round(v * self.mul))); self.sl.blockSignals(False); cb(v)

    def set(self, v):
        self.sp.blockSignals(True); self.sl.blockSignals(True)
        self.sp.setValue(v); self.sl.setValue(int(round(v * self.mul)))
        self.sp.blockSignals(False); self.sl.blockSignals(False)


class ColorButton(QPushButton):
    def __init__(self, value, on_change):
        super().__init__()
        self.value, self.cb = value, on_change
        self.setFixedWidth(110)
        self.clicked.connect(self.pick)
        self.paint()

    def paint(self):
        c = QColor(self.value)
        fg = "#000" if c.lightness() > 128 else "#fff"
        self.setText(self.value)
        self.setStyleSheet(f"background:{self.value};color:{fg};border:1px solid #666;padding:4px;")

    def pick(self):
        c = QColorDialog.getColor(QColor(self.value), self, "Choose colour")
        if c.isValid():
            self.value = c.name(); self.paint(); self.cb(self.value)

    def set(self, v):
        self.value = v; self.paint()


def make_widget(spec, value, on_change):
    t = spec["type"]
    if t == "bool":
        w = QCheckBox(); w.setChecked(bool(value)); w.toggled.connect(on_change); w.set = w.setChecked
    elif t in ("int", "float"):
        w = SliderSpin(spec, value, on_change)
    elif t == "choice":
        w = QComboBox()
        for ch in spec["choices"]:
            w.addItem(str(ch), ch)
        w.setCurrentIndex(max(0, w.findData(value)))
        w.currentIndexChanged.connect(lambda i, w=w: on_change(w.itemData(i)))
        w.set = lambda v, w=w: w.setCurrentIndex(max(0, w.findData(v)))
    elif t == "color":
        w = ColorButton(value, on_change)
    else:  # text / time
        w = QLineEdit(str(value)); w.textChanged.connect(on_change); w.set = w.setText
        if t == "time":
            w.setInputMask("99:99"); w.setFixedWidth(70)
    return w


class SettingsDialog(QDialog):
    LIVE_DELAY_MS = 500

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle(f"{C.APP_NAME} {C.VERSION} - Settings")
        self.resize(1060, 700)
        self.cfg = copy.deepcopy(engine.cfg)
        self.widgets, self.text_widgets, self.pet_widgets = {}, {}, {}
        self.cur = None            # selected object id
        self.cur_text = -1         # selected text index
        self._loading = True
        self._need_rebuild = False
        self.colors = TH.apply_theme(QApplication.instance(), self.cfg["theme"], self.cfg["ui_accent"])
        TILE["color"] = self.colors["tile"]
        self._debounce = QTimer(self); self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._live_apply)

        root = QVBoxLayout(self)
        self.tabs = QTabWidget(); root.addWidget(self.tabs, 1)
        self.tabs.addTab(self._objects_tab(), f"Objects ({len(REGISTRY)})")
        self.tabs.addTab(self._text_tab(), "Text")
        for grp in ("General", "Appearance", "Behaviour", "Badge"):
            n = sum(1 for s in C.SCHEMA if s["group"] == grp)
            self.tabs.addTab(self._form_tab(grp), f"{grp} ({n})")
        self.tabs.addTab(self._info_tab(), "Info")

        bar = QHBoxLayout(); root.addLayout(bar)
        self.status = QLabel(""); bar.addWidget(self.status, 1)
        self.live = QCheckBox("Live preview"); self.live.setChecked(True)
        self.live.setToolTip("Apply and save every change automatically after a short pause"); bar.addWidget(self.live)
        for text, fn in (("Export...", self.export_cfg), ("Import...", self.import_cfg),
                         ("Reset all", self.reset_all), ("Apply", self.apply)):
            b = QPushButton(text); b.clicked.connect(lambda _=False, f=fn: f()); bar.addWidget(b)
        ok = QPushButton("OK"); ok.setDefault(True); ok.clicked.connect(lambda: (self.apply(), self.hide()))
        cancel = QPushButton("Close"); cancel.clicked.connect(self.hide)
        bar.addWidget(ok); bar.addWidget(cancel)
        self._loading = False
        self.reload()

    # ───────────── change tracking / apply ─────────────
    def _touch(self, rebuild=True):
        """Called after every edit. With Live preview on, applies (and saves) after a short pause."""
        if self._loading:
            return
        self._need_rebuild = self._need_rebuild or rebuild
        if self.live.isChecked():
            self._debounce.start(self.LIVE_DELAY_MS)

    def _live_apply(self):
        self.apply(rebuild=self._need_rebuild)

    def apply(self, rebuild=True):
        """Validate, save to disk and (optionally) rebuild the on-screen objects. The engine gets its OWN copy,
        so later edits in this window never change the running config until applied."""
        self._debounce.stop()
        cfg = C.sanitize(copy.deepcopy(self.cfg))
        C.save(cfg)
        if rebuild or self._need_rebuild:
            self.engine.rebuild(cfg)
        else:
            self.engine.cfg = cfg
        self._need_rebuild = False
        self._update_status()

    def load(self, cfg):
        """Load a config into every widget (used for open, Reset all and Import)."""
        self._loading = True
        try:
            self.cfg = copy.deepcopy(cfg)
            self.retheme()
            for k, wdg in self.widgets.items():
                wdg.set(self.cfg[k])
            self.list.blockSignals(True)
            try:
                for pid, it in self.items.items():
                    it.setCheckState(Qt.Checked if self.cfg["pets"].get(pid, {}).get("enabled") else Qt.Unchecked)
            finally:
                self.list.blockSignals(False)
            self.refilter()
            self._rebuild_text_list(select=min(self.cur_text, len(self.cfg["texts"]) - 1) if self.cfg["texts"] else -1)
            if self.cur:
                self._load_pet(self.cur)
            self._update_status()
        finally:
            self._loading = False

    def reload(self):
        self.load(self.engine.cfg)

    # ───────────── Objects tab ─────────────
    def _objects_tab(self):
        w = QWidget(); lay = QHBoxLayout(w)
        left = QVBoxLayout(); lay.addLayout(left, 3)
        row = QHBoxLayout(); left.addLayout(row)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search objects...")
        self.search.textChanged.connect(self.refilter); row.addWidget(self.search, 1)
        self.catbox = QComboBox(); self.catbox.addItem("All categories"); self.catbox.addItems(CATEGORIES)
        self.catbox.currentIndexChanged.connect(self.refilter); row.addWidget(self.catbox)
        row2 = QHBoxLayout(); left.addLayout(row2)
        self.presetbox = QComboBox(); self.presetbox.addItems(PRESETS.keys()); row2.addWidget(self.presetbox, 1)
        for text, fn in (("Use preset", self.use_preset), ("Surprise me", self.surprise),
                         ("Select shown", lambda: self.bulk(True)), ("Clear shown", lambda: self.bulk(False))):
            b = QPushButton(text); b.clicked.connect(lambda _=False, f=fn: f()); row2.addWidget(b)

        self.list = QListWidget(); self.list.setViewMode(QListView.IconMode)
        self.list.setIconSize(QSize(84, 84)); self.list.setResizeMode(QListView.Adjust)
        self.list.setSpacing(8); self.list.setWordWrap(True); self.list.setUniformItemSizes(True)
        self.list.setMovement(QListView.Static); self.list.setGridSize(QSize(112, 130))
        self.items = {}
        for pid, spec in REGISTRY.items():
            it = QListWidgetItem(QIcon(preview_pixmap(spec)), spec.name)
            it.setData(Qt.UserRole, pid)
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Unchecked)
            it.setToolTip(f"{spec.name} - {spec.cat} ({spec.kind})")
            self.list.addItem(it); self.items[pid] = it
        self.list.itemChanged.connect(self._item_toggled)
        self.list.currentItemChanged.connect(self._select)
        left.addWidget(self.list, 1)

        right = QGroupBox("Selected object"); lay.addWidget(right, 2)
        rl = QVBoxLayout(right)
        self.sel_icon = QLabel(); self.sel_icon.setAlignment(Qt.AlignCenter); rl.addWidget(self.sel_icon)
        self.sel_name = QLabel("Click an object"); self.sel_name.setAlignment(Qt.AlignCenter)
        self.sel_name.setStyleSheet("font-weight:bold;font-size:15px;"); rl.addWidget(self.sel_name)
        form = QFormLayout(); rl.addLayout(form)
        for s in C.PET_SCHEMA:
            wdg = make_widget(s, s["default"], lambda v, k=s["key"]: self._pet_changed(k, v))
            self.pet_widgets[s["key"]] = wdg
            form.addRow(s["label"], wdg)
        self.zone_hint = QLabel("Where: top/middle/bottom = lane for walkers & flyers; "
                                "top-left / top-right etc. = corner for swingers & corner decor.")
        self.zone_hint.setWordWrap(True); self.zone_hint.setStyleSheet("color:#888;"); rl.addWidget(self.zone_hint)
        rb = QPushButton("Reset this object"); rb.clicked.connect(lambda: self.reset_pet()); rl.addWidget(rb)
        rl.addStretch(1)
        return w

    # ───────────── Text tab ─────────────
    def _text_tab(self):
        w = QWidget(); lay = QHBoxLayout(w)
        left = QVBoxLayout(); lay.addLayout(left, 2)
        left.addWidget(QLabel("Your custom texts (tick = show)"))
        self.text_list = QListWidget()
        self.text_list.itemChanged.connect(self._text_item_toggled)
        self.text_list.currentRowChanged.connect(self._select_text)
        left.addWidget(self.text_list, 1)
        r1 = QHBoxLayout(); left.addLayout(r1)
        for text, fn in (("Add text", lambda: self.add_text()), ("Duplicate", self.dup_text), ("Remove", self.remove_text)):
            b = QPushButton(text); b.clicked.connect(lambda _=False, f=fn: f()); r1.addWidget(b)
        r2 = QHBoxLayout(); left.addLayout(r2)
        for text, d in (("Up", -1), ("Down", 1)):
            b = QPushButton(text); b.clicked.connect(lambda _=False, d=d: self.move_text(d)); r2.addWidget(b)
        self.tpl = QComboBox(); self.tpl.addItems(C.TEXT_TEMPLATES.keys()); left.addWidget(QLabel("Start from a template:"))
        left.addWidget(self.tpl)
        b = QPushButton("Add from template"); b.clicked.connect(lambda: self.add_text(C.TEXT_TEMPLATES[self.tpl.currentText()]))
        left.addWidget(b)
        self.text_hint = QLabel(f"Up to {C.MAX_TEXTS} texts. Pick a position, an animation, and/or let it hang "
                                f"from a thread and swing.")
        self.text_hint.setWordWrap(True); self.text_hint.setStyleSheet("color:#888;"); left.addWidget(self.text_hint)

        sc = QScrollArea(); sc.setWidgetResizable(True); lay.addWidget(sc, 3)
        page = QWidget(); pl = QVBoxLayout(page)
        for grp in ("Text", "Position", "Animation", "Swing"):
            box = QGroupBox({"Text": "Text && look", "Position": "Position", "Animation": "Animation",
                             "Swing": "Swing (hang from a thread)"}[grp])
            fl = QFormLayout(box)
            for s in C.TEXT_SCHEMA:
                if s["group"] != grp:
                    continue
                wdg = make_widget(s, s["default"], lambda v, k=s["key"]: self._text_changed(k, v))
                self.text_widgets[s["key"]] = wdg
                if s["type"] == "bool":
                    wdg.setText(s["label"]); fl.addRow(wdg)
                else:
                    fl.addRow(s["label"], wdg)
            pl.addWidget(box)
        pl.addStretch(1); sc.setWidget(page)
        self.text_form = page
        return w

    def _text_label(self, i):
        t = self.cfg["texts"][i]["text"].replace("\n", " ")
        return f"{i + 1}. {t[:26] or '(empty)'}"

    def _rebuild_text_list(self, select=-1):
        self.text_list.blockSignals(True)
        self.text_list.clear()
        for i, tc in enumerate(self.cfg["texts"]):
            it = QListWidgetItem(self._text_label(i))
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked if tc["enabled"] else Qt.Unchecked)
            self.text_list.addItem(it)
        self.text_list.blockSignals(False)
        self.cur_text = select if 0 <= select < len(self.cfg["texts"]) else (0 if self.cfg["texts"] else -1)
        if self.cur_text >= 0:
            self.text_list.setCurrentRow(self.cur_text)
        self._load_text(self.cur_text)

    def _load_text(self, i):
        has = 0 <= i < len(self.cfg["texts"])
        self.text_form.setEnabled(has)
        was = self._loading; self._loading = True
        try:
            tc = self.cfg["texts"][i] if has else C.TEXT_DEFAULTS
            for k, wdg in self.text_widgets.items():
                wdg.set(tc[k])
        finally:
            self._loading = was

    def _select_text(self, row):
        self.cur_text = row; self._load_text(row)

    def _text_changed(self, key, val):
        if self._loading or not (0 <= self.cur_text < len(self.cfg["texts"])):
            return
        self.cfg["texts"][self.cur_text][key] = val
        it = self.text_list.item(self.cur_text)
        if key == "text" and it:
            it.setText(self._text_label(self.cur_text))
        if key == "enabled" and it:
            self.text_list.blockSignals(True); it.setCheckState(Qt.Checked if val else Qt.Unchecked); self.text_list.blockSignals(False)
        self._update_status(); self._touch()

    def _text_item_toggled(self, it):
        i = self.text_list.row(it)
        if 0 <= i < len(self.cfg["texts"]):
            self.cfg["texts"][i]["enabled"] = it.checkState() == Qt.Checked
            if i == self.cur_text:
                self._load_text(i)
            self._update_status(); self._touch()

    def add_text(self, over=None):
        if len(self.cfg["texts"]) >= C.MAX_TEXTS:
            QMessageBox.information(self, "Limit reached", f"You can have up to {C.MAX_TEXTS} custom texts.")
            return
        tc = dict(C.TEXT_DEFAULTS); tc.update(over or {})
        self.cfg["texts"].append(C.sanitize({"texts": [tc]})["texts"][0])
        self._rebuild_text_list(select=len(self.cfg["texts"]) - 1)
        self._update_status(); self._touch()

    def dup_text(self):
        i = self.cur_text
        if 0 <= i < len(self.cfg["texts"]) and len(self.cfg["texts"]) < C.MAX_TEXTS:
            self.cfg["texts"].insert(i + 1, dict(self.cfg["texts"][i]))
            self._rebuild_text_list(select=i + 1); self._update_status(); self._touch()

    def remove_text(self):
        i = self.cur_text
        if 0 <= i < len(self.cfg["texts"]):
            del self.cfg["texts"][i]
            self._rebuild_text_list(select=min(i, len(self.cfg["texts"]) - 1)); self._update_status(); self._touch()

    def move_text(self, d):
        i, j = self.cur_text, self.cur_text + d
        t = self.cfg["texts"]
        if 0 <= i < len(t) and 0 <= j < len(t):
            t[i], t[j] = t[j], t[i]
            self._rebuild_text_list(select=j); self._touch()

    # ───────────── global option tabs ─────────────
    def _form_tab(self, group):
        page = QWidget(); form = QFormLayout(page)
        for s in C.SCHEMA:
            if s["group"] != group:
                continue
            wdg = make_widget(s, s["default"], lambda v, k=s["key"]: self._global_changed(k, v))
            self.widgets[s["key"]] = wdg
            if s["type"] == "bool":
                wdg.setText(s["label"]); form.addRow(wdg)
            else:
                form.addRow(s["label"], wdg)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(page)
        return sc

    def _global_changed(self, key, val):
        if self._loading:
            return
        self.cfg[key] = val
        if key in ("theme", "ui_accent"):
            self.retheme(); self._touch(rebuild=False)
        else:
            self._touch()

    # ───────────── Info tab (slim) ─────────────
    def _info_tab(self):
        page = QWidget(); outer = QVBoxLayout(page); outer.setContentsMargins(18, 14, 18, 14)
        card = QFrame(); card.setObjectName("card"); cl = QHBoxLayout(card); cl.setContentsMargins(18, 16, 18, 16)
        self.info_icon = QLabel(); self.info_icon.setFixedSize(84, 84); self.info_icon.setAlignment(Qt.AlignCenter)
        cl.addWidget(self.info_icon)
        self.info_head = QLabel(); self.info_head.setTextFormat(Qt.RichText); self.info_head.setWordWrap(True)
        self.info_head.setOpenExternalLinks(True)
        cl.addWidget(self.info_head, 1); outer.addWidget(card)

        dev = QFrame(); dev.setObjectName("card"); dl = QVBoxLayout(dev); dl.setContentsMargins(18, 14, 18, 14)
        self.info_dev = QLabel(); self.info_dev.setTextFormat(Qt.RichText); self.info_dev.setWordWrap(True)
        self.info_dev.setOpenExternalLinks(True); dl.addWidget(self.info_dev); outer.addWidget(dev)

        row = QHBoxLayout()
        self.info_buttons = {}
        for key, text, fn in (("website", "Visit website", lambda: self._open_url(AI.WEBSITE)),
                              ("privacy", "Privacy policy", lambda: self._open_url(AI.PRIVACY_REPO_URL)),
                              ("terms", "Terms of use", lambda: self._open_url(AI.TERMS_REPO_URL)),
                              ("source", "Source code", lambda: self._open_url(AI.REPO_URL))):
            b = QPushButton(text); b.clicked.connect(lambda _=False, f=fn: f()); row.addWidget(b); self.info_buttons[key] = b
        outer.addLayout(row)
        outer.addStretch(1)
        self._fill_info()
        return page

    def _fill_info(self):
        c = getattr(self, "colors", TH.colors(self.cfg.get("theme", "pitch-black"), self.cfg.get("ui_accent", "#00ffd0")))
        acc, mut = c["accent"], c["muted"]
        from .engine import tray_icon
        self.info_icon.setPixmap(tray_icon().pixmap(72, 72))
        n = len(REGISTRY)
        self.info_head.setText(
            f"<div style='font-size:22px;font-weight:bold;color:{acc}'>{C.APP_NAME}</div>"
            f"<div style='color:{mut}'>Version {C.VERSION} &middot; "
            f"<a style='color:{mut}' href='{AI.LICENSE_URL}'>{AI.LICENSE_NAME}</a></div>"
            f"<p>{AI.APP_TAGLINE}.<br>{n} objects &middot; custom text &middot; "
            f"{len(C.SCHEMA)} global settings &middot; {len(C.PET_SCHEMA)} per object.</p>"
            f"<div style='color:{acc}'>{AI.PLEDGE}</div>")
        self.info_dev.setText(
            f"<div style='font-size:15px;font-weight:bold;color:{acc}'>Developer</div>"
            f"<table cellpadding='3'>"
            f"<tr><td style='color:{mut}'>Name</td><td><b>{AI.DEV_NAME}</b> ({AI.DEV_HANDLE})</td></tr>"
            f"<tr><td style='color:{mut}'>Team</td><td><b>{AI.BRAND}</b> &middot; {AI.LOCATION}</td></tr>"
            f"<tr><td style='color:{mut}'>Your data</td><td>Stays on this PC: <code>{C.config_path()}</code></td></tr>"
            f"</table>")

    def _open_url(self, url):
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        return QDesktopServices.openUrl(QUrl(url))

    # ───────────── theme ─────────────
    def retheme(self):
        self.colors = TH.apply_theme(QApplication.instance(), self.cfg["theme"], self.cfg["ui_accent"])
        TILE["color"] = self.colors["tile"]
        if hasattr(self, "items"):
            self.list.blockSignals(True)          # setIcon fires itemChanged -> would wipe the selection
            try:
                for pid, it in self.items.items():
                    it.setIcon(QIcon(preview_pixmap(REGISTRY[pid])))
            finally:
                self.list.blockSignals(False)
            if self.cur:
                self.sel_icon.setPixmap(preview_pixmap(REGISTRY[self.cur], 120))
        if hasattr(self, "info_head"):
            self._fill_info()

    # ───────────── objects: data <-> widgets ─────────────
    def _pet(self, pid):
        return self.cfg["pets"].setdefault(pid, dict(C.PET_DEFAULTS))

    def _item_toggled(self, it):
        self._pet(it.data(Qt.UserRole))["enabled"] = it.checkState() == Qt.Checked
        if self.cur == it.data(Qt.UserRole):
            was = self._loading; self._loading = True
            try: self.pet_widgets["enabled"].set(it.checkState() == Qt.Checked)
            finally: self._loading = was
        self._update_status(); self._touch()

    def _select(self, it, _prev=None):
        if it is None:
            return
        self.cur = it.data(Qt.UserRole); self._load_pet(self.cur)

    def _load_pet(self, pid):
        spec = REGISTRY[pid]
        self.sel_icon.setPixmap(preview_pixmap(spec, 120)); self.sel_name.setText(f"{spec.name}  ({spec.kind})")
        pc = self._pet(pid)
        was = self._loading; self._loading = True
        try:
            for k, wdg in self.pet_widgets.items():
                wdg.set(pc[k])
        finally:
            self._loading = was

    def _pet_changed(self, key, val):
        if self._loading or not self.cur:
            return
        self._pet(self.cur)[key] = val
        if key == "enabled":
            self.list.blockSignals(True)
            try: self.items[self.cur].setCheckState(Qt.Checked if val else Qt.Unchecked)
            finally: self.list.blockSignals(False)
        self._update_status(); self._touch()

    def reset_pet(self):
        if self.cur:
            en = self._pet(self.cur)["enabled"]
            self.cfg["pets"][self.cur] = dict(C.PET_DEFAULTS, enabled=en); self._load_pet(self.cur); self._touch()

    def refilter(self, *_):
        q, cat = self.search.text().lower().strip(), self.catbox.currentText()
        for pid, it in self.items.items():
            sp = REGISTRY[pid]
            it.setHidden(not ((not q or q in sp.name.lower() or q in sp.cat.lower() or q in sp.kind)
                              and (cat == "All categories" or sp.cat == cat)))

    def _set_enabled(self, ids):
        ids = set(ids)
        for pid, it in self.items.items():
            it.setCheckState(Qt.Checked if pid in ids else Qt.Unchecked)

    def use_preset(self):
        self._set_enabled(PRESETS[self.presetbox.currentText()])

    def surprise(self):
        self._set_enabled(random.sample(list(REGISTRY), 6))

    def bulk(self, on):
        for it in self.items.values():
            if not it.isHidden():
                it.setCheckState(Qt.Checked if on else Qt.Unchecked)

    def _update_status(self):
        n = sum(1 for d in self.cfg["pets"].values() if d.get("enabled"))
        nt = sum(1 for t in self.cfg["texts"] if t.get("enabled"))
        cap = self.cfg["max_active"]
        warn = f"  -  only the first {cap} objects are shown (raise 'Max pets' in General)" if n > cap else ""
        self.status.setText(f"{n} object(s), {nt} text(s) selected{warn}")

    # ───────────── actions ─────────────
    def reset_all(self):
        if QMessageBox.question(self, "Reset", "Reset every setting to default (objects, texts, badge, options)?") == QMessageBox.Yes:
            self.load(C.sanitize({})); self._touch()

    def export_cfg(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export settings", "king-animated-desktop-settings.json", "JSON (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(C.sanitize(self.cfg), f, indent=2)

    def import_cfg(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Import settings", "", "JSON (*.json)")
        if path:
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("not a King Animated Desktop settings file")
                self.load(C.sanitize(data)); self._touch()
            except Exception as e:
                QMessageBox.warning(self, "Import failed", str(e))
