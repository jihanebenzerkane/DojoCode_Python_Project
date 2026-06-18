"""
music_player.py — Widget flottant du lecteur de musique d'ambiance Lofi.
Deux modes :
  • Mode Local   : Lit un fichier MP3/WAV/OGG via QMediaPlayer
  • Mode Spotify : Affiche l'embed Spotify via QWebEngineView
"""
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QSlider, QWidget, QStackedWidget, QLineEdit, QFrame
)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings


class MusicPlayerDialog(QDialog):
    """
    Mini lecteur audio d'ambiance avec onglets Local / Spotify.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎵  Ambiance Musicale Dojo")
        self.setMinimumSize(420, 380)
        self.resize(460, 420)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

        # Backend audio local
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.6)
        self.player.mediaStatusChanged.connect(self._on_media_status)
        self.player.playbackStateChanged.connect(self._update_play_btn)

        self._current_path = None
        self._spotify_url = ""

        self._build()
        self._style()

        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.start(500)

   
    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 14)
        lay.setSpacing(12)

        # Title
        title = QLabel("🎵  Ambiance Musicale Dojo")
        title.setObjectName("music_title")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        # ── Tab Switcher ──────────────────────────────────────────────────
        tab_row = QHBoxLayout()
        tab_row.setSpacing(8)
        self.local_tab_btn = QPushButton("📁  Musique locale")
        self.local_tab_btn.setObjectName("music_tab_active")
        self.local_tab_btn.setCursor(Qt.PointingHandCursor)
        self.local_tab_btn.clicked.connect(lambda: self._switch_tab(0))

        self.spotify_tab_btn = QPushButton("🟢  Spotify")
        self.spotify_tab_btn.setObjectName("music_tab")
        self.spotify_tab_btn.setCursor(Qt.PointingHandCursor)
        self.spotify_tab_btn.clicked.connect(lambda: self._switch_tab(1))

        tab_row.addWidget(self.local_tab_btn)
        tab_row.addWidget(self.spotify_tab_btn)
        lay.addLayout(tab_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #4E533C;")
        lay.addWidget(sep)

        # ── Stacked pages ─────────────────────────────────────────────────
        self.stack = QStackedWidget()
        lay.addWidget(self.stack)

        self.stack.addWidget(self._build_local_page())
        self.stack.addWidget(self._build_spotify_page())

    def _build_local_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        self.track_lbl = QLabel("Aucune piste sélectionnée")
        self.track_lbl.setObjectName("music_track")
        self.track_lbl.setAlignment(Qt.AlignCenter)
        self.track_lbl.setWordWrap(True)
        lay.addWidget(self.track_lbl)

        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        self.progress.setObjectName("music_progress")
        self.progress.sliderMoved.connect(self._seek)
        lay.addWidget(self.progress)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)
        ctrl.setAlignment(Qt.AlignCenter)

        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("music_ctrl_btn")
        self.play_btn.setFixedSize(42, 42)
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.clicked.connect(self._toggle_play)

        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setObjectName("music_ctrl_btn")
        self.stop_btn.setFixedSize(42, 42)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.clicked.connect(self._stop)

        ctrl.addWidget(self.play_btn)
        ctrl.addWidget(self.stop_btn)
        lay.addLayout(ctrl)

        vol_row = QHBoxLayout()
        vol_lbl = QLabel("🔊")
        vol_lbl.setObjectName("music_vol_lbl")
        vol_row.addWidget(vol_lbl)

        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setObjectName("music_progress")
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(60)
        self.vol_slider.valueChanged.connect(
            lambda v: self.audio_output.setVolume(v / 100.0)
        )
        vol_row.addWidget(self.vol_slider)
        lay.addLayout(vol_row)

        open_btn = QPushButton("📁  Charger une musique (MP3 / WAV / OGG)")
        open_btn.setObjectName("music_open_btn")
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.clicked.connect(self._open_file)
        lay.addWidget(open_btn)

        lay.addStretch()
        return page

    def _build_spotify_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        hint = QLabel(
            "🟢  Colle un lien Spotify (playlist, album, piste) :\n"
            "Ex: https://open.spotify.com/playlist/37i9dQ..."
        )
        hint.setObjectName("music_track")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(hint)

        url_row = QHBoxLayout()
        self.spotify_input = QLineEdit()
        self.spotify_input.setPlaceholderText("https://open.spotify.com/playlist/...")
        self.spotify_input.setObjectName("spotify_input")
        self.spotify_input.returnPressed.connect(self._load_spotify)

        load_btn = QPushButton("▶  Ouvrir")
        load_btn.setObjectName("music_open_btn")
        load_btn.setFixedWidth(90)
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.clicked.connect(self._load_spotify)

        url_row.addWidget(self.spotify_input)
        url_row.addWidget(load_btn)
        lay.addLayout(url_row)

        # Quick playlist presets
        presets_lbl = QLabel("— Playlists Lofi populaires —")
        presets_lbl.setAlignment(Qt.AlignCenter)
        presets_lbl.setObjectName("music_track")
        lay.addWidget(presets_lbl)

        presets = [
            ("☕  Lofi Hip Hop", "https://open.spotify.com/playlist/0vvXsWCC9xrXsKd4eZs6ci"),
            ("🌿  Chill Focus",  "https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0"),
            ("🎋  Study Beats",  "https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn"),
        ]
        for label, url in presets:
            btn = QPushButton(label)
            btn.setObjectName("music_open_btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, u=url: self._load_spotify_url(u))
            lay.addWidget(btn)

        # WebEngineView for Spotify embed
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(160)
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.web_view.setHtml(
            "<html><body style='background:#1DB954; display:flex; align-items:center; "
            "justify-content:center; height:100vh; margin:0;'>"
            "<p style='color:white; font-family:sans-serif; font-size:16px;'>🟢 Colle un lien Spotify ci-dessus</p>"
            "</body></html>"
        )
        lay.addWidget(self.web_view)
        return page

    # ── Tab switching ──────────────────────────────────────────────────────

    def _switch_tab(self, idx: int):
        self.stack.setCurrentIndex(idx)
        if idx == 0:
            self.local_tab_btn.setObjectName("music_tab_active")
            self.spotify_tab_btn.setObjectName("music_tab")
        else:
            self.local_tab_btn.setObjectName("music_tab")
            self.spotify_tab_btn.setObjectName("music_tab_active")
        # Force style refresh
        for btn in [self.local_tab_btn, self.spotify_tab_btn]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── Spotify ───────────────────────────────────────────────────────────

    def _load_spotify(self):
        url = self.spotify_input.text().strip()
        if url:
            self._load_spotify_url(url)

    def _load_spotify_url(self, url: str):
        self.spotify_input.setText(url)
        # Convert share URL to embed URL
        # https://open.spotify.com/playlist/ID -> https://open.spotify.com/embed/playlist/ID
        embed_url = url.replace("open.spotify.com/", "open.spotify.com/embed/")
        # Remove query params
        embed_url = embed_url.split("?")[0]
        embed_url += "?utm_source=generator&theme=0"
        self.web_view.load(QUrl(embed_url))
        self._switch_tab(1)

    # ── Local player ──────────────────────────────────────────────────────

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une piste musicale", "",
            "Audio (*.mp3 *.wav *.ogg *.flac *.m4a *.aac)"
        )
        if path:
            self._load(path)
            self.player.play()

    def _load(self, path: str):
        self._current_path = path
        self.player.setSource(QUrl.fromLocalFile(path))
        name = os.path.basename(path)
        if len(name) > 36:
            name = name[:33] + "..."
        self.track_lbl.setText(f"♪  {name}")

    def _toggle_play(self):
        if not self._current_path:
            self._open_file()
            return
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _stop(self):
        self.player.stop()
        self.progress.setValue(0)

    def _seek(self, value: int):
        duration = self.player.duration()
        if duration > 0:
            pos = int(value / 1000.0 * duration)
            self.player.setPosition(pos)

    def _update_progress(self):
        duration = self.player.duration()
        if duration > 0:
            pos = self.player.position()
            self.progress.setValue(int(pos / duration * 1000))

    def _on_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

    def _update_play_btn(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # ── Stylesheet ────────────────────────────────────────────────────────

    def _style(self):
        self.setStyleSheet("""
            QDialog {
                background: #F5F7EC;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#music_title {
                font-size: 15px;
                font-weight: bold;
                color: #4E533C;
                border-bottom: 2px solid #4E533C;
                padding-bottom: 6px;
            }
            QLabel#music_track {
                font-size: 12px;
                color: #8D9078;
                font-weight: bold;
            }
            QLabel#music_vol_lbl {
                font-size: 16px;
                color: #4E533C;
            }
            QPushButton#music_tab_active {
                background: #CCD49F;
                color: #4E533C;
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #4E533C;
                border-bottom: 4px solid #4E533C;
                border-radius: 10px;
                padding: 6px 16px;
            }
            QPushButton#music_tab {
                background: #E5E8D6;
                color: #8D9078;
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #8D9078;
                border-bottom: 4px solid #8D9078;
                border-radius: 10px;
                padding: 6px 16px;
            }
            QPushButton#music_tab:hover {
                background: #F5F7EC;
                color: #4E533C;
            }
            QPushButton#music_ctrl_btn {
                background: #CCD49F;
                color: #4E533C;
                font-size: 16px;
                font-weight: bold;
                border: 3px solid #4E533C;
                border-bottom: 5px solid #4E533C;
                border-radius: 10px;
            }
            QPushButton#music_ctrl_btn:hover { background: #DCE3B5; }
            QPushButton#music_ctrl_btn:pressed {
                border-bottom: 3px solid #4E533C;
                margin-top: 2px;
            }
            QPushButton#music_open_btn {
                background: #E5E8D6;
                color: #4E533C;
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #4E533C;
                border-bottom: 4px solid #4E533C;
                border-radius: 10px;
                padding: 7px 14px;
            }
            QPushButton#music_open_btn:hover { background: #CCD49F; }
            QLineEdit#spotify_input {
                background: #FFFFFF;
                border: 2px solid #1DB954;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #4E533C;
                font-weight: bold;
            }
            QLineEdit#spotify_input:focus { border-color: #1DB954; }
            QSlider#music_progress::groove:horizontal {
                height: 6px;
                background: #CCD49F;
                border: 1px solid #4E533C;
                border-radius: 3px;
            }
            QSlider#music_progress::handle:horizontal {
                background: #4E533C;
                border: 1px solid #4E533C;
                width: 14px; height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider#music_progress::sub-page:horizontal {
                background: #8D9078;
                border-radius: 3px;
            }
        """)
