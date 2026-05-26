"""
music_player.py — Widget flottant du lecteur de musique d'ambiance Lofi.
Utilise PySide6.QtMultimedia pour la lecture audio locale.
"""
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QSlider, QWidget, QFrame
)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class MusicPlayerDialog(QDialog):
    """
    Mini lecteur audio d'ambiance.
    Permet de charger une musique locale (MP3, WAV, OGG) et de la jouer en boucle.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎵  Ambiance Musicale Dojo")
        self.setFixedSize(380, 280)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

        # Backend audio
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.6)

        # Rejouer en boucle quand la piste se termine
        self.player.mediaStatusChanged.connect(self._on_media_status)
        self.player.playbackStateChanged.connect(self._update_play_btn)

        self._current_path = None

        self._build()
        self._style()

        # Timer pour mettre à jour la barre de progression
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.start(500)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 16)
        lay.setSpacing(14)

        # ── Titre ──
        title = QLabel("🎵  Ambiance Musicale Lofi")
        title.setObjectName("music_title")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        # ── Info piste ──
        self.track_lbl = QLabel("Aucune piste sélectionnée")
        self.track_lbl.setObjectName("music_track")
        self.track_lbl.setAlignment(Qt.AlignCenter)
        self.track_lbl.setWordWrap(True)
        lay.addWidget(self.track_lbl)

        # ── Barre de progression ──
        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        self.progress.setObjectName("music_progress")
        self.progress.sliderMoved.connect(self._seek)
        lay.addWidget(self.progress)

        # ── Contrôles ──
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

        # ── Volume ──
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

        # ── Bouton chargement fichier ──
        open_btn = QPushButton("📁  Charger une musique (MP3 / WAV / OGG)")
        open_btn.setObjectName("music_open_btn")
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.clicked.connect(self._open_file)
        lay.addWidget(open_btn)

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une piste musicale",
            "",
            "Audio (*.mp3 *.wav *.ogg *.flac *.m4a *.aac)"
        )
        if path:
            self._load(path)
            self.player.play()

    def _load(self, path: str):
        self._current_path = path
        self.player.setSource(QUrl.fromLocalFile(path))
        name = os.path.basename(path)
        # Tronquer le nom si trop long
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
        """Rejoue en boucle quand la piste se termine."""
        if status == QMediaPlayer.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

    def _update_play_btn(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")

    def closeEvent(self, event):
        """Ne pas arrêter la musique quand on ferme le dialogue."""
        event.ignore()
        self.hide()

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
            QPushButton#music_ctrl_btn {
                background: #CCD49F;
                color: #4E533C;
                font-size: 16px;
                font-weight: bold;
                border: 3px solid #4E533C;
                border-bottom: 5px solid #4E533C;
                border-radius: 10px;
            }
            QPushButton#music_ctrl_btn:hover {
                background: #DCE3B5;
            }
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
            QPushButton#music_open_btn:hover {
                background: #CCD49F;
            }
            QSlider#music_progress::groove:horizontal {
                height: 6px;
                background: #CCD49F;
                border: 1px solid #4E533C;
                border-radius: 3px;
            }
            QSlider#music_progress::handle:horizontal {
                background: #4E533C;
                border: 1px solid #4E533C;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider#music_progress::sub-page:horizontal {
                background: #8D9078;
                border-radius: 3px;
            }
        """)
