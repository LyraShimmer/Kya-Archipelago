from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import os
import queue
import re
import shutil
import subprocess
import socket
import ssl
import struct
import sys
import threading
import time
import zipfile
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image, ImageDraw, ImageEnhance
except ImportError:
    raise SystemExit("Pillow is not installed. Run: python -m pip install pillow")

from kya_pine_raw import PineClient, PineError
from kya_data_loader import load_game_data
from kya_memory_bootstrap import ensure_memory_core, stop_owned_memory_core
from kya_ap_link import APLink
from kya_shop_native import NativeShopResolver, NativeSoldStateObserver
from kya_shop_audit import export_native_shop_audit
from kya_auto_save import AutoSaveController, default_sstates_path
from kya_map_guard import MapGuardRecovery
from kya_brazul_capture import BrazulCaptureGuard


APP_TITLE = "Kya: Dark Lineage - Archipelago Launcher 9.0.0-beta1"
WINDOW_W = 620
WINDOW_H = 1000

PINE_HOST = "127.0.0.1"
PINE_PORT = 28111  # MemoryCore proxy; only MemoryCore talks to real PCSX2 PINE :28011

# V0.8.16 correction from live purchase logs:
#   Silver Boomy = 100 Nooties (not 50)
#   Speed Board  = 50 Nooties (not 100)
# Golden Boomy remains 100. This fixes the Silver/Speed/Golden cross-identification.
# Vanilla Nativs City shop prices observed during our own playtests.  These are
# only an identity hint for purchases where the vanilla reward is already owned;
# money alone never overrides a contradictory live/serialized signal.
SHOP_PRICE_HINTS = {
    "Nativs City - Shop - Basic Boomy": 10,
    "Nativs City - Shop - Yellow Bracelet": 100,
    "Nativs City - Shop - Telescope": 30,
    "Nativs City - Shop - Magic Board": 50,
    "Nativs City - Shop - Green Bracelet": 150,
    "Nativs City - Shop - Climbing Gloves": 50,
    "Nativs City - Shop - Extra Energy Bar 1": 1000,
    "Nativs City - Shop - Blue Bracelet": 200,
    "Nativs City - Shop - Jamgut Birdcall": 70,
    "Nativs City - Shop - Speed Board": 50,
    "Nativs City - Shop - Golden Boomy": 100,
    "Nativs City - Shop - Silver Bracelet": 500,
    "Nativs City - Shop - Silver Boomy": 100,
    "Nativs City - Shop - Brown Bracelet": 250,
    "Nativs City - Shop - Magic Bouncers": 50,
    "Nativs City - Shop - Extra Energy Bar 2": 1000,
    "Nativs City - Shop - Black Bracelet": 400,
    "Nativs City - Shop - Gold Bracelet": 700,
}


# V0.8.17: live shop-source layout reconstructed from our own BWITCH order and
# the causally validated Yellow Bracelet flag.  The serializer's runtime source
# used a 0x18-byte stride; Yellow is the 5th BWITCH entry, therefore:
#     Yellow availability = shop_source + 5 * 0x18 = shop_source + 0x78
# which exactly matches the previously validated live flag.  We use the same
# layout for the surrounding one-shot entries.  The absolute 0x01A0xxxx address
# is NEVER hard-coded; the source base is found dynamically from the live 0/1
# availability pattern.
SHOP_RUNTIME_STRIDE = 0x18
SHOP_RUNTIME_SLOT_INDEX = {
    "Nativs City - Shop - Basic Boomy": 1,
    "Nativs City - Shop - Telescope": 4,
    "Nativs City - Shop - Yellow Bracelet": 5,
    "Nativs City - Shop - Magic Board": 6,
    "Nativs City - Shop - Climbing Gloves": 7,
    "Nativs City - Shop - Green Bracelet": 9,
    "Nativs City - Shop - Extra Energy Bar 1": 10,
    "Nativs City - Shop - Jamgut Birdcall": 11,
    "Nativs City - Shop - Blue Bracelet": 12,
    "Nativs City - Shop - Speed Board": 13,
    "Nativs City - Shop - Black Bracelet": 14,
    "Nativs City - Shop - Golden Boomy": 15,
    "Nativs City - Shop - Silver Boomy": 16,
    "Nativs City - Shop - Brown Bracelet": 17,
    "Nativs City - Shop - Magic Bouncers": 18,
    "Nativs City - Shop - Gold Bracelet": 19,
    "Nativs City - Shop - Silver Bracelet": 20,
}
SHOP_RUNTIME_SCAN_WINDOWS = (
    (0x01900000, 0x01C00000),  # fast path; validated source was in 0x01A0xxxx
    (0x01800000, 0x02000000),  # fallback for heap relocation
)


# V0.8.19 — Ghidra-backed grouped live shop flags.
#
# Our own Ghidra/breakpoint work on the shop serializer proved that one serialized
# bitfield is rebuilt from five live availability fields at +0x18, +0x30, +0x48,
# +0x60 and +0x78 from a relocatable source-group base.  The causally validated
# Yellow Bracelet is mask 0x10 in serialized group 0x006FC4D8 and lives at
# group_source + 0x78, proving the correspondence below:
#     mask 0x01 -> +0x18, 0x02 -> +0x30, 0x04 -> +0x48,
#     mask 0x08 -> +0x60, 0x10 -> +0x78.
#
# This is deliberately derived from the exact serialized address+mask mapping
# already present in kya_ap_data.json.  We no longer assume that every shop item
# belongs to one giant 0x18-stride array (the V0.8.17/18 mistake).
SHOP_RUNTIME_MASK_OFFSET = {
    0x01: 0x18,
    0x02: 0x30,
    0x04: 0x48,
    0x08: 0x60,
    0x10: 0x78,
}
SHOP_RUNTIME_GROUP_SCAN_WINDOWS = (
    (0x01900000, 0x01C00000),
    (0x01800000, 0x02000000),
)

# Progression playtest scanner.  These are direct PAL ScenarioVar addresses
# already validated during the reverse-engineering pass.  The scanner only
# writes them when the user explicitly asks for a manual TEST grant.
GLOBAL_FREED_WOLFENS_ADDR = 0x004253D4
TEST_PROGRESSION_ITEMS = (
    "Basic Boomy",
    "Magic Board",
    "Climbing Gloves",
    "Jamgut Birdcall",
    "Silver Boomy",
    "Magic Bouncers",
    "Speed Board",
    "Golden Boomy",
    "Receptacle",
)
TEST_ITEM_WRITES = {
    "Basic Boomy": (0x0042541C, 1),
    "Magic Board": (0x00425454, 1),
    "Climbing Gloves": (0x00425414, 1),
    "Jamgut Birdcall": (0x0042543C, 1),
    "Silver Boomy": (0x0042541C, 2),
    "Magic Bouncers": (0x0042540C, 1),
    "Speed Board": (0x00425454, 2),
    "Golden Boomy": (0x0042541C, 3),
    "Receptacle": (0x0042544C, 1),
}

# Dedicated shop-validation preset. This intentionally maxes the PLAYER-side
# progression while restoring all 18 serialized one-shot shop stock bits.
# It is a test harness only: player possession and shop availability are kept
# separate so every shop can be purchased as an AP location even when Kya
# already owns the vanilla reward.
SHOP_DEMO_WOLFENS = 260
SHOP_DEMO_NOOTIES = 0x0000FFFF
SHOP_DEMO_BOOMY_LEVEL = 3
SHOP_DEMO_BRACELET_BITS = 0xFF
SHOP_DEMO_BOARD_LEVEL = 2
SHOP_DEMO_MAGIC_GAUGE_LEVEL = 10
SHOP_DEMO_LIFE_GAUGE = 50
# Final validation labels for APWorld 0.7.10. These match the corrected
# Fast Travel Location mapping used by the AP checks.
FAST_TRAVEL_TEST_LABELS = {
    "Flying Forest": {
        0x0DB7: "FT01",
        0x0E48: "FT02",
        0x0ED1: "FT03",
        0x0FB0: "FT04",
    },
    "Hunters Domain": {
        0x15EF: "FT01",
        0x1197: "FT02",
        0x1307: "FT03",
        0x130D: "FT04",
        0x15C5: "FT05",
        0x123D: "FT06",
    },
}

EXPECTED_GAME_ID = "SLES_514.73"
EXPECTED_GAME_ID_NORMALIZED = "SLES51473"

# ---------------------------------------------------------------------------
# Supported PAL ISO / executable fingerprints
# ---------------------------------------------------------------------------
ISO_SECTOR_SIZE = 2048
KNOWN_GOOD_ISO_SHA256 = "21563BE6D8EE2E9C719B7F4BF6B349475C610E7C1ACF57BB74CCC6BF6B067E8A"
KNOWN_GOOD_EXE_SHA256 = "D7D85D0FC342F8F8F684AAC6EBBEA938CC3F1D9F063D071796F76DBF18B7C0CB"

STATUS_COLORS = {
    "disconnected": "#e04b4b",
    "connecting": "#f0a13e",
    "busy": "#f0a13e",  # A scan is late, but PCSX2/PINE has not reported a failure.
    "connected": "#45db68",
}

TEXT_MAIN = "#f7f8fa"
TEXT_SUB = "#c3cbd2"
ENTRY_BG = "#111a22"
ENTRY_BORDER = "#5b6975"
LOG_BG = "#091015"
BUTTON_GREEN = "#2fa653"
BUTTON_GREEN_ACTIVE = "#3bbd63"

# ---------------------------------------------------------------------------
# Camera routing validated in-game
# ---------------------------------------------------------------------------
INPUT_OBJECTS = (0x00450960, 0x00450FC0)
ROUTE_OFFSETS = (0x624, 0x628, 0x62C, 0x630)

HORIZONTAL_VANILLA = (0x0C, 0x0D)
HORIZONTAL_INVERTED = (0x0D, 0x0C)

VERTICAL_VANILLA = (0x0E, 0x0F)
VERTICAL_INVERTED = (0x0F, 0x0E)

# Confirmed MAP open/closed state.
MAP_STATE_ADDR = 0x00451ABC
MAP_CLOSED_VALUE = 0x00000000

# 0.9.58 - Camera submode used by the game's own zoom handler.
# Ghidra PAL SLES_514.73, FUN_0018E0E0 and neighbouring handler:
#   if (iRam00448e7c == 3) ... fStack_8 adjusts zoom by 0.975/1.025.
# This distinguishes zoom *input handling* from normal camera motion.
# IMPORTANT: The older MAP_STATE_ADDR 0x00451ABC also reacts to amber
# regeneration and MUST NOT be used for AP writes or gameplay gating.
MAP_ZOOM_CAMERA_MODE_ADDR = 0x00448E7C
MAP_ZOOM_CAMERA_MODE = 3

# Diagnostic 0.9.28: isolate UI-related memory writes after two menu incidents.
# ON by default in this special build. Both switches can be turned OFF
# independently by a developer when comparing with the 0.9.27 release.
# Disabling camera routing also disables inverted camera settings temporarily.
DIAGNOSTIC_DISABLE_ALL_CAMERA_ROUTE_WRITES = False
DIAGNOSTIC_SUSPEND_AP_TICKS_WHILE_MAP_OPEN = False

SIG_ADDRS = (0x0042BCA0, 0x0042BCA8, 0x0042BCB0, 0x0042BCB8)
SIG_VALUES = (0x0C, 0x0D, 0x0E, 0x0F)

LANGUAGES = (
    ("en", "🇬🇧", "English"),
    ("fr", "🇫🇷", "French"),
    ("de", "🇩🇪", "Deutsch"),
    ("es", "🇪🇸", "Español"),
    ("it", "🇮🇹", "Italiano"),
)

T = {
    "en": {
        "color_studio_button": "Personalize Kya",
        "texture_ok": "PCSX2 textures folder found",
        "texture_missing": "PCSX2 textures folder not found — click for details",
        "texture_search": "Looking for:",
        "texture_details": "PCSX2 texture replacement folder not found.\\n\\nChecked paths:\\n{paths}\\n\\nIn PCSX2, open Settings > Folders > Textures. Then choose the corresponding SLES-51473/replacements folder in Kya Color Studio.\\n\\nThe game must use hardware rendering and Load Texture Replacements must be enabled.",
        "server": "Server",
        "name": "Name",
        "password_optional": "Password (optional)",
        "connect": "CONNECT",
        "connecting": "CONNECTING...",
        "status_pine": "PCSX2 / PINE",
        "status_server": "Archipelago Server",
        "status_game": "Game Detected",
        "disconnected": "Disconnected",
        "connected": "Connected",
        "connecting_status": "Connecting...",
        "pine_busy_state": "Read delayed",
        "checking": "Checking...",
        "reachable": "Reachable",
        "not_detected": "Not detected",
        "unknown": "Unknown",
        "log": "Log",
        "clear": "Clear",
        "launcher_ready": "Launcher ready.",
        "starting_checks": "Starting connection checks...",
        "pine_ok": "PINE connection established.",
        "pine_fail": "PINE connection failed.",
        "pine_busy_hint": "PINE connected but did not answer. Close any other Kya camera/mapper tool using PINE, then try again.",
        "game_ok": "Supported game detected.",
        "game_fail": "Supported game not detected.",
        "server_ok": "Server connection available.",
        "server_fail": "Server connection failed.",
        "checks_ok": "Connection checks completed.",
        "checks_warn": "Connection checks completed with warnings.",
        "name_required": "Enter the Archipelago Name / slot.",
        "server_empty": "The server address is empty.",
        "server_format": "Expected format: archipelago.gg:12345",
        "host_invalid": "Invalid host name.",
        "port_number": "The port must be a number.",
        "port_invalid": "Invalid port.",
        "bg_missing": "Background image not found:\n{path}\n\nThe launcher uses BackIMG.webp.",
        "options": "Options",
        "ap_connection": "Archipelago connection",
        "save_connection": "Save connection settings",
        "connection_saved": "Connection settings saved.",
        "overlay_title": "Archipelago Overlay",
        "overlay_on": "Archipelago Overlay: ON",
        "overlay_off": "Archipelago Overlay: OFF",
        "overlay_test": "Send Archipelago test",
        "overlay_note": "Shows Archipelago item trades in the bottom-left corner of the PCSX2 window and follows it, while PCSX2 is windowed. It is intentionally hidden in fullscreen.",
        "overlay_test_in": "TEST • TestPlayer sent Progressive Boomy to you",
        "overlay_test_out": "TEST • You sent Nooties +100 to TestPlayer",
        "language": "Language",
        "camera": "Camera",
        "horizontal_camera": "Horizontal camera",
        "vertical_camera": "Vertical camera",
        "vanilla": "Vanilla",
        "inverted": "Inverted",
        "camera_note": "Camera inversion applies in-game; map zoom/dezoom remains normal even with inverted vertical camera.",
        "close": "Close",
        "camera_active": "Camera controls active.",
        "iso_compatibility": "ISO Compatibility",
        "iso_check_button": "ISO check Compatibility",
        "iso_not_checked": "Not checked",
        "iso_checking": "Checking ISO...",
        "iso_compatible": "Compatible",
        "iso_incompatible": "Not compatible",
        "iso_exact_ok": "Exact supported PAL Europe ISO.",
        "iso_exe_ok": "Different ISO image, but the PAL executable is identical and compatible.",
        "iso_wrong_serial": "Unsupported game version: {serial}",
        "iso_unknown_revision": "SLES-51473 detected, but the executable differs from the supported build.",
        "iso_read_error": "Unable to check this ISO: {error}",
    },
    "fr": {
        "color_studio_button": "Personnaliser Kya",
        "texture_ok": "Dossier de textures PCSX2 détecté",
        "texture_missing": "Textures PCSX2 introuvables — cliquer pour les détails",
        "texture_search": "Dossier recherché :",
        "texture_details": "Dossier de remplacement des textures PCSX2 introuvable.\\n\\nChemins vérifiés :\\n{paths}\\n\\nDans PCSX2 : Paramètres > Dossiers > Textures. Puis choisis le dossier SLES-51473/replacements correspondant dans Kya Color Studio.\\n\\nUtilise un rendu matériel et active le chargement des textures de remplacement.",
        "server": "Serveur",
        "name": "Nom",
        "password_optional": "Mot de passe (optionnel)",
        "connect": "CONNEXION",
        "connecting": "CONNEXION...",
        "status_pine": "PCSX2 / PINE",
        "status_server": "Serveur Archipelago",
        "status_game": "Jeu détecté",
        "disconnected": "Déconnecté",
        "connected": "Connecté",
        "connecting_status": "Connexion...",
        "pine_busy_state": "Lecture retardée",
        "checking": "Vérification...",
        "reachable": "Accessible",
        "not_detected": "Non détecté",
        "unknown": "Inconnu",
        "log": "Journal",
        "clear": "Effacer",
        "launcher_ready": "Launcher prêt.",
        "starting_checks": "Démarrage des vérifications de connexion...",
        "pine_ok": "Connexion PINE établie.",
        "pine_fail": "Échec de la connexion PINE.",
        "pine_busy_hint": "PINE accepte la connexion mais ne répond pas. Ferme tout autre outil caméra/mapper Kya qui utilise PINE, puis réessaie.",
        "game_ok": "Jeu compatible détecté.",
        "game_fail": "Jeu compatible non détecté.",
        "server_ok": "Serveur accessible.",
        "server_fail": "Échec de la connexion au serveur.",
        "checks_ok": "Vérifications terminées.",
        "checks_warn": "Vérifications terminées avec des avertissements.",
        "name_required": "Entre le nom / slot Archipelago.",
        "server_empty": "L'adresse du serveur est vide.",
        "server_format": "Format attendu : archipelago.gg:12345",
        "host_invalid": "Nom d'hôte invalide.",
        "port_number": "Le port doit être un nombre.",
        "port_invalid": "Port invalide.",
        "bg_missing": "Image de fond introuvable :\n{path}\n\nLe launcher utilise BackIMG.webp.",
        "options": "Options",
        "ap_connection": "Connexion Archipelago",
        "save_connection": "Enregistrer les paramètres",
        "connection_saved": "Paramètres de connexion enregistrés.",
        "overlay_title": "Archipelago Overlay",
        "overlay_on": "Archipelago Overlay : ACTIVÉ",
        "overlay_off": "Archipelago Overlay : DÉSACTIVÉ",
        "overlay_test": "Envoyer un test Archipelago",
        "overlay_note": "Affiche les trades Archipelago en bas à gauche de la fenêtre PCSX2 et suit automatiquement la fenêtre, tant que PCSX2 est en mode fenêtré. Il est volontairement masqué en plein écran.",
        "overlay_test_in": "TEST • TestPlayer vous envoie Progressive Boomy",
        "overlay_test_out": "TEST • Vous envoyez Nooties +100 à TestPlayer",
        "language": "Langue",
        "camera": "Caméra",
        "horizontal_camera": "Caméra horizontale",
        "vertical_camera": "Caméra verticale",
        "vanilla": "Vanilla",
        "inverted": "Inversé",
        "camera_note": "L'inversion de la caméra s'applique en jeu ; le zoom/dézoom de la carte reste normal, même avec la caméra verticale inversée.",
        "close": "Fermer",
        "camera_active": "Contrôles caméra actifs.",
        "iso_compatibility": "Compatibilité ISO",
        "iso_check_button": "ISO check Compatibility",
        "iso_not_checked": "Non vérifiée",
        "iso_checking": "Vérification de l’ISO...",
        "iso_compatible": "Compatible",
        "iso_incompatible": "Non compatible",
        "iso_exact_ok": "ISO PAL Europe exacte et supportée.",
        "iso_exe_ok": "L’ISO diffère, mais l’exécutable PAL est identique et compatible.",
        "iso_wrong_serial": "Version du jeu non supportée : {serial}",
        "iso_unknown_revision": "SLES-51473 détecté, mais l’exécutable diffère du build supporté.",
        "iso_read_error": "Impossible de vérifier cette ISO : {error}",
    },
    "de": {
        "color_studio_button": "Kya anpassen",
        "texture_ok": "PCSX2-Texturordner gefunden",
        "texture_missing": "PCSX2-Texturen nicht gefunden – für Details klicken",
        "texture_search": "Gesuchter Ordner:",
        "texture_details": "PCSX2-Texturersatzordner nicht gefunden.\\n\\nGeprüfte Pfade:\\n{paths}\\n\\nIn PCSX2: Einstellungen > Ordner > Texturen. Wähle den passenden SLES-51473/replacements-Ordner in Kya Color Studio.\\n\\nHardware-Rendering und Texturersatz aktivieren.",
        "server": "Server",
        "name": "Name",
        "password_optional": "Passwort (optional)",
        "connect": "VERBINDEN",
        "connecting": "VERBINDUNG...",
        "status_pine": "PCSX2 / PINE",
        "status_server": "Archipelago-Server",
        "status_game": "Spiel erkannt",
        "disconnected": "Getrennt",
        "connected": "Verbunden",
        "connecting_status": "Verbindung...",
        "pine_busy_state": "Lesezugriff verzögert",
        "checking": "Prüfung...",
        "reachable": "Erreichbar",
        "not_detected": "Nicht erkannt",
        "unknown": "Unbekannt",
        "log": "Protokoll",
        "clear": "Leeren",
        "launcher_ready": "Launcher bereit.",
        "starting_checks": "Verbindungsprüfungen werden gestartet...",
        "pine_ok": "PINE-Verbindung hergestellt.",
        "pine_fail": "PINE-Verbindung fehlgeschlagen.",
        "pine_busy_hint": "PINE nimmt die Verbindung an, antwortet aber nicht. Schließe andere Kya-Kamera/Mapper-Tools, die PINE verwenden, und versuche es erneut.",
        "game_ok": "Unterstütztes Spiel erkannt.",
        "game_fail": "Unterstütztes Spiel nicht erkannt.",
        "server_ok": "Server ist erreichbar.",
        "server_fail": "Serververbindung fehlgeschlagen.",
        "checks_ok": "Verbindungsprüfungen abgeschlossen.",
        "checks_warn": "Verbindungsprüfungen mit Warnungen abgeschlossen.",
        "name_required": "Archipelago-Name / Slot eingeben.",
        "server_empty": "Die Serveradresse ist leer.",
        "server_format": "Erwartetes Format: archipelago.gg:12345",
        "host_invalid": "Ungültiger Hostname.",
        "port_number": "Der Port muss eine Zahl sein.",
        "port_invalid": "Ungültiger Port.",
        "bg_missing": "Hintergrundbild nicht gefunden:\n{path}\n\nDer Launcher verwendet BackIMG.webp.",
        "options": "Optionen",
        "ap_connection": "Archipelago-Verbindung",
        "save_connection": "Verbindungseinstellungen speichern",
        "connection_saved": "Verbindungseinstellungen gespeichert.",
        "overlay_title": "Archipelago Overlay",
        "overlay_on": "Archipelago Overlay: AN",
        "overlay_off": "Archipelago Overlay: AUS",
        "overlay_test": "Archipelago-Test senden",
        "overlay_note": "Zeigt Archipelago-Item-Trades unten links im PCSX2-Fenster an und folgt dem Fenster, solange PCSX2 im Fenstermodus läuft. Im Vollbildmodus wird es absichtlich ausgeblendet.",
        "overlay_test_in": "TEST • TestPlayer hat dir Progressive Boomy gesendet",
        "overlay_test_out": "TEST • Du hast Nooties +100 an TestPlayer gesendet",
        "language": "Sprache",
        "camera": "Kamera",
        "horizontal_camera": "Horizontale Kamera",
        "vertical_camera": "Vertikale Kamera",
        "vanilla": "Vanilla",
        "inverted": "Invertiert",
        "camera_note": "Die Kameraumkehr gilt im Spiel; das Vergrößern/Verkleinern der Karte behält die normale Richtung bei.",
        "close": "Schließen",
        "camera_active": "Kamerasteuerung aktiv.",
        "iso_compatibility": "ISO-Kompatibilität",
        "iso_check_button": "ISO check Compatibility",
        "iso_not_checked": "Nicht geprüft",
        "iso_checking": "ISO wird geprüft...",
        "iso_compatible": "Kompatibel",
        "iso_incompatible": "Nicht kompatibel",
        "iso_exact_ok": "Exakte unterstützte PAL-Europe-ISO.",
        "iso_exe_ok": "Andere ISO-Datei, aber die PAL-Programmdatei ist identisch und kompatibel.",
        "iso_wrong_serial": "Nicht unterstützte Spielversion: {serial}",
        "iso_unknown_revision": "SLES-51473 erkannt, aber die Programmdatei unterscheidet sich vom unterstützten Build.",
        "iso_read_error": "ISO konnte nicht geprüft werden: {error}",
    },
    "es": {
        "color_studio_button": "Personalizar a Kya",
        "texture_ok": "Carpeta de texturas de PCSX2 detectada",
        "texture_missing": "No se encuentran las texturas de PCSX2 — ver detalles",
        "texture_search": "Carpeta buscada:",
        "texture_details": "No se encontró la carpeta de reemplazo de texturas de PCSX2.\\n\\nRutas comprobadas:\\n{paths}\\n\\nEn PCSX2: Ajustes > Carpetas > Texturas. Selecciona la carpeta SLES-51473/replacements correspondiente en Kya Color Studio.\\n\\nActiva el renderizado por hardware y la carga de texturas de reemplazo.",
        "server": "Servidor",
        "name": "Nombre",
        "password_optional": "Contraseña (opcional)",
        "connect": "CONECTAR",
        "connecting": "CONECTANDO...",
        "status_pine": "PCSX2 / PINE",
        "status_server": "Servidor Archipelago",
        "status_game": "Juego detectado",
        "disconnected": "Desconectado",
        "connected": "Conectado",
        "connecting_status": "Conectando...",
        "pine_busy_state": "Lectura retrasada",
        "checking": "Comprobando...",
        "reachable": "Accesible",
        "not_detected": "No detectado",
        "unknown": "Desconocido",
        "log": "Registro",
        "clear": "Limpiar",
        "launcher_ready": "Launcher listo.",
        "starting_checks": "Iniciando comprobaciones de conexión...",
        "pine_ok": "Conexión PINE establecida.",
        "pine_fail": "Error de conexión PINE.",
        "pine_busy_hint": "PINE acepta la conexión pero no responde. Cierra cualquier otra herramienta de cámara/mapper de Kya que use PINE e inténtalo de nuevo.",
        "game_ok": "Juego compatible detectado.",
        "game_fail": "Juego compatible no detectado.",
        "server_ok": "Servidor accesible.",
        "server_fail": "Error de conexión al servidor.",
        "checks_ok": "Comprobaciones completadas.",
        "checks_warn": "Comprobaciones completadas con avisos.",
        "name_required": "Introduce el nombre / slot de Archipelago.",
        "server_empty": "La dirección del servidor está vacía.",
        "server_format": "Formato esperado: archipelago.gg:12345",
        "host_invalid": "Nombre de host no válido.",
        "port_number": "El puerto debe ser un número.",
        "port_invalid": "Puerto no válido.",
        "bg_missing": "No se encontró la imagen de fondo:\n{path}\n\nEl launcher usa BackIMG.webp.",
        "options": "Opciones",
        "ap_connection": "Conexión de Archipelago",
        "save_connection": "Guardar ajustes de conexión",
        "connection_saved": "Ajustes de conexión guardados.",
        "overlay_title": "Archipelago Overlay",
        "overlay_on": "Archipelago Overlay: ACTIVADO",
        "overlay_off": "Archipelago Overlay: DESACTIVADO",
        "overlay_test": "Enviar prueba de Archipelago",
        "overlay_note": "Muestra los intercambios de objetos de Archipelago abajo a la izquierda de la ventana de PCSX2 y sigue la ventana, mientras PCSX2 esté en modo ventana. Se oculta intencionadamente a pantalla completa.",
        "overlay_test_in": "TEST • TestPlayer te envió Progressive Boomy",
        "overlay_test_out": "TEST • Enviaste Nooties +100 a TestPlayer",
        "language": "Idioma",
        "camera": "Cámara",
        "horizontal_camera": "Cámara horizontal",
        "vertical_camera": "Cámara vertical",
        "vanilla": "Vanilla",
        "inverted": "Invertido",
        "camera_note": "La inversión de cámara se aplica en el juego; el zoom del mapa mantiene su dirección normal.",
        "close": "Cerrar",
        "camera_active": "Controles de cámara activos.",
        "iso_compatibility": "Compatibilidad ISO",
        "iso_check_button": "ISO check Compatibility",
        "iso_not_checked": "Sin comprobar",
        "iso_checking": "Comprobando ISO...",
        "iso_compatible": "Compatible",
        "iso_incompatible": "No compatible",
        "iso_exact_ok": "ISO PAL Europa exacta y compatible.",
        "iso_exe_ok": "La ISO es diferente, pero el ejecutable PAL es idéntico y compatible.",
        "iso_wrong_serial": "Versión del juego no compatible: {serial}",
        "iso_unknown_revision": "Se detectó SLES-51473, pero el ejecutable difiere de la versión compatible.",
        "iso_read_error": "No se pudo comprobar esta ISO: {error}",
    },
    "it": {
        "color_studio_button": "Personalizza Kya",
        "texture_ok": "Cartella texture PCSX2 trovata",
        "texture_missing": "Texture PCSX2 non trovate — clicca per dettagli",
        "texture_search": "Cartella cercata:",
        "texture_details": "Cartella di sostituzione texture PCSX2 non trovata.\\n\\nPercorsi verificati:\\n{paths}\\n\\nIn PCSX2: Impostazioni > Cartelle > Texture. Seleziona la cartella SLES-51473/replacements corrispondente in Kya Color Studio.\\n\\nAttiva il rendering hardware e il caricamento delle texture sostitutive.",
        "server": "Server",
        "name": "Nome",
        "password_optional": "Password (opzionale)",
        "connect": "CONNETTI",
        "connecting": "CONNESSIONE...",
        "status_pine": "PCSX2 / PINE",
        "status_server": "Server Archipelago",
        "status_game": "Gioco rilevato",
        "disconnected": "Disconnesso",
        "connected": "Connesso",
        "connecting_status": "Connessione...",
        "pine_busy_state": "Lettura in ritardo",
        "checking": "Verifica...",
        "reachable": "Raggiungibile",
        "not_detected": "Non rilevato",
        "unknown": "Sconosciuto",
        "log": "Registro",
        "clear": "Pulisci",
        "launcher_ready": "Launcher pronto.",
        "starting_checks": "Avvio dei controlli di connessione...",
        "pine_ok": "Connessione PINE stabilita.",
        "pine_fail": "Connessione PINE non riuscita.",
        "pine_busy_hint": "PINE accetta la connessione ma non risponde. Chiudi qualsiasi altro strumento camera/mapper di Kya che usa PINE e riprova.",
        "game_ok": "Gioco supportato rilevato.",
        "game_fail": "Gioco supportato non rilevato.",
        "server_ok": "Server raggiungibile.",
        "server_fail": "Connessione al server non riuscita.",
        "checks_ok": "Controlli di connessione completati.",
        "checks_warn": "Controlli completati con avvisi.",
        "name_required": "Inserisci il nome / slot Archipelago.",
        "server_empty": "L'indirizzo del server è vuoto.",
        "server_format": "Formato previsto: archipelago.gg:12345",
        "host_invalid": "Nome host non valido.",
        "port_number": "La porta deve essere un numero.",
        "port_invalid": "Porta non valida.",
        "bg_missing": "Immagine di sfondo non trovata:\n{path}\n\nIl launcher usa BackIMG.webp.",
        "options": "Opzioni",
        "ap_connection": "Connessione Archipelago",
        "save_connection": "Salva impostazioni di connessione",
        "connection_saved": "Impostazioni di connessione salvate.",
        "overlay_title": "Archipelago Overlay",
        "overlay_on": "Archipelago Overlay: ATTIVO",
        "overlay_off": "Archipelago Overlay: DISATTIVO",
        "overlay_test": "Invia test Archipelago",
        "overlay_note": "Mostra gli scambi di oggetti Archipelago in basso a sinistra nella finestra PCSX2 e segue la finestra, finché PCSX2 è in modalità finestra. In modalità schermo intero viene nascosto intenzionalmente.",
        "overlay_test_in": "TEST • TestPlayer ti ha inviato Progressive Boomy",
        "overlay_test_out": "TEST • Hai inviato Nooties +100 a TestPlayer",
        "language": "Lingua",
        "camera": "Telecamera",
        "horizontal_camera": "Telecamera orizzontale",
        "vertical_camera": "Telecamera verticale",
        "vanilla": "Vanilla",
        "inverted": "Invertito",
        "camera_note": "L'inversione della telecamera si applica nel gioco; lo zoom della mappa mantiene la direzione normale.",
        "close": "Chiudi",
        "camera_active": "Controlli telecamera attivi.",
        "iso_compatibility": "Compatibilità ISO",
        "iso_check_button": "ISO check Compatibility",
        "iso_not_checked": "Non verificata",
        "iso_checking": "Verifica ISO...",
        "iso_compatible": "Compatibile",
        "iso_incompatible": "Non compatibile",
        "iso_exact_ok": "ISO PAL Europa esatta e supportata.",
        "iso_exe_ok": "L’ISO è diversa, ma l’eseguibile PAL è identico e compatibile.",
        "iso_wrong_serial": "Versione del gioco non supportata: {serial}",
        "iso_unknown_revision": "SLES-51473 rilevato, ma l’eseguibile differisce dalla build supportata.",
        "iso_read_error": "Impossibile verificare questa ISO: {error}",
    },
}


def resource_path(name: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")) / name
    return Path(__file__).resolve().parent / name


def game_data_dir() -> Path:
    # In EXE mode prefer editable JSON files beside the Launcher.  The bundled
    # copy is only a fallback so users can patch mappings without recompiling.
    if getattr(sys, "frozen", False):
        external = Path(sys.executable).resolve().parent / "data"
        if (external / "manifest.json").exists():
            return external
    return resource_path("data")


KYA_AP_TEXTURE_FILENAME = "9ec63ff9a73c4adf-f25ef499ddb275c6-00002213.png"


def install_kya_ap_texture() -> tuple[str, Path | None]:
    """Install user's in-game logo, never modify the Launcher background.

    Copy to the PCSX2 Documents layout explicitly requested by the author.
    Back up a pre-existing different texture rather than silently losing it.
    Return a status for the GUI log; no writes on non-Windows platforms.
    """
    if sys.platform != "win32":
        return "skipped", None
    src = resource_path(KYA_AP_TEXTURE_FILENAME)
    if not src.is_file():
        return "missing", src
    dst = (Path.home() / "Documents" / "PCSX2" / "textures" /
           "SLES-51473" / "replacements" / KYA_AP_TEXTURE_FILENAME)
    # Avoid creating an unrelated PCSX2 folder for users with custom or
    # portable installations. If PCSX2 has not been configured yet, the user
    # can place this PNG manually in their actual replacement directory.
    pcsx2_root = Path.home() / "Documents" / "PCSX2"
    if not pcsx2_root.is_dir():
        return "pcsx2_not_found", dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_file() and dst.read_bytes() == src.read_bytes():
        return "unchanged", dst
    if dst.exists():
        backup = dst.with_name(dst.name + ".pre-archipelago.bak")
        if not backup.exists():
            shutil.copy2(dst, backup)
    tmp = dst.with_name(dst.name + ".tmp")
    try:
        shutil.copyfile(src, tmp)
        tmp.replace(dst)
    finally:
        if tmp.exists():
            tmp.unlink()
    return "installed", dst


def config_path() -> Path:
    base = os.getenv("APPDATA") or str(Path.home())
    folder = Path(base) / "KyaArchipelagoLauncher"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "config.json"


_CONFIG_LOCK = threading.RLock()


def load_config() -> dict:
    path = config_path()
    with _CONFIG_LOCK:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}


def save_config_data(data: dict) -> None:
    # Watcher state (pending checks / item cursor) and UI preferences can be
    # written from different threads.  Serialize writes and replace atomically so
    # a crash cannot leave a half-written JSON file that silently loses AP state.
    path = config_path()
    tmp = path.with_name(path.name + ".tmp")
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    with _CONFIG_LOCK:
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, path)



class ISO9660Reader:
    """Small ISO9660 reader used only for the compatibility check."""

    def __init__(self, path: Path):
        self.file = path.open("rb")
        self.root_extent = 0
        self.root_size = 0
        self._read_pvd()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.file.close()

    def _read_pvd(self) -> None:
        self.file.seek(16 * ISO_SECTOR_SIZE)
        pvd = self.file.read(ISO_SECTOR_SIZE)
        if len(pvd) != ISO_SECTOR_SIZE or pvd[0] != 1 or pvd[1:6] != b"CD001":
            raise ValueError("ISO9660 not recognized")
        root = pvd[156:]
        if not root or root[0] < 34:
            raise ValueError("Invalid ISO9660 root directory")
        self.root_extent = int.from_bytes(root[2:6], "little")
        self.root_size = int.from_bytes(root[10:14], "little")

    @staticmethod
    def _clean_name(raw: bytes) -> str:
        if raw == b"\x00":
            return "."
        if raw == b"\x01":
            return ".."
        return raw.decode("ascii", errors="replace").split(";", 1)[0]

    def _read_directory(self, extent: int, size: int) -> list[dict]:
        self.file.seek(extent * ISO_SECTOR_SIZE)
        data = self.file.read(size)
        entries: list[dict] = []
        pos = 0
        while pos < len(data):
            length = data[pos]
            if length == 0:
                pos = ((pos // ISO_SECTOR_SIZE) + 1) * ISO_SECTOR_SIZE
                continue
            if length < 34 or pos + length > len(data):
                break
            rec = data[pos:pos + length]
            entries.append({
                "name": self._clean_name(rec[33:33 + rec[32]]),
                "extent": int.from_bytes(rec[2:6], "little"),
                "size": int.from_bytes(rec[10:14], "little"),
                "is_dir": bool(rec[25] & 0x02),
            })
            pos += length
        return entries

    def find(self, target_name: str) -> dict | None:
        target = target_name.upper()
        seen: set[tuple[int, int]] = set()
        stack = [("", self.root_extent, self.root_size)]
        while stack:
            base, extent, size = stack.pop()
            key = (extent, size)
            if key in seen:
                continue
            seen.add(key)
            for ent in self._read_directory(extent, size):
                name = ent["name"]
                if name in (".", ".."):
                    continue
                rel = f"{base}/{name}" if base else name
                if name.upper() == target:
                    result = dict(ent)
                    result["path"] = rel
                    return result
                if ent["is_dir"]:
                    stack.append((rel, ent["extent"], ent["size"]))
        return None

    def read_entry(self, ent: dict) -> bytes:
        self.file.seek(int(ent["extent"]) * ISO_SECTOR_SIZE)
        data = self.file.read(int(ent["size"]))
        if len(data) != int(ent["size"]):
            raise IOError("Unexpected EOF while reading ISO")
        return data

    def sha256_entry(self, ent: dict) -> str:
        h = hashlib.sha256()
        remaining = int(ent["size"])
        self.file.seek(int(ent["extent"]) * ISO_SECTOR_SIZE)
        while remaining:
            chunk = self.file.read(min(8 * 1024 * 1024, remaining))
            if not chunk:
                raise IOError("Unexpected EOF while hashing ISO entry")
            h.update(chunk)
            remaining -= len(chunk)
        return h.hexdigest().upper()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _parse_iso_boot_serial(system_cnf: bytes) -> str | None:
    text = system_cnf.decode("latin-1", errors="ignore")
    match = re.search(
        r"BOOT2\s*=\s*cdrom0:\\+([A-Z]{4}[_-]\d{3}\.\d{2})",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1).upper().replace("-", "_")


def check_kya_iso_compatibility(path: Path) -> dict:
    iso_sha = _sha256_file(path)
    with ISO9660Reader(path) as iso:
        cnf = iso.find("SYSTEM.CNF")
        if cnf is None:
            return {"compatible": False, "reason": "wrong_serial", "serial": "UNKNOWN", "iso_sha256": iso_sha, "exe_sha256": None}
        serial = _parse_iso_boot_serial(iso.read_entry(cnf))
        if serial != EXPECTED_GAME_ID:
            return {"compatible": False, "reason": "wrong_serial", "serial": serial or "UNKNOWN", "iso_sha256": iso_sha, "exe_sha256": None}
        exe = iso.find(EXPECTED_GAME_ID)
        if exe is None:
            return {"compatible": False, "reason": "unknown_revision", "serial": serial, "iso_sha256": iso_sha, "exe_sha256": None}
        exe_sha = iso.sha256_entry(exe)

    if iso_sha == KNOWN_GOOD_ISO_SHA256:
        return {"compatible": True, "reason": "exact_ok", "serial": serial, "iso_sha256": iso_sha, "exe_sha256": exe_sha}
    if exe_sha == KNOWN_GOOD_EXE_SHA256:
        return {"compatible": True, "reason": "exe_ok", "serial": serial, "iso_sha256": iso_sha, "exe_sha256": exe_sha}
    return {"compatible": False, "reason": "unknown_revision", "serial": serial, "iso_sha256": iso_sha, "exe_sha256": exe_sha}

def parse_server(value: str, tr: dict) -> tuple[str, int]:
    value = value.strip()
    if not value:
        raise ValueError(tr["server_empty"])
    value = value.removeprefix("ws://").removeprefix("wss://")
    value = value.split("/", 1)[0]
    if ":" not in value:
        raise ValueError(tr["server_format"])
    host, port_text = value.rsplit(":", 1)
    if not host:
        raise ValueError(tr["host_invalid"])
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ValueError(tr["port_number"]) from exc
    if not 1 <= port <= 65535:
        raise ValueError(tr["port_invalid"])
    return host, port


def recv_exact(sock: socket.socket, length: int) -> bytes:
    data = bytearray()
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise ConnectionError("PINE connection closed while waiting for a response.")
        data.extend(chunk)
    return bytes(data)


def probe_pine_game(timeout: float = 1.2) -> tuple[bool, str | None, bool, str | None]:
    try:
        with socket.create_connection((PINE_HOST, PINE_PORT), timeout=timeout) as sock:
            sock.settimeout(timeout)
            payload = bytes([0x0C])
            sock.sendall(struct.pack("<I", len(payload) + 4) + payload)

            header = recv_exact(sock, 4)
            total_size = struct.unpack("<I", header)[0]
            if total_size < 5:
                raise ValueError(f"Invalid PINE response ({total_size} bytes).")

            body = recv_exact(sock, total_size - 4)
            if not body or body[0] != 0x00:
                code = body[0] if body else 0xFF
                raise ValueError(f"PINE Game ID command rejected (0x{code:02X}).")

            data = body[1:]
            if len(data) < 4:
                raise ValueError("PINE Game ID response is too short.")

            string_size = struct.unpack("<I", data[:4])[0]
            raw = data[4:4 + string_size]
            if len(raw) != string_size:
                raise ValueError("PINE Game ID response is truncated.")

            game_id = raw.rstrip(b"\x00").decode("utf-8", errors="replace")
            normalized = re.sub(r"[^A-Z0-9]", "", game_id.upper())
            return True, game_id, normalized == EXPECTED_GAME_ID_NORMALIZED, None
    except Exception as exc:
        return False, None, False, str(exc)


def can_connect(host: str, port: int, timeout: float = 2.0) -> tuple[bool, str | None]:
    """Probe an Archipelago endpoint, trying plain and TLS WebSockets.

    Archipelago's normal client starts with ws:// and retries wss:// when the
    endpoint appears encrypted. Mirror that behavior so the launcher can check
    either locally hosted servers or TLS-enabled hosted rooms.
    """
    websocket_guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    errors: list[str] = []

    def probe(use_tls: bool) -> None:
        mode = "wss" if use_tls else "ws"
        with socket.create_connection((host, port), timeout=timeout) as raw_sock:
            raw_sock.settimeout(timeout)
            if use_tls:
                context = ssl.create_default_context()
                sock = context.wrap_socket(raw_sock, server_hostname=host)
            else:
                sock = raw_sock

            with sock:
                raw_key = os.urandom(16)
                ws_key = base64.b64encode(raw_key).decode("ascii")
                request = (
                    "GET / HTTP/1.1\r\n"
                    f"Host: {host}:{port}\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Key: {ws_key}\r\n"
                    "Sec-WebSocket-Version: 13\r\n"
                    "User-Agent: KyaArchipelagoLauncher/2.6.8\r\n"
                    "\r\n"
                )
                sock.sendall(request.encode("ascii"))

                response = bytearray()
                while b"\r\n\r\n" not in response:
                    chunk = sock.recv(1024)
                    if not chunk:
                        raise ConnectionError(f"Server closed during {mode.upper()} WebSocket handshake.")
                    response.extend(chunk)
                    if len(response) > 16384:
                        raise ValueError("WebSocket handshake response is too large.")

                header_blob = bytes(response).split(b"\r\n\r\n", 1)[0]
                header_text = header_blob.decode("latin-1", errors="replace")
                lines = header_text.split("\r\n")
                if not lines or " 101 " not in f" {lines[0]} ":
                    raise ConnectionError(
                        f"{mode.upper()} handshake rejected: {lines[0] if lines else 'empty response'}"
                    )

                headers = {}
                for line in lines[1:]:
                    if ":" in line:
                        name, value = line.split(":", 1)
                        headers[name.strip().lower()] = value.strip()

                if headers.get("upgrade", "").lower() != "websocket":
                    raise ConnectionError("Server response is not a WebSocket upgrade.")
                connection_tokens = {
                    token.strip().lower()
                    for token in headers.get("connection", "").split(",")
                }
                if "upgrade" not in connection_tokens:
                    raise ConnectionError("Missing WebSocket Connection: Upgrade header.")

                expected_accept = base64.b64encode(
                    hashlib.sha1((ws_key + websocket_guid).encode("ascii")).digest()
                ).decode("ascii")
                if headers.get("sec-websocket-accept") != expected_accept:
                    raise ConnectionError("Invalid WebSocket Sec-WebSocket-Accept value.")

                close_payload = struct.pack("!H", 1000)
                mask = os.urandom(4)
                masked_payload = bytes(byte ^ mask[i % 4] for i, byte in enumerate(close_payload))
                sock.sendall(bytes([0x88, 0x80 | len(close_payload)]) + mask + masked_payload)

    for use_tls in (False, True):
        try:
            probe(use_tls)
            return True, None
        except Exception as exc:
            mode = "wss" if use_tls else "ws"
            errors.append(f"{mode}: {type(exc).__name__}: {exc}")

    return False, " | ".join(errors)


def build_gameplay_route(horizontal_mode: str, vertical_mode: str):
    ab = HORIZONTAL_INVERTED if horizontal_mode == "inverted" else HORIZONTAL_VANILLA
    cd = VERTICAL_INVERTED if vertical_mode == "inverted" else VERTICAL_VANILLA
    return tuple(ab + cd)


def build_map_route(horizontal_mode: str, vertical_mode: str = "vanilla"):
    """Preserve vanilla zoom/dezoom while retaining horizontal camera preference.

    Map zoom shares the gameplay vertical input entries C/D (0x0E/0x0F),
    so a vertical inverted camera must NOT invert the map's zoom controls.
    `vertical_mode` is accepted for compatibility but is intentionally unused.
    """
    return build_gameplay_route(horizontal_mode, "vanilla")


def select_camera_input_route(horizontal_mode: str, vertical_mode: str,
                              camera_mode: int, map_state: int = 0):
    """Route camera axes without ever gating gameplay or Archipelago writes.

    The 0.9.58 mode==3 test alone was not a reliable map-open indicator: it
    describes a camera zoom handler. Keep it as a secondary hint, but the old
    map state is needed to catch real map zoom. MAP_STATE_ADDR is shared with
    amber regeneration; using it for input orientation may briefly give vanilla
    camera inversion near ambers, but must NEVER suspend AP watchers.
    """
    if int(map_state) == 1 or int(camera_mode) == MAP_ZOOM_CAMERA_MODE:
        return build_map_route(horizontal_mode, vertical_mode)
    return build_gameplay_route(horizontal_mode, vertical_mode)


def hunters_boss_recovery_eligible(zone: str, conditions, active: bool,
                                    joined: bool, seed_verified: bool,
                                    stream_hold: bool, location_id,
                                    checked: set, pending: dict) -> bool:
    """Unique Hunter boss completed-save recovery; never applies to other events."""
    return (zone == "Hunters Domain"
            and conditions == [[0x004254EC, 2]]
            and bool(active) and bool(joined) and bool(seed_verified)
            and not bool(stream_hold) and location_id is not None
            and location_id not in checked and location_id not in pending)


def read_route(pine: PineClient, obj: int):
    vals = pine.read32_many([obj + off for off in ROUTE_OFFSETS], batch_size=8)
    return tuple(int(v) for v in vals)


def write_route(pine: PineClient, obj: int, route):
    for off, value in zip(ROUTE_OFFSETS, route):
        pine.write32(obj + off, int(value))


def _set_windows_app_user_model_id() -> None:
    """Give the taskbar and Alt+Tab a stable application identity on Windows."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        shell32 = ctypes.WinDLL("shell32", use_last_error=True)
        set_app_id = shell32.SetCurrentProcessExplicitAppUserModelID
        set_app_id.argtypes = [ctypes.c_wchar_p]
        set_app_id.restype = ctypes.c_long
        set_app_id("Sharoms.KyaArchipelagoLauncher")
    except (AttributeError, OSError):
        pass


PINE_UI_FRESH_SECONDS = 10.0


def pine_indicator_state(camera_ready: bool, pine_lost: bool,
                         heartbeat_at: float, now: float) -> str:
    """Distinguish an explicit PINE failure from a late cooperative scan.

    There is deliberately only ONE upstream PINE socket. The camera thread
    must finish AP/watchers work before it can refresh its heartbeat. If a
    scan takes longer than 10 s, it does NOT prove PCSX2 has disconnected.
    """
    if not camera_ready or pine_lost or heartbeat_at <= 0.0:
        return "disconnected"
    if now - heartbeat_at >= PINE_UI_FRESH_SECONDS:
        return "busy"
    return "connected"


class KyaLauncher(tk.Tk):
    def __init__(self) -> None:
        _set_windows_app_user_model_id()
        super().__init__()
        self.withdraw()
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.resizable(False, False)
        self.configure(bg="black")
        self.overrideredirect(True)

        icon = resource_path("Icon.ico")
        if icon.exists():
            try:
                self.iconbitmap(default=str(icon))
            except tk.TclError:
                pass

        cfg = load_config()

        # English is the default when no language has ever been selected.
        self.language = cfg.get("language", "en")
        if self.language not in T:
            self.language = "en"

        # Camera radio buttons also start on Vanilla by default.
        self.camera_horizontal = cfg.get("camera_horizontal", "vanilla")
        self.camera_vertical = cfg.get("camera_vertical", "vanilla")
        if self.camera_horizontal not in ("vanilla", "inverted"):
            self.camera_horizontal = "vanilla"
        if self.camera_vertical not in ("vanilla", "inverted"):
            self.camera_vertical = "vanilla"

        self._drag_origin: tuple[int, int] | None = None
        self._bg_photo: tk.PhotoImage | None = None
        self.status_widgets: dict[str, tuple[int, int, int]] = {}
        self._ui_queue: queue.Queue[tuple] = queue.Queue()
        self._queue_after_id: str | None = None
        self._closing = False

        self._worker_thread: threading.Thread | None = None
        self._camera_thread: threading.Thread | None = None
        self._close_poll_after_id: str | None = None
        self._close_deadline = 0.0

        self._stop_event = threading.Event()
        self._camera_stop_event = threading.Event()
        # V0.9.35: AutoSave defaults to ON each session, as requested.
        # User can still turn it OFF at any time. The single PINE-owner thread
        # executes autosave commands; UI never opens PINE directly.
        self._auto_save_requested = threading.Event()
        self._auto_save_requested.set()
        self._auto_save_var = tk.BooleanVar(value=True)
        # Optional and deliberately OFF by default: a user closing PCSX2 looks
        # like a crash to PINE. Only re-load a marked state from this AP session.
        self._auto_recover_var = tk.BooleanVar(value=bool(cfg.get('kya_auto_reload_after_pcsx2_loss', False)))
        self._auto_recover_enabled = bool(self._auto_recover_var.get())
        self._pine_was_online = False
        self._pine_lost_at: float | None = None
        self._pine_recovery_candidate: dict | None = None
        self._pine_auto_restore_pending: dict | None = None
        self._pine_auto_restore_started = 0.0
        self._pine_last_heartbeat_at = 0.0
        self._pine_service_stage = 'initializing'
        # A pending user-selected reload must survive scene transitions.
        self._manual_reload_pending: tuple[int, float] | None = None
        self._manual_reload_wait_logged = False
        self._connected_requested = False
        self._last_connection_indicator_state: tuple | None = None
        self._auto_save_reload_request: queue.Queue[int] = queue.Queue(maxsize=1)
        self._auto_save_entry_by_label = {}
        self._auto_save_last_labels = ()
        self._auto_save_refresh_at = 0.0
        self._ap_reload_pause_until = 0.0
        saved_path = cfg.get('kya_auto_save_sstates_path')
        self._auto_save_controller = AutoSaveController(
            self._log_threadsafe,
            Path(saved_path) if isinstance(saved_path, str) and saved_path else default_sstates_path(),
        )
        self._auto_save_controller.language = self.language

        # PCSX2/PINE effectively behaves as a single-client endpoint here.
        # The camera service pauses and releases its PINE socket while the
        # launcher's explicit connection test is running.
        # Single-owner PINE design:
        # the camera service is the ONLY thread that opens a PINE socket.
        # CONNECT only reads its validated state, so it can never steal or
        # interrupt the camera/MAP patch connection.
        self._camera_ready_event = threading.Event()
        self._camera_last_error = "PINE not connected yet."
        self._ap_link: APLink | None = None
        self._ap_joined = False
        self._ap_seed_build_verified = False
        self._ap_data = load_game_data(game_data_dir())
        self._ap_baselined = False
        self._ap_wolfen_states: dict[int, int] = {}
        self._ap_actor_states: dict[int, int] = {}
        self._ap_actor_keys: dict[int, int] = {}
        self._ap_actor_descriptors: dict[int, int] = {}
        self._ap_special_states: dict[str, bool] = {}
        self._ap_special_baselined = False
        self._ap_hunter_boss_recovery_since: float | None = None
        # 0.9.51: independent scene-safe observer for the first Brazul event.
        # An already-completed flag loaded from a savestate NEVER backfills a boss check.
        self._ap_first_brazul_last_value: int | None = None
        self._ap_first_brazul_zone_since: float | None = None
        self._ap_first_brazul_next_poll = 0.0
        # 0.9.59 Lava Worm: observation-only until two independent live edges.
        self._ap_lava_last_var: int | None = None
        self._ap_lava_actor_generation: int | None = None
        self._ap_lava_actor_address: int | None = None
        self._ap_lava_actor_last_state: int | None = None
        self._ap_lava_pending_at: float | None = None
        self._ap_fast_travel_states: dict[int, int] = {}
        self._ap_fast_travel_keys: dict[int, int] = {}
        self._ap_fast_travel_baselined = False
        self._ap_validation_probe_states: dict[str, int] = {}
        self._ap_validation_probes_baselined = False
        self._ap_current_zone: str | None = None
        self._ap_shop_states: dict[str, bool] = {}
        self._ap_shop_reward_snapshots: dict[str, int] = {}
        self._ap_pending_shop_suppressions: dict[int, tuple[str, dict, int]] = {}
        self._ap_shop_suppressed: set[int] = set()
        self._ap_shop_baselined = False
        self._ap_shop_live_reward_states: dict[str, int] = {}
        self._ap_shop_live_baselined = False
        self._ap_shop_live_ignore_until = 0.0
        self._ap_shop_money_last: int | None = None
        self._ap_shop_purchase_tokens: list[tuple[float, int]] = []
        self._ap_shop_ambiguous_token_warned: set[float] = set()
        # V0.8.15: same-price duplicate purchases are never batch-guessed.
        # If live/serialized state cannot identify the exact article, the launcher
        # asks for a one-click confirmation immediately and keeps that spend token
        # isolated until the answer is provided.
        self._ap_shop_manual_choices: dict[float, str] = {}
        self._ap_shop_prompted_tokens: set[float] = set()
        # V0.8.15: if a newer purchase occurs before an older ambiguous token is
        # resolved, the older token is marked as deferred so its dialog can never be
        # mistaken for the most recent click.
        self._ap_shop_deferred_prompt_tokens: set[float] = set()
        # V0.8.15: exact purchase hints captured when AP inventory authority
        # repairs a vanilla downgrade (e.g. Golden->Silver, Speed->Magic).
        # They persist briefly so they can be paired with a Nooties token even
        # when the repair and the money decrement land on different watcher ticks.
        self._ap_shop_exact_reconcile_hints: list[tuple[float, str, int]] = []
        # V0.8.17 live stock-source resolver.  The base is runtime/relocatable;
        # only structural offsets are retained.
        self._ap_shop_runtime_source: int | None = None
        self._ap_shop_runtime_last_scan = 0.0
        self._ap_shop_runtime_scan_fail_logged = False
        # V0.8.18: when several heap bases have the same structural score, keep
        # the whole plausible set instead of discarding the live-stock signal.
        # A before/after snapshot and consensus vote then identify the exact slot.
        self._ap_shop_runtime_candidates: list[int] = []
        self._ap_shop_runtime_candidate_scores: dict[int, tuple[int, int]] = {}
        self._ap_shop_runtime_snapshots: dict[int, dict[str, int]] = {}
        self._ap_shop_runtime_prime_logged = False
        # V0.8.19: grouped runtime sources derived from the serializer's exact
        # destination address/mask semantics discovered in Ghidra.
        self._ap_shop_group_candidates: dict[int, list[int]] = {}
        self._ap_shop_group_scores: dict[tuple[int, int], tuple[int, int]] = {}
        self._ap_shop_group_snapshots: dict[int, dict[int, dict[str, int]]] = {}
        self._ap_shop_group_last_scan = 0.0
        self._ap_shop_group_scan_logged = False
        self._ap_shop_group_prime_logged = False
        # V0.8.20: rolling per-poll Ghidra stock edges. Unlike the old startup
        # baseline, these advance even while older ambiguous tokens are pending.
        self._ap_shop_group_rolling_states: dict[int, dict[int, dict[str, int]]] = {}
        self._ap_shop_group_edge_events: list[tuple[float, dict[str, int], dict[str, int], dict[str, list[tuple[int, int]]]]] = []
        # V0.8.21: native Shop resolver reconstructed from the purchase getter chain.
        # Runtime heap addresses are rescanned; only native item identity/context is trusted.
        self._ap_shop_native = NativeShopResolver()
        self._ap_shop_sold_observer = NativeSoldStateObserver()
        self._ap_shop_native_sold_state_last: dict[str, tuple[int, int]] = {}
        self._ap_shop_native_hints: dict[float, tuple[str, int, str]] = {}
        self._ap_shop_native_ready_logged = False
        self._ap_shop_native_last_attempt = 0.0
        self._ap_shop_native_last_report: tuple | None = None
        self._ap_shop_native_last_report_at = 0.0
        # V0.8.23 Run-Safe Economy10. Values come from AP slot_data / YAML and are normalized to 10% steps.
        self._ap_slot_data: dict = {}
        self._ap_nooties_modifier_pct = 0
        self._ap_shop_price_modifier_pct = 0
        self._ap_shop_price_modifier_logged: int | None = None
        # V0.8.24 Fast Travel options / runtime. Values are authoritative slot_data.
        self._ap_fast_travel_progression = "archipelago"
        self._ap_starting_fast_travel_routes: list[dict] = []
        self._ap_initial_fast_travel_route_ids: set[str] = set()
        self._ap_selected_target_keys: set[int] = set()
        self._ap_lock_the_root = True
        self._ap_lock_flying_forest = True
        self._ap_lock_wolfen_city = True
        self._ap_lock_the_fortress = True
        self._ap_ft_nativ_loaded_last = False
        self._ap_ft_departure_pending = False
        self._ap_ft_departure_since = 0.0
        self._ap_ft_active_bridge: dict | None = None
        self._ap_ft_next_runtime_scan = 0.0
        self._ap_ft_wind_triggered: set[tuple[int, int]] = set()
        self._ap_ft_last_source_signature = None
        # V0.9.15 STRICT VANILLA RELAY:
        # - EntryFallback may bootstrap an undiscovered world.
        # - The destination FT01 is then guarded against the remote 0->1 side-effect
        #   until Kya physically reaches the pad.
        # - Only a local/proximity-confirmed 0->1 event hands that ONE world back
        #   to vanilla. AP checked IDs alone never change ownership.
        self._ap_ft_detector_handoff_sources: set[int] = set()
        self._ap_ft_detector_guard_targets: set[int] = set()
        self._ap_ft_detector_remote_logged: set[int] = set()
        self._ap_ft_detector_handoff_logged: set[int] = set()
        self._ap_ft_detector_near_wait_logged: set[int] = set()
        self._ap_ft_detector_handoff_key = ""
        self._ap_ft_plank_patches: dict[int, dict] = {}
        self._ap_ft_plank_handler_cache: dict[int, int] = {}
        self._ap_ft_plank_open_logged: set[tuple[int, int]] = set()
        self._ap_ft_plank_warned: set[tuple[int, int]] = set()
        self._ap_ft_plank_room_logged = False
        # V0.8.40: Fast Travel is a critical section. Once the vanilla tunnel
        # starts, only the proven FT bridge may write game memory. AP events that
        # would write are deferred until arrival is fully confirmed.
        self._ap_ft_exclusive = False
        self._ap_ft_exclusive_route_id: str | None = None
        self._ap_ft_exclusive_since = 0.0
        self._ap_ft_exclusive_confirmed_at: float | None = None
        self._ap_ft_deferred_events: list[tuple[str, object]] = []
        self._ap_ft_defer_logged = False
        # V0.8.43: True BAT Cleanroom. As soon as the complete Nativ Fast Travel room
        # is loaded, the normal Launcher loop is suspended and the exact proven
        # sidecar sequence owns PINE until Kya leaves the room / completes travel.
        self._ap_ft_sanctuary_enabled = True
        self._ap_ft_sanctuary_active = False
        # V0.8.43: TRUE BAT CLEANROOM.  When AP Fast Travel is used from
        # Nativs City, the original working BAT logic gets exclusive ownership
        # BEFORE any Launcher inventory/access/shop writer can touch game memory.
        self._ap_ft_cleanroom_pending = False
        self._ap_ft_cleanroom_active = False
        # 0.9.55: cooperative cleanroom remembers its scan state across PINE
        # heartbeats instead of monopolising the one owner for 120 seconds.
        self._ap_ft_sanctuary_generator = None
        # V0.8.45 lifecycle: the join-time cleanroom is one-shot.  Later
        # cleanrooms are entered only when the *real runtime* Nativ FT room is
        # present, never from the cached/stale zone name left over after streaming.
        self._ap_ft_initial_cleanroom_consumed = False
        # V0.8.45: after any cleanroom session, require a real disappearance of
        # the Nativ FT actors before another session may arm. This prevents stale
        # streamed actors from immediately re-entering the cleanroom at arrival.
        self._ap_ft_waiting_for_nativ_exit = False
        self._ap_ft_next_room_probe = 0.0
        # V0.8.47: Nativ room detection must be scene-specific. Persistent keys
        # are not globally unique across Kya scenes, so source keys such as
        # 0x0225/0x0239 can legitimately exist in destination zones. Re-arming
        # a cleanroom from a single key therefore corrupted Flying Forest and
        # froze Wolfen watchers. We now require the complete wooden-kiosk room
        # fingerprint and a short verified absence before another transaction.
        self._ap_ft_nativ_absent_since = 0.0
        self._ap_ft_nativ_return_generation = 0
        self._ap_ft_cleanroom_lock_clear_logged = set()
        # V0.9.1: keep access locks and shops independent from the FT transport core.
        # The proven V49 transport stays intact; this scheduler only decides when it owns memory.
        self._ap_ft_session_departed = False
        self._ap_ft_room_far_since = 0.0
        # Carry actual landing-guard provenance through a cleanroom watchdog.
        # A timeout in the SAME Nativ room is not a fresh FT arrival.
        self._ap_ft_cleanroom_continuation = None
        # V0.9.4: event-driven mana rescue. It is armed only around a real FT

        # activation/arrival and never scans permanently. If Kya becomes
        # stationary for a short dwell with exactly zero runtime mana, give 3.
        self._ap_ft_mana_stall_rescue: dict | None = None
        self._ap_access_guard_next = 0.0
        self._ap_access_lock_last: dict[str, tuple] = {}
        self._ap_access_owned_actors: dict[str, int] = {}  # only clear actor flags explicitly written by AP
        self._ap_shop_choice_window: tk.Toplevel | None = None
        self._ap_shop_choice_token: float | None = None
        self._ap_shop_choice_backlog: list[tuple[float, int, tuple[str, ...]]] = []
        self._ap_pending_special_life_suppressions: dict[int, int] = {}
        self._ap_shop_test_mode = False
        self._ap_shop_unpaired_live_hits: dict[str, tuple[float, int, int]] = {}
        self._ap_shop_unconfirmed_stock: set[str] = set()
        self._ap_shop_audit_requested = False
        self._ap_goal_last_value: int | None = None
        self._ap_goal_credits_last_value: int | None = None
        # 0.9.52: never use the unrelated 0x0044982C (false Goal at Nativs City).
        # Only a LIVE Fortress Var61 1->2, stable since before the fight, can
        # authorize auto Goal AFTER the real AP boss location is ACKed.
        self._ap_goal_fortress_since: float | None = None
        self._ap_goal_boss_witness_at: float | None = None
        self._ap_goal_auto_candidate_at: float | None = None  # kept for 0.9.50 compatibility
        self._ap_goal_auto_candidate_samples = 0
        self._ap_goal_auto_last_diag_at = 0.0
        self._ap_goal_reached = False
        self._ap_goal_status_sent = False
        self._ap_goal_message_logged = False
        self._ap_next_goal_poll = 0.0
        self._ap_checked: set[int] = set()
        # Durable local queue for one-shot physical events. A Wolfen/FT/shop/special
        # transition must survive a websocket drop or Launcher restart until AP ACKs it.
        self._ap_seed_name = ""
        self._ap_pending_check_key = ""
        self._ap_pending_checks: dict[int, str] = {}
        # Highest AP ReceivedItems index already committed to Kya.  This is
        # persisted per seed so reconnecting can rebuild progression counts
        # without re-granting consumable Nooties/HP/Magic rewards.
        self._ap_item_cursor_key = ""
        self._ap_applied_item_cursor = 0
        # Delayed vanilla-Rune rollback; never race physical pickup/check ACK.
        self._ap_rune_rollback_due: dict[str, float] = {}
        self._ap_items = {int(v): k for k, v in self._ap_data["ITEM_NAME_TO_ID"].items()}
        self._ap_item_counts: dict[int, int] = {}
        self._ap_life_gauge_key = ""
        self._ap_life_gauge_progress: dict = {}
        self._ap_pending_hp_restore = 0
        self._ap_pending_magic_restore = 0
        self._ap_damage_last_hp: dict[int, float] = {}
        self._ap_player_last_hp: float | None = None
        self._ap_damage_effect_logged = False
        self._ap_protection_effect_logged = False
        self._ap_next_combat_poll = 0.0
        self._ap_next_inventory_reconcile = 0.0
        self._ap_overlay_recent_incoming: dict[tuple[int, int], float] = {}
        self._ap_next_poll = 0.0
        self._ap_next_actor_refresh = 0.0
        self._ap_actor_count: int | None = None
        self._ap_actor_manager_state: tuple | None = None
        # V0.9.22: STOP all ordinary AP/camera writers while a zone is streaming.
        # The FT BAT worked with no concurrent Launcher watchers. This provides
        # that same no-write gap until the destination Actor Manager is stable.
        self._ap_stream_hold = True
        self._map_guard_recovery = MapGuardRecovery()
        # Native Brazul captivity is authoritative. AP must NOT undo his
        # confiscation, including on a ReceivedItems replay or savestate load.
        self._brazul_capture_guard = BrazulCaptureGuard()
        self._ap_stream_candidate = None
        self._ap_stream_ready_since = 0.0
        self._ap_stream_last_valid_generation = None
        self._ap_stream_departure_generation = None
        self._ap_stream_warning_logged = False
        self._last_pine_service_error = ""

        # DEBUG playtest cheats. They run inside the existing single-owner PINE
        # service, so no second socket can steal PINE from AP/camera.
        self._debug_infinite_life = False
        self._debug_infinite_mana = False
        self._debug_one_shot = False
        self._debug_wolfen_hp: dict[int, float] = {}
        self._debug_next_actor_scan = 0.0
        self._debug_buttons: dict[str, tk.Button] = {}

        # Progression-run scanner: UI thread enqueues requests; the existing
        # single-owner PINE thread executes them.  This avoids a second PINE
        # socket fighting the AP/camera watcher.
        self._test_action_queue: queue.Queue = queue.Queue()
        self._test_item_var = tk.StringVar(value="Jamgut Birdcall")
        self._test_grant_var = tk.BooleanVar(value=True)

        # Read-only Fast Travel forensic recorder.  It shares the existing
        # single-owner PINE service: no second PINE socket is opened.
        self._ft_forensic_active = False
        self._ft_forensic_started = 0.0
        self._ft_forensic_deadline = 0.0
        self._ft_forensic_next_sample = 0.0
        self._ft_forensic_samples: list[dict] = []
        self._ft_forensic_runtime_logs: list[dict] = []
        self._ft_forensic_start_snapshot: dict | None = None
        self._ft_forensic_log_seed = ""
        self._ft_forensic_lock = threading.Lock()
        self._ft_forensic_button: tk.Button | None = None

        self.options_window: tk.Toplevel | None = None
        self.options_widgets: dict[str, object] = {}

        # Archipelago trade overlay.  It is rendered as a borderless, click-through
        # Tk window and anchored to the PCSX2 client area.
        self.overlay_enabled = bool(cfg.get("overlay_enabled", False))
        self._overlay_window: tk.Toplevel | None = None
        self._overlay_canvas: tk.Canvas | None = None
        self._overlay_messages: list[dict] = []
        self._overlay_after_id: str | None = None
        self._overlay_last_rect: tuple[int, int, int, int] | None = None
        self._overlay_pcsx2_hwnd: int | None = None
        self._overlay_pcsx2_pid: int | None = None
        self._overlay_next_window_scan = 0.0
        self._ap_slot_id: int | None = None

        self._iso_check_thread: threading.Thread | None = None
        self._iso_check_generation = 0
        self._iso_last_result: dict | None = None

        self._center_window()
        self._build_background()
        self._build_ui()
        # v0.9.38: copy the supplied logo into PCSX2's texture replacement
        # directory upon window creation, without waiting for AP Connect.
        try:
            texture_status, texture_dest = install_kya_ap_texture()
            if texture_status == "installed":
                self._log_threadsafe(f"Kya Archipelago PCSX2 texture installed: {texture_dest}", "ok")
            elif texture_status == "pcsx2_not_found":
                self._log_threadsafe(
                    "PCSX2 Documents folder not found; in-game logo not installed automatically. "
                    f"Copy {KYA_AP_TEXTURE_FILENAME} to your actual PCSX2 textures/SLES-51473/replacements folder.",
                    "warn")
            elif texture_status == "missing":
                self._log_threadsafe("Kya Archipelago PCSX2 texture missing from Launcher files.", "warn")
        except (OSError, ValueError) as exc:
            self._log_threadsafe(f"PCSX2 texture installation skipped: {exc}", "warn")

        self.bind("<Escape>", lambda _e: self._request_close())
        self.bind("<Return>", lambda _e: self._on_connect())
        self._queue_after_id = self.after(50, self._drain_ui_queue)

        # IMPORTANT:
        # Do not connect to PINE at launcher startup.
        # The standalone camera patch that was validated in-game connects only
        # when the user explicitly applies it. We mirror that behavior here:
        # the camera/PINE service starts on CONNECT, when PCSX2/Kya is expected
        # to be ready.
        self.deiconify()
        self.lift()
        # Tk's overrideredirect window is otherwise treated like a tool window
        # and omitted from Windows taskbar/Alt+Tab. Reapply after Tk maps it.
        self.after_idle(self._ensure_windows_taskbar_presence)
        self.after(250, self._ensure_windows_taskbar_presence)
        self._overlay_after_id = self.after(50, self._overlay_tick)

    def _ensure_windows_taskbar_presence(self) -> None:
        """Keep the custom borderless main window in taskbar and Alt+Tab."""
        if sys.platform != "win32" or self._closing:
            return
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
            user32.GetAncestor.restype = wintypes.HWND
            hwnd = wintypes.HWND(self.winfo_id())
            hwnd_root = user32.GetAncestor(hwnd, 2)  # GA_ROOT
            if hwnd_root:
                hwnd = hwnd_root

            get_long = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
            set_long = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
            long_type = ctypes.c_ssize_t if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long
            get_long.argtypes = [wintypes.HWND, ctypes.c_int]
            get_long.restype = long_type
            set_long.argtypes = [wintypes.HWND, ctypes.c_int, long_type]
            set_long.restype = long_type

            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW = 0x00040000
            style = int(get_long(hwnd, GWL_EXSTYLE))
            style = (style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
            set_long(hwnd, GWL_EXSTYLE, style)

            user32.SetWindowPos.argtypes = [
                wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                ctypes.c_int, ctypes.c_int, wintypes.UINT,
            ]
            user32.SetWindowPos.restype = wintypes.BOOL
            user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0027)
        except (AttributeError, OSError, tk.TclError):
            # Preserve startup if a Windows shell API is unavailable.
            return

    def _ensure_aux_window_taskbar_presence(self, win: tk.Toplevel) -> None:
        """Expose a borderless auxiliary window in Alt+Tab/taskbar and group it with Kya Launcher."""
        if sys.platform != "win32" or self._closing:
            return
        try:
            import ctypes
            from ctypes import wintypes

            win.update_idletasks()
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
            user32.GetAncestor.restype = wintypes.HWND
            hwnd = wintypes.HWND(win.winfo_id())
            hwnd_root = user32.GetAncestor(hwnd, 2)  # GA_ROOT
            if hwnd_root:
                hwnd = hwnd_root

            get_long = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
            set_long = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
            long_type = ctypes.c_ssize_t if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long
            get_long.argtypes = [wintypes.HWND, ctypes.c_int]
            get_long.restype = long_type
            set_long.argtypes = [wintypes.HWND, ctypes.c_int, long_type]
            set_long.restype = long_type

            # Detach the Toplevel from Tk's owner relationship.  A transient/owned
            # borderless window is intentionally hidden by Windows from Alt+Tab.
            GWLP_HWNDPARENT = -8
            set_long(hwnd, GWLP_HWNDPARENT, long_type(0))

            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW = 0x00040000
            style = int(get_long(hwnd, GWL_EXSTYLE))
            style = (style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
            set_long(hwnd, GWL_EXSTYLE, long_type(style))

            user32.SetWindowPos.argtypes = [
                wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                ctypes.c_int, ctypes.c_int, wintypes.UINT,
            ]
            user32.SetWindowPos.restype = wintypes.BOOL
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOZORDER = 0x0004
            SWP_FRAMECHANGED = 0x0020
            user32.SetWindowPos(
                hwnd, None, 0, 0, 0, 0,
                SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_FRAMECHANGED,
            )
        except (AttributeError, OSError, tk.TclError):
            return

    @property
    def tr(self) -> dict:
        return T[self.language]

    def _read_cfg(self) -> dict:
        return load_config()

    def _update_cfg(self, **changes) -> None:
        cfg = self._read_cfg()
        cfg.update(changes)
        save_config_data(cfg)

    def _center_window(self) -> None:
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - WINDOW_W) // 2)
        y = max(0, (sh - WINDOW_H) // 2)
        self.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

    def _build_background(self) -> None:
        path = resource_path("BackIMG.webp")
        if not path.exists():
            messagebox.showerror(
                APP_TITLE,
                self.tr["bg_missing"].format(path=path),
            )
            self.destroy()
            raise SystemExit(1)

        image = Image.open(path).convert("RGB")
        src_ratio = image.width / image.height
        dst_ratio = WINDOW_W / WINDOW_H
        if src_ratio > dst_ratio:
            new_w = int(image.height * dst_ratio)
            left = (image.width - new_w) // 2
            image = image.crop((left, 0, left + new_w, image.height))
        else:
            new_h = int(image.width / dst_ratio)
            top = (image.height - new_h) // 2
            image = image.crop((0, top, image.width, top + new_h))
        image = image.resize((WINDOW_W, WINDOW_H), Image.Resampling.LANCZOS)
        image = ImageEnhance.Brightness(image).enhance(0.83)

        image = image.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle(
            (18, 543, WINDOW_W - 18, 626),
            radius=18,
            fill=(8, 13, 18, 108),
            outline=(235, 242, 248, 72),
            width=1,
        )
        image = Image.alpha_composite(image, overlay)

        # Launcher background uses BackIMG.webp only. The Kya logo is a
        # PCSX2 texture replacement, installed separately at GUI startup.

        png_buffer = io.BytesIO()
        image.save(png_buffer, format="PNG")
        png_b64 = base64.b64encode(png_buffer.getvalue()).decode("ascii")
        self._bg_photo = tk.PhotoImage(data=png_b64, format="png")

        self.canvas = tk.Canvas(
            self,
            width=WINDOW_W,
            height=WINDOW_H,
            bd=0,
            highlightthickness=0,
            bg="black",
        )
        self.canvas.place(x=0, y=0, width=WINDOW_W, height=WINDOW_H)
        self.canvas.create_image(0, 0, image=self._bg_photo, anchor="nw")
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag_window)

        # Gear button just left of the close X.
        gear_x, gear_y = WINDOW_W - 69, 23
        self._gear_glow = self.canvas.create_text(
            gear_x,
            gear_y,
            text="⚙",
            anchor="center",
            fill="#3b6f91",
            font=("Segoe UI Symbol", 29),
            state="hidden",
            tags=("gear_hit",),
        )
        self._gear_text = self.canvas.create_text(
            gear_x,
            gear_y,
            text="⚙",
            anchor="center",
            fill="white",
            font=("Segoe UI Symbol", 22),
            tags=("gear_hit",),
        )
        self.canvas.tag_bind("gear_hit", "<Enter>", self._gear_hover_on)
        self.canvas.tag_bind("gear_hit", "<Leave>", self._gear_hover_off)
        self.canvas.tag_bind("gear_hit", "<Button-1>", lambda _e: self._open_options())

        close_x, close_y = WINDOW_W - 25, 23
        self._close_glow = self.canvas.create_text(
            close_x,
            close_y,
            text="×",
            anchor="center",
            fill="#8f2020",
            font=("Segoe UI Semibold", 31),
            state="hidden",
            tags=("close_hit",),
        )
        self._close_text = self.canvas.create_text(
            close_x,
            close_y,
            text="×",
            anchor="center",
            fill="white",
            font=("Segoe UI Semibold", 23),
            tags=("close_hit",),
        )
        self.canvas.tag_bind("close_hit", "<Enter>", self._close_hover_on)
        self.canvas.tag_bind("close_hit", "<Leave>", self._close_hover_off)
        self.canvas.tag_bind("close_hit", "<Button-1>", lambda _e: self._request_close())
        self.canvas.configure(cursor="arrow")

    def _post_ui(self, func, *args, **kwargs) -> None:
        if self._closing:
            return
        self._ui_queue.put((func, args, kwargs))

    def _drain_ui_queue(self) -> None:
        # The most recent confirmed on-disk AutoSave is selected by default.
        self._refresh_auto_save_choices()

        if self._closing:
            return
        try:
            while True:
                item = self._ui_queue.get_nowait()
                if len(item) == 2:
                    func, args = item
                    kwargs = {}
                else:
                    func, args, kwargs = item
                if not self._closing:
                    func(*args, **kwargs)
        except queue.Empty:
            pass
        if not self._closing:
            self._refresh_live_connection_indicators()
            self._queue_after_id = self.after(50, self._drain_ui_queue)

    def _refresh_live_connection_indicators(self) -> None:
        """Use three-state PINE status: connected, busy/stale, or confirmed lost."""
        if not self._connected_requested:
            return
        ap_link = self._ap_link
        server_online = bool(ap_link is not None and ap_link.connected_event.is_set())
        now = time.monotonic()
        pine_state = pine_indicator_state(
            self._camera_ready_event.is_set(),
            self._pine_lost_at is not None,
            self._pine_last_heartbeat_at, now,
        )
        state = (pine_state, server_online)
        if state == self._last_connection_indicator_state:
            return
        previous = self._last_connection_indicator_state
        self._last_connection_indicator_state = state
        if pine_state == 'busy' and (previous is None or previous[0] != 'busy'):
            age = now - self._pine_last_heartbeat_at
            self._log_threadsafe(
                f'PINE UI BUSY: no completed memory read for {age:.1f}s '
                f'(stage={self._pine_service_stage}); not marking PCSX2 offline '
                'without an actual read failure.', 'warn')
        elif pine_state == 'connected' and previous is not None and previous[0] == 'busy':
            self._log_threadsafe('PINE UI RECOVERED: successful memory read; indicators green.', 'ok')
        self._set_status('pine', pine_state)
        self._set_status('game', pine_state,
                         EXPECTED_GAME_ID if pine_state == 'connected'
                         else self.tr['pine_busy_state'] if pine_state == 'busy'
                         else self.tr['not_detected'])
        self._set_status('server', 'connected' if server_online else 'disconnected',
                         self.tr['connected'] if server_online else self.tr['disconnected'])

    @staticmethod
    def _configure_widget(widget, **kwargs) -> None:
        try:
            widget.configure(**kwargs)
        except Exception:
            pass

    def _request_close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self._stop_event.set()
        self._camera_stop_event.set()
        if self._ap_link is not None:
            self._ap_link.close()

        if self._queue_after_id is not None:
            try:
                self.after_cancel(self._queue_after_id)
            except tk.TclError:
                pass
            self._queue_after_id = None

        try:
            if self.options_window is not None and self.options_window.winfo_exists():
                self.options_window.destroy()
        except tk.TclError:
            pass

        if self._overlay_after_id is not None:
            try:
                self.after_cancel(self._overlay_after_id)
            except tk.TclError:
                pass
            self._overlay_after_id = None
        try:
            if self._overlay_window is not None and self._overlay_window.winfo_exists():
                self._overlay_window.destroy()
        except tk.TclError:
            pass
        self._overlay_window = None
        self._overlay_canvas = None

        try:
            self.withdraw()
        except tk.TclError:
            pass

        self._close_deadline = time.monotonic() + 5.0
        self._wait_for_workers_then_destroy()

    def _wait_for_workers_then_destroy(self) -> None:
        alive = []
        for worker in (self._worker_thread, self._camera_thread):
            if worker is not None and worker.is_alive():
                alive.append(worker)

        if alive and time.monotonic() < self._close_deadline:
            try:
                self._close_poll_after_id = self.after(50, self._wait_for_workers_then_destroy)
            except tk.TclError:
                pass
            return

        self._close_poll_after_id = None
        try:
            while True:
                self._ui_queue.get_nowait()
        except queue.Empty:
            pass

        try:
            self.canvas.delete("all")
        except (tk.TclError, AttributeError):
            pass
        self._bg_photo = None

        try:
            self.destroy()
        except tk.TclError:
            pass

    def _gear_hover_on(self, _event: tk.Event) -> None:
        self.canvas.itemconfigure(self._gear_glow, state="normal")
        self.canvas.itemconfigure(self._gear_text, fill="#a9ddff")
        self.canvas.configure(cursor="hand2")

    def _gear_hover_off(self, _event: tk.Event) -> None:
        self.canvas.itemconfigure(self._gear_glow, state="hidden")
        self.canvas.itemconfigure(self._gear_text, fill="white")
        self.canvas.configure(cursor="arrow")

    def _close_hover_on(self, _event: tk.Event) -> None:
        self.canvas.itemconfigure(self._close_glow, state="normal")
        self.canvas.itemconfigure(self._close_text, fill="#ff8b8b")
        self.canvas.configure(cursor="hand2")

    def _close_hover_off(self, _event: tk.Event) -> None:
        self.canvas.itemconfigure(self._close_glow, state="hidden")
        self.canvas.itemconfigure(self._close_text, fill="white")
        self.canvas.configure(cursor="arrow")

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_origin = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def _drag_window(self, event: tk.Event) -> None:
        if self._drag_origin is None:
            return
        ox, oy = self._drag_origin
        self.geometry(f"+{event.x_root - ox}+{event.y_root - oy}")

    def _canvas_label(self, text: str, x: int, y: int, *, size: int = 10, weight: str = "semibold") -> int:
        family = "Segoe UI Semibold" if weight == "semibold" else "Segoe UI"
        return self.canvas.create_text(
            x,
            y,
            text=text,
            anchor="nw",
            fill=TEXT_MAIN,
            font=(family, size),
        )

    def _build_ui(self) -> None:
        cfg = self._read_cfg()

        left = 28
        width = WINDOW_W - 56

        self.server_label_id = self._canvas_label(self.tr["server"], left, 260)
        self.server_var = tk.StringVar(value=cfg.get("server", "archipelago.gg:42497"))
        self.server_entry = self._entry(self.server_var, left, 283, width)

        self.name_label_id = self._canvas_label(self.tr["name"], left, 335)
        self.name_var = tk.StringVar(value=cfg.get("name", "Kya"))
        self.name_entry = self._entry(self.name_var, left, 358, width)

        self.password_label_id = self._canvas_label(self.tr["password_optional"], left, 410)
        self.password_var = tk.StringVar(value=cfg.get("password", ""))
        self.password_entry = self._entry(self.password_var, left, 433, width, show="•")

        self.connect_button = tk.Button(
            self,
            text=self.tr["connect"],
            command=self._on_connect,
            font=("Segoe UI Semibold", 14),
            fg="white",
            bg=BUTTON_GREEN,
            activebackground=BUTTON_GREEN_ACTIVE,
            activeforeground="white",
            disabledforeground="#e2e7e4",
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        self.connect_button.place(x=left, y=486, width=width, height=52)

        self._build_status_row(left, 553, width)
        self._build_color_studio_button(left, 646, width)
        self._build_texture_folder_status(left, 700, width)
        self._build_auto_save_ui(left, 762, width)
        self._build_log(left, 851, width)

    def _build_auto_save_ui(self, left: int, y: int, width: int) -> None:
        """Autosave UI and explicit, opt-in recovery; user slots 0..9 untouched."""
        self._auto_save_bar = tk.Frame(self, bg='#14231f', highlightbackground='#427263',
                                       highlightthickness=1)
        self._auto_save_bar.place(x=left, y=y, width=width, height=80)
        self._auto_save_check = tk.Checkbutton(
            self._auto_save_bar, variable=self._auto_save_var,
            command=self._on_auto_save_toggle, font=('Segoe UI Semibold', 10),
            fg='#e7f9ef', bg='#14231f', activebackground='#14231f',
            activeforeground='white', selectcolor='#14231f', bd=0,
            highlightthickness=0, cursor='hand2', anchor='w')
        self._auto_save_check.place(x=10, y=4, width=177, height=23)
        self._auto_save_subtitle = tk.Label(self._auto_save_bar, fg='#afd3c2', bg='#14231f',
                                            font=('Segoe UI', 8), anchor='w')
        self._auto_save_subtitle.place(x=196, y=5, width=width-355, height=22)
        self._auto_save_folder_btn = tk.Button(
            self._auto_save_bar, command=self._choose_auto_save_folder,
            font=('Segoe UI', 8), fg='white', bg='#315847', activeforeground='white',
            activebackground='#427261', relief='flat', bd=0, cursor='hand2')
        self._auto_save_folder_btn.place(x=width-149, y=4, width=139, height=22)
        self._auto_save_selected = tk.StringVar(value='')
        self._auto_save_combo = ttk.Combobox(self._auto_save_bar, textvariable=self._auto_save_selected,
                                             state='readonly', font=('Segoe UI', 9))
        self._auto_save_combo.place(x=10, y=30, width=width-183, height=22)
        self._auto_save_reload_btn = tk.Button(
            self._auto_save_bar, command=self._on_auto_save_reload,
            font=('Segoe UI Semibold', 9), fg='white', bg='#315847',
            activeforeground='white', activebackground='#427261', relief='flat', bd=0,
            cursor='hand2')
        self._auto_save_reload_btn.place(x=width-166, y=29, width=156, height=23)
        self._auto_recover_check = tk.Checkbutton(
            self._auto_save_bar, variable=self._auto_recover_var,
            command=self._on_auto_recover_toggle, font=('Segoe UI', 9),
            fg='#ffddb1', bg='#14231f', activebackground='#14231f',
            activeforeground='white', selectcolor='#14231f', bd=0,
            highlightthickness=0, cursor='hand2', anchor='w')
        self._auto_recover_check.place(x=10, y=55, width=width-20, height=20)
        self._update_auto_save_language()
        self._refresh_auto_save_choices(force=True)

    def _update_auto_save_language(self) -> None:
        self._auto_save_controller.language = self.language
        translations = {
            'en': ('Enable auto save', 'Every 2 min + zone', 'PCSX2 folder...', 'Reload auto-save',
                   'Auto-save reload', 'Reload slot {slot}? Unsaved game progress will be lost.',
                   'Disable auto save before changing the folder.', 'Choose the PCSX2 savestates folder'),
            'fr': ('Activer auto-save', '2 min + changement zone', 'Dossier PCSX2...', 'Charger auto-save',
                   'Chargement auto-save', 'Charger le slot {slot} ? La progression non sauvegardée sera perdue.',
                   'Désactive l’auto-save avant de changer le dossier.', 'Choisir le dossier savestates PCSX2'),
            'de': ('Auto-Speichern aktiv', 'Alle 2 Min. + Gebiet', 'PCSX2-Ordner...', 'Auto-Save laden',
                   'Auto-Save laden', 'Slot {slot} laden? Ungespeicherter Fortschritt geht verloren.',
                   'Auto-Speichern vor Ordnerwechsel deaktivieren.', 'PCSX2-Savestate-Ordner auswählen'),
            'es': ('Activar autoguardado', 'Cada 2 min + zona', 'Carpeta PCSX2...', 'Cargar autoguardado',
                   'Cargar autoguardado', '¿Cargar ranura {slot}? Se perderá el progreso no guardado.',
                   'Desactiva el autoguardado antes de cambiar la carpeta.', 'Elegir carpeta de estados PCSX2'),
            'it': ('Attiva salvataggio auto', 'Ogni 2 min + zona', 'Cartella PCSX2...', 'Carica salvataggio',
                   'Carica salvataggio', 'Caricare slot {slot}? I progressi non salvati andranno persi.',
                   'Disattiva il salvataggio automatico prima di cambiare cartella.', 'Scegli cartella savestate PCSX2'),
        }
        self._autosave_strings = translations.get(self.language, translations['en'])
        self._auto_save_check.configure(text=self._autosave_strings[0])
        self._auto_save_subtitle.configure(text=self._autosave_strings[1])
        self._auto_save_folder_btn.configure(text=self._autosave_strings[2])
        self._auto_save_reload_btn.configure(text=self._autosave_strings[3])
        self._auto_recover_check.configure(text={
            'fr': 'Après coupure PCSX2 : recharger auto-save (optionnel)',
            'en': 'After PCSX2 disconnect: restore last auto-save (optional)',
            'de': 'Nach PCSX2-Abbruch: letztes Auto-Save laden (optional)',
            'es': 'Tras caída de PCSX2: restaurar auto-save (opcional)',
            'it': 'Dopo crash PCSX2: ripristina auto-save (opzionale)',
        }.get(self.language, 'After PCSX2 disconnect: restore last auto-save (optional)'))

    def _refresh_auto_save_choices(self, force: bool = False) -> None:
        """Executed on Tk thread: list on-disk slots; newest becomes default."""
        if not hasattr(self, '_auto_save_combo'):
            return
        now = time.monotonic()
        if not force and now < self._auto_save_refresh_at:
            return
        self._auto_save_refresh_at = now + 3.0
        records = self._auto_save_controller.list_recoverable()
        labels = tuple(f"{r['date']}  |  Slot {r['slot']}" for r in records)
        selected = self._auto_save_selected.get()
        if force or labels != self._auto_save_last_labels:
            self._auto_save_entry_by_label = dict(zip(labels, records))
            self._auto_save_combo.configure(values=labels)
            self._auto_save_last_labels = labels
            # Whenever a NEW confirmed snapshot appears, put the newest state
            # back in focus.  Previously the old slot remained selected and
            # could be loaded accidentally after a crash.
            self._auto_save_selected.set(labels[0] if labels else '')
        self._auto_save_reload_btn.configure(state='normal' if labels else 'disabled')

    def _autosave_log(self, key: str, **fmt) -> str:
        strings = {
            'en': {
                'requested':'AUTO SAVE requested: checking PCSX2 savestate folder.',
                'off_request':'AUTO SAVE disabled.', 'folder':'AUTO SAVE folder: {path}',
                'reload_queued':'AUTO SAVE RELOAD queued: slot {slot}.',
                'reload_requested':'AUTO SAVE RELOAD sent to PCSX2: slot {slot}, {file}. Waiting for stable scene.',
                'reload_failed':'AUTO SAVE RELOAD refused/failed: {error}', 'refused':'AUTO SAVE refused: {error}'},
            'fr': {
                'requested':'AUTO SAVE demandé : vérification du dossier PCSX2.',
                'off_request':'AUTO SAVE désactivé.', 'folder':'Dossier AUTO SAVE : {path}',
                'reload_queued':'Chargement AUTO SAVE demandé : slot {slot}.',
                'reload_requested':'Chargement AUTO SAVE envoyé à PCSX2 : slot {slot}, {file}. Attente de stabilisation.',
                'reload_failed':'Échec/refus du chargement AUTO SAVE : {error}', 'refused':'AUTO SAVE refusé : {error}'},
            'de': {
                'requested':'AUTO SAVE angefordert: PCSX2-Ordner wird geprüft.',
                'off_request':'AUTO SAVE deaktiviert.', 'folder':'AUTO SAVE-Ordner: {path}',
                'reload_queued':'AUTO SAVE-Laden angefordert: Slot {slot}.',
                'reload_requested':'AUTO SAVE-Laden an PCSX2 gesendet: Slot {slot}, {file}. Warte auf stabile Szene.',
                'reload_failed':'AUTO SAVE-Laden fehlgeschlagen: {error}', 'refused':'AUTO SAVE abgelehnt: {error}'},
            'es': {
                'requested':'AUTO SAVE solicitado: comprobando carpeta PCSX2.',
                'off_request':'AUTO SAVE desactivado.', 'folder':'Carpeta AUTO SAVE: {path}',
                'reload_queued':'Carga AUTO SAVE solicitada: ranura {slot}.',
                'reload_requested':'Carga AUTO SAVE enviada a PCSX2: ranura {slot}, {file}. Esperando escena estable.',
                'reload_failed':'Carga AUTO SAVE fallida: {error}', 'refused':'AUTO SAVE rechazado: {error}'},
            'it': {
                'requested':'AUTO SAVE richiesto: verifica cartella PCSX2.',
                'off_request':'AUTO SAVE disattivato.', 'folder':'Cartella AUTO SAVE: {path}',
                'reload_queued':'Caricamento AUTO SAVE richiesto: slot {slot}.',
                'reload_requested':'Caricamento AUTO SAVE inviato a PCSX2: slot {slot}, {file}. Attesa scena stabile.',
                'reload_failed':'Caricamento AUTO SAVE fallito: {error}', 'refused':'AUTO SAVE rifiutato: {error}'},
        }
        template = strings.get(self.language, strings['en']).get(key, strings['en'].get(key, key))
        return template.format(**fmt)

    def _on_auto_save_reload(self) -> None:
        entry = self._auto_save_entry_by_label.get(self._auto_save_selected.get())
        if not entry:
            self._refresh_auto_save_choices(force=True)
            return
        # Spell out exactly which checkpoint will be loaded.  Old checkpoints
        # remain available for intentional rollback, never as an ambiguous
        # one-click recovery action.
        latest = self._auto_save_controller.list_recoverable()
        is_latest = bool(latest and latest[0]['slot'] == entry['slot'])
        prompt = self._autosave_strings[5].format(slot=entry['slot'])
        prompt += f"\n\n{entry['date']} — {entry['path'].name}"
        if not is_latest:
            prompt += ("\n\nATTENTION : cette sauvegarde est PLUS ANCIENNE que la dernière confirmée."
                       if self.language == 'fr' else
                       "\n\nWARNING: this save is OLDER than the latest confirmed backup.")
        if not messagebox.askyesno(self._autosave_strings[4], prompt, parent=self):
            return
        if self._auto_save_reload_request.full():
            return
        self._auto_save_reload_request.put_nowait(int(entry['slot']))
        self._log(self._autosave_log('reload_queued', slot=entry['slot']), 'info')

    def _on_auto_save_toggle(self) -> None:
        if self._auto_save_var.get():
            self._auto_save_requested.set()
            self._log(self._autosave_log('requested'), 'info')
        else:
            self._auto_save_requested.clear()
            self._log(self._autosave_log('off_request'), 'info')

    def _on_auto_recover_toggle(self) -> None:
        self._auto_recover_enabled = bool(self._auto_recover_var.get())
        self._update_cfg(kya_auto_reload_after_pcsx2_loss=self._auto_recover_enabled)
        if not self._auto_recover_enabled:
            self._pine_recovery_candidate = None
        self._log('PCSX2 auto-reload after disconnect: ' +
                  ('ENABLED (same-session only; closing PCSX2 manually also counts as disconnect)' if self._auto_recover_enabled
                   else 'DISABLED'), 'warn' if self._auto_recover_enabled else 'info')

    def _choose_auto_save_folder(self) -> None:
        if self._auto_save_var.get():
            messagebox.showwarning(APP_TITLE, self._autosave_strings[6], parent=self)
            return
        path = filedialog.askdirectory(parent=self, initialdir=str(self._auto_save_controller.path),
                                       title=self._autosave_strings[7])
        if not path:
            return
        self._auto_save_controller.path = Path(path)
        self._update_cfg(kya_auto_save_sstates_path=path)
        self._refresh_auto_save_choices(force=True)
        self._log(self._autosave_log('folder', path=path), 'info')

    def _auto_save_tick(self, pine: PineClient, *, safe_ft_room: bool = False) -> None:
        """Drive optional AutoSave without EVER taking down the AP watcher.

        Restored after 0.9.30 accidentally omitted the method when the reload
        UI was inserted. This is called only by the single PINE owner thread.
        """
        controller = self._auto_save_controller
        try:
            wanted = self._auto_save_requested.is_set()
            if wanted != controller.enabled:
                controller.set_enabled(wanted)
            if not controller.enabled:
                return

            blocked = (
                self._ap_stream_hold
                or self._ap_ft_exclusive
                or (self._ap_ft_cleanroom_active and not safe_ft_room)
                or (self._ap_ft_cleanroom_pending and not safe_ft_room)
                or (self._ap_ft_sanctuary_active and not safe_ft_room)
            )
            # Only stable scenes may trigger a new save. The controller itself
            # additionally checks MAP, movement and PCSX2 VM state.
            # Capture AP identity when the save is requested; the controller
            # writes it to the metadata only after the state is verified on disk.
            controller.ap_identity = (self._ap_pending_storage_key(self._ap_data)
                                      if self._ap_joined and self._ap_seed_build_verified else '')
            controller.tick(
                pine,
                self._ap_current_zone,
                (self._ap_stream_last_valid_generation if safe_ft_room else self._ap_stream_candidate)
                if not blocked else None,
                blocked=bool(blocked),
            )
            if not controller.enabled and self._auto_save_requested.is_set():
                self._auto_save_requested.clear()
                self._post_ui(self._auto_save_var.set, False)
        except Exception as exc:
            # AutoSave is optional. A disk error, marker mismatch or programming
            # error must NEVER break _ap_tick (Wolfen checks, items, AP packets).
            self._auto_save_requested.clear()
            try:
                controller.set_enabled(False)
            except Exception:
                controller.enabled = False
            try:
                self._post_ui(self._auto_save_var.set, False)
            except Exception:
                pass
            self._log_threadsafe(
                self._autosave_log('refused', error=f'{type(exc).__name__}: {exc}'),
                'error',
            )


    def _pine_vm_ready_for_savestate_load(self, pine: PineClient) -> bool:
        """PCSX2 LoadState is emulator-level: it does not require live actors.

        AP game-memory writers must still wait for the actor stream guard,
        but using that guard to permit PCSX2's LoadState deadlocks at the
        title screen, where the actor manager may never become populated.
        Require a responsive running VM and the exact supported game instead.
        """
        state = pine._packet(b'\x0f')  # VM status (same check as AutoSave)
        if len(state) < 4 or struct.unpack('<I', state[:4])[0] != 0:
            return False
        return int(pine.read32(SIG_ADDRS[0])) == int(SIG_VALUES[0])

    def _auto_save_reload_tick(self, pine: PineClient) -> bool:
        """User-requested LoadState; never gated on Kya's actor streaming.

        The old 0.9.39 gate waited for an actor manager that need not exist
        on the title screen. Validate disk, AP identity and PCSX2 VM instead.
        """
        if self._manual_reload_pending is None:
            try:
                slot = self._auto_save_reload_request.get_nowait()
            except queue.Empty:
                return False
            self._manual_reload_pending = (int(slot), time.monotonic())
            self._manual_reload_wait_logged = False
        slot, started = self._manual_reload_pending
        now = time.monotonic()
        if now - started > 120.0:
            self._manual_reload_pending = None
            self._manual_reload_wait_logged = False
            self._log_threadsafe('AUTO SAVE RELOAD timed out after 120s; PCSX2 VM not ready.', 'warn')
            return False
        # A new AP connection must identify the current room BEFORE we permit
        # any marked state from a different seed to be loaded.
        if self._ap_link is not None and not (self._ap_joined and self._ap_seed_build_verified):
            if not self._manual_reload_wait_logged:
                self._log_threadsafe('AUTO SAVE RELOAD deferred: waiting for AP slot verification.', 'info')
                self._manual_reload_wait_logged = True
            return False
        try:
            # Preflight BEFORE waiting for scene stability: wrong-seed states
            # should be rejected immediately, not reported as 'streaming'.
            path = self._auto_save_controller.verify_reload_slot(int(slot))
            if self._ap_joined and self._ap_seed_build_verified:
                identity = self._ap_pending_storage_key(self._ap_data)
                entry = next((e for e in self._auto_save_controller.list_recoverable()
                              if int(e['slot']) == int(slot)), None)
                if entry is None or not identity or entry.get('ap_identity') != identity:
                    raise RuntimeError('AutoSave belongs to another Archipelago slot/seed')
        except Exception as exc:
            self._manual_reload_pending = None
            self._manual_reload_wait_logged = False
            self._log_threadsafe(self._autosave_log('reload_failed', error=str(exc)), 'error')
            return True
        if now < self._ap_reload_pause_until or not self._pine_vm_ready_for_savestate_load(pine):
            if not self._manual_reload_wait_logged:
                self._log_threadsafe('AUTO SAVE RELOAD deferred: waiting for running PCSX2/Kya VM (not actor streaming).', 'info')
                self._manual_reload_wait_logged = True
            return False
        # V0.9.46: MAP_STATE_ADDR is shared with regeneration ambers, and
        # it may remain active in cinematics. A trusted PCSX2 VM + seed/file
        # identity is enough for a user-requested emulator LoadState.
        try:
            response = pine._packet(bytes((0x0A, int(slot))))
            if response:
                raise RuntimeError('Unexpected PCSX2 LoadState response')
            self._reset_after_pcsx2_state_change()
            self._log_threadsafe(self._autosave_log('reload_requested', slot=slot, file=path.name), 'ok')
        except Exception as exc:
            # PINE connection errors propagate to the single-owner service.
            if 'PINE' in str(exc) and ('connecte' in str(exc).lower() or 'perdue' in str(exc).lower()):
                raise
            self._log_threadsafe(self._autosave_log('reload_failed', error=str(exc)), 'error')
        finally:
            self._manual_reload_pending = None
            self._manual_reload_wait_logged = False
        return True

    def _build_color_studio_button(self, left: int, y: int, width: int) -> None:
        """Launcher integration: separate process, no PINE or Archipelago writes."""
        self.color_studio_button = tk.Button(
            self,
            text=self._color_studio_button_text(),
            command=self._launch_color_studio,
            font=("Segoe UI Semibold", 11),
            fg="white", bg="#6c419a", activebackground="#8752b6",
            activeforeground="white", relief="flat", bd=0, cursor="hand2",
        )
        self.color_studio_button.place(x=left, y=y, width=width, height=38)

    def _color_studio_button_text(self) -> str:
        return f"🎨  KYA COLOR STUDIO  •  {self.tr['color_studio_button']}"

    def _color_studio_directory(self) -> Path:
        """Support source runs as well as compiled EXEs under Launcher/dist/."""
        parent = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False)
                  else Path(__file__).resolve().parent)
        candidates = (parent / "tools" / "Kya_Color_Studio_v4_3_3",
                      parent.parent / "tools" / "Kya_Color_Studio_v4_3_3")
        for candidate in candidates:
            if (candidate / "START_KYA_COLOR_STUDIO.bat").is_file():
                return candidate
        return candidates[0]

    def _texture_search_paths(self) -> list[Path]:
        """Inspect configured studio destination, then standard PCSX2 paths; no writes."""
        studio = self._color_studio_directory()
        candidates: list[Path] = []
        settings = studio / "studio_settings.json"
        if settings.is_file():
            try:
                configured = json.loads(settings.read_text(encoding="utf-8")).get("destination", "")
                if isinstance(configured, str) and configured.strip():
                    candidates.append(Path(os.path.expandvars(os.path.expanduser(configured.strip()))))
            except (OSError, ValueError, TypeError):
                pass
        docs = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Documents"
        roots = [docs / "PCSX2", Path.home() / "Documents" / "PCSX2",
                 Path.home() / "PCSX2"]
        # Some installations use a redirected Documents folder (OneDrive).
        profile = os.getenv("USERPROFILE")
        if profile:
            roots.append(Path(profile) / "OneDrive" / "Documents" / "PCSX2")
        for root in roots:
            candidates.append(root / "textures" / "SLES-51473" / "replacements")
        unique = []
        seen = set()
        for p in candidates:
            key = os.path.normcase(str(p)).casefold()
            if key not in seen:
                unique.append(p)
                seen.add(key)
        return unique

    def _build_texture_folder_status(self, left: int, y: int, width: int) -> None:
        """An unobtrusive status line inside the launcher's own palette."""
        self._texture_status_bg = tk.Frame(self, bg="#231c31", highlightbackground="#554264",
                                           highlightthickness=1)
        self._texture_status_bg.place(x=left, y=y, width=width, height=50)
        self._texture_status_title = tk.Label(
            self._texture_status_bg, text="", bg="#231c31", fg="#ffc78d",
            font=("Segoe UI Semibold", 9), anchor="w", cursor="hand2")
        self._texture_status_title.place(x=10, y=4, width=width-20, height=18)
        self._texture_status_path = tk.Label(
            self._texture_status_bg, text="", bg="#231c31", fg="#cbb5e0",
            font=("Segoe UI", 8), anchor="w", cursor="hand2")
        self._texture_status_path.place(x=10, y=24, width=width-20, height=17)
        for widget in (self._texture_status_bg, self._texture_status_title, self._texture_status_path):
            widget.bind("<Button-1>", lambda _event: self._show_texture_folder_details())
        self._refresh_texture_folder_status(schedule=False)
        self.after(5500, self._refresh_texture_folder_status)

    def _refresh_texture_folder_status(self, schedule: bool = True) -> None:
        if self._closing:
            return
        paths = self._texture_search_paths()
        # If Color Studio has a custom destination, do not silently report
        # a different PCSX2 folder as valid: Studio would still write into
        # its configured path and could fail on APPLY.
        settings_path = self._color_studio_directory() / "studio_settings.json"
        configured = False
        try:
            if settings_path.is_file():
                configured = bool(json.loads(settings_path.read_text(encoding="utf-8"))
                                  .get("destination", "").strip())
        except (OSError, ValueError, AttributeError, TypeError):
            configured = False
        if configured and paths:
            primary = paths[0]
            found = primary if primary.is_dir() else None
        else:
            found = next((candidate for candidate in paths if candidate.is_dir()), None)
            primary = found or (paths[0] if paths else None)
        self._texture_found = found
        self._texture_paths = paths
        if found:
            self._texture_status_bg.configure(bg="#1d302b", highlightbackground="#3c735d")
            self._texture_status_title.configure(bg="#1d302b", fg="#9ff1ba",
                                                  text="✓ " + self.tr["texture_ok"])
            self._texture_status_path.configure(bg="#1d302b", fg="#b7d6c5")
        else:
            self._texture_status_bg.configure(bg="#231c31", highlightbackground="#735369")
            self._texture_status_title.configure(bg="#231c31", fg="#ffc78d",
                                                  text="⚠ " + self.tr["texture_missing"])
            self._texture_status_path.configure(bg="#231c31", fg="#cbb5e0")
        path_label = str(primary) if primary else "textures/SLES-51473/replacements"
        if len(path_label) > 76:
            path_label = "…" + path_label[-75:]
        self._texture_status_path.configure(text=f"{self.tr['texture_search']}  {path_label}")
        if schedule:
            self.after(5500, self._refresh_texture_folder_status)

    def _show_texture_folder_details(self) -> None:
        paths = getattr(self, "_texture_paths", []) or self._texture_search_paths()
        if getattr(self, "_texture_found", None):
            body = self.tr["texture_ok"] + "\n\n" + str(self._texture_found)
        else:
            body = self.tr["texture_details"].replace("\\n", "\n").format(
                paths="\n".join("• " + str(path) for path in paths))
        messagebox.showinfo(APP_TITLE, body, parent=self)

    def _launch_color_studio(self) -> None:
        studio = self._color_studio_directory()
        start = studio / "START_KYA_COLOR_STUDIO.bat"
        if not start.is_file():
            self._log("Kya Color Studio introuvable : " + str(start), "error")
            messagebox.showerror(APP_TITLE, "Dossier Kya Color Studio introuvable :\n" + str(start), parent=self)
            return
        if os.name != "nt":
            self._log("Kya Color Studio requiert Windows.", "warn")
            return
        try:
            subprocess.Popen(
                ["cmd.exe", "/c", str(start)], cwd=str(studio),
                creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
            )
            self._log("Kya Color Studio v4.3.4 lancé dans une fenêtre séparée.", "ok")
        except (OSError, ValueError) as exc:
            self._log(f"Kya Color Studio : {exc}", "error")
            messagebox.showerror(APP_TITLE, f"Impossible de lancer Kya Color Studio :\n{exc}", parent=self)

    def _build_debug_row(self, left: int, y: int, width: int) -> None:
        specs = [
            ("life", "Vie infinie"),
            ("mana", "Mana infinie"),
            ("oneshot", "OS des mobs"),
            ("zero_mana", "0 MANA"),
            ("ft_forensic", "FT SCAN"),
        ]
        gap = 5
        w = (width - gap * 4) // 5
        for i, (key, label) in enumerate(specs):
            if key == "zero_mana":
                command = self._queue_zero_mana
            elif key == "ft_forensic":
                command = self._queue_ft_forensic_scan
            else:
                command = (lambda k=key: self._toggle_debug_cheat(k))

            if key == "zero_mana":
                bg, active = "#7b3f00", "#9a5200"
            elif key == "ft_forensic":
                bg, active = "#563b83", "#704ea8"
            else:
                bg, active = "#2a3945", "#3a5060"

            btn = tk.Button(
                self,
                text=label,
                command=command,
                font=("Segoe UI Semibold", 8),
                fg="white",
                bg=bg,
                activebackground=active,
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
            )
            btn.place(x=left + i * (w + gap), y=y, width=w, height=29)
            self._debug_buttons[key] = btn
            if key == "ft_forensic":
                self._ft_forensic_button = btn

    def _queue_zero_mana(self) -> None:
        # Infinite mana would immediately overwrite the test value, so disable it
        # automatically before the one-shot write.
        if self._debug_infinite_mana:
            self._debug_infinite_mana = False
            button = self._debug_buttons.get("mana")
            if button is not None:
                button.configure(bg="#2a3945")
            self._log("DEBUG • Mana infinie : OFF (test 0 MANA)", "info")

        self._test_action_queue.put({"kind": "zero_mana"})
        self._log("DEBUG • 0 MANA demandé.", "warn")

    def _toggle_debug_cheat(self, key: str) -> None:
        if key == "life":
            self._debug_infinite_life = not self._debug_infinite_life
            enabled = self._debug_infinite_life
        elif key == "mana":
            self._debug_infinite_mana = not self._debug_infinite_mana
            enabled = self._debug_infinite_mana
        elif key == "oneshot":
            self._debug_one_shot = not self._debug_one_shot
            enabled = self._debug_one_shot
            self._debug_wolfen_hp.clear()
        else:
            return
        button = self._debug_buttons.get(key)
        if button is not None:
            button.configure(bg=(BUTTON_GREEN if enabled else "#2a3945"))
        labels = {"life":"Vie infinie", "mana":"Mana infinie", "oneshot":"OS des mobs"}
        self._log(f"DEBUG • {labels[key]} : {'ON' if enabled else 'OFF'}", "warn" if enabled else "info")

    def _build_shop_demo_button(self, left: int, y: int, width: int) -> None:
        btn = tk.Button(
            self,
            text="SHOP TEST SAFE • 260/260 + ITEMS SHOP + 65535 NOOTIES",
            command=self._queue_shop_demo_setup,
            font=("Segoe UI Semibold", 9),
            fg="white",
            bg="#6b3fa0",
            activebackground="#8050bd",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        btn.place(x=left, y=y, width=width, height=25)

    def _queue_shop_demo_setup(self) -> None:
        self._test_action_queue.put({"kind": "shop_demo_setup"})
        self._log("SHOP TEST SAFE demandé : 260 Wolfens + items du shop + 65535 Nooties. Runes/story/HP max non forcés.", "warn")

    def _build_progression_test_row(self, left: int, y: int, width: int) -> None:
        self._canvas_label("Test progression / blocages", left, y, size=9)

        combo = ttk.Combobox(
            self,
            textvariable=self._test_item_var,
            values=TEST_PROGRESSION_ITEMS,
            state="readonly",
            font=("Segoe UI", 9),
        )
        combo.place(x=left, y=y + 25, width=190, height=29)

        grant = tk.Checkbutton(
            self,
            text="Donner l'item après scan",
            variable=self._test_grant_var,
            font=("Segoe UI", 8),
            fg="#dce7ed",
            bg="#11161b",
            activebackground="#11161b",
            activeforeground="white",
            selectcolor="#11161b",
            relief="flat",
            bd=0,
        )
        grant.place(x=left + 198, y=y + 25, width=155, height=29)

        scan_btn = tk.Button(
            self,
            text="SCAN COMPLET",
            command=lambda: self._queue_progression_snapshot(False),
            font=("Segoe UI Semibold", 8),
            fg="white",
            bg="#2a3945",
            activebackground="#3a5060",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        scan_btn.place(x=left + 361, y=y + 25, width=95, height=29)

        block_btn = tk.Button(
            self,
            text="TOUT RÉCUPÉRÉ\nBESOIN DE...",
            command=lambda: self._queue_progression_snapshot(True),
            font=("Segoe UI Semibold", 8),
            fg="white",
            bg="#8a5a24",
            activebackground="#a66b2a",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        block_btn.place(x=left + 464, y=y + 18, width=width - 464, height=43)

    def _queue_progression_snapshot(self, blocker: bool) -> None:
        item = self._test_item_var.get().strip() or "Unknown"
        grant = bool(blocker and self._test_grant_var.get())
        self._test_action_queue.put({"kind": "snapshot", "blocker": blocker, "item": item, "grant": grant})
        if blocker:
            self._log(f"TEST demandé : tout accessible récupéré, besoin de {item}.", "warn")
        else:
            self._log("Scan complet demandé.", "info")


    def _queue_ft_forensic_scan(self) -> None:
        # Capture the visible log while we are on Tk's UI thread.
        try:
            self._ft_forensic_log_seed = self.log_text.get("1.0", "end-1c")
        except Exception:
            self._ft_forensic_log_seed = ""
        self._test_action_queue.put({"kind": "ft_forensic_toggle"})
        self._log(
            "FT FORENSICS demandé. Une fois READY, utilise immédiatement le Fast Travel à tester.",
            "warn",
        )

    def _ft_forensic_output_dir(self) -> Path:
        try:
            base = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
        except Exception:
            base = Path.cwd()
        out = base / "ft_scans"
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _ft_forensic_route_catalog(self) -> list[dict]:
        routes = []
        for zone, group in self._ap_data.get("FAST_TRAVEL_ALLOWED_ROUTES", {}).items():
            for raw in group:
                route = dict(raw)
                route.setdefault("zone", zone)
                routes.append(route)
        return routes

    def _ft_forensic_known_labels(self) -> dict[int, list[str]]:
        labels: dict[int, list[str]] = {}
        d = self._ap_data
        for source_key in d.get("NATIV_FAST_TRAVEL_SOURCE_KEYS", []):
            labels.setdefault(int(source_key), []).append("Nativ source")
        for route in self._ft_forensic_route_catalog():
            labels.setdefault(int(route["target_key"]), []).append(
                f"{route.get('label', route.get('id', '?'))} TARGET"
            )
            labels.setdefault(int(route["master_key"]), []).append(
                f"{route.get('label', route.get('id', '?'))} MASTER"
            )
        for source_key, master_key in d.get("NATIV_WOOD_MASTER_KEYS", {}).items():
            labels.setdefault(int(master_key), []).append(
                f"Nativ wood Master for source 0x{int(source_key):04X}"
            )
        for source_key, controller_key in d.get("NATIV_WIND_CONTROLLER_KEYS", {}).items():
            labels.setdefault(int(controller_key), []).append(
                f"Nativ wind controller for source 0x{int(source_key):04X}"
            )
        return labels

    def _ft_forensic_actor_index(self, pine: PineClient, *, full: bool) -> dict:
        d = self._ap_data
        manager_global = int(d.get("ADDR_ACTOR_MANAGER_GLOBAL", 0x004516A4))
        manager = int(pine.read32(manager_global))
        out = {
            "manager": manager,
            "active_list": 0,
            "active_count": 0,
            "actors": [],
            "by_key": {},
        }
        if not self._ap_valid_pointer(manager):
            return out

        active_list, active_count = pine.read32_many([
            manager + int(d.get("ACTOR_MANAGER_ACTIVE_LIST_OFFSET", 0x54)),
            manager + int(d.get("ACTOR_MANAGER_ACTIVE_COUNT_OFFSET", 0x58)),
        ])
        active_list = int(active_list)
        active_count = int(active_count)
        out["active_list"] = active_list
        out["active_count"] = active_count

        if (
            not self._ap_valid_pointer(active_list)
            or active_count < 0
            or active_count > int(d.get("ACTOR_MANAGER_MAX_ACTIVE", 4096))
        ):
            return out

        slots = pine.read32_many(
            [active_list + i * 4 for i in range(active_count)]
        ) if active_count else []
        actors = sorted(set(int(a) for a in slots if self._ap_valid_pointer(int(a))))
        if not actors:
            return out

        vtables = pine.read32_many(actors)
        descs = pine.read32_many(
            [a + int(d["FAST_TRAVEL_DESCRIPTOR_OFFSET"]) for a in actors]
        )

        valid_desc = [
            (a, int(vt), int(desc))
            for a, vt, desc in zip(actors, vtables, descs)
            if self._ap_valid_pointer(int(desc))
        ]
        keys = pine.read32_many(
            [desc + int(d["FAST_TRAVEL_KEY_OFFSET"]) for _, _, desc in valid_desc]
        ) if valid_desc else []

        keyed = [
            (a, vt, desc, int(key) & 0xFFFFFFFF)
            for (a, vt, desc), key in zip(valid_desc, keys)
        ]

        # Full snapshots keep all keyed actors; trace samples only keep
        # FastTravel/MasterEvent + known AP keys to stay light.
        ft_vt = int(d["FAST_TRAVEL_VTABLE"])
        master_vt = int(d["MASTER_EVENT_VTABLE"])
        wind_vt = int(d.get("WIND_CONTROLLER_VTABLE", 0))
        wood_handler_vt = int(d.get("NATIV_WOOD_HANDLER_VTABLE", 0))
        known_keys = set(self._ft_forensic_known_labels())

        chosen = []
        for a, vt, desc, key in keyed:
            if full or vt in (ft_vt, master_vt, wind_vt, wood_handler_vt) or key in known_keys:
                chosen.append((a, vt, desc, key))

        if not chosen:
            return out

        # Common actor fields, useful to correlate with Ghidra.
        common_addrs = []
        for a, _vt, _desc, _key in chosen:
            common_addrs.extend([
                a + int(d["ACTOR_FLAGS_OFFSET"]),
                a + int(d["ACTOR_STATE_OFFSET"]),
                a + int(d["ACTOR_PREV_STATE_OFFSET"]),
                a + int(d["ACTOR_POS_X_OFFSET"]),
                a + int(d["ACTOR_POS_Y_OFFSET"]),
                a + int(d["ACTOR_POS_Z_OFFSET"]),
            ])
        common_vals = pine.read32_many(common_addrs)

        labels = self._ft_forensic_known_labels()
        rows = []
        vi = 0
        for a, vt, desc, key in chosen:
            flags, state, prev, rx, ry, rz = map(int, common_vals[vi:vi + 6])
            vi += 6
            try:
                x = self._ap_raw_to_float(rx)
                y = self._ap_raw_to_float(ry)
                z = self._ap_raw_to_float(rz)
            except Exception:
                x = y = z = float("nan")

            row = {
                "actor": a,
                "vtable": vt,
                "descriptor": desc,
                "key": key,
                "labels": " | ".join(labels.get(key, [])),
                "flags": flags,
                "state": state,
                "prev": prev,
                "x": x,
                "y": y,
                "z": z,
            }

            if vt == ft_vt:
                vals = pine.read32_many([
                    a + int(d["FAST_TRAVEL_INDEX_OFFSET"]),
                    a + int(d["FAST_TRAVEL_INDEX_COPY_OFFSET"]),
                    a + int(d["FAST_TRAVEL_MASK_OFFSET"]),
                    a + int(d["FAST_TRAVEL_ACTIVE_OFFSET"]),
                    a + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]),
                    a + 0x2AC,
                    a + 0x2B0,
                    a + int(d["FAST_TRAVEL_ROUTE_TABLE_OFFSET"]),
                ])
                row.update({
                    "ft_index": int(vals[0]),
                    "ft_index_copy": int(vals[1]),
                    "ft_mask": int(vals[2]),
                    "ft_active": int(vals[3]),
                    "ft_available": int(vals[4]),
                    "ft_2ac": int(vals[5]),
                    "ft_2b0": int(vals[6]),
                    "ft_route_ptr": int(vals[7]),
                })

            rows.append(row)
            out["by_key"].setdefault(key, []).append(row)

        out["actors"] = rows
        return out

    def _ft_forensic_kya(self, pine: PineClient) -> dict:
        d = self._ap_data
        actor = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
        row = {"actor": actor, "x": float("nan"), "y": float("nan"), "z": float("nan")}
        if self._ap_valid_pointer(actor):
            vals = pine.read32_many([
                actor + int(d["ACTOR_POS_X_OFFSET"]),
                actor + int(d["ACTOR_POS_Y_OFFSET"]),
                actor + int(d["ACTOR_POS_Z_OFFSET"]),
            ])
            row["x"] = self._ap_raw_to_float(int(vals[0]))
            row["y"] = self._ap_raw_to_float(int(vals[1]))
            row["z"] = self._ap_raw_to_float(int(vals[2]))
        return row

    @staticmethod
    def _ft_forensic_distance(a: dict, b: dict) -> float | None:
        try:
            ax, ay, az = float(a["x"]), float(a["y"]), float(a["z"])
            bx, by, bz = float(b["x"]), float(b["y"]), float(b["z"])
            if not all(v == v and abs(v) < 1e6 for v in (ax, ay, az, bx, by, bz)):
                return None
            return ((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2) ** 0.5
        except Exception:
            return None

    def _ft_forensic_sample(self, pine: PineClient) -> None:
        if not self._ft_forensic_active:
            return
        now = time.monotonic()
        if now < self._ft_forensic_next_sample:
            return
        self._ft_forensic_next_sample = now + 0.15

        idx = self._ft_forensic_actor_index(pine, full=False)
        kya = self._ft_forensic_kya(pine)
        t_ms = int((now - self._ft_forensic_started) * 1000.0)
        zone_hint = str(self._ap_current_zone or "?")

        rows = idx.get("actors", [])
        if not rows:
            self._ft_forensic_samples.append({
                "t_ms": t_ms,
                "zone_hint": zone_hint,
                "manager": idx.get("manager", 0),
                "active_list": idx.get("active_list", 0),
                "active_count": idx.get("active_count", 0),
                "kya_actor": kya["actor"],
                "kya_x": kya["x"],
                "kya_y": kya["y"],
                "kya_z": kya["z"],
                "role": "NO_RELEVANT_ACTORS",
            })
            return

        d = self._ap_data
        ft_vt = int(d["FAST_TRAVEL_VTABLE"])
        master_vt = int(d["MASTER_EVENT_VTABLE"])
        wind_vt = int(d.get("WIND_CONTROLLER_VTABLE", 0))

        for row in rows:
            vt = int(row["vtable"])
            if vt == ft_vt:
                role = "FastTravel"
            elif vt == master_vt:
                role = "MasterEvent"
            elif vt == wind_vt:
                role = "WindController"
            else:
                role = "KnownActor"

            sample = {
                "t_ms": t_ms,
                "zone_hint": zone_hint,
                "manager": idx.get("manager", 0),
                "active_list": idx.get("active_list", 0),
                "active_count": idx.get("active_count", 0),
                "kya_actor": kya["actor"],
                "kya_x": kya["x"],
                "kya_y": kya["y"],
                "kya_z": kya["z"],
                "role": role,
                **row,
            }
            dist = self._ft_forensic_distance(kya, row)
            sample["kya_distance"] = dist
            self._ft_forensic_samples.append(sample)

    def _ft_forensic_memory_rows(self, pine: PineClient, snapshot: dict, phase: str) -> tuple[list[dict], list[dict]]:
        d = self._ap_data
        known_keys = set(self._ft_forensic_known_labels())
        source_keys = {int(x) for x in d.get("NATIV_FAST_TRAVEL_SOURCE_KEYS", [])}
        relevant = [
            row for row in snapshot.get("actors", [])
            if int(row.get("key", -1)) in known_keys | source_keys
            and int(row.get("vtable", 0)) in (
                int(d["FAST_TRAVEL_VTABLE"]),
                int(d["MASTER_EVENT_VTABLE"]),
                int(d.get("WIND_CONTROLLER_VTABLE", 0)),
            )
        ]

        memory_rows: list[dict] = []
        pointer_rows: list[dict] = []
        for row in relevant:
            actor = int(row["actor"])
            # 0x000..0x33C includes FT fields through the route pointer and
            # enough Master state/context for Ghidra correlation.
            offsets = list(range(0, 0x340, 4))
            vals = pine.read32_many([actor + off for off in offsets])
            pointer_candidates = [
                int(v) for v in vals if self._ap_valid_pointer(int(v))
            ]
            pointed = {}
            if pointer_candidates:
                unique = sorted(set(pointer_candidates))
                pvals = pine.read32_many(unique)
                pointed = dict(zip(unique, [int(x) for x in pvals]))

            for off, raw in zip(offsets, vals):
                raw = int(raw)
                try:
                    as_float = self._ap_raw_to_float(raw)
                except Exception:
                    as_float = float("nan")
                is_ptr = self._ap_valid_pointer(raw)
                memory_rows.append({
                    "phase": phase,
                    "key": f"0x{int(row['key']):04X}",
                    "labels": row.get("labels", ""),
                    "actor": f"0x{actor:08X}",
                    "vtable": f"0x{int(row['vtable']):08X}",
                    "offset": f"0x{off:03X}",
                    "address": f"0x{actor + off:08X}",
                    "raw_hex": f"0x{raw:08X}",
                    "raw_u32": raw,
                    "as_float": as_float,
                    "is_pointer": int(is_ptr),
                    "pointed_dword": f"0x{pointed.get(raw, 0):08X}" if is_ptr else "",
                })
                if is_ptr:
                    pointer_rows.append({
                        "phase": phase,
                        "key": f"0x{int(row['key']):04X}",
                        "labels": row.get("labels", ""),
                        "actor": f"0x{actor:08X}",
                        "offset": f"0x{off:03X}",
                        "pointer": f"0x{raw:08X}",
                        "pointed_dword": f"0x{pointed.get(raw, 0):08X}",
                    })

        return memory_rows, pointer_rows

    def _ft_forensic_route_table_rows(self, pine: PineClient, snapshot: dict, phase: str) -> list[dict]:
        d = self._ap_data
        out: list[dict] = []
        for row in snapshot.get("actors", []):
            if int(row.get("vtable", 0)) != int(d["FAST_TRAVEL_VTABLE"]):
                continue
            ptr = int(row.get("ft_route_ptr", 0) or 0)
            if not self._ap_valid_pointer(ptr):
                continue
            offsets = list(range(0, 0x100, 4))
            vals = pine.read32_many([ptr + off for off in offsets])
            for off, raw in zip(offsets, vals):
                raw = int(raw)
                out.append({
                    "phase": phase,
                    "ft_key": f"0x{int(row['key']):04X}",
                    "labels": row.get("labels", ""),
                    "ft_actor": f"0x{int(row['actor']):08X}",
                    "route_ptr": f"0x{ptr:08X}",
                    "offset": f"0x{off:03X}",
                    "address": f"0x{ptr + off:08X}",
                    "raw_hex": f"0x{raw:08X}",
                    "raw_u32": raw,
                    "as_float": self._ap_raw_to_float(raw),
                    "is_pointer": int(self._ap_valid_pointer(raw)),
                })
        return out

    def _ft_forensic_static_snapshot(self, pine: PineClient, phase: str) -> dict:
        idx = self._ft_forensic_actor_index(pine, full=True)
        kya = self._ft_forensic_kya(pine)
        memory_rows, pointer_rows = self._ft_forensic_memory_rows(pine, idx, phase)
        route_table_rows = self._ft_forensic_route_table_rows(pine, idx, phase)
        return {
            "phase": phase,
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "zone_hint": str(self._ap_current_zone or "?"),
            "kya": kya,
            "manager": idx.get("manager", 0),
            "active_list": idx.get("active_list", 0),
            "active_count": idx.get("active_count", 0),
            "actors": idx.get("actors", []),
            "memory_rows": memory_rows,
            "pointer_rows": pointer_rows,
            "route_table_rows": route_table_rows,
        }

    @staticmethod
    def _ft_write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
        if fields is None:
            fields = []
            seen = set()
            for row in rows:
                for key in row.keys():
                    if key not in seen:
                        seen.add(key)
                        fields.append(key)
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fields, delimiter=";", extrasaction="ignore")
            w.writeheader()
            for row in rows:
                w.writerow(row)

    def _ft_forensic_summary_text(self, start: dict, end: dict) -> str:
        d = self._ap_data
        routes = self._ft_forensic_route_catalog()
        lines = [
            "KYA FAST TRAVEL FORENSIC SCAN",
            "=" * 88,
            f"Launcher: {APP_TITLE}",
            f"Start: {start.get('timestamp')}",
            f"End:   {end.get('timestamp')}",
            f"Start zone hint: {start.get('zone_hint')}",
            f"End zone hint:   {end.get('zone_hint')}",
            "",
            "GHIDRA / RUNTIME LANDMARKS",
            "-" * 88,
            f"Fast Travel VTable : 0x{int(d['FAST_TRAVEL_VTABLE']):08X}",
            f"Master Event VTable: 0x{int(d['MASTER_EVENT_VTABLE']):08X}",
            f"Wind controller VT : 0x{int(d.get('WIND_CONTROLLER_VTABLE', 0)):08X}",
            f"Wood C2D0 handler  : 0x{int(d.get('NATIV_WOOD_HANDLER_VTABLE', 0)):08X}",
            "Actor persistent key: Read32(Read32(actor+0x1C)+0x28)",
            "Master state/prev  : actor+0x104 / actor+0x108",
            "FT fields           : +294 index, +298 copy, +29C mask, +2A0 active,",
            "                      +2A4 available, +2AC/+2B0 runtime, +2BC route ptr",
            "Ghidra FUN_00168820: C2D0+0x04 -> Master Event; +0x14 required; +0x18 radius.",
            "",
            "AP STARTING FAST TRAVELS",
            "-" * 88,
        ]
        for route in self._ap_starting_fast_travel_routes:
            lines.append(
                f"{route.get('label')} | source=0x{int(route['source_key']):04X}/idx {int(route['source_index'])} "
                f"| target=0x{int(route['target_key']):04X} | master=0x{int(route['master_key']):04X}"
            )

        lines += ["", "TRACE IDENTITY / POSITION SUMMARY", "-" * 88]
        samples = list(self._ft_forensic_samples)

        def fmt_pos(rows):
            vals = []
            seen = set()
            for r in rows:
                try:
                    pos = (round(float(r["x"]), 3), round(float(r["y"]), 3), round(float(r["z"]), 3))
                except Exception:
                    continue
                if pos not in seen:
                    seen.add(pos)
                    vals.append(pos)
            return vals

        for route in routes:
            target_key = int(route["target_key"])
            master_key = int(route["master_key"])
            tr = [r for r in samples if int(r.get("key", -1)) == target_key]
            mr = [r for r in samples if int(r.get("key", -1)) == master_key]
            if not tr and not mr:
                continue
            targ_addrs = sorted({int(r["actor"]) for r in tr if r.get("actor") is not None})
            mast_addrs = sorted({int(r["actor"]) for r in mr if r.get("actor") is not None})
            dists = [
                float(r["kya_distance"]) for r in tr
                if r.get("kya_distance") is not None
            ]
            states = sorted({int(r["state"]) for r in mr if r.get("state") is not None})
            lines.append(
                f"{route.get('label')}: target addrs="
                f"{', '.join(f'0x{x:08X}' for x in targ_addrs) or '-'} | "
                f"master addrs={', '.join(f'0x{x:08X}' for x in mast_addrs) or '-'} | "
                f"master states={states or '-'} | "
                f"min Kya->target={min(dists):.3f}m" if dists else
                f"{route.get('label')}: target addrs="
                f"{', '.join(f'0x{x:08X}' for x in targ_addrs) or '-'} | "
                f"master addrs={', '.join(f'0x{x:08X}' for x in mast_addrs) or '-'} | "
                f"master states={states or '-'} | min Kya->target=-"
            )
            tpos = fmt_pos(tr)
            mpos = fmt_pos(mr)
            if tpos:
                lines.append(f"  target positions: {tpos[:12]}")
            if mpos:
                lines.append(f"  master positions: {mpos[:12]}")

        lines += [
            "",
            "START / END KYA",
            "-" * 88,
            f"START: actor=0x{int(start['kya']['actor']):08X} "
            f"pos=({start['kya']['x']:.3f}, {start['kya']['y']:.3f}, {start['kya']['z']:.3f})",
            f"END:   actor=0x{int(end['kya']['actor']):08X} "
            f"pos=({end['kya']['x']:.3f}, {end['kya']['y']:.3f}, {end['kya']['z']:.3f})",
            "",
            "FILES",
            "-" * 88,
            "trace.csv            = 150 ms timeline of relevant FT/Master actors + Kya position",
            "actors_start/end.csv = all keyed Actor Manager actors at both ends",
            "memory.csv           = raw 0x000..0x33C dumps for known FT/Master/source actors",
            "pointers.csv         = plausible pointers found in those actor dumps",
            "route_tables.csv     = raw +0x000..+0x0FC of every loaded FT +0x2BC route table",
            "launcher_log.txt     = launcher log before + during the capture",
            "manifest.json        = AP slot/routes and scan metadata",
        ]
        return "\n".join(lines) + "\n"

    def _ft_forensic_finalize(self, pine: PineClient, reason: str = "timeout") -> Path:
        end = self._ft_forensic_static_snapshot(pine, "end")
        start = self._ft_forensic_start_snapshot or self._ft_forensic_static_snapshot(pine, "start_fallback")

        self._ft_forensic_active = False
        if self._ft_forensic_button is not None:
            self._post_ui(self._configure_widget, self._ft_forensic_button, text="FT SCAN", bg="#563b83")

        out_dir = self._ft_forensic_output_dir()
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"Kya_FT_Forensic_{stamp}"
        work = out_dir / base
        work.mkdir(parents=True, exist_ok=True)

        # Flatten actor snapshots.
        def actor_rows(snapshot):
            rows = []
            for row in snapshot.get("actors", []):
                r = dict(row)
                for key in ("actor", "vtable", "descriptor", "key", "flags", "state", "prev",
                            "ft_mask", "ft_2ac", "ft_2b0", "ft_route_ptr"):
                    if key in r and isinstance(r[key], int):
                        width = 4 if key == "key" else 8
                        r[key + "_hex"] = f"0x{int(r[key]):0{width}X}"
                rows.append(r)
            return rows

        start_actors = actor_rows(start)
        end_actors = actor_rows(end)

        self._ft_write_csv(work / "trace.csv", list(self._ft_forensic_samples))
        self._ft_write_csv(work / "actors_start.csv", start_actors)
        self._ft_write_csv(work / "actors_end.csv", end_actors)
        self._ft_write_csv(
            work / "memory.csv",
            list(start.get("memory_rows", [])) + list(end.get("memory_rows", [])),
        )
        self._ft_write_csv(
            work / "pointers.csv",
            list(start.get("pointer_rows", [])) + list(end.get("pointer_rows", [])),
        )
        self._ft_write_csv(
            work / "route_tables.csv",
            list(start.get("route_table_rows", [])) + list(end.get("route_table_rows", [])),
        )

        # Log seed + runtime log entries collected thread-safely.
        with self._ft_forensic_lock:
            runtime_logs = list(self._ft_forensic_runtime_logs)
        log_lines = [self._ft_forensic_log_seed.rstrip(), "", "===== DURING FORENSIC CAPTURE ====="]
        for entry in runtime_logs:
            log_lines.append(
                f"[{entry['clock']}] [{entry['tag']}] +{entry['t_ms']}ms {entry['message']}"
            )
        (work / "launcher_log.txt").write_text("\n".join(log_lines).strip() + "\n", encoding="utf-8")

        summary = self._ft_forensic_summary_text(start, end)
        (work / "summary.txt").write_text(summary, encoding="utf-8")

        manifest = {
            "launcher": APP_TITLE,
            "reason": reason,
            "start_timestamp": start.get("timestamp"),
            "end_timestamp": end.get("timestamp"),
            "duration_seconds_requested": 30,
            "sample_interval_seconds": 0.15,
            "slot_data": dict(self._ap_slot_data),
            "starting_fast_travel_routes": [dict(x) for x in self._ap_starting_fast_travel_routes],
            "current_zone_at_end": self._ap_current_zone,
            "samples": len(self._ft_forensic_samples),
            "ghidra_landmarks": {
                "FAST_TRAVEL_VTABLE": f"0x{int(self._ap_data['FAST_TRAVEL_VTABLE']):08X}",
                "MASTER_EVENT_VTABLE": f"0x{int(self._ap_data['MASTER_EVENT_VTABLE']):08X}",
                "C2D0_VTABLE": f"0x{int(self._ap_data.get('NATIV_WOOD_HANDLER_VTABLE', 0)):08X}",
                "FUN_00168820": "C2D0+0x04 -> Master; +0x14 required; +0x18 radius",
            },
        }
        (work / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        zip_path = out_dir / f"{base}.zip"
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for p in sorted(work.iterdir()):
                if p.is_file():
                    zf.write(p, p.name)

        self._ft_forensic_samples = []
        self._ft_forensic_runtime_logs = []
        self._ft_forensic_start_snapshot = None

        return zip_path

    def _ft_forensic_tick(self, pine: PineClient) -> None:
        if not self._ft_forensic_active:
            return
        self._ft_forensic_sample(pine)
        if time.monotonic() >= self._ft_forensic_deadline:
            try:
                zip_path = self._ft_forensic_finalize(pine, "timeout")
                self._log_threadsafe(
                    f"FT FORENSICS terminé -> {zip_path}. Envoie-moi ce ZIP.",
                    "ok",
                )
            except Exception as exc:
                self._ft_forensic_active = False
                self._log_threadsafe(
                    f"FT FORENSICS finalisation failed: {type(exc).__name__}: {exc}",
                    "error",
                )


    def _test_output_dir(self) -> Path:
        try:
            base = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
        except Exception:
            base = Path.cwd()
        out = base / "test_scans"
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _scan_runtime_state(self, pine: PineClient) -> dict:
        d = self._ap_data
        zone = self._ap_current_zone or "?"
        freed = int(pine.read32(GLOBAL_FREED_WOLFENS_ADDR))
        progression_addrs = {
            "Magic Bouncers": 0x0042540C,
            "Climbing Gloves": 0x00425414,
            "Boomy Level": 0x0042541C,
            "Bracelet Bitfield": 0x00425424,
            "Magic Regeneration": 0x00425434,
            "Jamgut Birdcall": 0x0042543C,
            "Telescope": 0x00425444,
            "Receptacle": 0x0042544C,
            "Board Level": 0x00425454,
            "Magic Gauge Level": 0x0042545C,
            "Life Gauge": 0x00425474,
            "Nooties": 0x0048EABC,
        }
        vals = pine.read32_many(list(progression_addrs.values()))
        progression = dict(zip(progression_addrs, [int(v) for v in vals]))

        actor_info = {"manager": None, "active_list": None, "active_count": 0, "fast_travels": [], "wolfens": {}}
        manager_global = int(d.get("ADDR_ACTOR_MANAGER_GLOBAL", 0x004516A4))
        manager = int(pine.read32(manager_global))
        if self._ap_valid_pointer(manager):
            active = int(pine.read32(manager + int(d.get("ACTOR_MANAGER_ACTIVE_LIST_OFFSET", 0x54))))
            count = int(pine.read32(manager + int(d.get("ACTOR_MANAGER_ACTIVE_COUNT_OFFSET", 0x58))))
            actor_info["manager"] = f"0x{manager:08X}"
            actor_info["active_list"] = f"0x{active:08X}" if self._ap_valid_pointer(active) else None
            actor_info["active_count"] = count
            if self._ap_valid_pointer(active) and 0 <= count <= 5000:
                slots = pine.read32_many([active + i * 4 for i in range(count)]) if count else []
                actors = sorted(set(a for a in slots if self._ap_valid_pointer(a)))
                vtables = pine.read32_many(actors) if actors else []
                ft_actors = [a for a, vt in zip(actors, vtables) if vt == int(d["FAST_TRAVEL_VTABLE"])]
                if ft_actors:
                    states = pine.read32_many([a + int(d["FAST_TRAVEL_STATE_OFFSET"]) for a in ft_actors])
                    descs = pine.read32_many([a + int(d["FAST_TRAVEL_DESCRIPTOR_OFFSET"]) for a in ft_actors])
                    valid = [(a, st, desc) for a, st, desc in zip(ft_actors, states, descs) if self._ap_valid_pointer(desc)]
                    keys = pine.read32_many([desc + int(d["FAST_TRAVEL_KEY_OFFSET"]) for _, _, desc in valid]) if valid else []
                    zone_labels = FAST_TRAVEL_TEST_LABELS.get(zone, {})
                    ap_map = d.get("FAST_TRAVEL_ZONE_KEY_TO_LOCATION", {}).get(zone, {})
                    for (a, st, desc), key in zip(valid, keys):
                        key = int(key)
                        actor_info["fast_travels"].append({
                            "key": f"0x{key:04X}",
                            "state": int(st),
                            "actor": f"0x{int(a):08X}",
                            "descriptor": f"0x{int(desc):08X}",
                            "test_label": zone_labels.get(key, ""),
                            "ap_location": ap_map.get(str(key), ""),
                        })
                wolf_actors = [a for a, vt in zip(actors, vtables) if vt == int(d["WOLFEN_VTABLE"])]
                if wolf_actors:
                    states = pine.read32_many([a + int(d["WOLFEN_STATE_OFFSET"]) for a in wolf_actors])
                    actor_info["wolfens"] = {
                        "active": len(wolf_actors),
                        "present_state1": sum(1 for x in states if int(x) == int(d["WOLFEN_STATE_PRESENT"])),
                        "freed_state2": sum(1 for x in states if int(x) == int(d["WOLFEN_STATE_FREED"])),
                    }
        return {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "zone": zone,
            "global_freed_wolfens": freed,
            "progression": progression,
            "actors": actor_info,
            "ap_checked_count": len(self._ap_checked),
        }

    def _manual_test_grant(self, pine: PineClient, item: str) -> tuple[int, int, int] | None:
        spec = TEST_ITEM_WRITES.get(item)
        if spec is None:
            return None
        address, minimum = spec
        before = int(pine.read32(address))
        target = max(before, int(minimum))
        if target != before:
            pine.write32(address, target)
        after = int(pine.read32(address))
        return address, before, after

    def _write_test_snapshot(self, data: dict, blocker: bool, item: str, grant_result) -> None:
        out = self._test_output_dir()
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        data = dict(data)
        data["event"] = "BLOCKER" if blocker else "SCAN"
        data["needed_item"] = item if blocker else ""
        if grant_result is not None:
            address, before, after = grant_result
            data["manual_test_grant"] = {"address": f"0x{address:08X}", "before": before, "after": after}
        else:
            data["manual_test_grant"] = None

        (out / f"Kya_Test_{stamp}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

        csv_path = out / "Kya_Progression_Blockers.csv"
        new_file = not csv_path.exists()
        with csv_path.open("a", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            if new_file:
                w.writerow(["Timestamp", "Event", "Zone", "Global Freed", "Needed Item", "Manual Grant", "FT Keys/States"])
            ft_text = ", ".join(f"{x['key']}={x['state']} {x.get('test_label','')}".strip() for x in data.get("actors", {}).get("fast_travels", []))
            grant_text = ""
            if grant_result is not None:
                address, before, after = grant_result
                grant_text = f"0x{address:08X}: {before}->{after}"
            w.writerow([data["timestamp"], data["event"], data["zone"], data["global_freed_wolfens"], data["needed_item"], grant_text, ft_text])

    def _apply_shop_demo_setup(self, pine: PineClient) -> None:
        d = self._ap_data

        self._ap_shop_test_mode = True
        SHOP_DEMO_LIFE_TARGET = self._ap_owned_life_target(d)

        # SHOP-SAFE player state only. The previous demo wrote every Rune/story
        # flag and maxed the magic gauge at once; that was unnecessary for shop
        # validation and could leave PCSX2 in an invalid transient state. Only
        # vanilla rewards that are actually sold in Nativs City are pre-owned.
        player_writes = {
            int(d.get("ADDR_GLOBAL_WOLFEN_COUNT", GLOBAL_FREED_WOLFENS_ADDR)): SHOP_DEMO_WOLFENS,
            int(d["ADDR_MONEY"]): SHOP_DEMO_NOOTIES,
            int(d["ADDR_BOOMY_TYPE"]): SHOP_DEMO_BOOMY_LEVEL,
            int(d["ADDR_BRACELET_BITFIELD"]): SHOP_DEMO_BRACELET_BITS,
            int(d["ADDR_BOARD_LEVEL"]): SHOP_DEMO_BOARD_LEVEL,
            int(d["ITEM_SCENARIO_FLAGS"]["Magic Bouncers"]): 1,
            int(d["ITEM_SCENARIO_FLAGS"]["Climbing Gloves"]): 1,
            int(d["ITEM_SCENARIO_FLAGS"]["Jamgut Birdcall"]): 1,
            int(d["ITEM_SCENARIO_FLAGS"]["Telescope"]): 1,
            # Energy Bars are deliberately NOT pre-owned by forcing Life Gauge.
            # Their vanilla +HP is tested naturally then rolled back to AP authority.
            int(d["ADDR_LIFE_GAUGE"]): SHOP_DEMO_LIFE_TARGET,
        }

        for address, value in player_writes.items():
            pine.write32(address, int(value))

        player = self._ap_player_pointer(pine, d)
        if player is not None:
            max_addr = player + int(d["PLAYER_MAX_HP_OFFSET"])
            hp_addr = player + int(d["PLAYER_HP_OFFSET"])
            pine.write32(max_addr, self._ap_float_to_raw(float(SHOP_DEMO_LIFE_TARGET)))
            hp = self._ap_raw_to_float(pine.read32(hp_addr))
            if hp == hp and 0.0 <= hp < 10000.0 and hp > float(SHOP_DEMO_LIFE_TARGET):
                pine.write32(hp_addr, self._ap_float_to_raw(float(SHOP_DEMO_LIFE_TARGET)))

        # Re-arm every randomized one-shot shop location independently from the
        # inventory. OR-ing the masks preserves unrelated serialized bits.
        shop_conditions = d.get("SHOP_LOCATION_CONDITIONS", {})
        shop_by_addr = {}
        for name, spec in shop_conditions.items():
            address, mask = int(spec[0]), int(spec[1])
            shop_by_addr.setdefault(address, 0)
            shop_by_addr[address] |= mask
        for address, combined_mask in shop_by_addr.items():
            current = int(pine.read32(address))
            pine.write32(address, current | int(combined_mask))

        # Verify the important test values and rebuild the watcher baselines so
        # the preparation writes themselves can never look like shop purchases.
        wolfens = int(pine.read32(int(d.get("ADDR_GLOBAL_WOLFEN_COUNT", GLOBAL_FREED_WOLFENS_ADDR))))
        nooties = int(pine.read32(int(d["ADDR_MONEY"])))

        parsed_shop = {name: (int(spec[0]), int(spec[1])) for name, spec in shop_conditions.items()}
        shop_addrs = sorted({addr for addr, _mask in parsed_shop.values()})
        shop_vals = dict(zip(shop_addrs, pine.read32_many(shop_addrs))) if shop_addrs else {}
        current_shop = {name: bool(shop_vals[addr] & mask) for name, (addr, mask) in parsed_shop.items()}
        armed_count = sum(1 for value in current_shop.values() if value)

        live_rules = d.get("SHOP_LIVE_REWARD_RULES", {})
        live_addrs = sorted({int(spec["address"]) for spec in live_rules.values()})
        live_vals = dict(zip(live_addrs, pine.read32_many(live_addrs))) if live_addrs else {}
        self._ap_shop_live_reward_states = {
            name: int(live_vals[int(spec["address"])]) for name, spec in live_rules.items()
        }
        self._ap_shop_live_baselined = True
        self._ap_shop_states = current_shop
        self._ap_shop_baselined = True
        self._ap_shop_reward_snapshots = {
            name: int(self._ap_shop_live_reward_states[name])
            for name, available in current_shop.items()
            if available and name in self._ap_shop_live_reward_states
        }
        self._ap_shop_purchase_tokens.clear()
        self._ap_shop_ambiguous_token_warned.clear()
        self._ap_shop_group_rolling_states.clear()
        self._ap_shop_group_edge_events.clear()
        self._ap_shop_unpaired_live_hits.clear()
        self._ap_shop_unconfirmed_stock.clear()
        self._ap_pending_shop_suppressions.clear()
        self._ap_pending_special_life_suppressions.clear()
        self._ap_shop_live_ignore_until = time.monotonic() + 1.0

        # Validation probes are re-baselined after the intentional mass write.
        probes = d.get("DEBUG_VALIDATION_PROBES", {})
        probe_addrs = sorted({int(spec["address"]) for spec in probes.values()})
        probe_vals = dict(zip(probe_addrs, pine.read32_many(probe_addrs))) if probe_addrs else {}
        self._ap_validation_probe_states = {
            name: int(probe_vals[int(spec["address"])]) for name, spec in probes.items()
        }
        self._ap_validation_probes_baselined = True

        self._log_threadsafe(
            f"SHOP TEST READY: Wolfens={wolfens}/260, Nooties={nooties} (0x{nooties:04X}), "
            f"shop items=owned (Energy Bars natural), shop stock armed={armed_count}/{len(current_shop)}.",
            "ok" if wolfens == SHOP_DEMO_WOLFENS and nooties == SHOP_DEMO_NOOTIES and armed_count == len(current_shop) else "warn",
        )
        self._log_threadsafe(
            "Ouvre maintenant le shop et achète les 18 entrées une par une. Le mode SAFE ne touche plus aux Runes, au Receptacle, au Blue Egg ni au niveau de magie. "
            "Chaque achat doit produire SHOP STOCK CHECK ou SHOP DUPLICATE CHECK puis un ACK AP.",
            "info",
        )

    def _process_test_actions(self, pine: PineClient) -> None:
        while True:
            try:
                action = self._test_action_queue.get_nowait()
            except queue.Empty:
                return
            try:
                if action.get("kind") == "ft_forensic_toggle":
                    if self._ft_forensic_active:
                        zip_path = self._ft_forensic_finalize(pine, "manual_stop")
                        self._log_threadsafe(
                            f"FT FORENSICS arrêté manuellement -> {zip_path}. Envoie-moi ce ZIP.",
                            "ok",
                        )
                    else:
                        self._ft_forensic_samples = []
                        self._ft_forensic_runtime_logs = []
                        self._ft_forensic_started = time.monotonic()
                        self._ft_forensic_deadline = self._ft_forensic_started + 30.0
                        self._ft_forensic_next_sample = self._ft_forensic_started
                        self._ft_forensic_start_snapshot = self._ft_forensic_static_snapshot(pine, "start")
                        self._ft_forensic_active = True
                        if self._ft_forensic_button is not None:
                            self._post_ui(
                                self._configure_widget,
                                self._ft_forensic_button,
                                text="STOP SCAN",
                                bg="#8a3f67",
                            )
                        self._log_threadsafe(
                            "FT FORENSICS READY • capture READ-ONLY 30s. Utilise maintenant le Fast Travel à tester; "
                            "le ZIP sera créé automatiquement dans ft_scans.",
                            "warn",
                        )
                    continue

                if action.get("kind") == "shop_demo_setup":
                    self._apply_shop_demo_setup(pine)
                    continue
                if action.get("kind") == "zero_mana":
                    d = self._ap_data
                    player = self._ap_player_pointer(pine, d)
                    if player is None:
                        self._log_threadsafe(
                            "DEBUG • 0 MANA impossible : player pointer indisponible.",
                            "error",
                        )
                        continue

                    magic_obj = player + int(d["PLAYER_MAGIC_OBJECT_OFFSET"])
                    current_address = magic_obj + int(d["MAGIC_CURRENT_OFFSET"])
                    max_address = magic_obj + int(d["MAGIC_MAX_OFFSET"])

                    before = self._ap_raw_to_float(pine.read32(current_address))
                    maximum = self._ap_raw_to_float(pine.read32(max_address))

                    if not (0.0 <= before <= maximum <= float(d["MAGIC_MAX_CAP"]) and maximum > 0.0):
                        self._log_threadsafe(
                            f"DEBUG • 0 MANA refusé : valeurs runtime invalides "
                            f"(current={before:g}, max={maximum:g}).",
                            "error",
                        )
                        continue

                    pine.write32(current_address, self._ap_float_to_raw(0.0))
                    verified = self._ap_raw_to_float(pine.read32(current_address))

                    if abs(verified) <= 0.05:
                        self._log_threadsafe(
                            f"DEBUG • 0 MANA OK : {before:g} -> {verified:g} "
                            f"(runtime 0x{current_address:08X}).",
                            "ok",
                        )
                    else:
                        self._log_threadsafe(
                            f"DEBUG • 0 MANA échec readback : {before:g} -> {verified:g}.",
                            "error",
                        )
                    continue
                if action.get("kind") != "snapshot":
                    continue
                blocker = bool(action.get("blocker"))
                item = str(action.get("item") or "Unknown")
                data = self._scan_runtime_state(pine)
                grant_result = self._manual_test_grant(pine, item) if bool(action.get("grant")) else None
                self._write_test_snapshot(data, blocker, item, grant_result)
                ft_text = ", ".join(f"{x['key']}={x['state']}" for x in data["actors"].get("fast_travels", [])) or "aucun"
                if blocker:
                    self._log_threadsafe(
                        f"TEST BLOCKAGE enregistré : {data['global_freed_wolfens']} Wolfens/Nativs, zone={data['zone']}, besoin={item}. FT: {ft_text}",
                        "warn",
                    )
                    if grant_result is not None:
                        address, before, after = grant_result
                        self._log_threadsafe(f"TEST GRANT manuel : {item} @0x{address:08X} {before}->{after}", "ok")
                else:
                    self._log_threadsafe(
                        f"SCAN COMPLET enregistré : {data['global_freed_wolfens']} Wolfens/Nativs, zone={data['zone']}. FT: {ft_text}",
                        "info",
                    )
            except Exception as exc:
                self._log_threadsafe(f"Progression scanner failed: {type(exc).__name__}: {exc}", "error")

    def _entry(self, variable: tk.StringVar, x: int, y: int, width: int, show: str | None = None) -> tk.Entry:
        entry = tk.Entry(
            self,
            textvariable=variable,
            font=("Segoe UI", 11),
            fg=TEXT_MAIN,
            bg=ENTRY_BG,
            insertbackground="white",
            selectbackground="#47627a",
            selectforeground="white",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=ENTRY_BORDER,
            highlightcolor="#8193a1",
            show=show or "",
        )
        entry.place(x=x, y=y, width=width, height=40)
        return entry

    def _build_status_row(self, left: int, y: int, width: int) -> None:
        specs = [
            ("pine", "status_pine"),
            ("server", "status_server"),
            ("game", "status_game"),
        ]
        col_w = width / 3
        for i, (key, tr_key) in enumerate(specs):
            base_x = left + int(i * col_w)
            dot = self.canvas.create_oval(
                base_x + 8,
                y + 13,
                base_x + 25,
                y + 30,
                fill=STATUS_COLORS["disconnected"],
                outline="",
            )
            title_id = self.canvas.create_text(
                base_x + 36,
                y + 8,
                text=self.tr[tr_key],
                anchor="nw",
                fill=TEXT_MAIN,
                font=("Segoe UI Semibold", 9),
            )
            state_text = self.canvas.create_text(
                base_x + 36,
                y + 34,
                text=self.tr["disconnected"],
                anchor="nw",
                fill=TEXT_SUB,
                font=("Segoe UI", 8),
            )
            self.status_widgets[key] = (dot, title_id, state_text)

    def _set_status(self, key: str, state: str, text: str | None = None) -> None:
        dot, _title_id, state_text = self.status_widgets[key]
        self.canvas.itemconfigure(dot, fill=STATUS_COLORS[state])
        if text is None:
            text = {
                "disconnected": self.tr["disconnected"],
                "connecting": self.tr["connecting_status"],
                "busy": self.tr["pine_busy_state"],
                "connected": self.tr["connected"],
            }[state]
        self.canvas.itemconfigure(state_text, text=text)

    def _build_log(self, left: int, y: int, width: int) -> None:
        self.log_label_id = self._canvas_label(self.tr["log"], left, y)

        self.clear_button = tk.Button(
            self,
            text=self.tr["clear"],
            command=self._clear_log,
            font=("Segoe UI", 8),
            fg="#b7d8ef",
            bg="#11161b",
            activebackground="#1a252e",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
        )
        self.clear_button.place(x=left + width - 58, y=y - 4, width=58, height=26)

        self.log_text = tk.Text(
            self,
            font=("Consolas", 9),
            fg="#dce7ed",
            bg=LOG_BG,
            insertbackground="white",
            relief="flat",
            bd=0,
            wrap="word",
            state="disabled",
            padx=10,
            pady=8,
            highlightthickness=1,
            highlightbackground="#41505b",
        )
        self.log_text.place(x=left, y=y + 28, width=width, height=106)
        self.log_text.tag_configure("ok", foreground="#71ed90")
        self.log_text.tag_configure("warn", foreground="#f4b45e")
        self.log_text.tag_configure("error", foreground="#f57a7a")
        self.log_text.tag_configure("info", foreground="#dce7ed")
        self._log(self.tr["launcher_ready"])

    def _clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _log(self, message: str, tag: str = "info") -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _log_threadsafe(self, message: str, tag: str = "info") -> None:
        if self._ft_forensic_active:
            try:
                with self._ft_forensic_lock:
                    self._ft_forensic_runtime_logs.append({
                        "t_ms": int((time.monotonic() - self._ft_forensic_started) * 1000.0),
                        "clock": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "tag": str(tag),
                        "message": str(message),
                    })
            except Exception:
                pass
        self._post_ui(self._log, message, tag)

    def _set_busy(self, busy: bool) -> None:
        self.connect_button.configure(
            state=("disabled" if busy else "normal"),
            text=(self.tr["connecting"] if busy else self.tr["connect"]),
            bg=("#5b646c" if busy else BUTTON_GREEN),
        )

    # ------------------------------------------------------------------
    # Options / language / camera UI
    # ------------------------------------------------------------------
    def _open_options(self) -> None:
        if self.options_window is not None:
            try:
                if self.options_window.winfo_exists():
                    self.options_window.lift()
                    self.options_window.focus_force()
                    return
            except tk.TclError:
                pass

        win = tk.Toplevel(self)
        self.options_window = win
        win.withdraw()
        win.title(f"{APP_TITLE} - {self.tr['options']}")
        # The old 790px options dialog left ~250px of unused background
        # after removal of the three debug controls in 0.9.62.
        # Final size is fitted to content after all controls are created.
        win.geometry("520x790")
        win.resizable(False, False)
        # Do not make this window transient: Windows hides transient/owned
        # borderless windows from Alt+Tab and the taskbar.
        win.configure(bg="#111820")
        win.overrideredirect(True)

        # Center the borderless options window over the launcher.
        self.update_idletasks()
        x = self.winfo_x() + max(0, (self.winfo_width() - 520) // 2)
        y = max(0, self.winfo_y() + (self.winfo_height() - 790) // 2)
        win.geometry(f"520x790+{x}+{y}")

        icon = resource_path("Icon.ico")
        if icon.exists():
            try:
                win.iconbitmap(default=str(icon))
            except tk.TclError:
                pass

        self.options_widgets = {}

        def close_options() -> None:
            try:
                win.destroy()
            finally:
                self.options_window = None

        # Custom dark title bar: removes the white Windows bar completely.
        titlebar = tk.Frame(win, bg="#0b1117", height=42)
        titlebar.pack(fill="x", side="top")
        titlebar.pack_propagate(False)

        title = tk.Label(
            titlebar,
            text=f"⚙  {self.tr['options']}",
            bg="#0b1117",
            fg="white",
            font=("Segoe UI Semibold", 12),
            anchor="w",
            padx=14,
        )
        title.pack(side="left", fill="both", expand=True)

        close_top = tk.Button(
            titlebar,
            text="×",
            command=close_options,
            font=("Segoe UI Semibold", 23),
            fg="white",
            bg="#0b1117",
            activebackground="#8f2020",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            width=3,
        )
        close_top.pack(side="right", fill="y")

        drag_state = {"x": 0, "y": 0}

        def start_drag(event):
            drag_state["x"] = event.x_root - win.winfo_x()
            drag_state["y"] = event.y_root - win.winfo_y()

        def do_drag(event):
            win.geometry(
                f"+{event.x_root - drag_state['x']}+{event.y_root - drag_state['y']}"
            )

        for widget in (titlebar, title):
            widget.bind("<ButtonPress-1>", start_drag)
            widget.bind("<B1-Motion>", do_drag)

        self.options_widgets["title"] = title

        content = tk.Frame(win, bg="#111820")
        content.pack(fill="both", expand=True, padx=0, pady=0)

        lang_frame = tk.LabelFrame(
            content,
            text=self.tr["language"],
            bg="#111820",
            fg="#e8eef3",
            font=("Segoe UI Semibold", 10),
            bd=1,
            relief="groove",
            padx=12,
            pady=10,
        )
        lang_frame.pack(fill="x", padx=22, pady=(18, 16))
        self.options_widgets["lang_frame"] = lang_frame

        lang_buttons = {}
        for code, flag, name in LANGUAGES:
            btn = tk.Button(
                lang_frame,
                text=f"{flag}  {name}",
                command=lambda c=code: self._set_language(c),
                font=("Segoe UI Emoji", 9),
                fg="white",
                bg=("#2e6b4d" if code == self.language else "#1a2530"),
                activebackground="#2f4354",
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=8,
                pady=6,
            )
            btn.pack(side="left", expand=True, fill="x", padx=3)
            lang_buttons[code] = btn
        self.options_widgets["lang_buttons"] = lang_buttons

        overlay_frame = tk.LabelFrame(
            content,
            text=self.tr["overlay_title"],
            bg="#111820",
            fg="#e8eef3",
            font=("Segoe UI Semibold", 10),
            bd=1,
            relief="groove",
            padx=12,
            pady=10,
        )
        overlay_frame.pack(fill="x", padx=22, pady=(0, 16))
        self.options_widgets["overlay_frame"] = overlay_frame

        overlay_toggle_btn = tk.Button(
            overlay_frame,
            text=self.tr["overlay_on"] if self.overlay_enabled else self.tr["overlay_off"],
            command=self._toggle_archipelago_overlay,
            font=("Segoe UI Semibold", 10),
            fg="white",
            bg=("#2e6b4d" if self.overlay_enabled else "#2a3945"),
            activebackground="#3a5060",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            pady=7,
        )
        overlay_toggle_btn.pack(fill="x", pady=(0, 7))
        self.options_widgets["overlay_toggle_btn"] = overlay_toggle_btn

        overlay_test_btn = tk.Button(
            overlay_frame,
            text=self.tr["overlay_test"],
            command=self._send_overlay_test,
            font=("Segoe UI Semibold", 9),
            fg="white",
            bg="#2a3945",
            activebackground="#3a5060",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            pady=6,
        )
        overlay_test_btn.pack(fill="x")
        self.options_widgets["overlay_test_btn"] = overlay_test_btn

        overlay_note = tk.Label(
            overlay_frame,
            text=self.tr["overlay_note"],
            bg="#111820",
            fg="#9fb0bd",
            font=("Segoe UI", 8),
            anchor="w",
            justify="left",
            wraplength=445,
        )
        overlay_note.pack(fill="x", pady=(8, 0))
        self.options_widgets["overlay_note"] = overlay_note

        camera_frame = tk.LabelFrame(
            content,
            text=self.tr["camera"],
            bg="#111820",
            fg="#e8eef3",
            font=("Segoe UI Semibold", 10),
            bd=1,
            relief="groove",
            padx=14,
            pady=12,
        )
        camera_frame.pack(fill="x", padx=22, pady=(0, 16))
        self.options_widgets["camera_frame"] = camera_frame

        self._opt_horizontal_var = tk.StringVar(value=self.camera_horizontal)
        self._opt_vertical_var = tk.StringVar(value=self.camera_vertical)

        h_label = tk.Label(
            camera_frame,
            text=self.tr["horizontal_camera"],
            bg="#111820",
            fg="white",
            font=("Segoe UI Semibold", 10),
            width=22,
            anchor="w",
        )
        h_label.grid(row=0, column=0, sticky="w", pady=6)
        self.options_widgets["h_label"] = h_label

        h_van = tk.Radiobutton(
            camera_frame,
            text=self.tr["vanilla"],
            variable=self._opt_horizontal_var,
            value="vanilla",
            command=self._camera_option_changed,
            bg="#111820",
            fg="white",
            selectcolor="#1a2530",
            activebackground="#111820",
            activeforeground="white",
            font=("Segoe UI", 10),
        )
        h_van.grid(row=0, column=1, padx=(10, 16))
        self.options_widgets["h_van"] = h_van

        h_inv = tk.Radiobutton(
            camera_frame,
            text=self.tr["inverted"],
            variable=self._opt_horizontal_var,
            value="inverted",
            command=self._camera_option_changed,
            bg="#111820",
            fg="white",
            selectcolor="#1a2530",
            activebackground="#111820",
            activeforeground="white",
            font=("Segoe UI", 10),
        )
        h_inv.grid(row=0, column=2)
        self.options_widgets["h_inv"] = h_inv

        v_label = tk.Label(
            camera_frame,
            text=self.tr["vertical_camera"],
            bg="#111820",
            fg="white",
            font=("Segoe UI Semibold", 10),
            width=22,
            anchor="w",
        )
        v_label.grid(row=1, column=0, sticky="w", pady=6)
        self.options_widgets["v_label"] = v_label

        v_van = tk.Radiobutton(
            camera_frame,
            text=self.tr["vanilla"],
            variable=self._opt_vertical_var,
            value="vanilla",
            command=self._camera_option_changed,
            bg="#111820",
            fg="white",
            selectcolor="#1a2530",
            activebackground="#111820",
            activeforeground="white",
            font=("Segoe UI", 10),
        )
        v_van.grid(row=1, column=1, padx=(10, 16))
        self.options_widgets["v_van"] = v_van

        v_inv = tk.Radiobutton(
            camera_frame,
            text=self.tr["inverted"],
            variable=self._opt_vertical_var,
            value="inverted",
            command=self._camera_option_changed,
            bg="#111820",
            fg="white",
            selectcolor="#1a2530",
            activebackground="#111820",
            activeforeground="white",
            font=("Segoe UI", 10),
        )
        v_inv.grid(row=1, column=2)
        self.options_widgets["v_inv"] = v_inv

        note = tk.Label(
            content,
            text=self.tr["camera_note"],
            bg="#111820",
            fg="#bfcbd4",
            font=("Segoe UI", 9),
            wraplength=460,
            justify="left",
        )
        note.pack(fill="x", padx=28, pady=(0, 18))
        self.options_widgets["note"] = note

        # 0.9.62: beta Options contains player-facing settings only.
        # ISO compatibility check, manual credits and shop audit are no longer exposed.

        close_btn = tk.Button(
            content,
            text=self.tr["close"],
            command=close_options,
            font=("Segoe UI Semibold", 10),
            fg="white",
            bg="#2a3945",
            activebackground="#3a5060",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        close_btn.pack(fill="x", padx=80, pady=(0, 18))
        self.options_widgets["close_btn"] = close_btn

        # Size the window to the actual contents; extra free vertical space
        # must not remain below Close. Use requested widget heights so this
        # also adapts to a translated text wrapping onto another line.
        win.update_idletasks()
        desired_h = max(480, min(740,
            titlebar.winfo_reqheight() + content.winfo_reqheight() + 6))
        new_x = self.winfo_x() + max(0, (self.winfo_width() - 520) // 2)
        new_y = max(0, self.winfo_y() + (self.winfo_height() - desired_h) // 2)
        win.geometry(f"520x{desired_h}+{new_x}+{new_y}")

        win.bind("<Escape>", lambda _e: close_options())
        win.protocol("WM_DELETE_WINDOW", close_options)
        win.deiconify()
        win.update_idletasks()
        self._ensure_aux_window_taskbar_presence(win)
        self.after(150, lambda: self._ensure_aux_window_taskbar_presence(win) if win.winfo_exists() else None)
        win.lift()
        win.focus_force()

    # ------------------------------------------------------------------
    # Archipelago trade overlay
    # ------------------------------------------------------------------
    def _refresh_overlay_options_button(self) -> None:
        button = self.options_widgets.get("overlay_toggle_btn")
        if button is None:
            return
        try:
            button.configure(
                text=self.tr["overlay_on"] if self.overlay_enabled else self.tr["overlay_off"],
                bg=("#2e6b4d" if self.overlay_enabled else "#2a3945"),
            )
        except tk.TclError:
            pass

    def _toggle_archipelago_overlay(self) -> None:
        self.overlay_enabled = not self.overlay_enabled
        self._update_cfg(overlay_enabled=self.overlay_enabled)
        self._refresh_overlay_options_button()
        if self.overlay_enabled:
            self._overlay_ensure_window()
            self._overlay_render()
        else:
            self._overlay_messages.clear()
            try:
                if self._overlay_window is not None and self._overlay_window.winfo_exists():
                    self._overlay_window.withdraw()
            except tk.TclError:
                pass

    def _send_overlay_test(self) -> None:
        # Development helper: generate a short burst so the queue/scroll/fade
        # behaviour can be checked without a live multiworld trade burst.
        if not self.overlay_enabled:
            self.overlay_enabled = True
            self._update_cfg(overlay_enabled=True)
            self._refresh_overlay_options_button()

        samples = [
            (self.tr["overlay_test_in"], "incoming"),
            (self.tr["overlay_test_out"], "outgoing"),
            ("TEST • TestPlayer vous envoie Progressive Board", "incoming"),
            ("TEST • TestPlayer vous envoie +5% Attack", "incoming"),
            ("TEST • TestPlayer vous envoie Magic Restore +50", "incoming"),
        ]
        for index, (message, kind) in enumerate(samples):
            self.after(index * 260, lambda m=message, k=kind: self._overlay_notify(m, k, duration=6.0))

    def _overlay_notify_threadsafe(self, text: str, kind: str = "trade", duration: float = 7.0) -> None:
        self._post_ui(self._overlay_notify, text, kind, duration)

    def _overlay_start_fade(self, message: dict, now: float, *, slide_out: bool = False) -> None:
        if message.get("fade_start") is not None:
            return
        message["fade_start"] = now
        message["fade_duration"] = 0.48
        message["slide_out"] = bool(slide_out)
        if slide_out:
            current_y = message.get("y")
            if current_y is not None:
                message["fade_target_y"] = float(current_y) - 76.0

    def _overlay_notify(self, text: str, kind: str = "trade", duration: float = 7.0) -> None:
        if not self.overlay_enabled:
            return
        raw = str(text).replace("\r", "\n")
        clean_lines = [" ".join(line.split()) for line in raw.split("\n") if line.strip()]
        clean = "\n".join(clean_lines)
        if not clean:
            return
        now = time.monotonic()
        message = {
            "text": clean,
            "kind": kind,
            "created": now,
            "expires": now + max(1.0, float(duration)),
            "fade_start": None,
            "fade_duration": 0.48,
            "slide_out": False,
            "y": None,
        }
        self._overlay_messages.append(message)

        # Four active cards maximum.  A fifth message does not pop the oldest
        # instantly: it pushes the stack upward while the oldest card fades out.
        active = [m for m in self._overlay_messages if m.get("fade_start") is None]
        while len(active) > 4:
            victim = active.pop(0)
            self._overlay_start_fade(victim, now, slide_out=True)

        # Keep only a small animation backlog during very large item bursts.
        if len(self._overlay_messages) > 10:
            fading = [m for m in self._overlay_messages if m.get("fade_start") is not None]
            while len(self._overlay_messages) > 10 and fading:
                victim = fading.pop(0)
                if victim in self._overlay_messages:
                    self._overlay_messages.remove(victim)

        self._overlay_ensure_window()
        self._overlay_render()

    def _handle_ap_printjson_overlay(self, packet: dict, text: str) -> None:
        # Resolve AP numeric PrintJSON nodes locally. Custom clients may receive
        # raw IDs (e.g. "51473018 (51474011)") even though the semantic item
        # packet contains the real item/location IDs.
        if not self.overlay_enabled or packet.get("type") not in {"ItemSend", "ItemCheat"}:
            return
        receiving = packet.get("receiving")
        kind = "trade"
        try:
            if self._ap_slot_id is not None and int(receiving) == int(self._ap_slot_id):
                kind = "incoming"
            elif receiving is not None:
                kind = "outgoing"
        except (TypeError, ValueError):
            pass

        item_id = None
        location_id = None
        semantic = packet.get("item")
        if isinstance(semantic, dict):
            item_id = semantic.get("item")
            location_id = semantic.get("location")
        if item_id is None or location_id is None:
            for part in packet.get("data", []):
                if not isinstance(part, dict):
                    continue
                ptype = part.get("type")
                if ptype == "item_id" and item_id is None:
                    item_id = part.get("item", part.get("text"))
                elif ptype == "location_id" and location_id is None:
                    location_id = part.get("location", part.get("text"))
        try:
            item_id = int(item_id)
        except (TypeError, ValueError):
            item_id = None
        try:
            location_id = int(location_id)
        except (TypeError, ValueError):
            location_id = None

        # Incoming items are rendered only from ReceivedItems in _apply_ap_item.
        # PrintJSON is retained for outgoing trades only.
        if kind == "incoming":
            return
        resolved = text
        if item_id is not None:
            item_name = self._ap_items.get(item_id, f"Item {item_id}")
            id_to_location = {int(v): k for k, v in self._ap_data.get("LOCATION_NAME_TO_ID", {}).items()}
            location_name = id_to_location.get(location_id, f"Location {location_id}" if location_id is not None else "Unknown location")
            location_name = self._ap_public_location_name(location_name)
            slot_name = self.name_var.get().strip() or "Kya"
            if kind == "incoming":
                resolved = f"{slot_name} found their {item_name} ({location_name})"
            elif kind == "outgoing":
                resolved = f"{slot_name} sent {item_name} ({location_name})"
            else:
                resolved = f"{item_name} ({location_name})"
        self._overlay_notify_threadsafe(resolved, kind, 7.0)

    def _overlay_ensure_window(self) -> None:
        if self._closing or not self.overlay_enabled:
            return
        try:
            if self._overlay_window is not None and self._overlay_window.winfo_exists():
                return
        except tk.TclError:
            pass

        win = tk.Toplevel(self)
        self._overlay_window = win
        win.withdraw()
        win.overrideredirect(True)
        win.configure(bg="#010203")
        try:
            win.attributes("-topmost", True)
            if sys.platform == "win32":
                win.wm_attributes("-transparentcolor", "#010203")
        except tk.TclError:
            pass

        canvas = tk.Canvas(
            win,
            width=500,
            height=320,
            bg="#010203",
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)
        self._overlay_canvas = canvas
        win.update_idletasks()
        self._overlay_make_clickthrough()

    def _overlay_make_clickthrough(self) -> None:
        if sys.platform != "win32" or self._overlay_window is None:
            return
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.WinDLL("user32", use_last_error=True)
            hwnd = wintypes.HWND(self._overlay_window.winfo_id())
            user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
            user32.GetAncestor.restype = wintypes.HWND
            root_hwnd = user32.GetAncestor(hwnd, 2)  # GA_ROOT
            if root_hwnd:
                hwnd = root_hwnd

            get_long = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
            set_long = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
            long_type = ctypes.c_ssize_t if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long
            get_long.argtypes = [wintypes.HWND, ctypes.c_int]
            get_long.restype = long_type
            set_long.argtypes = [wintypes.HWND, ctypes.c_int, long_type]
            set_long.restype = long_type

            # Keep the overlay independent from the Launcher.  Owned windows can
            # be forced behind a borderless/fullscreen PCSX2 render window.
            GWLP_HWNDPARENT = -8
            set_long(hwnd, GWLP_HWNDPARENT, long_type(0))

            GWL_EXSTYLE = -20
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_LAYERED = 0x00080000
            WS_EX_NOACTIVATE = 0x08000000
            style = int(get_long(hwnd, GWL_EXSTYLE))
            style |= WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_LAYERED | WS_EX_NOACTIVATE
            style &= ~0x00040000  # WS_EX_APPWINDOW: never show overlay in taskbar/Alt+Tab.
            set_long(hwnd, GWL_EXSTYLE, long_type(style))
            self._overlay_force_topmost()
        except (AttributeError, OSError, tk.TclError):
            pass

    def _overlay_force_topmost(self) -> None:
        """Keep the click-through overlay above the active windowed PCSX2 window without activation."""
        if sys.platform != "win32" or self._overlay_window is None:
            return
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.WinDLL("user32", use_last_error=True)
            hwnd = wintypes.HWND(self._overlay_window.winfo_id())
            user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
            user32.GetAncestor.restype = wintypes.HWND
            root_hwnd = user32.GetAncestor(hwnd, 2)
            if root_hwnd:
                hwnd = root_hwnd

            user32.SetWindowPos.argtypes = [
                wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                ctypes.c_int, ctypes.c_int, wintypes.UINT,
            ]
            user32.SetWindowPos.restype = wintypes.BOOL
            user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
            user32.ShowWindow.restype = wintypes.BOOL
            HWND_TOPMOST = wintypes.HWND(-1)
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040
            SW_SHOWNOACTIVATE = 4
            user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
            )
            user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
        except (AttributeError, OSError, tk.TclError):
            pass

    def _overlay_find_pcsx2_rect(self) -> tuple[int, int, int, int] | None:
        if sys.platform != "win32":
            return None
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.WinDLL("user32", use_last_error=True)
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

            user32.IsWindow.argtypes = [wintypes.HWND]
            user32.IsWindow.restype = wintypes.BOOL
            user32.IsWindowVisible.argtypes = [wintypes.HWND]
            user32.IsWindowVisible.restype = wintypes.BOOL
            user32.IsIconic.argtypes = [wintypes.HWND]
            user32.IsIconic.restype = wintypes.BOOL
            user32.GetForegroundWindow.restype = wintypes.HWND
            user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
            user32.GetWindowThreadProcessId.restype = wintypes.DWORD
            user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
            user32.GetWindowTextLengthW.restype = ctypes.c_int
            user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
            user32.GetWindowTextW.restype = ctypes.c_int
            user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
            user32.GetWindowRect.restype = wintypes.BOOL
            user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
            user32.GetClientRect.restype = wintypes.BOOL
            user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
            user32.ClientToScreen.restype = wintypes.BOOL
            kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
            kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL

            def hwnd_int(hwnd) -> int:
                return int(hwnd) if isinstance(hwnd, int) else int(hwnd.value or 0)

            def pid_for(hwnd) -> int:
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                return int(pid.value)

            def process_name_for_pid(pid: int) -> str:
                handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
                if not handle:
                    return ""
                try:
                    size = wintypes.DWORD(1024)
                    buf = ctypes.create_unicode_buffer(size.value)
                    if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
                        return Path(buf.value).name.lower()
                finally:
                    kernel32.CloseHandle(handle)
                return ""

            def is_pcsx2(hwnd) -> tuple[bool, int]:
                if not hwnd or not user32.IsWindow(hwnd):
                    return False, 0
                pid = pid_for(hwnd)
                if self._overlay_pcsx2_pid is not None and pid == self._overlay_pcsx2_pid:
                    return True, pid
                name = process_name_for_pid(pid)
                return name.startswith("pcsx2"), pid

            def rect_for(hwnd) -> tuple[int, int, int, int] | None:
                if not hwnd or not user32.IsWindow(hwnd) or user32.IsIconic(hwnd):
                    return None
                client = wintypes.RECT()
                if user32.GetClientRect(hwnd, ctypes.byref(client)):
                    tl = wintypes.POINT(client.left, client.top)
                    br = wintypes.POINT(client.right, client.bottom)
                    if user32.ClientToScreen(hwnd, ctypes.byref(tl)) and user32.ClientToScreen(hwnd, ctypes.byref(br)):
                        if br.x > tl.x and br.y > tl.y:
                            return (int(tl.x), int(tl.y), int(br.x), int(br.y))
                rect = wintypes.RECT()
                if user32.GetWindowRect(hwnd, ctypes.byref(rect)) and rect.right > rect.left and rect.bottom > rect.top:
                    return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
                return None

            # When PCSX2 is foreground, use that HWND immediately.  PCSX2 may
            # switch to a different top-level render window when entering fullscreen.
            foreground = user32.GetForegroundWindow()
            ok, pid = is_pcsx2(foreground)
            if ok:
                fg_rect = rect_for(foreground)
                if fg_rect is not None:
                    self._overlay_pcsx2_hwnd = hwnd_int(foreground)
                    self._overlay_pcsx2_pid = pid
                    return fg_rect

            now = time.monotonic()
            cached = wintypes.HWND(self._overlay_pcsx2_hwnd or 0)
            if self._overlay_pcsx2_hwnd and now < self._overlay_next_window_scan:
                cached_rect = rect_for(cached)
                if cached_rect is not None:
                    return cached_rect

            # Re-enumerate periodically so windowed <-> fullscreen switches are
            # detected quickly, while normal window dragging uses the cached HWND
            # and can be tracked every frame without an expensive EnumWindows call.
            self._overlay_next_window_scan = now + 0.20
            candidates: list[tuple[int, int, int]] = []
            EnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            user32.EnumWindows.argtypes = [EnumProc, wintypes.LPARAM]
            user32.EnumWindows.restype = wintypes.BOOL

            @EnumProc
            def enum_cb(hwnd, _lparam):
                if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
                    return True
                pid = pid_for(hwnd)
                if self._overlay_pcsx2_pid is not None and pid == self._overlay_pcsx2_pid:
                    matches = True
                else:
                    title_len = user32.GetWindowTextLengthW(hwnd)
                    title_buf = ctypes.create_unicode_buffer(title_len + 1)
                    user32.GetWindowTextW(hwnd, title_buf, title_len + 1)
                    title = title_buf.value.lower()
                    matches = process_name_for_pid(pid).startswith("pcsx2") or "pcsx2" in title
                if not matches:
                    return True
                rect = wintypes.RECT()
                if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                    return True
                area = max(0, rect.right - rect.left) * max(0, rect.bottom - rect.top)
                if area > 0:
                    candidates.append((area, hwnd_int(hwnd), pid))
                return True

            user32.EnumWindows(enum_cb, 0)
            if candidates:
                _, best_hwnd, best_pid = max(candidates, key=lambda item: item[0])
                self._overlay_pcsx2_hwnd = best_hwnd
                self._overlay_pcsx2_pid = best_pid
                best_rect = rect_for(wintypes.HWND(best_hwnd))
                if best_rect is not None:
                    return best_rect

            # Last chance: keep using the cached PCSX2 window if enumeration
            # briefly misses it during a fullscreen transition.
            cached_rect = rect_for(cached) if self._overlay_pcsx2_hwnd else None
            if cached_rect is not None:
                return cached_rect
        except (AttributeError, OSError):
            return None
        return None

    def _overlay_target_is_fullscreen(self, rect: tuple[int, int, int, int]) -> bool:
        """Return True when the selected PCSX2 window essentially covers its monitor.

        External topmost overlays can steal the visible foreground relationship from
        PCSX2 in this mode, so the legacy implementation deliberately does not show the overlay there.
        """
        if sys.platform != "win32" or not self._overlay_pcsx2_hwnd:
            return False
        try:
            import ctypes
            from ctypes import wintypes

            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT),
                    ("dwFlags", wintypes.DWORD),
                ]

            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
            user32.MonitorFromWindow.restype = wintypes.HANDLE
            user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFO)]
            user32.GetMonitorInfoW.restype = wintypes.BOOL
            monitor = user32.MonitorFromWindow(wintypes.HWND(int(self._overlay_pcsx2_hwnd)), 2)
            if not monitor:
                return False
            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(MONITORINFO)
            if not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
                return False

            left, top, right, bottom = rect
            ml, mt, mr, mb = info.rcMonitor.left, info.rcMonitor.top, info.rcMonitor.right, info.rcMonitor.bottom
            tolerance = 3
            exact_cover = (
                abs(left - ml) <= tolerance and abs(top - mt) <= tolerance and
                abs(right - mr) <= tolerance and abs(bottom - mb) <= tolerance
            )
            window_area = max(0, right - left) * max(0, bottom - top)
            monitor_area = max(1, mr - ml) * max(1, mb - mt)
            near_cover = window_area / monitor_area >= 0.985 and left <= ml + tolerance and top <= mt + tolerance
            return bool(exact_cover or near_cover)
        except (AttributeError, OSError, ValueError):
            return False

    def _overlay_pcsx2_is_foreground(self) -> bool:
        """Only draw over PCSX2 itself, never over another application."""
        if sys.platform != "win32" or not self._overlay_pcsx2_pid:
            return True
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.GetForegroundWindow.restype = wintypes.HWND
            user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
            user32.GetWindowThreadProcessId.restype = wintypes.DWORD
            foreground = user32.GetForegroundWindow()
            if not foreground:
                return False
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(foreground, ctypes.byref(pid))
            return int(pid.value) == int(self._overlay_pcsx2_pid)
        except (AttributeError, OSError, ValueError):
            return True

    def _overlay_position(self) -> bool:
        if self._overlay_window is None:
            return False
        rect = self._overlay_find_pcsx2_rect()
        if rect is None:
            try:
                self._overlay_window.withdraw()
            except tk.TclError:
                pass
            return False

        self._overlay_last_rect = rect

        # No overlay in PCSX2 fullscreen.  This avoids the fullscreen z-order
        # behaviour that looked like an Alt+Tab and could take the game out of
        # its normal foreground state.
        if self._overlay_target_is_fullscreen(rect) or not self._overlay_pcsx2_is_foreground():
            try:
                self._overlay_window.withdraw()
            except tk.TclError:
                pass
            return False

        left, top, right, bottom = rect
        width, height = 500, 372
        margin = 18
        x = min(max(left + margin, left + 4), max(left + 4, right - width - 4))
        y = max(top + 4, bottom - height - margin)
        try:
            self._overlay_window.geometry(f"{width}x{height}+{x}+{y}")
            self._overlay_window.attributes("-topmost", True)
            return True
        except tk.TclError:
            return False

    @staticmethod
    def _overlay_round_rect(canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, radius: int, **kwargs):
        r = max(2, min(radius, (x2 - x1) // 2, (y2 - y1) // 2))
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, splinesteps=18, **kwargs)

    @staticmethod
    def _overlay_blend_color(color: str, alpha: float, background: str = "#010203") -> str:
        alpha = max(0.0, min(1.0, float(alpha)))
        try:
            c = color.lstrip("#")
            b = background.lstrip("#")
            cr, cg, cb = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
            br, bg, bb = int(b[0:2], 16), int(b[2:4], 16), int(b[4:6], 16)
            r = round(br + (cr - br) * alpha)
            g = round(bg + (cg - bg) * alpha)
            bl = round(bb + (cb - bb) * alpha)
            return f"#{r:02x}{g:02x}{bl:02x}"
        except (ValueError, IndexError):
            return color

    def _overlay_update_animation_state(self, now: float) -> None:
        # Start timed fades instead of removing cards instantly.
        for message in list(self._overlay_messages):
            if message.get("fade_start") is None and now >= float(message.get("expires", now + 1.0)):
                self._overlay_start_fade(message, now, slide_out=False)

        # Purge cards only once their fade animation is complete.
        kept = []
        for message in self._overlay_messages:
            fade_start = message.get("fade_start")
            if fade_start is None:
                kept.append(message)
                continue
            fade_duration = max(0.05, float(message.get("fade_duration", 0.48)))
            if now - float(fade_start) < fade_duration:
                kept.append(message)
        self._overlay_messages = kept

    def _overlay_render(self) -> None:
        if not self.overlay_enabled:
            return
        self._overlay_ensure_window()
        canvas = self._overlay_canvas
        win = self._overlay_window
        if canvas is None or win is None:
            return

        now = time.monotonic()
        self._overlay_update_animation_state(now)
        if not self._overlay_messages:
            try:
                win.withdraw()
            except tk.TclError:
                pass
            return

        if not self._overlay_position():
            return

        canvas.delete("all")
        card_h = 82
        gap = 7
        step = card_h + gap
        bottom = 364

        active = [m for m in self._overlay_messages if m.get("fade_start") is None][-4:]
        active_targets: dict[int, float] = {}
        count = len(active)
        first_slot = 4 - count
        for index, message in enumerate(active):
            slot = first_slot + index
            target_y = float(bottom - (3 - slot) * step - card_h)
            active_targets[id(message)] = target_y
            if message.get("y") is None:
                # New cards enter from below the stack and slide into place.
                message["y"] = target_y + step

        draw_order = list(self._overlay_messages)
        for message in draw_order:
            fade_start = message.get("fade_start")
            if fade_start is None:
                target_y = active_targets.get(id(message))
                if target_y is None:
                    continue
                current_y = float(message.get("y", target_y))
                current_y += (target_y - current_y) * 0.28
                if abs(target_y - current_y) < 0.4:
                    current_y = target_y
                message["y"] = current_y
                age = max(0.0, now - float(message.get("created", now)))
                alpha = min(1.0, age / 0.20)
            else:
                fade_duration = max(0.05, float(message.get("fade_duration", 0.48)))
                progress = max(0.0, min(1.0, (now - float(fade_start)) / fade_duration))
                alpha = 1.0 - progress
                current_y = float(message.get("y") if message.get("y") is not None else 8.0)
                if message.get("slide_out"):
                    target_y = float(message.get("fade_target_y", current_y - step))
                    current_y += (target_y - current_y) * 0.22
                    message["y"] = current_y

            if alpha <= 0.01:
                continue

            y1 = int(round(float(message.get("y", 8.0))))
            y2 = y1 + card_h
            kind = str(message.get("kind", "trade"))
            accent_base = {
                "incoming": "#63d68b",
                "outgoing": "#75b8ff",
                "test": "#f0c765",
            }.get(kind, "#b9c7d2")
            fill = self._overlay_blend_color("#0e1720", alpha)
            outline = self._overlay_blend_color("#334754", alpha)
            accent = self._overlay_blend_color(accent_base, alpha)
            primary = self._overlay_blend_color("#f7fafc", alpha)

            self._overlay_round_rect(
                canvas, 8, y1, 492, y2, 12,
                fill=fill, outline=outline, width=1,
            )
            canvas.create_rectangle(8, y1+8, 13, y2-8, fill=accent, outline="")
            canvas.create_text(
                27, y1+12, text=str(message["text"]), anchor="nw",
                fill=primary, font=("Segoe UI Semibold", 11), width=448,
                justify="left",
            )

        try:
            # WS_EX_NOACTIVATE is applied when the window is created.  Do not use
            # lift()/focus_force() here: the game must remain the foreground app.
            win.deiconify()
            win.attributes("-topmost", True)
            self._overlay_force_topmost()
        except tk.TclError:
            pass

    def _overlay_tick(self) -> None:
        self._overlay_after_id = None
        if self._closing:
            return
        if self.overlay_enabled:
            if self._overlay_messages:
                # Redraw at ~60 Hz: this drives the slide/fade animation and still
                # keeps the window attached smoothly while PCSX2 is being moved.
                self._overlay_render()
            else:
                try:
                    if self._overlay_window is not None:
                        self._overlay_window.withdraw()
                except tk.TclError:
                    pass
        self._overlay_after_id = self.after(16, self._overlay_tick)

    def _save_connection_settings(self) -> None:
        self._update_cfg(
            server=self.server_var.get().strip(),
            name=self.name_var.get().strip(),
            password=self.password_var.get(),
        )
        messagebox.showinfo(APP_TITLE, self.tr["connection_saved"], parent=self.options_window or self)

    def _set_language(self, code: str) -> None:
        if code not in T:
            return
        self.language = code
        self._update_cfg(language=code)
        self._apply_language()

    def _apply_language(self) -> None:
        if hasattr(self, '_auto_save_check'):
            self._update_auto_save_language()
        self.color_studio_button.configure(text=self._color_studio_button_text())
        self._refresh_texture_folder_status(schedule=False)
        self.canvas.itemconfigure(self.server_label_id, text=self.tr["server"])
        self.canvas.itemconfigure(self.name_label_id, text=self.tr["name"])
        self.canvas.itemconfigure(self.password_label_id, text=self.tr["password_optional"])
        self.canvas.itemconfigure(self.log_label_id, text=self.tr["log"])

        self.connect_button.configure(text=self.tr["connect"])
        self.clear_button.configure(text=self.tr["clear"])

        status_title_keys = {
            "pine": "status_pine",
            "server": "status_server",
            "game": "status_game",
        }
        for key, tr_key in status_title_keys.items():
            _dot, title_id, state_text = self.status_widgets[key]
            self.canvas.itemconfigure(title_id, text=self.tr[tr_key])

            current_fill = self.canvas.itemcget(_dot, "fill")
            if current_fill == STATUS_COLORS["connected"]:
                # Keep special game/server values if they are already displayed.
                current_text = self.canvas.itemcget(state_text, "text")
                if key == "pine":
                    self.canvas.itemconfigure(state_text, text=self.tr["connected"])
                elif key == "server" and current_text in ("Reachable", "Accessible", "Erreichbar", "Raggiungibile"):
                    self.canvas.itemconfigure(state_text, text=self.tr["reachable"])
            elif current_fill == STATUS_COLORS["busy"]:
                previous_text = self.canvas.itemcget(state_text, "text")
                waiting_labels = {tr.get("pine_busy_state", "") for tr in T.values()}
                if previous_text in waiting_labels:
                    self.canvas.itemconfigure(state_text, text=self.tr["pine_busy_state"])
                else:
                    self.canvas.itemconfigure(state_text, text=self.tr["connecting_status"])
            else:
                current_text = self.canvas.itemcget(state_text, "text")
                generic_values = {
                    "Disconnected", "Déconnecté", "Getrennt", "Desconectado", "Disconnesso",
                    "Not detected", "Non détecté", "Nicht erkannt", "No detectado", "Non rilevato",
                }
                if current_text in generic_values:
                    if key == "game":
                        self.canvas.itemconfigure(state_text, text=self.tr["not_detected"])
                    else:
                        self.canvas.itemconfigure(state_text, text=self.tr["disconnected"])

        if self.options_window is not None:
            try:
                if self.options_window.winfo_exists():
                    self.options_window.title(f"{APP_TITLE} - {self.tr['options']}")
                    ow = self.options_widgets
                    ow["title"].configure(text=self.tr["options"])
                    ow["lang_frame"].configure(text=self.tr["language"])
                    ow["overlay_frame"].configure(text=self.tr["overlay_title"])
                    ow["overlay_test_btn"].configure(text=self.tr["overlay_test"])
                    ow["overlay_note"].configure(text=self.tr["overlay_note"])
                    self._refresh_overlay_options_button()
                    ow["camera_frame"].configure(text=self.tr["camera"])
                    ow["h_label"].configure(text=self.tr["horizontal_camera"])
                    ow["v_label"].configure(text=self.tr["vertical_camera"])
                    ow["h_van"].configure(text=self.tr["vanilla"])
                    ow["h_inv"].configure(text=self.tr["inverted"])
                    ow["v_van"].configure(text=self.tr["vanilla"])
                    ow["v_inv"].configure(text=self.tr["inverted"])
                    ow["note"].configure(text=self.tr["camera_note"])
                    ow["close_btn"].configure(text=self.tr["close"])

                    for c, _flag, _name in LANGUAGES:
                        ow["lang_buttons"][c].configure(
                            bg=("#2e6b4d" if c == self.language else "#1a2530")
                        )
            except tk.TclError:
                pass

    def _refresh_iso_check_widgets(self) -> None:
        try:
            if self.options_window is None or not self.options_window.winfo_exists():
                return
        except tk.TclError:
            return
        if not self.options_widgets:
            return
        led = self.options_widgets.get("iso_led")
        circle = self.options_widgets.get("iso_led_circle")
        status = self.options_widgets.get("iso_status")
        detail = self.options_widgets.get("iso_detail")
        if led is None or circle is None or status is None or detail is None:
            return

        result = self._iso_last_result
        if result is None:
            led.itemconfigure(circle, fill="#6b7280")
            status.configure(text=self.tr["iso_not_checked"], fg="#c7d0d7")
            detail.configure(text="")
            return

        if result.get("checking"):
            led.itemconfigure(circle, fill="#f0a13e")
            status.configure(text=self.tr["iso_checking"], fg="#f0c070")
            detail.configure(text=result.get("path", ""))
            return

        compatible = bool(result.get("compatible"))
        led.itemconfigure(circle, fill=("#45db68" if compatible else "#e04b4b"))
        status.configure(
            text=(self.tr["iso_compatible"] if compatible else self.tr["iso_incompatible"]),
            fg=("#71ed90" if compatible else "#f57a7a"),
        )

        reason = result.get("reason")
        if reason == "exact_ok":
            reason_text = self.tr["iso_exact_ok"]
        elif reason == "exe_ok":
            reason_text = self.tr["iso_exe_ok"]
        elif reason == "wrong_serial":
            reason_text = self.tr["iso_wrong_serial"].format(serial=result.get("serial") or "UNKNOWN")
        elif reason == "unknown_revision":
            reason_text = self.tr["iso_unknown_revision"]
        else:
            reason_text = self.tr["iso_read_error"].format(error=result.get("error") or "Unknown error")

        filename = Path(result.get("path", "")).name if result.get("path") else ""
        serial = result.get("serial") or "N/A"
        detail.configure(text=f"{reason_text}\n{filename}  •  {serial}")

    def _start_iso_check(self) -> None:
        path_text = filedialog.askopenfilename(
            parent=self.options_window or self,
            title=self.tr["iso_compatibility"],
            filetypes=[("PlayStation 2 ISO", "*.iso"), ("All files", "*.*")],
        )
        if not path_text:
            return

        path = Path(path_text)
        self._iso_check_generation += 1
        generation = self._iso_check_generation
        self._iso_last_result = {"checking": True, "path": str(path)}
        self._refresh_iso_check_widgets()

        button = self.options_widgets.get("iso_btn")
        if button is not None:
            button.configure(state="disabled")

        self._iso_check_thread = threading.Thread(
            target=self._iso_check_worker,
            args=(generation, path),
            daemon=True,
            name="KyaISOCompatibilityCheck",
        )
        self._iso_check_thread.start()

    def _iso_check_worker(self, generation: int, path: Path) -> None:
        try:
            result = check_kya_iso_compatibility(path)
            result["path"] = str(path)
        except Exception as exc:
            result = {
                "compatible": False,
                "reason": "read_error",
                "serial": None,
                "iso_sha256": None,
                "exe_sha256": None,
                "path": str(path),
                "error": f"{type(exc).__name__}: {exc}",
            }
        self.after(0, self._finish_iso_check, generation, result)

    def _finish_iso_check(self, generation: int, result: dict) -> None:
        if generation != self._iso_check_generation:
            return
        self._iso_last_result = result
        self._refresh_iso_check_widgets()

        button = self.options_widgets.get("iso_btn")
        if button is not None:
            try:
                button.configure(state="normal")
            except tk.TclError:
                pass

        self._update_cfg(
            iso_last_path=result.get("path", ""),
            iso_last_compatible=bool(result.get("compatible")),
            iso_last_serial=result.get("serial"),
            iso_last_sha256=result.get("iso_sha256"),
            iso_last_exe_sha256=result.get("exe_sha256"),
        )

    def _camera_option_changed(self) -> None:
        self.camera_horizontal = self._opt_horizontal_var.get()
        self.camera_vertical = self._opt_vertical_var.get()
        self._update_cfg(
            camera_horizontal=self.camera_horizontal,
            camera_vertical=self.camera_vertical,
        )

    def _ensure_camera_service_started(self) -> None:
        if self._camera_thread is not None and self._camera_thread.is_alive():
            return

        self._camera_ready_event.clear()
        self._camera_last_error = "PINE connection is starting."
        self._camera_thread = threading.Thread(
            target=self._camera_service_loop,
            daemon=True,
            name="KyaCameraService",
        )
        self._camera_thread.start()

    # ------------------------------------------------------------------
    # Connection checks
    # ------------------------------------------------------------------
    def _on_connect(self) -> None:
        server = self.server_var.get().strip()
        name = self.name_var.get().strip()

        if not name:
            messagebox.showwarning(APP_TITLE, self.tr["name_required"])
            return

        try:
            host, port = parse_server(server, self.tr)
        except ValueError as exc:
            messagebox.showwarning(APP_TITLE, str(exc))
            return

        self._update_cfg(server=server, name=name, password=self.password_var.get())
        self._connected_requested = True
        self._last_connection_indicator_state = None

        # Start the same PINE/camera path as the validated standalone patch,
        # but only now, after the user explicitly clicks CONNECT.
        self._ensure_camera_service_started()

        self._set_busy(True)
        self._set_status("pine", "connecting")
        self._set_status("server", "connecting")
        self._set_status("game", "connecting", self.tr["checking"])
        self._log(self.tr["starting_checks"])

        self._stop_event.clear()
        self._worker_thread = threading.Thread(
            target=self._connection_test,
            args=(host, port),
            daemon=True,
            name="KyaLauncherConnectionCheck",
        )
        self._worker_thread.start()

    def _connection_test(self, host: str, port: int) -> None:
        tr = self.tr.copy()

        if self._stop_event.is_set():
            return

        # Do NOT open a second PINE connection here.
        # The integrated camera service owns the only PINE socket and also
        # validates the supported Kya build through the confirmed signature.
        self._camera_ready_event.wait(timeout=10.0)

        pine_ok = self._camera_ready_event.is_set()
        game_ok = pine_ok

        if pine_ok:
            self._post_ui(self._set_status, "pine", "connected", tr["connected"])
            self._post_ui(self._set_status, "game", "connected", EXPECTED_GAME_ID)
            self._log_threadsafe(tr["pine_ok"], "ok")
            self._log_threadsafe(tr["game_ok"], "ok")
        else:
            self._post_ui(self._set_status, "pine", "disconnected", tr["disconnected"])
            self._post_ui(self._set_status, "game", "disconnected", tr["not_detected"])
            self._log_threadsafe(
                f"{tr['pine_fail']} ({self._camera_last_error})",
                "error",
            )

        if self._stop_event.is_set():
            return

        server_ok, _server_error = can_connect(host, port, timeout=2.5)
        if self._stop_event.is_set():
            return

        if server_ok:
            self._post_ui(self._set_status, "server", "connected", tr["reachable"])
            self._log_threadsafe(tr["server_ok"], "ok")
        else:
            self._post_ui(self._set_status, "server", "disconnected", tr["disconnected"])
            if _server_error:
                self._log_threadsafe(
                    f"{tr['server_fail']} ({_server_error})",
                    "error",
                )
            else:
                self._log_threadsafe(tr["server_fail"], "error")

        self._post_ui(self._finish_connection_test, pine_ok, game_ok, server_ok, tr)

    def _finish_connection_test(self, pine_ok: bool, game_ok: bool, server_ok: bool, tr: dict) -> None:
        self._set_busy(False)
        if self.server_var.get().strip() and self.name_var.get().strip():
            if server_ok and pine_ok:
                self._log(tr["checks_ok"], "ok")
            else:
                self._log("Archipelago link starting in recovery mode; automatic network/PCSX2 reconnection is enabled.", "warn")
            if self._ap_link is None:
                self._ap_baselined = False
                self._ap_joined = False
                self._ap_seed_build_verified = False
                self._ap_wolfen_states.clear()
                self._ap_actor_states.clear()
                self._ap_actor_keys.clear()
                self._ap_actor_descriptors.clear()
                self._ap_special_states.clear()
                self._ap_special_baselined = False
                self._ap_first_brazul_last_value = None
                self._ap_first_brazul_zone_since = None
                self._ap_first_brazul_next_poll = 0.0
                self._ap_fast_travel_states.clear()
                self._ap_fast_travel_keys.clear()
                self._ap_fast_travel_baselined = False
                self._ap_validation_probe_states.clear()
                self._ap_validation_probes_baselined = False
                self._ap_current_zone = None
                self._ap_shop_states.clear()
                self._ap_shop_reward_snapshots.clear()
                self._ap_pending_shop_suppressions.clear()
                self._ap_shop_suppressed.clear()
                self._ap_shop_baselined = False
                self._ap_shop_live_reward_states.clear()
                self._ap_shop_live_baselined = False
                self._ap_shop_live_ignore_until = 0.0
                self._ap_shop_money_last = None
                self._ap_shop_purchase_tokens.clear()
                self._ap_shop_ambiguous_token_warned.clear()
                self._ap_shop_unpaired_live_hits.clear()
                self._ap_shop_unconfirmed_stock.clear()
                self._ap_shop_group_candidates.clear()
                self._ap_shop_group_scores.clear()
                self._ap_shop_group_snapshots.clear()
                self._ap_shop_group_last_scan = 0.0
                self._ap_shop_group_scan_logged = False
                self._ap_shop_group_prime_logged = False
                self._ap_shop_group_rolling_states.clear()
                self._ap_shop_group_edge_events.clear()
                self._ap_shop_native.reset()
                self._ap_shop_sold_observer.reset()
                self._ap_shop_native_sold_state_last = {}
                self._ap_shop_native_hints.clear()
                self._ap_shop_native_ready_logged = False
                self._ap_shop_native_last_attempt = 0.0
                self._ap_shop_native_last_report = None
                self._ap_shop_native_last_report_at = 0.0
                self._ap_next_goal_poll = 0.0
                self._ap_goal_last_value = None
                self._ap_goal_credits_last_value = None
                self._ap_goal_auto_candidate_at = None
                self._ap_goal_auto_candidate_samples = 0
                self._ap_goal_auto_last_diag_at = 0.0
                self._ap_goal_fortress_since = None
                self._ap_goal_boss_witness_at = None
                self._ap_goal_reached = False
                self._ap_goal_status_sent = False
                self._ap_goal_message_logged = False
                self._ap_checked.clear()
                self._ap_ft_detector_handoff_sources.clear()
                self._ap_ft_detector_guard_targets.clear()
                self._ap_ft_detector_remote_logged.clear()
                self._ap_ft_detector_handoff_logged.clear()
                self._ap_ft_detector_near_wait_logged.clear()
                self._ap_ft_detector_handoff_key = ""
                self._ap_seed_name = ""
                self._ap_pending_check_key = ""
                self._ap_pending_checks.clear()
                self._ap_item_cursor_key = ""
                self._ap_applied_item_cursor = 0
                self._ap_item_counts.clear()
                self._ap_pending_hp_restore = 0
                self._ap_pending_magic_restore = 0
                self._ap_damage_last_hp.clear()
                self._ap_player_last_hp = None
                self._ap_damage_effect_logged = False
                self._ap_protection_effect_logged = False
                self._ap_next_combat_poll = 0.0
                self._ap_next_inventory_reconcile = 0.0
                self._ap_overlay_recent_incoming.clear()
                self._ap_life_gauge_key = "|".join((
                    self.server_var.get().strip().lower(),
                    self.name_var.get().strip().lower(),
                    str(self._ap_data.get("AP_BUILD_VERSION") or self._ap_data.get("PROTOTYPE_VERSION") or "unknown"),
                ))
                self._ap_life_gauge_progress = load_config().get("ap_life_gauge_progress", {})
                if not isinstance(self._ap_life_gauge_progress, dict):
                    self._ap_life_gauge_progress = {}
                self._ap_link = APLink(self.server_var.get().strip(), self.name_var.get().strip(), self.password_var.get().strip())
                self._ap_link.start()
                self._log("Joining Kya slot on Archipelago…", "info")
        else:
            self._log(tr["checks_warn"], "warn")

    def _ap_pending_storage_key(self, d: dict) -> str:
        if not self._ap_seed_name:
            return ""
        # seed_name + slot + build is stable even if the same hosted room moves
        # to another IP/port.  Server address is deliberately not part of identity.
        return "|".join((
            self.name_var.get().strip().lower(),
            str(d.get("AP_BUILD_VERSION") or d.get("PROTOTYPE_VERSION") or "unknown"),
            self._ap_seed_name,
        ))

    def _ap_save_pending_checks(self, d: dict) -> bool:
        key = self._ap_pending_check_key or self._ap_pending_storage_key(d)
        if not key:
            # RoomInfo normally arrives before Connected. If a non-standard server
            # omits seed_name we still send live, but deliberately do not persist
            # across runs because we cannot distinguish two seeds safely.
            return False
        self._ap_pending_check_key = key
        try:
            cfg = load_config()
            store = cfg.get("ap_pending_checks", {})
            if not isinstance(store, dict):
                store = {}
            if self._ap_pending_checks:
                store[key] = {str(i): label for i, label in sorted(self._ap_pending_checks.items())}
            else:
                store.pop(key, None)
            cfg["ap_pending_checks"] = store
            save_config_data(cfg)
            return True
        except Exception as exc:
            self._log_threadsafe(f"Could not persist pending AP checks: {type(exc).__name__}: {exc}", "warn")
            return False

    def _ap_load_pending_checks(self, d: dict) -> None:
        key = self._ap_pending_storage_key(d)
        self._ap_pending_check_key = key
        self._ap_pending_checks.clear()
        if not key:
            return
        try:
            cfg = load_config()
            store = cfg.get("ap_pending_checks", {})
            raw = store.get(key, {}) if isinstance(store, dict) else {}
            if isinstance(raw, dict):
                for raw_id, label in raw.items():
                    try:
                        self._ap_pending_checks[int(raw_id)] = str(label)
                    except (TypeError, ValueError):
                        continue
        except Exception as exc:
            self._log_threadsafe(f"Could not load pending AP checks: {type(exc).__name__}: {exc}", "warn")

    def _ap_ft_handoff_storage_key(self, d: dict) -> str:
        base = self._ap_pending_storage_key(d)
        return (base + "|ft_detector_handoff_v0915") if base else ""

    def _ap_load_detector_handoffs(self, d: dict) -> None:
        """Load only handoffs confirmed by V0.9.15's local read-only discovery detector.

        Archipelago checked IDs are intentionally not trusted here because older
        experimental builds could check FT01 from the bootstrap itself.
        """
        key = self._ap_ft_handoff_storage_key(d)
        self._ap_ft_detector_handoff_key = key
        self._ap_ft_detector_handoff_sources.clear()
        if not key:
            return
        try:
            cfg = load_config()
            store = cfg.get("ft_detector_handoffs", {})
            raw = store.get(key, []) if isinstance(store, dict) else []
            if isinstance(raw, list):
                valid_sources = {
                    int(r.get("source_key", -1))
                    for routes in d.get("FAST_TRAVEL_ALLOWED_ROUTES", {}).values()
                    if isinstance(routes, list)
                    for r in routes
                    if isinstance(r, dict) and int(r.get("source_index", -1)) == 0
                }
                for value in raw:
                    try:
                        source = int(value)
                    except (TypeError, ValueError):
                        continue
                    if source in valid_sources:
                        self._ap_ft_detector_handoff_sources.add(source)
            if self._ap_ft_detector_handoff_sources:
                self._log_threadsafe(
                    "FT DETECTOR persistent vanilla handoff restored for Nativ source(s): "
                    + ", ".join(f"0x{x:04X}" for x in sorted(self._ap_ft_detector_handoff_sources))
                    + ".",
                    "ok",
                )
        except Exception as exc:
            self._log_threadsafe(
                f"Could not load FT detector handoffs: {type(exc).__name__}: {exc}",
                "warn",
            )

    def _ap_save_detector_handoffs(self, d: dict) -> bool:
        key = self._ap_ft_detector_handoff_key or self._ap_ft_handoff_storage_key(d)
        if not key:
            return False
        self._ap_ft_detector_handoff_key = key
        try:
            cfg = load_config()
            store = cfg.get("ft_detector_handoffs", {})
            if not isinstance(store, dict):
                store = {}
            if self._ap_ft_detector_handoff_sources:
                store[key] = sorted(int(x) for x in self._ap_ft_detector_handoff_sources)
            else:
                store.pop(key, None)
            cfg["ft_detector_handoffs"] = store
            save_config_data(cfg)
            return True
        except Exception as exc:
            self._log_threadsafe(
                f"Could not persist FT detector handoffs: {type(exc).__name__}: {exc}",
                "warn",
            )
            return False

    def _ap_item_cursor_storage_key(self, d: dict) -> str:
        # Same seed identity as durable LocationChecks.  The suffix keeps both
        # namespaces independent in config.json.
        base = self._ap_pending_storage_key(d)
        return (base + "|items") if base else ""

    def _ap_load_item_cursor(self, d: dict) -> None:
        key = self._ap_item_cursor_storage_key(d)
        self._ap_item_cursor_key = key
        self._ap_applied_item_cursor = 0
        if not key:
            return
        try:
            cfg = load_config()
            store = cfg.get("ap_item_cursors", {})
            if isinstance(store, dict):
                self._ap_applied_item_cursor = max(0, int(store.get(key, 0)))
        except Exception as exc:
            self._log_threadsafe(f"Could not load AP item cursor: {type(exc).__name__}: {exc}", "warn")

    def _ap_save_item_cursor(self, d: dict) -> bool:
        key = self._ap_item_cursor_key or self._ap_item_cursor_storage_key(d)
        if not key:
            return False
        self._ap_item_cursor_key = key
        try:
            cfg = load_config()
            store = cfg.get("ap_item_cursors", {})
            if not isinstance(store, dict):
                store = {}
            store[key] = int(self._ap_applied_item_cursor)
            cfg["ap_item_cursors"] = store
            save_config_data(cfg)
            return True
        except Exception as exc:
            self._log_threadsafe(f"Could not persist AP item cursor: {type(exc).__name__}: {exc}", "warn")
            return False

    def _ap_queue_location_check(self, link: APLink, location_id: int, name: str, d: dict) -> bool:
        """Queue a LocationCheck once and report whether it is crash-durable locally."""
        location_id = int(location_id)
        if location_id in self._ap_checked:
            return True
        # A second detector (live reward + duplicate fallback, for example) can
        # observe the same purchase before the server ACK arrives.  The durable
        # pending queue is already our proof that the check was sent, so never
        # send/log it twice during the same session. Reconnect resends are handled
        # explicitly by the join path.
        if location_id in self._ap_pending_checks:
            return True
        durable = bool(self._ap_pending_check_key or self._ap_pending_storage_key(d))
        self._ap_pending_checks[location_id] = str(name)
        durable = self._ap_save_pending_checks(d)
        link.check(location_id)
        return durable

    def _ap_ack_pending_checks(self, checked_ids: set[int], d: dict) -> None:
        changed = False
        for location_id in checked_ids:
            if self._ap_pending_checks.pop(int(location_id), None) is not None:
                changed = True
        if changed:
            self._ap_save_pending_checks(d)

    def _ap_final_recovery_eligible(self, d: dict) -> bool:
        """Strict proof of this seed's Fortress progress for a missed boss edge.

        The launcher was previously paused during the real final fight.  When
        reconnecting to a savestate *after* the fight, Var61 is already 2, so
        a 1->2-only watcher can never recover.  Require *server-authoritative*
        confirmation of all 13 Fortress Arena Wolfen locations. Merely
        opening a finished 100% vanilla savestate with an empty/new AP slot
        MUST NOT complete the goal.

        There is no cryptographic way to tie arbitrary PCSX2 savestate RAM to
        an AP slot; this guard is evidence-based for the user's live run.
        """
        if not (self._ap_joined and self._ap_seed_build_verified and self._ap_link):
            return False
        catalog = d.get('LOCATION_NAME_TO_ID', {})
        arena_ids = {int(v) for name, v in catalog.items()
                     if name.startswith('The Fortress - Fortress Arena - Wolfen ')}
        return len(arena_ids) == 13 and arena_ids.issubset(self._ap_checked)

    def _ap_process_goal_sample(self, brazul_value: int, credits_value: int, d: dict) -> None:
        """0.9.52 safe Goal: witnessed Fortress boss victory + server ACK.

        Previous 0.9.50/51 experiment used 0x0044982C 0->4. The user's
        100%-save Nativs City walk proved that unrelated transition falsely
        completed Archipelago. It is now *diagnostic only*, never a predicate.

        The listener must see a stable pre-boss 1 in the Fortress BEFORE the
        live transition to 2. A precompleted savestate, AP recovery of 13
        Wolfens, and replaying 0->4 alone cannot authorize victory. A server
        ACK is required, with a small post-edge stability window. Players
        resuming from an already-finished boss save can still use the manual
        confirmation control; we cannot safely infer a historical fight.
        """
        previous_brazul = self._ap_goal_last_value
        previous_credits = self._ap_goal_credits_last_value
        final_value = int(d['GOAL_BRAZUL_FINAL_VALUE'])
        pre_value = int(d['GOAL_BRAZUL_FINAL_FROM'])
        final_edge = previous_brazul == pre_value and brazul_value == final_value
        authenticated = bool(self._ap_joined and self._ap_seed_build_verified and self._ap_link)
        final_name = 'The Fortress - Brazul Final Defeated'
        final_location_id = d.get('LOCATION_NAME_TO_ID', {}).get(final_name)
        final_ack = bool(authenticated and final_location_id is not None
                         and int(final_location_id) in self._ap_checked)
        now = time.monotonic()

        if previous_brazul is None:
            self._log_threadsafe(
                f'AUTO GOAL 0.9.52 armed: Brazul Var61={brazul_value}; '
                f'final boss AP ACK={final_ack}. Legacy 0x0044982C={credits_value} '
                'is ignored for victory.', 'info')
        if previous_brazul is not None and brazul_value != previous_brazul:
            self._log_threadsafe(
                f'GOAL TRACE: Brazul Var61 {previous_brazul}->{brazul_value}; '
                f'AP boss ACK={final_ack}.', 'info')
        if previous_credits is not None and credits_value != previous_credits:
            self._log_threadsafe(
                f'GOAL LEGACY DIAGNOSTIC ONLY: 0x0044982C '
                f'{previous_credits}->{credits_value}; never triggers Goal.', 'info')

        # The observed live final fight must have been watched in the Fortress,
        # while Var61 remained in the pre-fight state long enough to rule out
        # immediate scene loading / a completed savestate baseline.
        in_fortress = self._ap_current_zone == 'The Fortress'
        if authenticated and in_fortress and brazul_value == pre_value:
            if self._ap_goal_fortress_since is None:
                self._ap_goal_fortress_since = now
        elif self._ap_goal_boss_witness_at is None and not final_edge:
            self._ap_goal_fortress_since = None

        stable_preboss = bool(self._ap_goal_fortress_since is not None and
                              now - self._ap_goal_fortress_since >= 1.0)
        if (final_edge and authenticated and in_fortress and stable_preboss):
            self._ap_goal_boss_witness_at = now
            self._ap_goal_auto_candidate_samples = 1
            self._log_threadsafe(
                'AUTO GOAL BOSS WITNESSED: live Fortress Brazul Var61 '
                '1->2; waiting for stable state and Archipelago boss ACK.', 'ok')
        elif final_edge:
            self._log_threadsafe(
                f'AUTO GOAL BOSS EDGE UNTRUSTED: zone={self._ap_current_zone or "?"}; '
                f'preboss stable={stable_preboss}. No automatic Goal.', 'warn')

        # Preserve the established independent boss CHECK path. Recovery may
        # resend the check when 13/13 Fortress Wolfens are server-ACKed, but it
        # must NEVER qualify as a LIVE victory/automatic Goal by itself.
        recovery = bool(authenticated and brazul_value == final_value
                        and self._ap_final_recovery_eligible(d))
        if authenticated and (final_edge or recovery):
            if (final_location_id is not None
                    and int(final_location_id) not in self._ap_checked
                    and int(final_location_id) not in self._ap_pending_checks):
                if self._ap_queue_location_check(self._ap_link, int(final_location_id), final_name, d):
                    reason = ('witnessed Brazul Var61 1->2' if final_edge
                              else 'recovered boss check only: Var61=2 + 13/13 arena AP ACKs')
                    self._log_threadsafe(
                        f'FINAL BRAZUL CHECK queued -> Archipelago: {final_name} ({reason}).', 'ok')

        if self._ap_goal_boss_witness_at is not None:
            if not authenticated or brazul_value != final_value:
                self._ap_goal_boss_witness_at = None
                self._ap_goal_auto_candidate_samples = 0
                self._log_threadsafe('AUTO GOAL BOSS WITNESS CANCELLED: game/AP state changed.', 'warn')
            else:
                self._ap_goal_auto_candidate_samples += 1
                if (not self._ap_goal_reached and final_ack
                        and self._ap_goal_auto_candidate_samples >= 3
                        and now - self._ap_goal_boss_witness_at >= 0.5):
                    self._ap_goal_reached = True
                    self._log_threadsafe(
                        'AUTO GOAL TRIGGERED: witnessed LIVE final Brazul defeat '
                        '+ stable Var61=2 + server boss ACK. No credits/Nativ flag used. '
                        'StatusUpdate=30 will be sent.', 'ok')
                    self._ap_goal_boss_witness_at = None

        if (authenticated and brazul_value == final_value
                and not self._ap_goal_reached
                and now - self._ap_goal_auto_last_diag_at >= 15.0):
            self._ap_goal_auto_last_diag_at = now
            self._log_threadsafe(
                f'AUTO GOAL WAITING: Brazul=2; AP boss ACK={final_ack}; '
                f'live boss witness={self._ap_goal_boss_witness_at is not None}. '
                'Pre-completed savestates require manual confirmation.', 'info')

        self._ap_goal_last_value = brazul_value
        self._ap_goal_credits_last_value = credits_value

    def _confirm_credits_manually(self) -> None:
        """Temporary user-attested credits Goal, with live boss and AP checks.

        This is a user action, not an automatic fallback from a stale memory
        flag.  Require the final-boss location to be ACKed by the actual AP
        server of the verified seed and live Var61=2 before confirmation.
        """
        parent = self.options_window or self
        fr = self.language == 'fr'
        if not (self._ap_joined and self._ap_seed_build_verified
                and self._ap_link is not None and self._ap_link.connected_event.is_set()):
            messagebox.showwarning(APP_TITLE,
                'Connecte d’abord ta seed Archipelago vérifiée.' if fr
                else 'Connect to your verified Archipelago seed first.',
                parent=parent)
            return
        final_id = self._ap_data.get('LOCATION_NAME_TO_ID', {}).get('The Fortress - Brazul Final Defeated')
        if final_id is None or int(final_id) not in self._ap_checked:
            messagebox.showwarning(APP_TITLE,
                'Le serveur AP n’a pas encore confirmé le check Brazul final.' if fr
                else 'The AP server has not acknowledged the final Brazul check yet.',
                parent=parent)
            return
        try:
            with PineClient(PINE_HOST, PINE_PORT, timeout=3.0) as pine:
                if int(pine.read32(SIG_ADDRS[0])) != int(SIG_VALUES[0]):
                    raise RuntimeError('Signature Kya invalide')
                brazul = int(pine.read32(int(self._ap_data['ADDR_GOAL_BRAZUL_FINAL'])))
        except Exception as exc:
            messagebox.showwarning(APP_TITLE,
                ('PCSX2 / Kya non vérifié : ' if fr else 'PCSX2/Kya not verified: ') + str(exc),
                parent=parent)
            return
        if brazul != int(self._ap_data['GOAL_BRAZUL_FINAL_VALUE']):
            messagebox.showwarning(APP_TITLE,
                'Brazul final n’est pas marqué vaincu dans le jeu.' if fr
                else 'Final Brazul is not marked defeated in game memory.',
                parent=parent)
            return
        question = (
            'As-tu RÉELLEMENT vu apparaître les crédits de fin de Kya dans PCSX2 ?\n\n'
            'Le flag historique 0x0044982C est NON FIABLE et ne prouve pas les crédits. '
            'En confirmant, tu enverras le statut GOAL au serveur Archipelago. '
            'Cette action ne peut pas être annulée depuis le Launcher.'
            if fr else
            'Have the actual Kya end credits appeared on screen in PCSX2?\n\n'
            'The historical 0x0044982C flag is UNRELIABLE. Confirming sends '
            'GOAL to Archipelago and cannot be undone from the Launcher.'
        )
        if not messagebox.askyesno(APP_TITLE + ' — Credits', question, parent=parent):
            return
        if not (self._ap_joined and self._ap_seed_build_verified
                and self._ap_link is not None and self._ap_link.connected_event.is_set()
                and int(final_id) in self._ap_checked):
            self._log_threadsafe('MANUAL CREDITS GOAL refused: AP slot changed during confirmation.', 'warn')
            return
        if self._ap_goal_status_sent or self._ap_goal_reached:
            self._log_threadsafe('MANUAL CREDITS GOAL already sent in this Launcher session.', 'info')
            return
        self._ap_goal_reached = True
        self._ap_goal_status_sent = True
        self._ap_goal_message_logged = True
        self._ap_link.goal()
        self._log_threadsafe('MANUAL CREDITS GOAL: user confirmed seeing real credits; '
                             'live Brazul=2 and final boss AP ACK verified. Goal sent.', 'ok')

    def _request_shop_audit(self) -> None:
        """UI-only request; actual PINE reads occur in the single-owner loop."""
        self._ap_shop_audit_requested = True
        self._log_threadsafe(
            'SHOP AUDIT requested (READ-ONLY): visit Nativs City with a stable '
            'scene. No Archipelago checks or memory writes will be sent.', 'info')

    def _ap_emit_shop_audit(self, current_shop: dict, current_rewards: dict,
                            loc_by_name: dict) -> None:
        """Export 18 AP ACKs and native actor sold markers, read-only."""
        if not self._ap_shop_audit_requested or self._ap_current_zone != 'Nativs City':
            return
        self._ap_shop_audit_requested = False
        names = sorted(n for n in current_shop if n.startswith('Nativs City - Shop - '))
        checked_count = sum(loc_by_name.get(n) in self._ap_checked for n in names)
        missing = len(names) - checked_count
        self._log_threadsafe(
            f'SHOP AUDIT READ-ONLY: {checked_count}/{len(names)} server-ACKed; '
            f'{missing} unchecked. A depleted stock or possessed item is NOT '
            'proof of a purchase in this AP seed.', 'warn' if missing else 'ok')
        for name in names:
            loc_id = loc_by_name.get(name)
            status = ('ACK' if loc_id in self._ap_checked else
                      'PENDING' if loc_id in self._ap_pending_checks else 'UNCHECKED')
            stock = 'AVAILABLE' if current_shop[name] else 'UNAVAILABLE'
            reward = current_rewards.get(name)
            self._log_threadsafe(
                f'SHOP AUDIT: {name} | AP={status} | serialized={stock} | '
                f'reward_value={reward} (not ownership proof)', 'info')
        # 0.9.61: same ID-resolved actor+0x08 sold signature used by the
        # recovery watcher. Audit export itself remains read-only.
        try:
            native_states = getattr(self, '_ap_shop_native_sold_state_last', {})
            filename, resolved = export_native_shop_audit(
                config_path().parent / 'Shop_Audits', names,
                loc_by_name, self._ap_checked, self._ap_pending_checks,
                current_shop, current_rewards, self._ap_shop_native, native_states,
            )
            self._log_threadsafe(
                f'SHOP AUDIT CSV: {filename} | native mappings={resolved}/{len(names)}; '
                'native actor+0x08 sold signature included. Audit export is read-only.',
                'ok' if resolved == len(names) else 'warn')
        except Exception as exc:
            self._log_threadsafe(
                f'SHOP AUDIT CSV deferred: {type(exc).__name__}: {exc}', 'warn')
        self._log_threadsafe(
            'SHOP AUDIT completed without modifying game memory or AP progression.', 'ok')

    def _report_native_shop_scan(self, status: tuple, message: str, now: float, tag: str = "info") -> None:
        """Keep the 1.5s scan cadence; only suppress repetitive log lines.

        Report on any changed resolved/object/table count and at most once per
        60 seconds for an unchanged state. Never throttle real shop checks.
        """
        if (status != self._ap_shop_native_last_report
                or now - self._ap_shop_native_last_report_at >= 60.0):
            self._ap_shop_native_last_report = status
            self._ap_shop_native_last_report_at = now
            self._log_threadsafe(message, tag)

    def _ap_update_zone(self, active_keys: set[int], d: dict) -> None:
        votes: dict[str, int] = {}
        for key in active_keys:
            for zone in d.get("WOLFEN_KEY_TO_ZONES", {}).get(str(key), []):
                votes[zone] = votes.get(zone, 0) + 1
        if not votes:
            return  # keep last stable zone through streaming/cinematics
        ranked = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            return
        new_zone = ranked[0][0]
        if new_zone != self._ap_current_zone:
            self._ap_current_zone = new_zone
            self._ap_baselined = False
            self._ap_special_baselined = False
            self._ap_hunter_boss_recovery_since = None
            self._ap_fast_travel_baselined = False
            self._ap_fast_travel_states.clear()
            self._ap_fast_travel_keys.clear()
            self._log_threadsafe(
                f"AP zone detected: {new_zone} ({ranked[0][1]} mapped Wolfen keys).",
                "ok",
            )

    def _ap_public_location_name(self, location_name: str) -> str:
        """Keep each Wolfen number/sub-zone visible in local AP logs.

        These numbers are the already-established AP location identities;
        stripping them made different Wolfen appear to be duplicate checks.
        Never rewrite a canonical APWorld name or ID in a live seed.
        """
        return str(location_name)

    @staticmethod
    def _ap_normalize_economy_percent(value: int) -> int:
        """Clamp to [-100, +1000] and snap to the nearest 10%."""
        value = max(-100, min(1000, int(value)))
        if value >= 0:
            return min(1000, ((value + 5) // 10) * 10)
        return max(-100, -(((-value + 5) // 10) * 10))

    @staticmethod
    def _ap_scale_percent(base: int, modifier_percent: int) -> int:
        modifier_percent = max(-100, min(1000, int(modifier_percent)))
        return max(0, (int(base) * (100 + modifier_percent) + 50) // 100)

    def _ap_shop_expected_price(self, name: str) -> int | None:
        if self._ap_shop_native.ready:
            current = self._ap_shop_native.current_price(str(name))
            if current is not None:
                return int(current)
        base = SHOP_PRICE_HINTS.get(str(name))
        if base is None:
            return None
        return self._ap_scale_percent(int(base), self._ap_shop_price_modifier_pct)

    def _ap_shop_allowed_spends(self, name: str) -> tuple[int, ...]:
        """Accepted money debits for a *confirmed* shop identity.

        A 2026-10-28 trace charged vanilla 30/100/50 despite a -30% AP
        setting and native item price fields reporting their reduced target.
        Never infer the item from this number alone: require a native selection,
        live reward transition or independent serialized stock transition.
        The discrepancy is logged; this does not pretend the discount worked.
        """
        current = self._ap_shop_expected_price(name)
        allowed = {int(current)} if current is not None else set()
        if self._ap_shop_price_modifier_pct != 0:
            vanilla = SHOP_PRICE_HINTS.get(str(name))
            if vanilla is not None:
                allowed.add(int(vanilla))
        return tuple(sorted(allowed))

    def _ap_shop_spend_matches(self, name: str, spent: int) -> bool:
        return int(spent) in self._ap_shop_allowed_spends(name)

    def _ap_shop_purchase_scene_proven(self) -> bool:
        """Reject stale Nativ zone hints while the Amber Quarry actor is live."""
        return bool(
            self._ap_current_zone == 'Nativs City'
            and self._ap_fast_travel_baselined
            and 0x0088 not in self._ap_fast_travel_keys.values()
        )

    def _ap_close_stale_shop_choice_dialog(self) -> None:
        """UI-thread cleanup after an actor-generation / savestate change."""
        try:
            win = self._ap_shop_choice_window
            if win is not None and win.winfo_exists():
                win.destroy()
        except Exception:
            pass
        self._ap_shop_choice_window = None
        self._ap_shop_choice_token = None
        self._ap_shop_choice_backlog.clear()

    def _ap_reset_shop_scene_evidence(self, now: float) -> None:
        """Discard non-durable purchase evidence on a new actor generation.

        AP ACKs and durable pending locations are untouched. A savestate or
        fast-travel replaces the inventory, Nooties and runtime stock address
        all at once; comparing them with the previous scene creates phantom
        spend tokens and ambiguous 1->0 shop checks.
        """
        had_evidence = bool(self._ap_shop_purchase_tokens or self._ap_shop_money_last is not None)
        if self._ap_shop_prompted_tokens or self._ap_shop_choice_token is not None:
            self._post_ui(self._ap_close_stale_shop_choice_dialog)
        self._ap_shop_money_last = None
        self._ap_shop_purchase_tokens.clear()
        self._ap_shop_manual_choices.clear()
        self._ap_shop_prompted_tokens.clear()
        self._ap_shop_deferred_prompt_tokens.clear()
        self._ap_shop_ambiguous_token_warned.clear()
        self._ap_shop_exact_reconcile_hints.clear()
        self._ap_shop_native_hints.clear()
        self._ap_shop_unpaired_live_hits.clear()
        self._ap_shop_unconfirmed_stock.clear()
        self._ap_shop_states.clear()
        self._ap_shop_reward_snapshots.clear()
        self._ap_shop_baselined = False
        self._ap_shop_live_reward_states.clear()
        self._ap_shop_live_baselined = False
        self._ap_shop_runtime_source = None
        self._ap_shop_runtime_candidates.clear()
        self._ap_shop_runtime_candidate_scores.clear()
        self._ap_shop_runtime_snapshots.clear()
        self._ap_shop_runtime_last_scan = 0.0
        self._ap_shop_runtime_prime_logged = False
        self._ap_shop_runtime_scan_fail_logged = False
        self._ap_shop_group_candidates.clear()
        self._ap_shop_group_scores.clear()
        self._ap_shop_group_snapshots.clear()
        self._ap_shop_group_rolling_states.clear()
        self._ap_shop_group_edge_events.clear()
        self._ap_shop_group_last_scan = 0.0
        self._ap_shop_group_scan_logged = False
        self._ap_shop_group_prime_logged = False
        self._ap_shop_native.reset()
        if hasattr(self, '_ap_shop_sold_observer'):
            self._ap_shop_sold_observer.reset()
        self._ap_shop_native_sold_state_last = {}
        self._ap_shop_native_hints.clear()
        self._ap_shop_native_ready_logged = False
        self._ap_shop_native_last_attempt = 0.0
        self._ap_shop_native_last_report = None
        self._ap_shop_native_last_report_at = 0.0
        self._ap_shop_live_ignore_until = max(self._ap_shop_live_ignore_until, now + 1.0)
        if had_evidence:
            self._log_threadsafe(
                'SHOP SCENE RESET: stale Nooties/stock/inventory baselines discarded; '
                'AP checks and durable pending locations preserved.', 'info')

    def _ap_stream_guard_tick(self, pine: PineClient, d: dict) -> bool:
        """Single-owner memory barrier during scene streaming (no writes).

        A departing Nativ FT room unloads before the next scene's actors are
        usable. The old Launcher resumed inventory, shops and access writers
        immediately; the working BAT did not. Wait for an Actor-Manager list
        generation that stays valid long enough before resuming AP writers.
        The barrier NEVER modifies game memory or destination FT chains.
        """
        if not bool(d.get("FAST_TRAVEL_STREAM_GUARD", True)):
            self._ap_stream_hold = False
            return False
        now = time.monotonic()
        generation = None
        try:
            manager = int(pine.read32(int(d["ADDR_ACTOR_MANAGER_GLOBAL"])))
            if self._ap_valid_pointer(manager):
                active, count = pine.read32_many([
                    manager + int(d["ACTOR_MANAGER_ACTIVE_LIST_OFFSET"]),
                    manager + int(d["ACTOR_MANAGER_ACTIVE_COUNT_OFFSET"]),
                ])
                if (self._ap_valid_pointer(int(active))
                        and 0 < int(count) <= int(d["ACTOR_MANAGER_MAX_ACTIVE"])):
                    generation = (manager, int(active))
        except Exception:
            pass

        if generation is None:
            if not self._ap_stream_hold:
                self._log_threadsafe("FT STREAM GUARD: actor list unavailable; all AP writes paused.", "warn")
            self._ap_stream_hold = True
            self._ap_stream_candidate = None
            self._ap_stream_ready_since = 0.0
            return True

        if generation != self._ap_stream_candidate:
            self._ap_reset_shop_scene_evidence(now)
            self._ap_stream_candidate = generation
            self._ap_stream_ready_since = now
            self._ap_stream_hold = True
            self._ap_stream_last_valid_generation = generation
            self._log_threadsafe(
                f"FT STREAM GUARD: actor generation 0x{generation[0]:08X}/0x{generation[1]:08X}; settling before AP writes.",
                "info",
            )
            return True

        # A FT departure must not restart writers into the previous Nativ
        # generation, even if PCSX2 temporarily still reports its old list.
        if (self._ap_stream_departure_generation is not None
                and generation == self._ap_stream_departure_generation):
            return True

        stable_for = float(d.get("FAST_TRAVEL_STREAM_STABLE_SECONDS", 1.50))
        if now - self._ap_stream_ready_since < stable_for:
            return True

        if self._ap_stream_hold:
            self._ap_stream_hold = False
            self._ap_stream_departure_generation = None
            # All actor addresses are ephemeral. On a new scene, rebuild live
            # baselines from the new generation, not stale runtime pointers.
            self._ap_next_actor_refresh = 0.0
            self._ap_fast_travel_baselined = False
            self._ap_special_baselined = False
            self._ap_next_poll = 0.0
            self._log_threadsafe(
                f"FT STREAM GUARD RELEASE: new actor list stable {now-self._ap_stream_ready_since:.2f}s; AP watchers resumed.",
                "ok",
            )
        return False

    def _ap_first_brazul_read_only_tick(self, pine: PineClient) -> None:
        """Watch the first Brazul *live edge* independently of actor streaming.

        Amber Quarry's actor vote often remains ``The Quarry``. The ordinary
        special-location watcher is reset whenever the actors disappear for a
        cutscene; it can baseline the completed flag=2 and lose the check.
        Here we sample the same verified ScenarioVar before the stream guard,
        without modifying the game. We only accept an observed 0/1 -> 2 edge
        after the player has spent >=0.5s in the correct area with a
        *previously unfinished* flag. No 100%-save/persistent-state recovery.
        """
        if not (self._ap_joined and self._ap_seed_build_verified and self._ap_link):
            return
        now = time.monotonic()
        if now < self._ap_first_brazul_next_poll:
            return
        self._ap_first_brazul_next_poll = now + 0.10
        name = 'Amber Quarry - Brazul First Encounter'
        loc_id = self._ap_data.get('LOCATION_NAME_TO_ID', {}).get(name)
        condition = self._ap_data.get('SPECIAL_LOCATION_CONDITIONS', {}).get(name)
        if loc_id is None or not condition or len(condition) != 1:
            return  # Seed/data without this location; never guess a flag.
        addr, final_state = (int(v) for v in condition[0])
        try:
            current = int(pine.read32(addr))
        except Exception:
            # The stream may be unloading. Retain the last actual sample.
            return
        previous = self._ap_first_brazul_last_value
        self._ap_first_brazul_last_value = current
        # The live 0x0088 secondary FT actor belongs to Amber Quarry. The
        # zone-vote can remain stale at Nativs City after loading a savestate:
        # the player's 06:26:58 trace proved the 1->2 edge was rejected solely
        # because of that hint. Read the current actor keys (never RAM-write).
        amber_ft_seen = bool(
            self._ap_fast_travel_baselined
            and 0x0088 in self._ap_fast_travel_keys.values()
            and not self._ap_stream_hold
        )
        in_quarry = bool(self._ap_current_zone in ('The Quarry', 'Amber Quarry')
                         or amber_ft_seen)
        if (previous in (0, 1) and current == final_state):
            self._log_threadsafe(
                f'BRAZUL FIRST TRACE: ScenarioVar 0x{addr:08X} '
                f'{previous}->{current}; detected zone={self._ap_current_zone or "?"}; '
                f'Quarry area eligible={in_quarry}; '
                f'Amber FT 0x0088 actor evidence={amber_ft_seen}.', 'info')
        if not in_quarry:
            self._ap_first_brazul_zone_since = None
            return
        if self._ap_first_brazul_zone_since is None:
            self._ap_first_brazul_zone_since = now
        # Reconnection, 100% saves and completed cutscenes are not valid
        # evidence. A fresh baseline at state=2 must never send a check.
        if previous is None or previous == final_state:
            return
        if previous not in (0, 1) or current != final_state:
            return
        if now - self._ap_first_brazul_zone_since < 0.5:
            self._log_threadsafe(
                'BRAZUL FIRST TRACE: 0/1->2 during early scene/zone setup; '
                'not enough stable area evidence; check NOT sent.', 'warn')
            return
        lid = int(loc_id)
        if lid in self._ap_checked or lid in self._ap_pending_checks:
            return
        if self._ap_queue_location_check(self._ap_link, lid, name, self._ap_data):
            self._ap_special_states[name] = True
            self._log_threadsafe(
                'BRAZUL FIRST LIVE CHECK queued: verified Quarry/Amber FT scene, '
                f'ScenarioVar 0x{addr:08X} {previous}->{current}; '
                'independent of the actor/stream watcher.', 'ok')

    def _ap_goal_read_only_tick(self, pine: PineClient) -> None:
        """Always-on final-boss/Goal heartbeat, independent of streaming and MAP.

        It reads stable ScenarioVars, but ONLY Brazul influences victory; it NEVER writes game memory,
        relies on no player actor/zone and never processes item effects.
        It may enqueue an observed boss AP location and report victory.
        """
        if not (self._ap_joined and self._ap_seed_build_verified):
            return
        now = time.monotonic()
        if now < self._ap_next_goal_poll:
            return
        self._ap_next_goal_poll = now + 0.25
        d = self._ap_data
        try:
            brazul, credits = pine.read32_many([
                int(d['ADDR_GOAL_BRAZUL_FINAL']), int(d['ADDR_GOAL_CREDITS'])])
            self._ap_process_goal_sample(int(brazul), int(credits), d)
            if (self._ap_goal_reached and not self._ap_goal_status_sent
                    and self._ap_link is not None):
                self._ap_link.goal()
                self._ap_goal_status_sent = True
                if not self._ap_goal_message_logged:
                    self._log_threadsafe('Game finished! Congratulations! (scene-independent goal polling)', 'ok')
                    self._ap_goal_message_logged = True
        except Exception:
            # Game memory may disappear during an elevator or credits transition.
            # A read failure must never resume AP writers prematurely.
            return

    def _ap_ft_finish_sanctuary_session(self) -> None:
        """Run the old FT post-session reset once, not after each scan slice."""
        self._ap_ft_initial_cleanroom_consumed = True
        if self._ap_ft_session_departed:
            self._ap_ft_cleanroom_continuation = None
        self._ap_ft_waiting_for_nativ_exit = bool(self._ap_ft_session_departed)
        self._ap_ft_nativ_absent_since = 0.0
        self._ap_next_actor_refresh = 0.0
        self._ap_next_inventory_reconcile = 0.0
        self._ap_next_combat_poll = 0.0
        self._ap_shop_native_last_attempt = 0.0
        self._ap_shop_group_last_scan = 0.0
        self._ap_shop_live_ignore_until = max(self._ap_shop_live_ignore_until, time.monotonic() + 0.25)
        self._ap_access_guard_next = 0.0
        self._ap_ft_next_room_probe = time.monotonic() + 0.20
        self._ap_ft_last_source_signature = None

    def _ap_tick(self, pine: PineClient) -> None:
        # 0.9.55: A cleanroom session runs cooperatively across owner ticks.
        # Resume BEFORE any normal AP watcher or memory writer can run. This
        # preserves the original BAT exclusivity while allowing the calling
        # PINE service to perform one signature heartbeat between each scan.
        if self._ap_ft_cleanroom_active:
            self._pine_service_stage = 'FT cleanroom scan'
            if self._ap_ft_sanctuary_session(pine, self._ap_data):
                self._ap_ft_finish_sanctuary_session()
            return
        # IMPORTANT: AP packet processing below also needs the embedded data.
        # An earlier build initialized this variable only *after* the event loop, so a
        # Connected packet could crash the watcher with UnboundLocalError.
        d = self._ap_data
        link = self._ap_link
        # Critical: decide BEFORE receiving AP items/ACKs or touching any
        # controller, panels, shop, elevator lock, inventory or camera state.
        if self._ap_stream_guard_tick(pine, d):
            return
        # Must run BEFORE AP ReceivedItems and inventory reconciliation. The
        # cutscene marks captivity via bracelet bit 0x10000; the scenario flag
        # persists after vanilla gives equipment back, but not the six Runes.
        self._ap_brazul_capture_tick(pine)

        # V0.9.1 RETURN-SIGNATURE + PROXIMITY GATE. Persistent actor keys in Kya are
        # scene-local, not globally unique. V0.8.45 treated the presence of a
        # single Nativ FT key/master as proof that Nativs City was loaded; the
        # same numeric keys can exist in Flying Forest/Hunters Domain, which
        # re-entered the cleanroom in the destination, froze Wolfen detection,
        # and wrote Nativ button masks into unrelated Fast Travel actors.
        #
        # The new gate only arms from the *complete Nativ wooden-room
        # fingerprint*: all 8 expected kiosk Masters plus their 8 fixed C2D0
        # handler -> Master reverse links.  That fingerprint is unique to the
        # Nativ Fast Travel room and cannot be satisfied by a destination zone.
        probe_now = time.monotonic()
        if (
            self._ap_joined
            and self._ap_seed_build_verified
            and self._ap_fast_travel_progression == "archipelago"
            and self._ap_starting_fast_travel_routes
            and not self._ap_ft_cleanroom_pending
            and not self._ap_ft_cleanroom_active
            and probe_now >= self._ap_ft_next_room_probe
        ):
            self._ap_ft_next_room_probe = probe_now + 0.08
            try:
                nativ_ft_verified = self._ap_ft_nativ_room_owner_present(pine, d)
            except Exception:
                nativ_ft_verified = False

            if self._ap_ft_waiting_for_nativ_exit:
                if not nativ_ft_verified:
                    if self._ap_ft_nativ_absent_since <= 0.0:
                        self._ap_ft_nativ_absent_since = probe_now
                    elif probe_now - self._ap_ft_nativ_absent_since >= 0.75:
                        self._ap_ft_waiting_for_nativ_exit = False
                        self._ap_ft_nativ_absent_since = 0.0
                        # A fresh streamed FT room needs a fresh early panel pass.
                        self._ap_ft_early_panels_done = False
                        self._ap_ft_early_panels_retry_at = 0.0
                        self._ap_ft_nativ_return_generation += 1
                        self._log_threadsafe(
                            "FT ROOM OWNER reset: Nativ FT room absent for 0.75s; destination watchers stay active until a real Nativ return.",
                            "info",
                        )
                else:
                    self._ap_ft_nativ_absent_since = 0.0
            elif nativ_ft_verified:
                # Structural presence identifies Nativs City even when its only
                # mapped Wolfen is already freed.  This recovery is independent
                # from whether the FT cleanroom actually needs to own PINE.
                if self._ap_current_zone != "Nativs City":
                    old_zone = self._ap_current_zone or "?"
                    self._ap_current_zone = "Nativs City"
                    self._ap_baselined = False
                    self._ap_special_baselined = False
                    self._ap_fast_travel_baselined = False
                    self._ap_fast_travel_states.clear()
                    self._ap_fast_travel_keys.clear()
                    self._log_threadsafe(
                        f"FT RETURN ZONE RECOVERY: structural Nativ room signature overrides stale zone hint {old_zone} -> Nativs City.",
                        "ok",
                    )

                # V0.9.1: do NOT freeze shops/Wolfen/access simply because the
                # FT room remains streamed. The cleanroom owns PINE only when Kya
                # is physically close enough to interact with the FT sources.
                room_dist = self._ap_ft_nativ_player_distance(pine, d)
                # V0.9.18: pre-open the wooden barriers as soon as the fully
                # fingerprinted Nativ room is streamed, before the 14m FT
                # interaction cleanroom starts. This changes only the wooden
                # C2D0 trigger radii temporarily; no remote FT chain is touched.
                early_radius = float(d.get("FAST_TRAVEL_EARLY_PANEL_RADIUS", 34.0))
                if (room_dist is not None and room_dist <= early_radius
                        and not getattr(self, "_ap_ft_early_panels_done", False)
                        and probe_now >= getattr(self, "_ap_ft_early_panels_retry_at", 0.0)):
                    self._ap_ft_early_panels_retry_at = probe_now + 1.0
                    try:
                        wood_keys = {int(x) for x in d.get("NATIV_WOOD_MASTER_KEYS", {}).values()}
                        wood_keyed = self._ap_ft_scan_keyed(pine, d, {int(d["MASTER_EVENT_VTABLE"])})
                        status = self._ap_ft_sanctuary_open_panels_exact(pine, wood_keyed, d)
                        if status:
                            self._log_threadsafe("FT EARLY WOOD PANELS: " + ", ".join(
                                f"0x{k:04X}={v}" for k, v in sorted(status.items())), "info")
                            self._ap_ft_early_panels_done = all(v in ("OPEN", "ALREADY") for v in status.values())
                    except Exception as exc:
                        self._log_threadsafe(f"FT EARLY WOOD PANELS retry: {exc}", "warn")
                if room_dist is not None and room_dist <= 14.0:
                    self._ap_ft_cleanroom_pending = True
                    self._log_threadsafe(
                        f"FT ROOM OWNER: structural Nativ room confirmed and Kya is within {room_dist:.2f}m; AP buttons rehydrating.",
                        "ok",
                    )

        if link is not None:
            while True:
                # While Fast Travel owns the memory bus, keep receiving AP packets
                # but postpone packets that can trigger game-memory writes. Once
                # the FT transaction ends, deferred packets are replayed FIFO.
                ft_memory_hold = bool(
                    self._ap_ft_exclusive
                    or self._ap_ft_cleanroom_pending
                    or self._ap_ft_cleanroom_active
                )
                if (not ft_memory_hold) and self._ap_ft_deferred_events:
                    kind, payload = self._ap_ft_deferred_events.pop(0)
                else:
                    try: kind, payload = link.events.get_nowait()
                    except queue.Empty: break

                # Once the seed has been joined, the cleanroom may already be
                # pending.  ReceivedItems / RoomUpdate are kept FIFO until the
                # BAT-equivalent FT transaction finishes.  This is deliberately
                # stricter than V42: even writes that happened *before* the room
                # was fully streamed are excluded from the test.
                if ft_memory_hold and kind in ("room_update", "item"):
                    self._ap_ft_deferred_events.append((kind, payload))
                    if not self._ap_ft_defer_logged:
                        self._ap_ft_defer_logged = True
                        self._log_threadsafe(
                            "FT CLEANROOM: AP memory-changing events are queued until the BAT transaction ends.",
                            "info",
                        )
                    continue

                if kind == "link_lost":
                    self._ap_joined = False
                    self._ap_seed_build_verified = False
                    self._ap_goal_status_sent = False
                    # No old credits candidate can survive a server reconnect.
                    self._ap_goal_auto_candidate_at = None
                    self._ap_goal_auto_candidate_samples = 0
                    self._ap_goal_fortress_since = None
                    self._ap_goal_boss_witness_at = None
                    self._log_threadsafe(str(payload), "warn")
                    continue
                if kind == "error":
                    self._log_threadsafe(f"Archipelago error: {payload}", "error")
                    link.close(); self._ap_link = None; self._ap_joined = False
                    self._ap_seed_build_verified = False
                    self._ap_goal_status_sent = False
                    return
                if kind == "status":
                    self._log_threadsafe(str(payload), "info")
                elif kind == "roominfo":
                    version = payload.get("version") if isinstance(payload, dict) else None
                    if isinstance(payload, dict):
                        self._ap_seed_name = str(payload.get("seed_name") or "").strip()
                    self._log_threadsafe(f"Archipelago RoomInfo received (server version={version}).", "info")
                elif kind == "joined":
                    # A new/rejoined AP room must NOT inherit an earlier candidate.
                    self._ap_goal_auto_candidate_at = None
                    self._ap_goal_auto_candidate_samples = 0
                    self._ap_goal_fortress_since = None
                    self._ap_goal_boss_witness_at = None
                    # Each AP Connected is followed by authoritative full ReceivedItems.
                    # Rebuild cumulative progression from zero to avoid duplicate levels
                    # on automatic reconnections; cursor still protects one-shot rewards.
                    self._ap_item_counts.clear()
                    self._ap_rune_rollback_due.clear()  # new server authority; restart grace window
                    self._ap_checked = set(int(x) for x in payload.get("checked_locations", []))
                    try:
                        self._ap_slot_id = int(payload.get("slot")) if payload.get("slot") is not None else None
                    except (TypeError, ValueError):
                        self._ap_slot_id = None
                    slot_data = payload.get("slot_data", {}) if isinstance(payload, dict) else {}
                    self._ap_slot_data = dict(slot_data) if isinstance(slot_data, dict) else {}
                    try:
                        self._ap_nooties_modifier_pct = self._ap_normalize_economy_percent(int(self._ap_slot_data.get("ap_nooties_modifier", 0)))
                    except (TypeError, ValueError):
                        self._ap_nooties_modifier_pct = 0
                    try:
                        self._ap_shop_price_modifier_pct = self._ap_normalize_economy_percent(int(self._ap_slot_data.get("shop_price_modifier", 0)))
                    except (TypeError, ValueError):
                        self._ap_shop_price_modifier_pct = 0
                    self._ap_shop_native.set_price_modifier(self._ap_shop_price_modifier_pct)
                    self._ap_shop_price_modifier_logged = None
                    self._log_threadsafe(
                        "AP slot economy received: "
                        f"raw Nooties={self._ap_slot_data.get('ap_nooties_modifier', '<missing>')!r}, "
                        f"raw shop={self._ap_slot_data.get('shop_price_modifier', '<missing>')!r}; "
                        f"applied={self._ap_nooties_modifier_pct:+d}%/"
                        f"{self._ap_shop_price_modifier_pct:+d}%.",
                        "info",
                    )

                    raw_ft_mode = self._ap_slot_data.get("fast_travel_progression", 0)
                    if isinstance(raw_ft_mode, str):
                        self._ap_fast_travel_progression = "vanilla" if raw_ft_mode.lower() == "vanilla" else "archipelago"
                    else:
                        try:
                            self._ap_fast_travel_progression = "vanilla" if int(raw_ft_mode) == 1 else "archipelago"
                        except (TypeError, ValueError):
                            self._ap_fast_travel_progression = "archipelago"
                    raw_routes = self._ap_slot_data.get("starting_fast_travel_routes", [])
                    self._ap_starting_fast_travel_routes = []
                    hydrated_routes = 0
                    route_catalog_by_id = {}
                    route_catalog_by_source_index = {}
                    route_catalog = d.get("FAST_TRAVEL_ALLOWED_ROUTES", {})
                    if isinstance(route_catalog, dict):
                        for _zone_name, _routes in route_catalog.items():
                            if not isinstance(_routes, list):
                                continue
                            for _meta in _routes:
                                if not isinstance(_meta, dict):
                                    continue
                                _rid = str(_meta.get("id", "")).strip()
                                if _rid:
                                    route_catalog_by_id[_rid] = dict(_meta)
                                try:
                                    _sig = (int(_meta["source_key"]), int(_meta["source_index"]))
                                    route_catalog_by_source_index[_sig] = dict(_meta)
                                except (KeyError, TypeError, ValueError):
                                    pass
                    if self._ap_fast_travel_progression == "archipelago" and isinstance(raw_routes, list):
                        for raw_route in raw_routes:
                            if not isinstance(raw_route, dict):
                                continue
                            try:
                                slot_route = dict(raw_route)
                                for field in ("source_key", "source_index", "target_key", "master_key"):
                                    slot_route[field] = int(slot_route[field])
                                # V0.9.6: slot_data is authoritative for WHICH route was
                                # selected, while fast_travel.json is authoritative for
                                # route-specific runtime metadata (arrival radius, Quarry
                                # cleanup mask, Air Post tail settings, Hunters departure
                                # profile, etc.).  Earlier modular builds never merged the
                                # two, so all those JSON fields were silently ignored.
                                meta = route_catalog_by_id.get(str(slot_route.get("id", "")))
                                if meta is None:
                                    meta = route_catalog_by_source_index.get((
                                        int(slot_route["source_key"]),
                                        int(slot_route["source_index"]),
                                    ))
                                if meta is not None:
                                    route = dict(meta)
                                    route.update(slot_route)
                                    hydrated_routes += 1
                                else:
                                    route = slot_route
                                for field in ("source_key", "source_index", "target_key", "master_key"):
                                    route[field] = int(route[field])
                                self._ap_starting_fast_travel_routes.append(route)
                            except (KeyError, TypeError, ValueError):
                                continue
                    if self._ap_fast_travel_progression == "archipelago" and self._ap_starting_fast_travel_routes:
                        self._log_threadsafe(
                            f"FT JSON route metadata hydrated: {hydrated_routes}/{len(self._ap_starting_fast_travel_routes)} selected route(s).",
                            "ok" if hydrated_routes == len(self._ap_starting_fast_travel_routes) else "warn",
                        )

                    # V0.9.9 beta rule: full destination-pad routing is postponed.
                    # Any unlocked route for a world now means "that world's FT01".
                    # This preserves the AP unlock decision (which worlds are available)
                    # while collapsing every destination to the first Fast Travel only.
                    if (
                        self._ap_fast_travel_progression == "archipelago"
                        and bool(d.get("FAST_TRAVEL_ENTRY_ONLY_BETA", False))
                        and self._ap_starting_fast_travel_routes
                    ):
                        primary_by_source = {}
                        for _zone_name, _routes in route_catalog.items() if isinstance(route_catalog, dict) else []:
                            if not isinstance(_routes, list):
                                continue
                            _primary = next((dict(_r) for _r in _routes if isinstance(_r, dict) and int(_r.get("source_index", -1)) == 0), None)
                            if _primary is not None:
                                try:
                                    primary_by_source[int(_primary["source_key"])] = _primary
                                except (KeyError, TypeError, ValueError):
                                    pass
                        _normalized = []
                        _seen_sources = set()
                        for _route in self._ap_starting_fast_travel_routes:
                            try:
                                _source = int(_route.get("source_key", -1))
                            except (TypeError, ValueError):
                                continue
                            if _source in _seen_sources:
                                continue
                            _seen_sources.add(_source)
                            _primary = primary_by_source.get(_source)
                            _normalized.append(dict(_primary) if _primary is not None else dict(_route))
                        self._ap_starting_fast_travel_routes = _normalized
                        self._log_threadsafe(
                            "FT V0.9.21 BAT FT01: unlocked worlds normalized to FT01; "
                            "Launcher never discovers destination FT01; confirmed local FT01s are handed back to vanilla.",
                            "warn",
                        )

                    self._ap_initial_fast_travel_route_ids = {str(r.get("id", "")) for r in self._ap_starting_fast_travel_routes}
                    self._ap_selected_target_keys = {int(r["target_key"]) for r in self._ap_starting_fast_travel_routes}
                    # New seeds are unequivocal: AP FT locks both Nativ exits;
                    # vanilla FT leaves both to vanilla.  Legacy seeds retain their
                    # original slot_data flags so updating Launcher cannot brick
                    # an existing generation which chose different entry rules.
                    if self._ap_slot_data.get("automatic_entry_access_locks") is True:
                        self._ap_lock_the_root = self._ap_fast_travel_progression == "archipelago"
                        self._ap_lock_flying_forest = self._ap_fast_travel_progression == "archipelago"
                    else:
                        self._ap_lock_the_root = bool(self._ap_slot_data.get("lock_the_root", False))
                        self._ap_lock_flying_forest = bool(self._ap_slot_data.get("lock_flying_forest", False))
                    self._ap_lock_wolfen_city = bool(self._ap_slot_data.get("lock_wolfen_city", False))
                    self._ap_lock_the_fortress = bool(self._ap_slot_data.get("lock_the_fortress", False))
                    if self._ap_fast_travel_progression == "vanilla":
                        self._ap_lock_the_root = False
                        self._ap_lock_flying_forest = False
                        self._ap_lock_wolfen_city = False
                        self._ap_lock_the_fortress = False
                    else:
                        self._ap_ft_restore_natural_routes(d)
                    self._ap_ft_reset_runtime()

                    server_build = str(slot_data.get("prototype_version", "<missing>")) if isinstance(slot_data, dict) else "<missing>"
                    launcher_build = str(d.get("AP_BUILD_VERSION") or d.get("PROTOTYPE_VERSION") or "<unknown>")
                    compatible_builds = {str(v) for v in d.get("AP_COMPATIBLE_BUILDS", [launcher_build])}
                    compatible_builds.add(launcher_build)
                    if server_build not in compatible_builds:
                        self._ap_joined = False
                        self._ap_seed_build_verified = False
                        self._log_threadsafe(
                            f"AP BUILD MISMATCH: seed={server_build} | compatible={', '.join(sorted(compatible_builds))}.",
                            "error",
                        )
                    else:
                        self._ap_joined = True
                        self._ap_seed_build_verified = True
                        self._log_threadsafe(
                            f"Archipelago slot joined. AP build verified: {server_build}. "
                            f"Server already has {len(self._ap_checked)} checked Kya locations.",
                            "ok",
                        )
                        self._log_threadsafe(
                            f"Economy settings (10% steps): AP Nooties {self._ap_nooties_modifier_pct:+d}% | "
                            f"Shop prices {self._ap_shop_price_modifier_pct:+d}%.",
                            "ok",
                        )
                        route_labels = ", ".join(str(r.get("label", r.get("id", "?"))) for r in self._ap_starting_fast_travel_routes) or "none"
                        self._log_threadsafe(
                            f"Fast Travel settings: mode={self._ap_fast_travel_progression} | starts={len(self._ap_starting_fast_travel_routes)} | "
                            f"Root lock={'ON' if self._ap_lock_the_root else 'OFF'} | Flying Forest lock={'ON' if self._ap_lock_flying_forest else 'OFF'} | {route_labels}",
                            "ok",
                        )
                        # V0.8.49: NEVER arm the FT cleanroom from AP-join timing.
                        # The Connected packet can arrive either before or after the first
                        # Nativ Wolfen is released; using it as a gate created a race where
                        # the Wolfen watcher was frozen on some launches.  Ownership is now
                        # acquired only when the actual Nativ FT room is physically present.
                        if server_build == '0.8.14-ft-safe-shop-audit':
                            self._log_threadsafe(
                                'FT ITEM SAFETY: this seed places NO advancement/key items '
                                'on Fast Travel checks; 0.8.13 did not enforce this. '
                                'Live/pending check replay remains the only FT recovery.', 'ok')
                        self._ap_load_pending_checks(d)
                        self._ap_load_detector_handoffs(d)
                        self._ap_load_item_cursor(d)
                        self._ap_life_gauge_key = "|".join((
                            self.name_var.get().strip().lower(),
                            server_build,
                            self._ap_seed_name or "unknown-seed",
                        ))
                        already_acked = set(self._ap_pending_checks) & self._ap_checked
                        if already_acked:
                            self._ap_ack_pending_checks(already_acked, d)
                        resend = sorted(i for i in self._ap_pending_checks if i not in self._ap_checked)
                        if resend:
                            for location_id in resend:
                                link.check(location_id)
                            pending_ft = sum(
                                1 for i in resend
                                if 'Fast Travel' in str(self._ap_pending_checks.get(i, '')))
                            pending_shops = sum(
                                1 for i in resend
                                if ' - Shop - ' in str(self._ap_pending_checks.get(i, '')))
                            self._log_threadsafe(
                                f"Resent {len(resend)} durable pending Kya check(s) after reconnect "
                                f"(FT={pending_ft}, Shop={pending_shops}). "
                                "Only live witnessed checks are replayed; no inference from 100% saves.",
                                "info",
                            )
                        # ReceivedItems packets are the authoritative ordered stream.
                        # Do not also replay any non-standard Connected payload here;
                        # doing so would double-count progressive items.
                elif kind == "room_update":
                    if isinstance(payload, dict) and "checked_locations" in payload:
                        updated = set(int(x) for x in payload.get("checked_locations", []))
                        newly_acked = updated - self._ap_checked
                        self._ap_checked |= updated
                        if newly_acked:
                            self._ap_ack_pending_checks(newly_acked, d)
                            for acked_id in list(newly_acked):
                                pending_shop = self._ap_pending_shop_suppressions.get(acked_id)
                                if pending_shop is not None:
                                    self._ap_suppress_shop_reward(pine, acked_id, pending_shop)
                                pending_life = self._ap_pending_special_life_suppressions.get(acked_id)
                                if pending_life is not None:
                                    id_to_name_local = {int(v): k for k, v in d.get("LOCATION_NAME_TO_ID", {}).items()}
                                    self._ap_suppress_special_life_reward(
                                        pine, acked_id, id_to_name_local.get(acked_id, "Vanilla HP Up"), pending_life
                                    )
                            id_to_name = {int(v): k for k, v in d.get("LOCATION_NAME_TO_ID", {}).items()}
                            labels = ", ".join(self._ap_public_location_name(id_to_name.get(i, 'unknown')) for i in sorted(newly_acked))
                            self._log_threadsafe(f"Archipelago ACK: {labels}", "ok")
                elif kind == "item": self._apply_ap_item(pine, payload)
                elif kind == "printjson":
                    data = payload.get("data", []) if isinstance(payload, dict) else []
                    text = "".join(str(part.get("text", "")) for part in data if isinstance(part, dict))
                    if text:
                        # AP PrintJSON sometimes uses bare 8-digit numeric IDs.
                        # Resolve them for the player without changing canonical
                        # names, IDs, or the packets sent to the server.
                        by_location_id = {int(v): self._ap_public_location_name(k)
                                          for k, v in d.get("LOCATION_NAME_TO_ID", {}).items()}
                        def display_id(match):
                            value = int(match.group(0))
                            return self._ap_items.get(value, by_location_id.get(value, match.group(0)))
                        text = re.sub(r"\b\d{8}\b", display_id, text)
                        self._log_threadsafe(text, "info")
                        self._handle_ap_printjson_overlay(payload, text)
                elif kind == "text":
                    # Backwards compatibility if an older APLink module is mixed in.
                    text = "".join(str(part.get("text", "")) for part in payload if isinstance(part, dict))
                    if text: self._log_threadsafe(text, "info")

        # V0.9.33: entry locks derived from FT mode for new seeds; preserve
        # legacy slot data on old seeds. Vanilla actors retain native control.
        # It yields completely to the critical FT cleanroom/bridge.
        self._ap_ft_access_guard_tick(pine, d)

        # V0.9.1 cleanroom lifecycle. Structural room identity is preserved, but
        # ownership is proximity-scoped so normal shops/Wolfen/access logic can
        # run while the FT room is merely streamed in the background.
        if self._ap_ft_cleanroom_pending and not self._ap_ft_cleanroom_active:
            self._ap_ft_cleanroom_pending = False
            self._ap_ft_session_departed = False
            self._pine_service_stage = 'FT cleanroom scan'
            if self._ap_ft_sanctuary_session(pine, d):
                self._ap_ft_finish_sanctuary_session()
            return

        now = time.monotonic()
        # Goal watcher runs before actor-manager reads. The last stable zone is
        # intentionally retained through cinematic streaming so the final
        # Fortress 1->2 transition remains zone-safe.
        if now >= self._ap_next_goal_poll:
            self._ap_next_goal_poll = now + 0.07
            brazul_address = int(d["ADDR_GOAL_BRAZUL_FINAL"])
            credits_address = int(d["ADDR_GOAL_CREDITS"])
            brazul_value, credits_value = pine.read32_many([brazul_address, credits_address])
            self._ap_process_goal_sample(brazul_value, credits_value, d)

        if link is not None and self._ap_goal_reached and self._ap_joined and self._ap_seed_build_verified and not self._ap_goal_status_sent:
            link.goal()
            self._ap_goal_status_sent = True
            if not self._ap_goal_message_logged:
                self._log_threadsafe("Game finished! Congratulations!", "ok")
                self._ap_goal_message_logged = True
            else:
                self._log_threadsafe("Kya goal status resent to Archipelago.", "info")
        if link is None:
            return
        if (self._ap_joined and self._ap_seed_build_verified
                and not self._ap_ft_sanctuary_enabled
                and not bool(d.get("FAST_TRAVEL_ACCESS_ONLY_TEST", True))):
            self._ap_ft_bridge_tick(pine, d, now)

        # V0.8.40 critical section: during the FT tunnel/arrival chain, NOTHING
        # else in the AP launcher may mutate game memory. The bridge itself has
        # everything it needs (Actor Manager scan, target patch, mana guard,
        # Master 5->6). Normal watchers resume only after confirmed arrival.
        if self._ap_ft_exclusive:
            return

        if now >= self._ap_next_inventory_reconcile:
            self._ap_next_inventory_reconcile = now + 0.50
            self._ap_reconcile_owned_inventory(pine, d)
        if self._ap_pending_hp_restore or self._ap_pending_magic_restore:
            self._ap_apply_pending_recovery(pine)
        if now >= self._ap_next_combat_poll:
            self._ap_next_combat_poll = now + 0.04
            self._ap_monitor_player_protection(pine, d)
        if now >= self._ap_next_actor_refresh:
            self._ap_next_actor_refresh = now + 0.40
            manager = pine.read32(int(d["ADDR_ACTOR_MANAGER_GLOBAL"]))
            if not (0x00100000 <= manager < 0x02000000 and manager % 4 == 0):
                self._ap_log_actor_manager_state(
                    ("invalid_manager", manager),
                    f"Actor Manager pointer unavailable: manager=0x{manager:08X}",
                )
                return
            active, count = pine.read32_many([manager+int(d["ACTOR_MANAGER_ACTIVE_LIST_OFFSET"]), manager+int(d["ACTOR_MANAGER_ACTIVE_COUNT_OFFSET"])])
            if not (0x00100000 <= active < 0x02000000 and count <= int(d["ACTOR_MANAGER_MAX_ACTIVE"])):
                self._ap_log_actor_manager_state(
                    ("invalid_list", manager, active),
                    f"Actor Manager list unavailable: manager=0x{manager:08X}, list=0x{active:08X}",
                )
                return
            self._ap_log_actor_manager_state(
                ("valid", manager, active),
                f"Actor Manager addresses changed/available: manager=0x{manager:08X}, list=0x{active:08X}",
            )
            self._ap_actor_count=count
            slots = pine.read32_many([active+i*4 for i in range(count)]) if count else []
            actors = sorted(set(a for a in slots if 0x00100000 <= a < 0x02000000 and a%4==0))
            vtables = pine.read32_many(actors) if actors else []
            self._ap_lava_worm_witness_tick(pine, d, actors, vtables, active, now)

            if self._ap_joined and self._ap_seed_build_verified:
                # V0.8.42: enter the Fast Travel sanctuary BEFORE any of the normal
                # zone/shop/inventory/wolfen writers below can run. This reproduces
                # the standalone sidecar environment from the moment the complete
                # Nativ FT room exists, not only after the loading tunnel begins.
                # V0.8.43 cleanroom is entered near the top of _ap_tick, before
                # normal writers.  Do not invoke the old late V42 sanctuary here.
                # Outside a cleanroom transaction the legacy world guard remains
                # available for non-Nativ gameplay / post-arrival state.
                self._ap_ft_world_guard(pine, actors, vtables, d)

            # Validation build: Fast Travel actors use a distinct vtable and a
            # live activation state at actor+0x2A0. Descriptor+0x28 is the
            # zone-scoped candidate identity recorded during mapping.
            fast_travels = sorted(a for a,vt in zip(actors,vtables) if vt==int(d["FAST_TRAVEL_VTABLE"]))
            ft_states = pine.read32_many([a+int(d["FAST_TRAVEL_STATE_OFFSET"]) for a in fast_travels]) if fast_travels else []
            ft_descs = pine.read32_many([a+int(d["FAST_TRAVEL_DESCRIPTOR_OFFSET"]) for a in fast_travels]) if fast_travels else []
            ft_valid = [(a,st,p) for a,st,p in zip(fast_travels,ft_states,ft_descs) if self._ap_valid_pointer(p)]
            ft_keys = pine.read32_many([p+int(d["FAST_TRAVEL_KEY_OFFSET"]) for _,_,p in ft_valid]) if ft_valid else []
            current_ft_states: dict[int,int] = {}
            current_ft_keys: dict[int,int] = {}
            for (a,st,_p),key in zip(ft_valid,ft_keys):
                if 0 < key < 0x10000:
                    current_ft_states[a]=st
                    current_ft_keys[a]=key
            if not self._ap_fast_travel_baselined:
                self._ap_fast_travel_states=current_ft_states
                self._ap_fast_travel_keys=current_ft_keys
                self._ap_fast_travel_baselined=True
                self._log_threadsafe(f"Fast Travel checks armed: zone={self._ap_current_zone or '?'}, active={len(current_ft_states)}", "info")
                if current_ft_keys:
                    diagnostic=", ".join(f"0x{current_ft_keys[a]:04X}={current_ft_states.get(a,-1)}" for a in sorted(current_ft_keys))
                    self._log_threadsafe(f"Fast Travel baseline candidates [{self._ap_current_zone or '?'}]: {diagnostic}", "info")
            else:
                zone_ft_map=d.get("FAST_TRAVEL_ZONE_KEY_TO_LOCATION",{}).get(self._ap_current_zone or "",{})
                entry_beta = bool(d.get("FAST_TRAVEL_ENTRY_ONLY_BETA", False))
                primary_routes_by_target = {}
                if entry_beta:
                    for _routes in d.get("FAST_TRAVEL_ALLOWED_ROUTES", {}).values():
                        if not isinstance(_routes, list):
                            continue
                        for _r in _routes:
                            if not isinstance(_r, dict) or int(_r.get("source_index", -1)) != 0:
                                continue
                            try:
                                primary_routes_by_target[int(_r["target_key"])] = _r
                            except (KeyError, TypeError, ValueError):
                                pass
                primary_target_keys = set(primary_routes_by_target) if entry_beta else None
                discovery_radius = float(d.get("FAST_TRAVEL_LOCAL_DISCOVERY_RADIUS", 10.0))
                state_off = int(d["FAST_TRAVEL_STATE_OFF"])
                state_on = int(d["FAST_TRAVEL_STATE_ON"])
                avail_off = int(d["FAST_TRAVEL_AVAILABLE_OFFSET"])
                active_off = int(d["FAST_TRAVEL_ACTIVE_OFFSET"])

                for a,st_raw in list(current_ft_states.items()):
                    st = int(st_raw)
                    key=current_ft_keys.get(a)
                    route = primary_routes_by_target.get(int(key)) if key is not None else None
                    source_key = None
                    if route is not None:
                        try:
                            source_key = int(route.get("source_key", -1))
                        except (TypeError, ValueError):
                            source_key = None

                    # V0.9.15: the bootstrap is allowed to load the zone, but it is
                    # NOT allowed to discover FT01.  While Kya is away from the pad
                    # we clamp only +0x2A0 (active) back to 0.  +0x2A4 available,
                    # masks, indices, actor state and C540 remain vanilla-owned.
                    if (
                        entry_beta
                        and key is not None
                        and int(key) in self._ap_ft_detector_guard_targets
                        and source_key is not None
                        and source_key not in self._ap_ft_detector_handoff_sources
                    ):
                        try:
                            dist = self._ap_ft_arrival_distance(pine, int(a), d)
                        except Exception:
                            dist = None
                        if dist is None or float(dist) > discovery_radius:
                            if st != state_off:
                                self._ap_ft_detector_hold_remote_active_off(
                                    pine, int(a), int(key), d, distance=dist
                                )
                                st = state_off
                                current_ft_states[a] = state_off
                        else:
                            # Inside the actual discovery radius the firewall is
                            # hands-off. The normal 0->1 edge block below remains
                            # the single place that can send the AP check/handoff.
                            # If active appears before the target/C540 chain is ready,
                            # keep the *watcher baseline* at 0 (without writing RAM) so
                            # the later genuine chain edge cannot be missed.
                            if st == state_on:
                                chain_ok, chain_desc = self._ap_ft_detector_chain_evidence(
                                    pine, int(a), d
                                )
                                if not chain_ok:
                                    current_ft_states[a] = state_off
                                    if int(key) not in self._ap_ft_detector_near_wait_logged:
                                        self._ap_ft_detector_near_wait_logged.add(int(key))
                                        self._log_threadsafe(
                                            f"FT DETECTOR NEAR: 0x{int(key):04X} active at {float(dist):.2f}m but local chain "
                                            f"not confirmed yet [{chain_desc}]; RAM untouched, no check/handoff.",
                                            "info",
                                        )

                    old_st=self._ap_fast_travel_states.get(a,st)
                    if old_st==state_off and st==state_on and key is not None:
                        name=zone_ft_map.get(str(key))
                        # 0.9.57: Amber's 0x0088 pad is unique and live-proven,
                        # but the Wolfen zone vote can remain Flying Forest or
                        # Nativs City through its entire scene. Resolve ONLY
                        # this key through its own actor-backed Amber mapping.
                        # Never use this fallback for any other zone/FT key.
                        amber_key = 0x0088
                        if int(key) == amber_key:
                            amber_name = d.get('FAST_TRAVEL_ZONE_KEY_TO_LOCATION', {}).get('Amber Quarry', {}).get(str(amber_key))
                            if amber_name is not None:
                                name = amber_name
                                # Older 0.8.11 seeds do not contain this AP
                                # location: never send them a phantom check.
                                required_build = str(d.get('FAST_TRAVEL_AMBER_AP_BUILD', ''))
                                current_build = str(self._ap_slot_data.get('prototype_version', ''))
                                if not required_build or current_build not in (required_build, '0.8.13-lava-witness-map-zoom', '0.8.14-ft-safe-shop-audit'):
                                    self._log_threadsafe(
                                        f'FT AMBER 0x0088: local activation observed, but seed={current_build} '
                                        f'has no Amber AP location (requires {required_build}); check NOT sent.', 'info')
                                    continue
                                # Memory Probe V1 confirmed both +0x2A0
                                # active and +0x2A4 available become 1 in the
                                # same local activation. Require both; never
                                # patch pad/index/mask/chain/remote destination.
                                available = int(pine.read32(int(a) + avail_off))
                                if available != state_on:
                                    # If active rises before available, retain
                                    # the 0 baseline until their real joint edge.
                                    # Never force any RAM value here.
                                    current_ft_states[a] = state_off
                                    self._log_threadsafe(
                                        f'FT AMBER 0x0088: active=1 but available={available}; '
                                        'local discovery not confirmed, no AP check.', 'info')
                                    continue
                                if name not in d.get('LOCATION_NAME_TO_ID', {}):
                                    self._log_threadsafe(
                                        'FT AMBER 0x0088: AP location absent from Launcher data; check NOT sent.', 'warn')
                                    continue
                        if (name == "Flying Forest - Fast Travel 04"
                                and str(self._ap_slot_data.get("prototype_version", "")) == "0.8.7-ft01-terrain-gates"):
                            self._log_threadsafe(
                                "FT04 0x0FB0 is mapped, but the running 0.8.7 seed "
                                "has no FT04 AP location. Requires a new 0.8.8 seed.", "info")
                            continue
                        if primary_target_keys is not None and int(key) not in primary_target_keys:
                            # Entry-only restricts the Nativ bootstrap, NOT local
                            # check detection. FT02+ are legitimate AP locations.
                            # Never unlock/patch their route from here; vanilla
                            # owns the travel mechanism after the FT01 arrival.
                            if name is None:
                                self._log_threadsafe(
                                    f"FT ENTRY-ONLY: unlisted secondary 0x{int(key):04X}; no AP location.",
                                    "info",
                                )
                                continue
                            try:
                                local_distance = self._ap_ft_arrival_distance(pine, int(a), d)
                            except Exception:
                                local_distance = None
                            if local_distance is None or local_distance > max(10.0, discovery_radius):
                                self._log_threadsafe(
                                    f"FT SECONDARY REMOTE: {name} 0x{int(key):04X} activation "
                                    f"ignored (distance={local_distance}).",
                                    "info",
                                )
                                continue
                            self._log_threadsafe(
                                f"FT SECONDARY LOCAL: {name} 0x{int(key):04X} "
                                f"0->1 near Kya ({local_distance:.2f}m); vanilla travel remains untouched.",
                                "ok",
                            )

                        # V0.9.15: ownership changes only after the read-only local
                        # chain detector has confirmed this one world.  A naked 0->1
                        # edge is never enough by itself.
                        if entry_beta and route is not None and source_key is not None:
                            if source_key not in self._ap_ft_detector_handoff_sources:
                                try:
                                    dist = self._ap_ft_arrival_distance(pine, int(a), d)
                                except Exception:
                                    dist = None
                                if dist is None or float(dist) > discovery_radius:
                                    self._ap_ft_detector_hold_remote_active_off(
                                        pine, int(a), int(key), d, distance=dist
                                    )
                                    current_ft_states[a] = state_off
                                    continue
                                chain_ok, chain_desc = self._ap_ft_detector_chain_evidence(
                                    pine, int(a), d
                                )
                                if not chain_ok:
                                    if int(key) not in self._ap_ft_detector_near_wait_logged:
                                        self._ap_ft_detector_near_wait_logged.add(int(key))
                                        self._log_threadsafe(
                                            f"FT DETECTOR EDGE WAIT: 0x{int(key):04X} 0->1 at {float(dist):.2f}m, "
                                            f"but chain is not confirmed [{chain_desc}]. No check/handoff yet.",
                                            "info",
                                        )
                                    continue
                                self._ap_ft_detector_guard_targets.discard(int(key))
                                self._ap_ft_detector_handoff_sources.add(int(source_key))
                                self._ap_ft_last_source_signature = None
                                self._ap_ft_detector_near_wait_logged.discard(int(key))
                                self._ap_save_detector_handoffs(d)
                                if int(source_key) not in self._ap_ft_detector_handoff_logged:
                                    self._ap_ft_detector_handoff_logged.add(int(source_key))
                                    self._log_threadsafe(
                                        f"FT DETECTOR CONFIRMED: {self._ap_current_zone} FT01 0x{int(key):04X} "
                                        f"locally discovered at {float(dist):.2f}m; chain [{chain_desc}]. "
                                        f"Only Nativ source 0x{int(source_key):04X} is now vanilla-owned.",
                                        "ok",
                                    )

                        # V0.9.4 anti-softlock: arm only after a confirmed local FT
                        # activation. Remote bootstrap side-effects never reach here.
                        if ((self._ap_current_zone or "") != "Nativs City"
                                and (not entry_beta or int(key) in primary_target_keys)):
                            # Secondary FT checks remain strictly read-only in
                            # FT01 entry mode: no newly armed rescue/writes.
                            try:
                                self._ap_ft_arm_mana_stall_rescue(
                                    pine, d,
                                    name or f"{self._ap_current_zone or '?'} Fast Travel 0x{int(key):04X}",
                                    now,
                                )
                            except Exception:
                                pass
                        if (
                            self._ap_fast_travel_progression == "archipelago"
                            and int(key) in self._ap_selected_target_keys
                            and not entry_beta
                        ):
                            continue
                        if name is not None:
                            self._ap_ft_unlock_route_for_location(name, d)
                            lid=int(d["LOCATION_NAME_TO_ID"][name])
                            if self._ap_joined and self._ap_seed_build_verified and lid not in self._ap_checked:
                                self._ap_queue_location_check(link, lid, name, d)
                                self._log_threadsafe(f"CHECK queued -> Archipelago: {self._ap_public_location_name(name)}", "ok")
                            elif not self._ap_joined or not self._ap_seed_build_verified:
                                self._log_threadsafe(f"CHECK detected but NOT sent (AP handshake/build not verified): {name} [id={lid}]", "warn")
                            self._log_threadsafe(
                                f"LIVE Fast Travel [{self._ap_current_zone}] key 0x{int(key):04X}: {name} | 0->1 (local check)",
                                "info",
                            )
                        else:
                            self._log_threadsafe(f"UNMAPPED Fast Travel activation [{self._ap_current_zone or '?'}] key 0x{int(key):04X} actor=0x{a:08X}", "warn")
                self._ap_fast_travel_states=current_ft_states
                self._ap_fast_travel_keys=current_ft_keys

            # V0.9.4: short-lived, event-driven anti-softlock monitor. It is
            # completely dormant unless a Fast Travel activation/arrival armed it.
            self._ap_ft_mana_stall_rescue_tick(pine, d, now)

            wolfens = {a for a,vt in zip(actors,vtables) if vt==int(d["WOLFEN_VTABLE"])}
            added = wolfens - set(self._ap_actor_states)
            removed = set(self._ap_actor_states) - wolfens
            for actor in removed:
                self._ap_damage_last_hp.pop(actor, None)
                self._ap_actor_states.pop(actor,None)
                old_key=self._ap_actor_keys.pop(actor,None)
                self._ap_actor_descriptors.pop(actor,None)
                if old_key is not None and old_key not in self._ap_wolfen_states:
                    self._ap_wolfen_states.pop(old_key,None)
            if added:
                added_sorted=sorted(added)
                vals=pine.read32_many([x+int(d["WOLFEN_STATE_OFFSET"]) for x in added_sorted])
                valid_states={int(d["WOLFEN_STATE_PRESENT"]),int(d["WOLFEN_STATE_FREED"])}
                self._ap_actor_states.update({a:s for a,s in zip(added_sorted,vals) if s in valid_states})
                descs=pine.read32_many([x+int(d["WOLFEN_DESCRIPTOR_OFFSET"]) for x in added_sorted])
                valid=[(x,p) for x,p in zip(added_sorted,descs) if 0x00100000<=p<0x02000000 and p%4==0]
                keys=pine.read32_many([p+int(d["WOLFEN_KEY_OFFSET"]) for _,p in valid]) if valid else []
                for (actor,desc),key in zip(valid,keys):
                    if 0 < key < 0x10000:
                        self._ap_actor_keys[actor]=key
                        # Keep the raw game key even when it is not in the AP
                        # table so a release log can identify missing mappings.
                        self._ap_actor_descriptors[actor]=desc
                        if str(key) in d.get("WOLFEN_KEY_TO_ZONES", {}):
                            self._ap_wolfen_states[key]=self._ap_actor_states.get(actor, 0)
            self._ap_update_zone(set(self._ap_actor_keys.values()), d)
        if now < self._ap_next_poll:
            return
        self._ap_next_poll = now + 0.07
        actors=sorted(self._ap_actor_states)
        live_states=pine.read32_many([a+int(d["WOLFEN_STATE_OFFSET"]) for a in actors]) if actors else []
        mapped=0
        valid_states={int(d["WOLFEN_STATE_PRESENT"]),int(d["WOLFEN_STATE_FREED"])}
        self._ap_monitor_wolfen_damage(pine, actors, live_states, d)
        zone=self._ap_current_zone
        zone_map=dict(d.get("WOLFEN_ZONE_KEY_TO_LOCATION",{}).get(zone,{}) if zone else {})
        # 0.9.41 LIVE AUDIT: Amber Quarry Wolfen actors coexist with The Quarry
        # scene/vote.  The Quarry has 31 mapped actors and the 14 Amber actors
        # cannot outvote them, so the zone vote remains 'The Quarry'.  Recover
        # ONLY globally unique Amber keys while this exact parent zone is live.
        # Their original AP location names and IDs stay unchanged for 0.8.11.
        if zone == "The Quarry":
            amber_map = d.get("WOLFEN_ZONE_KEY_TO_LOCATION", {}).get("Amber Quarry", {})
            key_zones = d.get("WOLFEN_KEY_TO_ZONES", {})
            for amber_key, amber_name in amber_map.items():
                if key_zones.get(str(amber_key), []) == ["Amber Quarry"]:
                    zone_map.setdefault(str(amber_key), amber_name)
        loc_by_name={n:int(i) for n,i in d["LOCATION_NAME_TO_ID"].items()}
        for actor,state in zip(actors,live_states):
            if state not in valid_states:
                continue
            key=self._ap_actor_keys.get(actor)
            old_state=self._ap_actor_states.get(actor)
            name=zone_map.get(str(key)) if key is not None else None
            if name is not None:
                mapped+=1
                # Reconnect/save-state catch-up. Persistently freed (state 2)
                # Wolfen actors were sometimes baselined without a live 1->2 edge.
                # Only send checks which the server itself says are not checked;
                # queue durable checks once, never based on global freed count.
                if (state == int(d["WOLFEN_STATE_FREED"])
                        and old_state == state and self._ap_joined and self._ap_seed_build_verified):
                    lid = loc_by_name[name]
                    if lid not in self._ap_checked and lid not in self._ap_pending_checks:
                        if self._ap_queue_location_check(link, lid, name, d):
                            self._log_threadsafe(
                                f"WOLFEN RECOVERY CHECK queued: {self._ap_public_location_name(name)} "
                                "(persistent freed state / server unchecked).", "ok")
                if old_state != state:
                    label = self._ap_public_location_name(name)
                    self._log_threadsafe(f"Wolfen libéré : {label} ({old_state}->{state})", "info")
                    lid=loc_by_name[name]
                    if old_state==int(d["WOLFEN_STATE_PRESENT"]) and state==int(d["WOLFEN_STATE_FREED"]) and lid not in self._ap_checked:
                        if self._ap_joined and self._ap_seed_build_verified:
                            self._ap_queue_location_check(link, lid, name, d)
                            self._log_threadsafe(f"CHECK queued -> Archipelago: {self._ap_public_location_name(name)}", "ok")
                        else:
                            self._log_threadsafe(f"CHECK detected but NOT sent (AP handshake/build not verified): {name} [id={lid}]", "warn")
            elif old_state != state and key is not None:
                self._log_threadsafe(f"Wolfen key 0x{key:04X} changed {old_state}->{state}, ignored outside mapped current zone ({zone or '?'}).", "info")
            self._ap_actor_states[actor]=state

        states_count={state:sum(1 for value in live_states if value==state) for state in (1,2)}
        if not self._ap_baselined:
            self._ap_baselined=True
            self._ap_checked.update(int(x) for x in getattr(link,"_known_checked",set()))
            self._log_threadsafe(f"AP watcher scan: zone={zone or '?'}, actor_count={self._ap_actor_count if self._ap_actor_count is not None else '?'}, wolfen_active={len(actors)}, mapped_in_zone={mapped}, state1={states_count[1]}, state2={states_count[2]}", "info")
            self._log_threadsafe("Kya zone-safe checks armed.", "ok")

        # IMPORTANT: do not reconcile pre-existing state=2 Wolfens on zone entry.
        # A location is emitted ONLY from a live 1->2 transition while its own
        # zone is currently detected. This avoids false floods from old/saved
        # actor states and keeps physical Wolfen numbering meaningful.

        # Zone-scoped fixed-address special checks.
        conds=d.get("SPECIAL_LOCATION_CONDITIONS",{})
        special_zones=d.get("SPECIAL_LOCATION_ZONES",{})
        # The first Brazul event is handled exclusively by the independent
        # read-only first-Brazul watcher, BEFORE the actor streaming barrier.
        # Never double-process it here: this loop is re-baselined on scene
        # change, and may otherwise mistake a loaded 100% state for a live edge.
        eligible={name:rows for name,rows in conds.items()
                  if name != "Amber Quarry - Brazul First Encounter"
                  and special_zones.get(name)==zone}
        addrs=sorted({int(a) for rows in eligible.values() for a,_ in rows})
        vals=dict(zip(addrs,pine.read32_many(addrs))) if addrs else {}
        current_special={}
        for name,conditions in eligible.items():
            active=all(vals[int(a)]==int(v) for a,v in conditions)
            current_special[name]=active
        if not self._ap_special_baselined:
            self._ap_special_states.update(current_special)
            self._ap_special_baselined=True
            self._ap_hunter_boss_recovery_since = None
            self._log_threadsafe(f"Special checks armed for zone: {zone or '?'}. Live transitions only.", "info")
            if zone == 'Hunters Domain':
                boss_addr = 0x004254EC
                self._log_threadsafe(
                    f'HUNTERS BOSS BASELINE: ScenarioVar 0x{boss_addr:08X}='
                    f'{vals.get(boss_addr, "NOT_READ")}; '
                    'completed-save recovery requires value 2 and stable scene.', 'info')
        elif self._ap_joined:
            for name,active in current_special.items():
                old_active=self._ap_special_states.get(name,active)
                lid=loc_by_name[name]
                if (not old_active) and active and lid not in self._ap_checked:
                    if self._ap_seed_build_verified:
                        if name == "Flying Forest - HP Upgrade":
                            hp_target = self._ap_owned_life_target(d)
                            self._ap_pending_special_life_suppressions[lid] = hp_target
                            self._ap_shop_live_ignore_until = max(self._ap_shop_live_ignore_until, time.monotonic() + 1.0)
                        self._ap_queue_location_check(link, lid, name, d)
                        self._log_threadsafe(f"CHECK queued -> Archipelago: {self._ap_public_location_name(name)}", "ok")
                        if name == "Flying Forest - HP Upgrade":
                            self._ap_suppress_special_life_reward(pine, lid, name, hp_target)
                    else:
                        self._log_threadsafe(f"CHECK detected but NOT sent (AP build not verified): {name} [id={lid}]", "warn")
                self._ap_special_states[name]=active

        # 0.9.62: Hunter boss uses its own persistent ScenarioVar 0x004254EC=2.
        # Unlike cinematic/live-only checks, a completed boss can be recovered
        # from a 100% savestate after a stable visit to Hunters Domain. Scope
        # this strictly to this one proven location; never backfill maps,
        # runes, Frank, Brazul or the victory Goal from old savestates.
        hunter_name = "Hunters Domain - Boss Defeated"
        hunter_conds = eligible.get(hunter_name)
        hunter_id = loc_by_name.get(hunter_name)
        hunter_active = bool(current_special.get(hunter_name, False))
        if (self._ap_special_baselined and hunters_boss_recovery_eligible(
                zone, hunter_conds, hunter_active, self._ap_joined,
                self._ap_seed_build_verified, self._ap_stream_hold,
                hunter_id, self._ap_checked, self._ap_pending_checks)):
            now_hunter = time.monotonic()
            if self._ap_hunter_boss_recovery_since is None:
                self._ap_hunter_boss_recovery_since = now_hunter
            elif (now_hunter - self._ap_hunter_boss_recovery_since >= 1.0
                  and hunter_id not in self._ap_checked
                  and hunter_id not in self._ap_pending_checks):
                if self._ap_queue_location_check(link, hunter_id, hunter_name, d):
                    self._log_threadsafe(
                        'HUNTERS BOSS RECOVERY CHECK queued: stable Hunters Domain '
                        'scene + persistent boss ScenarioVar 0x004254EC=2; '
                        'server unchecked.', 'ok')
        else:
            self._ap_hunter_boss_recovery_since = None

        # Debug-only validation of discovered key-item/progression addresses.
        probes=d.get("DEBUG_VALIDATION_PROBES",{})
        probe_addrs=sorted({int(spec["address"]) for spec in probes.values()})
        probe_vals=dict(zip(probe_addrs,pine.read32_many(probe_addrs))) if probe_addrs else {}
        current_probes={name:probe_vals[int(spec["address"])] for name,spec in probes.items()}
        if not self._ap_validation_probes_baselined:
            self._ap_validation_probe_states=current_probes
            self._ap_validation_probes_baselined=True
            self._log_threadsafe(f"Validation monitor armed ({len(current_probes)} key-item/progression probes).", "info")
        else:
            for name,value in current_probes.items():
                old_value=self._ap_validation_probe_states.get(name,value)
                if value != old_value:
                    target=probes[name].get("target")
                    suffix=" TARGET" if target is not None and value==int(target) else ""
                    self._log_threadsafe(f"VALIDATION state: {name} {old_value}->{value}{suffix} (game/AP source not distinguished)", "info")
                self._ap_validation_probe_states[name]=value

        # V0.8.15 SHOP WATCHER ------------------------------------------------------
        # Inventory/serialization transitions alone are NOT purchases: story changes,
        # savestate loads and AP item writes can all change the same values. A real
        # purchase must therefore be paired with a recent Nooties decrease.
        shop = d.get("SHOP_LOCATION_CONDITIONS", {})
        shop_rewards = d.get("SHOP_VANILLA_REWARD_STATE", {})
        live_rules = d.get("SHOP_LIVE_REWARD_RULES", {})
        now = time.monotonic()

        # V0.8.21 NATIVE SHOP RESOLVER -------------------------------------------
        # Ghidra/runtime proof gives a relocation-safe chain for every shop object:
        #   vtable+0xE8 -> 0x003BA710 -> object+0x160
        #   item+0x20 = native ID, item+0x30 = current price.
        # Scan only in Nativs City, then track the native table cursor every poll.
        native_before = {}
        native_current = {}
        if (self._ap_current_zone or "") == "Nativs City":
            if (not self._ap_shop_native.ready) and now - self._ap_shop_native_last_attempt >= 1.5:
                self._ap_shop_native_last_attempt = now
                try:
                    self._ap_shop_native.set_price_modifier(self._ap_shop_price_modifier_pct)
                    obj_count, table_count, resolved_count = self._ap_shop_native.scan(pine, now)
                    if self._ap_shop_native.ready:
                        if not self._ap_shop_native_ready_logged:
                            self._log_threadsafe(
                                f"Native Shop resolver armed: {resolved_count}/18 AP items "
                                f"({obj_count} runtime objects, {table_count} tables).",
                                "ok",
                            )
                            self._ap_shop_native_ready_logged = True
                    elif obj_count and not self._ap_shop_native_ready_logged:
                        self._report_native_shop_scan(
                            ("waiting", resolved_count, obj_count, table_count),
                            f"Native Shop resolver waiting: {resolved_count}/18 AP items "
                            f"({obj_count} runtime objects, {table_count} tables).",
                            now, "info",
                        )
                except Exception as exc:
                    if not self._ap_shop_native_ready_logged:
                        self._report_native_shop_scan(
                            ("deferred", type(exc).__name__, str(exc)),
                            f"Native Shop resolver scan deferred: {exc}", now, "info")
            if self._ap_shop_native.ready:
                try:
                    price_changes = self._ap_shop_native.enforce_prices(pine)
                    if self._ap_shop_price_modifier_logged != self._ap_shop_price_modifier_pct:
                        golden_name = "Nativs City - Shop - Golden Boomy"
                        golden_price = self._ap_shop_native.current_price(golden_name)
                        suffix = f" (Golden Boomy={golden_price})" if golden_price is not None else ""
                        self._log_threadsafe(
                            f"Shop price modifier active: {self._ap_shop_price_modifier_pct:+d}%{suffix}.",
                            "ok",
                        )
                        self._ap_shop_price_modifier_logged = self._ap_shop_price_modifier_pct
                    native_before, native_current = self._ap_shop_native.prepare_poll(pine, now)
                except Exception:
                    self._ap_shop_native.reset()
                    self._ap_shop_sold_observer.reset()
                    self._ap_shop_native_sold_state_last = {}
                    self._ap_shop_native.set_price_modifier(self._ap_shop_price_modifier_pct)
                    self._ap_shop_price_modifier_logged = None
                    self._ap_shop_native_hints.clear()
                    self._ap_shop_native_ready_logged = False
                    self._ap_shop_native_last_attempt = 0.0
                    self._ap_shop_native_last_report = None
                    self._ap_shop_native_last_report_at = 0.0
                    native_before = {}
                    native_current = {}

        # V0.9.61: a shop ACTOR state is the durable purchased/disabled marker.
        # 0% / 100% saves and two independent before/after transactions show
        # (obj+0x08 & 0x21) == 0x21 for items sold, independently of reward
        # inventory and unreliable serialized flags.  Require native-ID mapping,
        # an unchanged vtable, the structural Nativ scene, stable repeated polls,
        # AP seed handshake and server-side deduplication.  No memory writes.
        if (self._ap_shop_native.ready
                and self._ap_shop_purchase_scene_proven()
                and self._ap_joined and self._ap_seed_build_verified
                and now >= self._ap_shop_live_ignore_until):
            try:
                live_sold = self._ap_shop_native.read_native_sold_states(pine)
                self._ap_shop_native_sold_state_last = live_sold
                confirmed_sold = self._ap_shop_sold_observer.observe(live_sold, now)
                for sold_name in confirmed_sold:
                    sold_lid = loc_by_name.get(sold_name)
                    if sold_lid is None or (sold_lid in self._ap_checked
                            or sold_lid in self._ap_pending_checks
                            or sold_lid in self._ap_pending_shop_suppressions):
                        continue
                    if self._ap_queue_location_check(link, sold_lid, sold_name, d):
                        self._log_threadsafe(
                            f"SHOP NATIVE SOLD RECOVERY CHECK queued: {sold_name} "
                            f"(stable actor+0x08 sold bits 0x21; id={sold_lid}).",
                            "ok",
                        )
            except Exception as exc:
                self._ap_shop_sold_observer.reset()
                self._ap_shop_native_sold_state_last = {}
                self._log_threadsafe(
                    f"SHOP NATIVE SOLD observer deferred: {exc}", "info"
                )

        # A money decrease is only a purchase *candidate*. It never sends a check by
        # itself. Tokens expire after 10 minutes, allowing delayed serialized shop stock
        # to refresh after leaving a menu/area.
        money_now = pine.read32(int(d["ADDR_MONEY"]))
        if self._ap_shop_money_last is None:
            self._ap_shop_money_last = money_now
        else:
            old_money = self._ap_shop_money_last
            # V0.8.15: inventory-authority writes must never hide the money
            # decrement.  _ap_shop_live_ignore_until only suppresses noisy
            # inventory inference; Nooties are an independent purchase signal.
            if money_now < old_money:
                spent = old_money - money_now
                # Very large jumps are characteristic of savestate/debug rewinds, not
                # ordinary shop purchases. Keep the limit deliberately generous.
                shop_scene = self._ap_shop_purchase_scene_proven()
                if 0 < spent <= 50000 and shop_scene:
                    self._ap_shop_purchase_tokens.append((now, spent))
                    if self._ap_shop_price_modifier_pct:
                        expected_names = [n for n in SHOP_PRICE_HINTS
                                          if self._ap_shop_expected_price(n) == spent]
                        vanilla_names = [n for n in SHOP_PRICE_HINTS
                                         if SHOP_PRICE_HINTS[n] == spent
                                         and self._ap_shop_expected_price(n) != spent]
                        if vanilla_names and not expected_names:
                            self._log_threadsafe(
                                f"SHOP PRICE MISMATCH: spend={spent} matches vanilla pricing "
                                f"despite AP modifier {self._ap_shop_price_modifier_pct:+d}%. "
                                "Purchase identity requires a native/stock/live confirmation.",
                                "warn",
                            )

                    # V0.8.21: native runtime selection is authoritative identity.
                    if self._ap_shop_native.ready and native_before:
                        consumed_names = set()
                        for candidate_name, candidate_lid in loc_by_name.items():
                            if not candidate_name.startswith("Nativs City - Shop - "):
                                continue
                            if (candidate_lid in self._ap_checked or
                                    candidate_lid in self._ap_pending_checks or
                                    candidate_lid in self._ap_pending_shop_suppressions):
                                consumed_names.add(candidate_name)
                        native_name, native_reason, native_candidates = self._ap_shop_native.identify_purchase(
                            spent, native_before, now, consumed_names
                        )
                        if native_name is not None:
                            self._ap_shop_native_hints[now] = (native_name, int(spent), native_reason)
                            self._log_threadsafe(
                                f"Native Shop purchase identified: {native_name} "
                                f"(spend={spent}; {native_reason}).",
                                "ok",
                            )
                        elif native_candidates:
                            self._log_threadsafe(
                                "Native Shop purchase unresolved this tick; fallback watcher retained "
                                f"(spend={spent}; candidates={', '.join(native_candidates)}).",
                                "info",
                            )

                    # A dialog for an older token must never remain on screen
                    # while the player is making a newer purchase.
                    self._post_ui(self._ap_defer_shop_prompt_for_new_purchase, now)
                    self._log_threadsafe(
                        f"Shop purchase candidate: Nooties {old_money}->{money_now} (-{spent}).",
                        "info",
                    )
                else:
                    self._ap_shop_purchase_tokens.clear()
                    self._ap_shop_ambiguous_token_warned.clear()
                    self._log_threadsafe(
                        f"Nooties change ignored as shop input (rollback/non-shop scene): "
                        f"{old_money}->{money_now}.", "info")
            self._ap_shop_money_last = money_now
        if self._ap_shop_native.ready and native_current:
            self._ap_shop_native.commit_poll(native_current)
        self._ap_shop_purchase_tokens = [
            token for token in self._ap_shop_purchase_tokens if now - token[0] <= 180.0
        ]
        self._ap_shop_exact_reconcile_hints = [
            hint for hint in self._ap_shop_exact_reconcile_hints if now - hint[0] <= 3.0
        ]
        active_token_times = {token[0] for token in self._ap_shop_purchase_tokens}
        self._ap_shop_native_hints = {
            token_at: hint for token_at, hint in self._ap_shop_native_hints.items()
            if token_at in active_token_times
        }
        self._ap_shop_ambiguous_token_warned.intersection_update(active_token_times)
        self._ap_shop_deferred_prompt_tokens.intersection_update(active_token_times)

        def _consume_shop_token(max_age: float = 180.0, expected_spent: int | tuple[int, ...] | None = None):
            cutoff = time.monotonic() - max_age
            for i, token in enumerate(self._ap_shop_purchase_tokens):
                if token[0] < cutoff:
                    continue
                if expected_spent is not None:
                    allowed_spends = (expected_spent,) if isinstance(expected_spent, int) else expected_spent
                    if int(token[1]) not in allowed_spends:
                        continue
                popped = self._ap_shop_purchase_tokens.pop(i)
                self._ap_shop_ambiguous_token_warned.discard(popped[0])
                self._post_ui(self._ap_forget_shop_choice_token, popped[0])
                return popped
            return None

        def _consume_specific_shop_token(token: tuple[float, int]):
            """Consume this exact spend token without head-of-line blocking."""
            token_at, token_spent = token
            for i, candidate in enumerate(self._ap_shop_purchase_tokens):
                if candidate[0] == token_at and int(candidate[1]) == int(token_spent):
                    popped = self._ap_shop_purchase_tokens.pop(i)
                    self._ap_shop_ambiguous_token_warned.discard(popped[0])
                    self._post_ui(self._ap_forget_shop_choice_token, popped[0])
                    return popped
            return None

        def _shop_condition(spec):
            if isinstance(spec, dict):
                return int(spec["address"]), int(spec["mask"])
            if isinstance(spec, (list, tuple)) and len(spec) >= 2:
                return int(spec[0]), int(spec[1])
            raise ValueError(f"Invalid shop condition schema: {spec!r}")

        def _live_rule_satisfied(spec, value: int) -> bool:
            mode = str(spec.get("mode", "bool_gain"))
            if mode == "bool_gain":
                return value != 0
            if mode == "bit_gain":
                return (value & int(spec["mask"])) != 0
            if mode == "level_gain_to":
                return value >= int(spec["threshold"])
            if mode == "life_gain":
                threshold = int(spec.get("threshold", d.get("LIFE_GAUGE_BASE", 50) + d.get("LIFE_GAUGE_STEP", 50)))
                return value >= threshold
            return False

        # Read live vanilla reward states first. They are useful for immediate
        # purchase detection and for disambiguating later serialized stock flips.
        current_live = {}
        live_changes = []
        if live_rules:
            live_addrs = sorted({int(spec["address"]) for spec in live_rules.values()})
            live_vals = dict(zip(live_addrs, pine.read32_many(live_addrs)))
            current_live = {name: int(live_vals[int(spec["address"])]) for name, spec in live_rules.items()}
            if not self._ap_shop_live_baselined:
                self._ap_shop_live_reward_states = current_live
                self._ap_shop_live_baselined = True
                self._log_threadsafe(
                    f"Shop purchase watcher armed ({len(live_rules)} live rewards; Nooties-gated).",
                    "info",
                )
            else:
                for name, new in current_live.items():
                    old = int(self._ap_shop_live_reward_states.get(name, new))
                    if new != old:
                        live_changes.append((name, old, new))
                # A savestate commonly changes many inventory fields at once.
                if len(live_changes) >= 4 and now >= self._ap_shop_live_ignore_until:
                    self._ap_shop_purchase_tokens.clear()
                    self._ap_shop_ambiguous_token_warned.clear()
                    self._ap_shop_unpaired_live_hits.clear()
                    self._ap_shop_unconfirmed_stock.clear()
                    # A savestate/reload can relocate every 0x01xxxxxx Shop object.
                    # Throw away only the runtime cache; the next tick rebuilds it
                    # from the stable native getter/ID chain.
                    self._ap_shop_native.reset()
                    self._ap_shop_sold_observer.reset()
                    self._ap_shop_native_sold_state_last = {}
                    self._ap_shop_native.set_price_modifier(self._ap_shop_price_modifier_pct)
                    self._ap_shop_price_modifier_logged = None
                    self._ap_shop_native_hints.clear()
                    self._ap_shop_native_ready_logged = False
                    self._ap_shop_native_last_attempt = 0.0
                    self._ap_shop_native_last_report = None
                    self._ap_shop_native_last_report_at = 0.0
                    self._log_threadsafe(
                        f"Shop inference ignored: {len(live_changes)} simultaneous inventory changes look like a savestate/story load; native Shop cache reset.",
                        "info",
                    )

                # If the game's inventory field flips one poll before the Nooties
                # counter drops, keep the transition briefly instead of losing the
                # purchase. It still cannot check anything without a spend token.
                if now >= self._ap_shop_live_ignore_until and self._ap_shop_unpaired_live_hits:
                    for pending_name, (pending_at, pending_old, pending_new) in list(self._ap_shop_unpaired_live_hits.items()):
                        if now - pending_at > 3.0:
                            self._ap_shop_unpaired_live_hits.pop(pending_name, None)
                            continue
                        lid = loc_by_name.get(pending_name)
                        if lid is None or lid in self._ap_checked or lid in self._ap_pending_checks or lid in self._ap_pending_shop_suppressions:
                            self._ap_shop_unpaired_live_hits.pop(pending_name, None)
                            continue
                        token = _consume_shop_token(max_age=3.0, expected_spent=self._ap_shop_allowed_spends(pending_name))
                        if token is None:
                            break
                        reward_spec = shop_rewards.get(pending_name)
                        if reward_spec is not None:
                            self._ap_pending_shop_suppressions[lid] = (
                                pending_name, reward_spec, int(pending_old)
                            )
                        if self._ap_joined and self._ap_seed_build_verified:
                            durable = self._ap_queue_location_check(link, lid, pending_name, d)
                            if durable and lid in self._ap_pending_shop_suppressions:
                                self._ap_suppress_shop_reward(pine, lid, self._ap_pending_shop_suppressions[lid])
                            self._log_threadsafe(
                                f"SHOP LIVE CHECK queued -> Archipelago: {pending_name} [id={lid}] "
                                f"({pending_old}->{pending_new}; spend={token[1]}; paired after delayed Nooties update)",
                                "ok",
                            )
                        else:
                            self._ap_pending_shop_suppressions.pop(lid, None)
                            self._log_threadsafe(
                                f"SHOP LIVE purchase detected but NOT sent; vanilla reward preserved: {pending_name}.",
                                "warn",
                            )
                        self._ap_shop_unpaired_live_hits.pop(pending_name, None)

                if now >= self._ap_shop_live_ignore_until and len(live_changes) < 4:
                    live_hits = []
                    life_old = life_new = None
                    for name, old, new in live_changes:
                        spec = live_rules[name]
                        mode = str(spec.get("mode", "bool_gain"))
                        hit = False
                        if mode == "bool_gain":
                            hit = old == 0 and new != 0
                        elif mode == "bit_gain":
                            mask = int(spec["mask"])
                            hit = (old & mask) == 0 and (new & mask) != 0
                        elif mode == "level_gain_to":
                            threshold = int(spec["threshold"])
                            hit = old < threshold <= new
                        elif mode == "life_gain":
                            if new > old:
                                life_old, life_new = old, new
                            continue
                        if hit:
                            live_hits.append((name, old, new))

                    # Energy Bars share the same max-life field. Prefer the native
                    # active-Shop selection to distinguish ID16 Bar 1 vs Bar 2. This
                    # is especially important at -100% price because there is no
                    # Nooties debit to disambiguate the purchase afterward.
                    if life_old is not None and life_new is not None and life_new - life_old >= int(d.get("LIFE_GAUGE_STEP", 50)):
                        energy_names = (
                            "Nativs City - Shop - Extra Energy Bar 1",
                            "Nativs City - Shop - Extra Energy Bar 2",
                        )
                        remaining_energy = []
                        consumed_names = set()
                        for candidate in energy_names:
                            lid = loc_by_name.get(candidate)
                            if lid is None:
                                continue
                            if (lid in self._ap_checked or lid in self._ap_pending_checks or
                                    lid in self._ap_pending_shop_suppressions):
                                consumed_names.add(candidate)
                            else:
                                remaining_energy.append(candidate)
                        chosen_energy = None
                        if self._ap_shop_native.ready and native_before:
                            selected_name, _selected_reason, _selected_candidates = self._ap_shop_native.identify_selected(
                                native_before, now, consumed_names
                            )
                            if selected_name in remaining_energy:
                                chosen_energy = selected_name
                        if chosen_energy is None and len(remaining_energy) == 1:
                            chosen_energy = remaining_energy[0]
                        if chosen_energy is not None:
                            live_hits.append((chosen_energy, int(life_old), int(life_new)))

                    for name, old, new in live_hits:
                        lid = loc_by_name.get(name)
                        if lid is None or lid in self._ap_checked or lid in self._ap_pending_checks or lid in self._ap_pending_shop_suppressions:
                            continue
                        expected_price = self._ap_shop_expected_price(name)
                        if expected_price == 0 and self._ap_shop_native.ready:
                            reward_spec = shop_rewards.get(name)
                            if reward_spec is not None:
                                self._ap_pending_shop_suppressions[lid] = (name, reward_spec, int(old))
                            if self._ap_joined and self._ap_seed_build_verified:
                                durable = self._ap_queue_location_check(link, lid, name, d)
                                if durable and lid in self._ap_pending_shop_suppressions:
                                    self._ap_suppress_shop_reward(pine, lid, self._ap_pending_shop_suppressions[lid])
                                self._log_threadsafe(
                                    f"SHOP FREE CHECK queued -> Archipelago: {name} [id={lid}] "
                                    f"({old}->{new}; configured price=0)",
                                    "ok",
                                )
                            else:
                                self._ap_pending_shop_suppressions.pop(lid, None)
                            self._ap_shop_unpaired_live_hits.pop(name, None)
                            continue
                        token = _consume_shop_token(max_age=3.0, expected_spent=self._ap_shop_allowed_spends(name))
                        if token is None:
                            self._ap_shop_unpaired_live_hits[name] = (now, int(old), int(new))
                            self._log_threadsafe(
                                f"Shop-like inventory change waiting for matching Nooties spend: {name} {old}->{new}.",
                                "info",
                            )
                            continue
                        self._ap_shop_unpaired_live_hits.pop(name, None)
                        reward_spec = shop_rewards.get(name)
                        if reward_spec is not None:
                            self._ap_pending_shop_suppressions[lid] = (name, reward_spec, int(old))
                        if self._ap_joined and self._ap_seed_build_verified:
                            durable = self._ap_queue_location_check(link, lid, name, d)
                            if durable and lid in self._ap_pending_shop_suppressions:
                                self._ap_suppress_shop_reward(pine, lid, self._ap_pending_shop_suppressions[lid])
                            self._log_threadsafe(
                                f"SHOP LIVE CHECK queued -> Archipelago: {name} [id={lid}] "
                                f"({old}->{new}; spend={token[1]}; vanilla rollback protected by durable AP queue)",
                                "ok",
                            )
                        else:
                            self._ap_pending_shop_suppressions.pop(lid, None)
                            self._log_threadsafe(
                                f"SHOP LIVE purchase detected but NOT sent; vanilla reward preserved: {name}.",
                                "warn",
                            )
                self._ap_shop_live_reward_states = current_live

        # Serialized stock is the independent SHOP state. Player inventory is
        # deliberately NOT required here: an item may already be owned because AP
        # delivered it earlier. A stock 1->0 can still validate the purchase, but
        # only when paired with a natural Nooties decrease.
        #
        # Important: unpaired serialized 1->0 transitions are NOT committed to the
        # logical baseline. Serialized buffers can flicker during loads; keeping the
        # old=True state lets the later real purchase recover correctly instead of
        # being lost forever.
        if shop:
            parsed_shop = {name: _shop_condition(spec) for name, spec in shop.items()}
            shop_addrs = sorted({address for address, _mask in parsed_shop.values()})
            shop_vals = dict(zip(shop_addrs, pine.read32_many(shop_addrs)))
            current_shop = {name: bool(shop_vals[address] & mask) for name, (address, mask) in parsed_shop.items()}

            # V0.8.20: sample the exact Ghidra-derived live flags EVERY poll, even
            # while an older same-price purchase token is unresolved. This isolates
            # each physical purchase instead of accumulating many changes against
            # one stale baseline and releasing AP checks in a later burst.
            self._ap_capture_shop_group_edges(pine, current_shop)

            reward_addrs = sorted({int(spec["address"]) for spec in shop_rewards.values()})
            reward_vals = dict(zip(reward_addrs, pine.read32_many(reward_addrs))) if reward_addrs else {}
            current_rewards = {name: reward_vals.get(int(spec["address"])) for name, spec in shop_rewards.items()}
            self._ap_emit_shop_audit(current_shop, current_rewards, loc_by_name)

            if not self._ap_shop_baselined:
                self._ap_shop_states = current_shop
                self._ap_shop_reward_snapshots = {
                    name: int(current_rewards[name]) for name, available in current_shop.items()
                    if available and current_rewards.get(name) is not None
                }
                self._ap_shop_baselined = True
                self._log_threadsafe(
                    f"Serialized shop stock armed ({len(current_shop)} entries; Nooties-gated independent stock).",
                    "info",
                )
                if current_shop and not any(current_shop.values()):
                    self._log_threadsafe(
                        "SHOP STOCK 0/18 at baseline: serialized flags do not identify "
                        "purchases in this scene. Native item identity or a causal "
                        "inventory/stock transition is required; price alone never checks.",
                        "warn",
                    )
                if (self._ap_current_zone or "") == "Nativs City":
                    self._ap_prime_shop_runtime_sources(pine, current_shop)
                    self._ap_prime_shop_group_sources(pine, current_shop)
            else:
                next_states = dict(self._ap_shop_states)
                stock_candidates = []
                for name, available in current_shop.items():
                    old_available = bool(self._ap_shop_states.get(name, available))
                    lid = loc_by_name.get(name)

                    if lid is not None and (lid in self._ap_checked or lid in self._ap_pending_checks):
                        next_states[name] = available
                        self._ap_shop_unconfirmed_stock.discard(name)
                        continue

                    if available:
                        # A true stock state is safe to commit and refreshes the
                        # reward snapshot, including AP-owned items.
                        next_states[name] = True
                        self._ap_shop_unconfirmed_stock.discard(name)
                        if lid is not None:
                            self._ap_shop_suppressed.discard(lid)
                            self._ap_pending_shop_suppressions.pop(lid, None)
                        if current_rewards.get(name) is not None:
                            self._ap_shop_reward_snapshots[name] = int(current_rewards[name])
                    elif old_available:
                        if lid is not None and lid not in self._ap_pending_shop_suppressions:
                            stock_candidates.append(name)
                        # DO NOT set False yet: wait for a purchase token.

                free_stock = [name for name in stock_candidates if self._ap_shop_expected_price(name) == 0]
                for name in free_stock:
                    lid = loc_by_name[name]
                    reward_spec = shop_rewards.get(name)
                    previous_reward = self._ap_shop_reward_snapshots.get(name)
                    if reward_spec is not None and previous_reward is not None:
                        self._ap_pending_shop_suppressions[lid] = (name, reward_spec, int(previous_reward))
                    if self._ap_joined and self._ap_seed_build_verified:
                        durable = self._ap_queue_location_check(link, lid, name, d)
                        if durable and lid in self._ap_pending_shop_suppressions:
                            self._ap_suppress_shop_reward(pine, lid, self._ap_pending_shop_suppressions[lid])
                        next_states[name] = False
                        self._ap_shop_unconfirmed_stock.discard(name)
                        self._log_threadsafe(
                            f"SHOP FREE STOCK CHECK queued -> Archipelago: {name} [id={lid}] "
                            f"(stock 1->0; configured price=0)",
                            "ok",
                        )
                    else:
                        self._ap_pending_shop_suppressions.pop(lid, None)
                if free_stock:
                    stock_candidates = [name for name in stock_candidates if name not in free_stock]

                if stock_candidates and self._ap_shop_purchase_tokens:
                    # The stock bit identifies the exact article; the money token must
                    # independently match that article's observed vanilla price. This
                    # prevents stale/unrelated spends from validating the wrong stock
                    # entry when several serialized bits refresh at once.
                    unresolved_stock = []
                    for name in stock_candidates:
                        token = _consume_shop_token(expected_spent=self._ap_shop_allowed_spends(name))
                        if token is None:
                            unresolved_stock.append(name)
                            continue
                        lid = loc_by_name[name]
                        reward_spec = shop_rewards.get(name)
                        previous_reward = self._ap_shop_reward_snapshots.get(name)
                        if reward_spec is not None and previous_reward is not None:
                            self._ap_pending_shop_suppressions[lid] = (name, reward_spec, int(previous_reward))
                        if self._ap_joined and self._ap_seed_build_verified:
                            durable = self._ap_queue_location_check(link, lid, name, d)
                            if durable and lid in self._ap_pending_shop_suppressions:
                                self._ap_suppress_shop_reward(pine, lid, self._ap_pending_shop_suppressions[lid])
                            next_states[name] = False
                            self._ap_shop_unconfirmed_stock.discard(name)
                            self._log_threadsafe(
                                f"SHOP STOCK CHECK queued -> Archipelago: {name} [id={lid}] "
                                f"(stock 1->0; spend={token[1]}; price matched; inventory transition not required)",
                                "ok",
                            )
                        else:
                            self._ap_pending_shop_suppressions.pop(lid, None)
                            self._log_threadsafe(
                                f"SHOP stock purchase detected but NOT sent; vanilla reward preserved: {name}.",
                                "warn",
                            )
                    pending = [n for n in unresolved_stock if n not in self._ap_shop_unconfirmed_stock]
                    if pending:
                        self._log_threadsafe(
                            "Serialized shop changes waiting for matching-price purchase token: "
                            + ", ".join(pending),
                            "info",
                        )
                        self._ap_shop_unconfirmed_stock.update(pending)
                elif stock_candidates:
                    pending = [n for n in stock_candidates if n not in self._ap_shop_unconfirmed_stock]
                    if pending:
                        self._log_threadsafe(
                            "Serialized shop stock waiting for Nooties purchase token: " + ", ".join(pending),
                            "info",
                        )
                        self._ap_shop_unconfirmed_stock.update(pending)

                self._ap_shop_states = next_states

                # V0.8.18: proactively snapshot the live shop source while the
                # player is not between purchase and AP acknowledgement. This gives
                # same-price items a causal 1->0 baseline before the click happens.
                if not self._ap_shop_purchase_tokens and (self._ap_current_zone or "") == "Nativs City":
                    self._ap_prime_shop_runtime_sources(pine, current_shop)
                    self._ap_prime_shop_group_sources(pine, current_shop)

                # V0.8.15 duplicate-purchase recovery. Every spend token is
                # evaluated independently: an older ambiguous 50/100-Nooties buy can
                # no longer block a later unique 400 (Black Bracelet), 700 (Gold
                # Bracelet), etc. Exact live/stock signals still win whenever present.
                if self._ap_shop_purchase_tokens and now >= self._ap_shop_live_ignore_until and (self._ap_current_zone or "") == "Nativs City":
                    try:
                        wolfen_count_addr = int(d.get("ADDR_GLOBAL_WOLFEN_COUNT", 0x004253D4))
                        wolfen_count = min(260, int(pine.read32(wolfen_count_addr)))
                    except Exception:
                        wolfen_count = -1

                    unlock_groups = d.get("SHOP_UNLOCK_GROUPS", {})
                    unlocked_names = set()
                    for threshold, names in unlock_groups.items():
                        try:
                            required = int(threshold)
                        except Exception:
                            continue
                        if wolfen_count >= required:
                            unlocked_names.update(str(n) for n in names)

                    def _duplicate_candidates_for_spend(spent: int) -> tuple[list[str], list[str]]:
                        duplicate_candidates = []
                        for candidate_name in sorted(unlocked_names):
                            candidate_lid = loc_by_name.get(candidate_name)
                            if (candidate_lid is None or candidate_lid in self._ap_checked or
                                    candidate_lid in self._ap_pending_checks or
                                    candidate_lid in self._ap_pending_shop_suppressions):
                                continue
                            candidate_spec = live_rules.get(candidate_name)
                            candidate_value = current_live.get(candidate_name)
                            if candidate_spec is None or candidate_value is None:
                                continue
                            if _live_rule_satisfied(candidate_spec, int(candidate_value)):
                                duplicate_candidates.append(candidate_name)
                        priced = [
                            candidate_name for candidate_name in duplicate_candidates
                            if self._ap_shop_spend_matches(candidate_name, int(spent))
                        ]
                        return duplicate_candidates, priced

                    # Some progressive vanilla handlers identify the exact purchase by
                    # changing a stronger AP-owned level (Golden->Basic/Silver or
                    # Speed->Magic). V0.8.15 persists those hints for a few seconds so
                    # reconciliation cannot erase them before the Nooties token is read.
                    live_transition_hints: list[tuple[float, str, int]] = []
                    for changed_name, old_value, new_value in live_changes:
                        spec = live_rules.get(changed_name, {})
                        try:
                            address = int(spec.get("address", -1))
                        except Exception:
                            continue
                        hint = None
                        if address == int(d["ADDR_BOOMY_TYPE"]):
                            if int(new_value) == 1 and int(old_value) > int(new_value):
                                hint = "Nativs City - Shop - Basic Boomy"
                            elif int(new_value) == 2 and int(old_value) > int(new_value):
                                hint = "Nativs City - Shop - Silver Boomy"
                            elif int(new_value) >= 3 and int(old_value) < int(new_value):
                                hint = "Nativs City - Shop - Golden Boomy"
                        elif address == int(d["ADDR_BOARD_LEVEL"]):
                            if int(new_value) == 1 and int(old_value) > int(new_value):
                                hint = "Nativs City - Shop - Magic Board"
                            elif int(new_value) >= 2 and int(old_value) < int(new_value):
                                hint = "Nativs City - Shop - Speed Board"
                        if hint is not None:
                            for price in self._ap_shop_allowed_spends(hint):
                                live_transition_hints.append((now, hint, int(price)))

                    correlated_hints = list(self._ap_shop_exact_reconcile_hints) + live_transition_hints

                    def _exact_hint_for_token(token_at: float, spent: int, safe_candidates: list[str]) -> str | None:
                        # Pick only a unique, temporally close exact hint with matching
                        # vanilla price. Reconcile hints may precede the money sample;
                        # live hints may be in the same or immediately following poll.
                        matches = []
                        for hint_at, hint_name, hint_price in correlated_hints:
                            if int(hint_price) != int(spent):
                                continue
                            if hint_name not in safe_candidates:
                                hint_lid = loc_by_name.get(hint_name)
                                if (hint_lid is None or hint_lid in self._ap_checked or
                                        hint_lid in self._ap_pending_checks or hint_name not in unlocked_names):
                                    continue
                            if abs(float(hint_at) - float(token_at)) > 2.0:
                                continue
                            matches.append((abs(float(hint_at) - float(token_at)), hint_name))
                        if not matches:
                            return None
                        matches.sort(key=lambda row: row[0])
                        nearest = matches[0][0]
                        names = {name for distance, name in matches if distance <= nearest + 0.08}
                        if len(names) == 1:
                            return next(iter(names))
                        return None

                    def _queue_duplicate_shop(name: str, token: tuple[float, int], label: str = "SHOP DUPLICATE CHECK") -> None:
                        lid = loc_by_name[name]
                        if lid in self._ap_checked or lid in self._ap_pending_checks:
                            return
                        reward_spec = shop_rewards.get(name)
                        previous_reward = self._ap_shop_reward_snapshots.get(name)
                        if reward_spec is not None and previous_reward is not None:
                            self._ap_pending_shop_suppressions[lid] = (name, reward_spec, int(previous_reward))
                        if self._ap_joined and self._ap_seed_build_verified:
                            durable = self._ap_queue_location_check(link, lid, name, d)
                            if durable and lid in self._ap_pending_shop_suppressions:
                                self._ap_suppress_shop_reward(pine, lid, self._ap_pending_shop_suppressions[lid])
                            detail = "native runtime identity" if label == "SHOP NATIVE CHECK" else "item already owned"
                            self._log_threadsafe(
                                f"{label} queued -> Archipelago: {name} [id={lid}] "
                                f"(spend={token[1]}; {detail})",
                                "ok",
                            )
                        else:
                            self._ap_pending_shop_suppressions.pop(lid, None)
                            self._log_threadsafe(
                                f"Duplicate shop purchase identified but NOT sent: {name}.",
                                "warn",
                            )

                    # Pass 1: resolve every mature token independently. Exact live/stock
                    # identity wins automatically. For manual ambiguity, only the NEWEST
                    # unresolved spend may open a normal dialog. Older spends are marked
                    # deferred and, if they need a dialog later, are explicitly labelled
                    # as a PREVIOUS purchase. This prevents a 100-Nooties token from a
                    # Golden/Speed/Yellow purchase being mistaken for a later 50-Nooties
                    # Silver Boomy purchase.
                    token_snapshots = list(self._ap_shop_purchase_tokens)
                    newest_token_at = token_snapshots[-1][0] if token_snapshots else None
                    for token_snapshot in token_snapshots:
                        token_at, token_spent = token_snapshot
                        token_age = now - token_at
                        # Give live/serialized transitions a few watcher ticks to resolve
                        # automatically, but prompt quickly enough that the player cannot
                        # easily move on to another purchase and confuse the token.
                        if token_age < 1.20:
                            continue
                        # V0.8.21: native runtime identity wins before every older
                        # price/serializer heuristic.
                        native_hint = self._ap_shop_native_hints.pop(token_at, None)
                        if native_hint is not None:
                            native_name, native_spent, native_reason = native_hint
                            token = _consume_specific_shop_token(token_snapshot)
                            if token is not None:
                                self._ap_shop_prompted_tokens.discard(token_at)
                                self._ap_shop_deferred_prompt_tokens.discard(token_at)
                                self._log_threadsafe(
                                    f"Native Shop token resolved: {native_name} "
                                    f"(spend={native_spent}; {native_reason}).",
                                    "ok",
                                )
                                _queue_duplicate_shop(native_name, token, "SHOP NATIVE CHECK")
                            continue

                        duplicate_candidates, safe_candidates = _duplicate_candidates_for_spend(int(token_spent))

                        manual_choice = self._ap_shop_manual_choices.pop(token_at, None)
                        if manual_choice is not None:
                            if manual_choice in safe_candidates:
                                token = _consume_specific_shop_token(token_snapshot)
                                if token is not None:
                                    self._ap_shop_prompted_tokens.discard(token_at)
                                    self._ap_shop_deferred_prompt_tokens.discard(token_at)
                                    _queue_duplicate_shop(manual_choice, token, "SHOP CONFIRMED CHECK")
                                continue
                            self._ap_shop_prompted_tokens.discard(token_at)
                            self._log_threadsafe(
                                f"Shop confirmation ignored because the candidate set changed: {manual_choice}.",
                                "warn",
                            )

                        # V0.8.17: same-price duplicates are resolved from the LIVE
                        # shop availability array before any UI fallback. This is the
                        # exact stock state, independent from Kya's AP-owned inventory.
                        runtime_hint = None
                        if len(safe_candidates) > 1:
                            # V0.8.20: first correlate this exact Nooties token with
                            # the rolling 1->0 edge captured in the same/adjacent poll.
                            # This prevents old 50/100 tokens from being resolved only
                            # after several later purchases.
                            runtime_hint = self._ap_recent_shop_group_edge(token_at, int(token_spent), safe_candidates)
                            if runtime_hint is None:
                                # Retain the older long-baseline Ghidra/group and global
                                # source heuristics as safe secondary evidence.
                                runtime_hint = self._ap_grouped_live_shop_candidate(pine, current_shop, safe_candidates)
                            if runtime_hint is None:
                                runtime_hint = self._ap_live_shop_candidate(pine, current_shop, safe_candidates)
                        if runtime_hint is not None:
                            self._log_threadsafe(
                                f"Live shop slot identified automatically: {runtime_hint} (spend={token_spent}).",
                                "ok",
                            )
                            safe_candidates = [runtime_hint]

                        hint = _exact_hint_for_token(token_at, int(token_spent), safe_candidates)
                        if hint is not None:
                            safe_candidates = [hint]
                        # V0.9.35: PRICE-ONLY IS NOT IDENTITY. A single candidate
                        # surviving the price/unlock/owned filter is still just a
                        # guess when serialized shop stock is 0/18 (confirmed by
                        # 18 before/after purchase captures, Oct 30, 2026).
                        # Only an exact causal hint (native selection is handled
                        # earlier; live reward / selected shop source here) may
                        # authorize this automatic check. Unproven tokens remain
                        # pending rather than validating the wrong AP location.
                        if len(safe_candidates) == 1:
                            if hint is None and runtime_hint is None:
                                self._ap_shop_deferred_prompt_tokens.add(token_at)
                                continue
                            token = _consume_specific_shop_token(token_snapshot)
                            if token is not None:
                                self._post_ui(self._ap_forget_shop_choice_token, token_at)
                                _queue_duplicate_shop(safe_candidates[0], token, "SHOP EXACT-HINT CHECK")
                            continue

                        if len(safe_candidates) > 1:
                            # If a live-source pool exists, allow a few extra watcher
                            # ticks for the 1->0 transition to settle before falling
                            # back to UI. Normal runs should therefore remain fully
                            # automatic; the dialog is emergency-only.
                            if (self._ap_shop_runtime_source is not None or self._ap_shop_runtime_candidates or
                                    self._ap_shop_runtime_snapshots) and token_age < 3.0:
                                continue
                            # V0.8.20: no manual shop popup. Every item has an
                            # exact serialized destination address+mask, and Ghidra gives
                            # the live mask->offset relation. Keep the token isolated until
                            # one of those exact signals resolves it. This can be delayed by
                            # the game's serializer, but it can never guess the wrong shop.
                            self._ap_shop_deferred_prompt_tokens.add(token_at)

                    # Pass 2: diagnostics for any still-unresolved mature token. Warn
                    # per token instead of only looking at queue[0], so one ambiguous
                    # purchase can never hide the state of later purchases.
                    for token_at, token_spent in list(self._ap_shop_purchase_tokens):
                        token_age = now - token_at
                        if token_age < 3.0 or token_at in self._ap_shop_ambiguous_token_warned:
                            continue
                        duplicate_candidates, safe_candidates = _duplicate_candidates_for_spend(int(token_spent))
                        self._ap_shop_ambiguous_token_warned.add(token_at)
                        if safe_candidates:
                            self._log_threadsafe(
                                "Shop spend unconfirmed (price is NOT article identity); token retained for "
                                "native item / exact live or stock confirmation: "
                                f"spend={token_spent}, candidate_prices={', '.join(safe_candidates)}, wolfens={wolfen_count}.",
                                "warn",
                            )
                        elif duplicate_candidates:
                            self._log_threadsafe(
                                "Duplicate shop spend did not match the observed price table; token retained independently: "
                                f"spend={token_spent}, owned candidates={', '.join(duplicate_candidates)}.",
                                "warn",
                            )
                        else:
                            self._log_threadsafe(
                                "Duplicate shop spend has no owned/unlocked candidate yet; token retained independently "
                                f"for serialized confirmation: spend={token_spent}, wolfens={wolfen_count}.",
                                "warn",
                            )



    def _ap_shop_group_definitions(self, d: dict) -> dict[int, dict[str, tuple[int, int]]]:
        """Return serialized shop groups as {dest_addr: {name: (mask, live_offset)}}.

        0x006FA7F0 (Basic Boomy) is a special standalone serialization record and
        is intentionally omitted here; Basic Boomy already has an exact price and
        an exact Boomy downgrade signal.
        """
        groups: dict[int, dict[str, tuple[int, int]]] = {}
        for name, spec in d.get("SHOP_LOCATION_CONDITIONS", {}).items():
            try:
                dest_addr, mask = int(spec[0]), int(spec[1])
            except Exception:
                continue
            live_offset = SHOP_RUNTIME_MASK_OFFSET.get(mask)
            if live_offset is None or dest_addr == 0x006FA7F0:
                continue
            groups.setdefault(dest_addr, {})[str(name)] = (mask, live_offset)
        return groups

    def _ap_scan_shop_group_bases(self, pine: PineClient, current_shop: dict[str, bool]) -> None:
        """Find relocatable five-slot shop source groups without guessing item order.

        Ghidra showed that each serializer group owns five boolean availability
        fields at fixed +0x18 steps.  We first locate structures whose five fields
        are genuinely 0/1, then score each structure against each *serialized*
        group using that group's exact address/mask mapping.
        """
        if (self._ap_current_zone or "") != "Nativs City":
            return
        now = time.monotonic()
        if now - float(getattr(self, "_ap_shop_group_last_scan", 0.0)) < 4.0:
            return
        self._ap_shop_group_last_scan = now
        groups = self._ap_shop_group_definitions(self._ap_data)
        if not groups:
            return

        generic: list[int] = []
        offsets = (0x18, 0x30, 0x48, 0x60, 0x78)
        for scan_start, scan_end in SHOP_RUNTIME_GROUP_SCAN_WINDOWS:
            start = (int(scan_start) + 0xF) & ~0xF
            candidates = list(range(start, int(scan_end), 0x10))
            for off in offsets:
                if not candidates:
                    break
                try:
                    vals = pine.read32_many([base + off for base in candidates], batch_size=4096)
                except Exception:
                    candidates = []
                    break
                candidates = [base for base, value in zip(candidates, vals) if int(value) in (0, 1)]
                if len(candidates) <= 512 and off >= 0x48:
                    # Keep filtering all five offsets, but the candidate set is now
                    # small enough that later reads are cheap.
                    pass
            generic.extend(int(x) for x in candidates[:2048])
            if generic:
                break
        generic = list(dict.fromkeys(generic))
        if not generic:
            if not getattr(self, "_ap_shop_group_scan_logged", False):
                self._log_threadsafe(
                    "Ghidra shop-group source not found yet; exact serialized-address watcher remains armed.",
                    "warn",
                )
                self._ap_shop_group_scan_logged = True
            return

        group_candidates: dict[int, list[int]] = {}
        group_scores: dict[tuple[int, int], tuple[int, int]] = {}
        for dest_addr, items in groups.items():
            rows = []
            names = list(items)
            for base in generic:
                try:
                    vals = pine.read32_many([base + items[name][1] for name in names])
                except Exception:
                    continue
                valid = sum(1 for v in vals if int(v) in (0, 1))
                matches = sum(
                    1 for name, v in zip(names, vals)
                    if int(v) == (1 if bool(current_shop.get(name, False)) else 0)
                )
                rows.append((matches, valid, int(base)))
            if not rows:
                continue
            rows.sort(reverse=True)
            best_matches, best_valid, _ = rows[0]
            # Retain tied/near-tied copies; causal before/after transitions pick the
            # actual master copy.  Max 32 per group keeps polling inexpensive.
            kept = []
            for matches, valid, base in rows:
                if valid < len(names):
                    continue
                if matches < max(0, best_matches - 1):
                    continue
                kept.append(base)
                group_scores[(dest_addr, base)] = (matches, valid)
                if len(kept) >= 32:
                    break
            if kept:
                group_candidates[int(dest_addr)] = kept

        if group_candidates:
            self._ap_shop_group_candidates = group_candidates
            self._ap_shop_group_scores = group_scores
            self._ap_shop_group_scan_logged = False
            total = sum(len(v) for v in group_candidates.values())
            if not getattr(self, "_ap_shop_group_prime_logged", False):
                self._log_threadsafe(
                    f"Ghidra grouped shop watcher armed: {len(group_candidates)} serialized group(s), "
                    f"{total} live source candidate(s). Exact mask->offset mapping active.",
                    "ok",
                )

    def _ap_prime_shop_group_sources(self, pine: PineClient, current_shop: dict[str, bool]) -> None:
        if (self._ap_current_zone or "") != "Nativs City":
            return
        self._ap_scan_shop_group_bases(pine, current_shop)
        groups = self._ap_shop_group_definitions(self._ap_data)
        snapshots: dict[int, dict[int, dict[str, int]]] = {}
        for dest_addr, bases in getattr(self, "_ap_shop_group_candidates", {}).items():
            items = groups.get(int(dest_addr), {})
            if not items:
                continue
            names = list(items)
            for base in bases[:32]:
                try:
                    vals = pine.read32_many([int(base) + items[name][1] for name in names])
                except Exception:
                    continue
                row = {name: int(v) for name, v in zip(names, vals)}
                if all(v in (0, 1) for v in row.values()):
                    snapshots.setdefault(int(dest_addr), {})[int(base)] = row
        if snapshots:
            self._ap_shop_group_snapshots = snapshots
            if not getattr(self, "_ap_shop_group_prime_logged", False):
                self._log_threadsafe(
                    "Ghidra grouped shop pre-purchase baselines captured; same-price purchases can resolve without UI.",
                    "ok",
                )
                self._ap_shop_group_prime_logged = True


    def _ap_capture_shop_group_edges(self, pine: PineClient, current_shop: dict[str, bool]) -> None:
        """Capture *per-poll* 1->0 live stock edges for the Ghidra shop groups.

        V0.8.19 compared every ambiguous purchase against one old baseline.  If an
        early 50/100-Nooties token stayed unresolved, later purchases accumulated
        against that same baseline and several AP checks could therefore arrive in
        a burst.  This sampler advances its baseline every watcher poll, so one
        physical purchase produces one isolated edge event even while older tokens
        are still pending.
        """
        if (self._ap_current_zone or "") != "Nativs City":
            return
        groups = self._ap_shop_group_definitions(self._ap_data)
        if not groups:
            return
        if not getattr(self, "_ap_shop_group_candidates", None):
            self._ap_scan_shop_group_bases(pine, current_shop)
        if not getattr(self, "_ap_shop_group_candidates", None):
            return

        now = time.monotonic()
        previous = getattr(self, "_ap_shop_group_rolling_states", {})
        next_states: dict[int, dict[int, dict[str, int]]] = {}
        votes: dict[str, int] = {}
        evidence: dict[str, int] = {}
        sources: dict[str, list[tuple[int, int]]] = {}

        for dest_addr, bases in getattr(self, "_ap_shop_group_candidates", {}).items():
            items = groups.get(int(dest_addr), {})
            if not items:
                continue
            names = list(items)
            for base in bases[:32]:
                try:
                    vals = pine.read32_many([int(base) + items[name][1] for name in names])
                except Exception:
                    continue
                row = {name: int(v) for name, v in zip(names, vals)}
                if not all(v in (0, 1) for v in row.values()):
                    continue
                next_states.setdefault(int(dest_addr), {})[int(base)] = row
                before = previous.get(int(dest_addr), {}).get(int(base))
                if not before:
                    continue
                transitioned = [name for name in names if before.get(name) == 1 and row.get(name) == 0]
                if len(transitioned) != 1:
                    continue
                name = transitioned[0]
                score = getattr(self, "_ap_shop_group_scores", {}).get((int(dest_addr), int(base)), (0, 0))
                weight = 10 + int(score[0]) * 2 + int(score[1])
                votes[name] = votes.get(name, 0) + weight
                evidence[name] = evidence.get(name, 0) + 1
                sources.setdefault(name, []).append((int(dest_addr), int(base)))

        self._ap_shop_group_rolling_states = next_states
        # Keep only a tight history: watcher cadence is ~0.75 s and a real purchase
        # edge should occur in the same or adjacent poll as the Nooties decrement.
        self._ap_shop_group_edge_events = [
            event for event in getattr(self, "_ap_shop_group_edge_events", [])
            if now - float(event[0]) <= 4.0
        ]
        if votes:
            self._ap_shop_group_edge_events.append((now, votes, evidence, sources))

    def _ap_recent_shop_group_edge(self, token_at: float, spent: int, candidates: list[str]) -> str | None:
        """Correlate one Nooties token with the isolated live edge from that purchase."""
        allowed = {
            str(name) for name in candidates
            if self._ap_shop_spend_matches(str(name), int(spent))
        }
        if not allowed:
            return None
        total_votes: dict[str, int] = {}
        total_evidence: dict[str, int] = {}
        for event_at, votes, evidence, _sources in getattr(self, "_ap_shop_group_edge_events", []):
            delta = abs(float(event_at) - float(token_at))
            if delta > 2.25:
                continue
            # Prefer the same watcher tick / adjacent tick.  This is intentionally
            # temporal: an old unresolved token can no longer inherit a later edge.
            factor = 4 if delta <= 0.80 else (3 if delta <= 1.30 else (2 if delta <= 1.80 else 1))
            for name in allowed:
                if name in votes:
                    total_votes[name] = total_votes.get(name, 0) + int(votes[name]) * factor
                    total_evidence[name] = total_evidence.get(name, 0) + int(evidence.get(name, 0))
        if not total_votes:
            return None
        ranking = sorted(total_votes.items(), key=lambda row: row[1], reverse=True)
        if len(ranking) > 1:
            top, second = ranking[0][1], ranking[1][1]
            # Never guess on a tie or near-tie. Other exact signals remain available.
            if top <= second or top < int(second * 1.15):
                return None
        winner = ranking[0][0]
        self._log_threadsafe(
            f"Per-purchase Ghidra shop edge identified automatically: {winner} "
            f"(spend={spent}; evidence={total_evidence.get(winner, 0)}).",
            "ok",
        )
        return winner

    def _ap_grouped_live_shop_candidate(self, pine: PineClient, current_shop: dict[str, bool], candidates: list[str]) -> str | None:
        """Resolve a same-price purchase from exact serialized group/mask semantics."""
        candidates = [str(n) for n in candidates]
        if len(candidates) <= 1:
            return candidates[0] if candidates else None
        groups = self._ap_shop_group_definitions(self._ap_data)
        if not getattr(self, "_ap_shop_group_snapshots", None):
            self._ap_prime_shop_group_sources(pine, current_shop)
        votes: dict[str, int] = {}
        evidence = 0
        for dest_addr, items in groups.items():
            relevant = [n for n in candidates if n in items]
            if not relevant:
                continue
            for base, before in getattr(self, "_ap_shop_group_snapshots", {}).get(int(dest_addr), {}).items():
                try:
                    vals = pine.read32_many([int(base) + items[n][1] for n in relevant])
                except Exception:
                    continue
                now_row = {n: int(v) for n, v in zip(relevant, vals)}
                transitioned = [n for n in relevant if before.get(n) == 1 and now_row.get(n) == 0]
                if len(transitioned) != 1:
                    continue
                name = transitioned[0]
                score = getattr(self, "_ap_shop_group_scores", {}).get((int(dest_addr), int(base)), (0, 0))
                weight = 10 + int(score[0]) * 2 + int(score[1])
                votes[name] = votes.get(name, 0) + weight
                evidence += 1
        if not votes:
            return None
        ranking = sorted(votes.items(), key=lambda row: row[1], reverse=True)
        if len(ranking) > 1 and ranking[0][1] == ranking[1][1]:
            return None
        winner = ranking[0][0]
        self._log_threadsafe(
            f"Ghidra live shop flag identified automatically: {winner} "
            f"(exact serialized group/mask; evidence={evidence}).",
            "ok",
        )
        return winner

    def _ap_find_shop_runtime_source(self, pine: PineClient, current_shop: dict[str, bool], ignore_names=()) -> int | None:
        """Locate the relocatable live shop availability array.

        V0.8.18 keeps *all* high-scoring bases when the heap contains several
        look-alike 0/1 patterns.  V0.8.17 rejected the source whenever the best
        and second-best scores tied (the real log reached 14 valid / 13 matches),
        which forced the manual dialog even though the useful signal was present.
        """
        now = time.monotonic()
        ignored = {str(n) for n in ignore_names}
        loc_map = self._ap_data.get("LOCATION_NAME_TO_ID", {})

        def expected_for(name: str) -> int:
            lid = loc_map.get(name)
            if lid is not None and (int(lid) in self._ap_checked or int(lid) in self._ap_pending_checks):
                return 0
            return 1 if bool(current_shop.get(name, False)) else 0

        def validate_base(base: int, sample_names: list[str]) -> tuple[int, int]:
            if not sample_names:
                return (0, 0)
            vals = pine.read32_many([
                int(base) + SHOP_RUNTIME_SLOT_INDEX[n] * SHOP_RUNTIME_STRIDE for n in sample_names
            ])
            valid = sum(1 for v in vals if int(v) in (0, 1))
            matches = sum(1 for n, v in zip(sample_names, vals) if int(v) == expected_for(n))
            return valid, matches

        # Validate the unique cached base first.
        if self._ap_shop_runtime_source is not None:
            sample_names = [n for n in SHOP_RUNTIME_SLOT_INDEX if n not in ignored][:10]
            try:
                valid, matches = validate_base(self._ap_shop_runtime_source, sample_names)
                if valid >= max(6, len(sample_names) - 1) and matches >= max(5, len(sample_names) - 2):
                    return self._ap_shop_runtime_source
            except Exception:
                pass
            self._ap_shop_runtime_source = None

        # A candidate pool found during the proactive baseline scan is still useful
        # even when there is no single winner. Do not rescan the full heap every tick.
        if now - float(self._ap_shop_runtime_last_scan) < 4.0:
            return None
        self._ap_shop_runtime_last_scan = now

        names = [n for n in SHOP_RUNTIME_SLOT_INDEX if n not in ignored and n in current_shop]
        if len(names) < 6:
            return None
        names.sort(key=lambda n: (expected_for(n) == 0, SHOP_RUNTIME_SLOT_INDEX[n]))
        anchor_names = names[:10]

        scored: list[tuple[tuple[int, int], int]] = []
        for scan_start, scan_end in SHOP_RUNTIME_SCAN_WINDOWS:
            start = (int(scan_start) + 0xF) & ~0xF
            candidates = list(range(start, int(scan_end), 0x10))
            for anchor_name in anchor_names[:6]:
                if not candidates:
                    break
                offset = SHOP_RUNTIME_SLOT_INDEX[anchor_name] * SHOP_RUNTIME_STRIDE
                try:
                    vals = pine.read32_many([base + offset for base in candidates], batch_size=4096)
                except Exception:
                    candidates = []
                    break
                expected = expected_for(anchor_name)
                candidates = [base for base, value in zip(candidates, vals) if int(value) == expected]
                if len(candidates) <= 192:
                    break
            if not candidates:
                continue

            verify_names = [n for n in SHOP_RUNTIME_SLOT_INDEX if n not in ignored and n in current_shop]
            for base in candidates[:1024]:
                try:
                    valid, matches = validate_base(base, verify_names)
                except Exception:
                    continue
                scored.append(((valid, matches), int(base)))

            # If we already have a compact high-quality pool in the fast window,
            # there is no need to scan the wider fallback region.
            if scored:
                scored.sort(key=lambda row: row[0], reverse=True)
                top_valid, top_matches = scored[0][0]
                if top_valid >= max(8, len(names) - 2) and top_matches >= max(6, len(names) - 3):
                    break

        if not scored:
            self._ap_shop_runtime_candidates = []
            self._ap_shop_runtime_candidate_scores = {}
            if not self._ap_shop_runtime_scan_fail_logged:
                self._log_threadsafe("Live shop source not found yet; exact-address fallback remains armed; no manual popup.", "warn")
                self._ap_shop_runtime_scan_fail_logged = True
            return None

        scored.sort(key=lambda row: row[0], reverse=True)
        top_score = scored[0][0]
        required_valid = max(8, len(names) - 2)
        required_matches = max(6, len(names) - 3)

        # Keep bases that are structurally strong and no more than one match below
        # the best candidate. This converts a score tie from a failure into a pool
        # that can be disambiguated causally by the next purchase transition.
        plausible = []
        for score, base in scored:
            valid, matches = score
            if valid < required_valid or matches < required_matches:
                continue
            if valid < top_score[0] - 1 or matches < top_score[1] - 1:
                continue
            plausible.append((score, base))
            if len(plausible) >= 64:
                break

        self._ap_shop_runtime_candidates = [base for _score, base in plausible]
        self._ap_shop_runtime_candidate_scores = {base: score for score, base in plausible}

        if not plausible:
            if not self._ap_shop_runtime_scan_fail_logged:
                self._log_threadsafe(
                    f"Live shop source scan too weak (best valid={top_score[0]}, matches={top_score[1]}); "
                    "exact-address fallback kept; no manual popup.",
                    "warn",
                )
                self._ap_shop_runtime_scan_fail_logged = True
            return None

        # A strictly better best row is safe to cache as the unique source. A tie is
        # deliberately retained for consensus instead of rejected.
        second_score = plausible[1][0] if len(plausible) > 1 else (-1, -1)
        if len(plausible) == 1 or plausible[0][0] > second_score:
            self._ap_shop_runtime_source = int(plausible[0][1])
            self._ap_shop_runtime_scan_fail_logged = False
            self._log_threadsafe(
                f"Live shop source resolved dynamically: 0x{self._ap_shop_runtime_source:08X} "
                f"(structural Yellow offset +0x78; score={top_score[1]}/{len(names)}).",
                "ok",
            )
            return self._ap_shop_runtime_source

        self._ap_shop_runtime_source = None
        self._ap_shop_runtime_scan_fail_logged = False
        if not self._ap_shop_runtime_prime_logged:
            self._log_threadsafe(
                f"Live shop source pool retained for causal consensus: {len(plausible)} candidate base(s), "
                f"best valid={top_score[0]}, matches={top_score[1]}. No manual choice is needed while a "
                "unique 1->0 slot transition can be observed.",
                "info",
            )
        return None

    def _ap_prime_shop_runtime_sources(self, pine: PineClient, current_shop: dict[str, bool]) -> None:
        """Snapshot plausible live-source bases while no purchase is pending.

        This is the key V0.8.18 change: the launcher learns the pre-purchase 1/0
        state *before* the user buys an ambiguous same-price item. Later, a unique
        1->0 transition identifies Silver/Golden/Yellow or the 50-Nooties group
        without touching Kya's inventory and without a popup.
        """
        if (self._ap_current_zone or "") != "Nativs City":
            return
        try:
            unique = self._ap_find_shop_runtime_source(pine, current_shop, ignore_names=())
        except Exception:
            return
        bases = []
        if unique is not None:
            bases.append(int(unique))
        bases.extend(int(b) for b in self._ap_shop_runtime_candidates if int(b) not in bases)
        if not bases:
            return

        names = [n for n in SHOP_RUNTIME_SLOT_INDEX if n in current_shop]
        snapshots: dict[int, dict[str, int]] = {}
        for base in bases[:64]:
            try:
                vals = pine.read32_many([
                    base + SHOP_RUNTIME_SLOT_INDEX[name] * SHOP_RUNTIME_STRIDE for name in names
                ])
            except Exception:
                continue
            row = {name: int(value) for name, value in zip(names, vals)}
            # Keep only bases with enough actual boolean availability fields.
            if sum(1 for value in row.values() if value in (0, 1)) >= max(8, len(names) - 3):
                snapshots[base] = row
        if snapshots:
            self._ap_shop_runtime_snapshots = snapshots
            if not self._ap_shop_runtime_prime_logged:
                label = f"0x{unique:08X}" if unique is not None else f"{len(snapshots)} consensus bases"
                self._log_threadsafe(
                    f"Live shop pre-purchase baseline armed ({label}); same-price shops can auto-resolve by 1->0 transition.",
                    "ok",
                )
                self._ap_shop_runtime_prime_logged = True

    def _ap_live_shop_candidate(self, pine: PineClient, current_shop: dict[str, bool], candidates: list[str]) -> str | None:
        """Return an exact same-price candidate from live stock by causal consensus."""
        candidates = [str(n) for n in candidates if n in SHOP_RUNTIME_SLOT_INDEX]
        if len(candidates) < 2:
            return candidates[0] if len(candidates) == 1 else None

        source = self._ap_find_shop_runtime_source(pine, current_shop, ignore_names=candidates)
        bases = []
        if source is not None:
            bases.append(int(source))
        # Prefer the pre-purchase snapshot pool because it contains the causal
        # baseline. Add any newly found plausible bases only as lower-confidence
        # absolute-state voters.
        bases.extend(int(b) for b in self._ap_shop_runtime_snapshots if int(b) not in bases)
        bases.extend(int(b) for b in self._ap_shop_runtime_candidates if int(b) not in bases)
        if not bases:
            return None

        transition_votes: dict[str, int] = {}
        absolute_votes: dict[str, int] = {}
        diagnostics = []
        for base in bases[:64]:
            try:
                vals = pine.read32_many([
                    base + SHOP_RUNTIME_SLOT_INDEX[name] * SHOP_RUNTIME_STRIDE for name in candidates
                ])
            except Exception:
                continue
            row = {name: int(value) for name, value in zip(candidates, vals)}
            if any(value not in (0, 1) for value in row.values()):
                continue

            before = self._ap_shop_runtime_snapshots.get(base, {})
            transitioned = [name for name in candidates if before.get(name) == 1 and row.get(name) == 0]
            sold = [name for name in candidates if row.get(name) == 0]
            score = self._ap_shop_runtime_candidate_scores.get(base, (0, 0))
            weight = 1 + int(score[0]) + int(score[1])
            if len(transitioned) == 1:
                transition_votes[transitioned[0]] = transition_votes.get(transitioned[0], 0) + weight * 4
                diagnostics.append((base, "delta", transitioned[0]))
            elif len(sold) == 1:
                absolute_votes[sold[0]] = absolute_votes.get(sold[0], 0) + weight
                diagnostics.append((base, "state", sold[0]))

        def choose(votes: dict[str, int], require_margin: bool) -> str | None:
            if not votes:
                return None
            ranking = sorted(votes.items(), key=lambda row: row[1], reverse=True)
            if len(ranking) == 1:
                return ranking[0][0]
            if ranking[0][1] == ranking[1][1]:
                return None
            if require_margin and ranking[0][1] < ranking[1][1] + 3:
                return None
            return ranking[0][0]

        winner = choose(transition_votes, require_margin=False)
        method = "1->0 transition consensus"
        if winner is None:
            winner = choose(absolute_votes, require_margin=True)
            method = "live-state consensus"
        if winner is None:
            return None

        self._log_threadsafe(
            f"Live shop slot identified automatically by {method}: {winner} "
            f"(candidates={len(candidates)}, source_votes={len(diagnostics)}).",
            "ok",
        )
        return winner

    def _ap_defer_shop_prompt_for_new_purchase(self, new_token_at: float) -> None:
        """Close any older ambiguity dialog as soon as a newer purchase is seen.

        The older token remains unresolved and may be offered later as a clearly
        labelled PREVIOUS purchase, but it can never sit on screen and masquerade
        as the player's new click.
        """
        current = self._ap_shop_choice_token
        if current is None or float(current) >= float(new_token_at):
            return
        self._ap_shop_deferred_prompt_tokens.add(float(current))
        self._ap_shop_prompted_tokens.discard(float(current))
        try:
            if self._ap_shop_choice_window is not None and self._ap_shop_choice_window.winfo_exists():
                self._ap_shop_choice_window.destroy()
        except Exception:
            pass
        self._ap_shop_choice_window = None
        self._ap_shop_choice_token = None
        # Drop scheduled/open backlog rows older than this new click. Their spend
        # tokens remain in the watcher and can be requested again later if needed.
        for old_at, _spent, _candidates in self._ap_shop_choice_backlog:
            if float(old_at) < float(new_token_at):
                self._ap_shop_deferred_prompt_tokens.add(float(old_at))
                self._ap_shop_prompted_tokens.discard(float(old_at))
        self._ap_shop_choice_backlog = [
            row for row in self._ap_shop_choice_backlog if float(row[0]) >= float(new_token_at)
        ]



    def _ap_request_shop_disambiguation(self, token_at: float, spent: int, candidates: list[str]) -> None:
        """Ask the player which same-price shop entry was just bought.

        This is a safety fallback only. Exact live inventory transitions and exact
        serialized stock transitions still resolve automatically first.  The dialog
        exists so an already-owned duplicate can NEVER be delayed until later shop
        purchases or guessed as the wrong location.
        """
        if self._closing or token_at in self._ap_shop_manual_choices or token_at in self._ap_shop_prompted_tokens:
            return
        clean = tuple(dict.fromkeys(str(name) for name in candidates if name))
        if len(clean) < 2:
            return
        self._ap_shop_prompted_tokens.add(token_at)
        self._post_ui(self._ap_enqueue_shop_choice_dialog, float(token_at), int(spent), clean)

    def _ap_enqueue_shop_choice_dialog(self, token_at: float, spent: int, candidates: tuple[str, ...]) -> None:
        if token_at not in self._ap_shop_prompted_tokens:
            return  # Scene changed while this UI event was queued.
        if self._closing:
            self._ap_shop_prompted_tokens.discard(token_at)
            return
        if self._ap_shop_choice_window is not None:
            try:
                if self._ap_shop_choice_window.winfo_exists():
                    if not any(abs(t - token_at) < 1e-9 for t, _s, _c in self._ap_shop_choice_backlog):
                        self._ap_shop_choice_backlog.append((token_at, spent, candidates))
                    return
            except Exception:
                pass
        self._ap_open_shop_choice_dialog(token_at, spent, candidates)

    def _ap_open_shop_choice_dialog(self, token_at: float, spent: int, candidates: tuple[str, ...]) -> None:
        if self._closing:
            self._ap_shop_prompted_tokens.discard(token_at)
            return
        win = tk.Toplevel(self)
        self._ap_shop_choice_window = win
        self._ap_shop_choice_token = token_at
        win.title("Kya AP - Achat Shop ambigu")
        win.resizable(False, False)
        win.transient(self)
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass

        frame = tk.Frame(win, padx=16, pady=14)
        frame.pack(fill="both", expand=True)
        deferred = token_at in self._ap_shop_deferred_prompt_tokens
        if deferred:
            title_text = (
                f"Achat PRÉCÉDENT resté en attente : {spent} Nooties\n"
                "Quel objet correspondait à CE paiement ?"
            )
        else:
            title_text = f"Achat détecté : {spent} Nooties\nQuel objet viens-tu d'acheter ?"
        tk.Label(
            frame,
            text=title_text,
            font=("Segoe UI Semibold", 11),
            justify="center",
        ).pack(pady=(0, 10))
        explanation = "Aucun check AP n'est envoyé tant que l'objet exact n'est pas choisi."
        if deferred:
            explanation += "\nCe dialogue ne correspond PAS forcément à ton dernier achat."
        tk.Label(
            frame,
            text=explanation,
            font=("Segoe UI", 9),
            justify="center",
        ).pack(pady=(0, 10))

        def finish(choice: str | None) -> None:
            if choice is not None:
                self._ap_shop_manual_choices[token_at] = choice
                self._ap_shop_deferred_prompt_tokens.discard(token_at)
                short = choice.replace("Nativs City - Shop - ", "")
                self._log(f"SHOP confirmé manuellement : {short} ({spent} Nooties).", "ok")
            else:
                # Keep the token alive and allow the watcher to ask again later.
                self._ap_shop_prompted_tokens.discard(token_at)
                self._log("Achat Shop ambigu laissé en attente; aucun check AP n'a été envoyé.", "warn")
            try:
                win.destroy()
            except Exception:
                pass
            self._ap_shop_choice_window = None
            self._ap_shop_choice_token = None
            if self._ap_shop_choice_backlog:
                nxt = self._ap_shop_choice_backlog.pop(0)
                self.after(30, lambda args=nxt: self._ap_open_shop_choice_dialog(*args))

        for name in candidates:
            short = name.replace("Nativs City - Shop - ", "")
            tk.Button(
                frame,
                text=short,
                width=32,
                command=lambda n=name: finish(n),
            ).pack(fill="x", pady=2)

        tk.Button(frame, text="Annuler / laisser en attente", command=lambda: finish(None)).pack(fill="x", pady=(10, 0))
        win.protocol("WM_DELETE_WINDOW", lambda: finish(None))
        try:
            win.update_idletasks()
            x = self.winfo_rootx() + max(0, (self.winfo_width() - win.winfo_width()) // 2)
            y = self.winfo_rooty() + max(0, (self.winfo_height() - win.winfo_height()) // 2)
            win.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _ap_forget_shop_choice_token(self, token_at: float) -> None:
        """UI-safe cleanup when a token was auto-resolved before a pending dialog."""
        self._ap_shop_prompted_tokens.discard(token_at)
        self._ap_shop_deferred_prompt_tokens.discard(token_at)
        self._ap_shop_manual_choices.pop(token_at, None)
        self._ap_shop_choice_backlog = [row for row in self._ap_shop_choice_backlog if abs(row[0] - token_at) >= 1e-9]
        if self._ap_shop_choice_token is not None and abs(self._ap_shop_choice_token - token_at) < 1e-9:
            try:
                if self._ap_shop_choice_window is not None and self._ap_shop_choice_window.winfo_exists():
                    self._ap_shop_choice_window.destroy()
            except Exception:
                pass
            self._ap_shop_choice_window = None
            self._ap_shop_choice_token = None

    def _ap_intro_wolfen_completed(self, d: dict) -> bool:
        """Return True only after a real Wolfen rescue has become an AP check.

        No Boomy writes during the opening whistle tutorial: receiving any AP
        Boomy before that moment must be banked, not physically equipped.
        Check acknowledged AND queued checks so it also works while offline.
        """
        location_ids = d.get("LOCATION_NAME_TO_ID", {})
        sent_or_queued = self._ap_checked | set(self._ap_pending_checks)
        first_id = location_ids.get("Nativs City - Wolfen 01")
        if first_id is not None and int(first_id) in sent_or_queued:
            return True
        # Fallback for a saved game whose intro rescue was not in AP's history.
        # No other check types (shops/FT/etc.) unlock the Boomy during the intro.
        return any(" - Wolfen " in name and int(lid) in sent_or_queued
                   for name, lid in location_ids.items())

    def _ap_brazul_capture_tick(self, pine: PineClient) -> None:
        """Read-only story-state tracking; NEVER remove equipment ourselves.

        Captivity: bracelet high bit is set by vanilla; AP physical equipment
        writes stop. After the scripted pickup: normal equipment authority can
        resume, but vanilla's removal of Runes, Receptacle and mana level is
        kept even though their old AP item grants are still on the server.
        """
        before = self._brazul_capture_guard.phase
        after = self._brazul_capture_guard.poll(pine)
        if before == after:
            return
        if after == "captive":
            self._ap_rune_rollback_due.clear()
            self._ap_shop_live_ignore_until = max(self._ap_shop_live_ignore_until, time.monotonic() + 2.0)
            self._log_threadsafe(
                "BRAZUL CAPTURE: vanilla confiscation detected; AP equipment, "
                "Runes, Receptacle and max-mana restoration SUSPENDED.", "warn")
        elif after == "recovered":
            self._ap_rune_rollback_due.clear()
            self._ap_next_inventory_reconcile = 0.0
            self._log_threadsafe(
                "BRAZUL VANILLA RETURN: gear may sync again. Six Runes, "
                "Receptacle and max mana remain confiscated (vanilla story).", "ok")
        else:
            self._ap_next_inventory_reconcile = 0.0
            self._log_threadsafe(
                "BRAZUL STORY RESET: pre-capture state detected (e.g. savestate rollback); "
                "normal AP inventory authority resumed.", "info")

    def _ap_shop_authoritative_reward_target(self, name: str, reward_spec: dict, d: dict) -> int:
        """Return the inventory value that is allowed after a vanilla shop purchase.

        Nativs City shop entries are AP Locations only: buying them must never grant,
        remove, downgrade or otherwise mutate Kya's permanent inventory.  The player
        state is derived exclusively from items already received from Archipelago.
        The dedicated DEMO shop mode intentionally pre-owns all shop equipment, so it
        uses the corresponding max test values while still keeping Energy Bars under
        AP Progressive Life Gauge authority.
        """
        reward_addr = int(reward_spec["address"])
        kind = str(reward_spec.get("kind", "u32"))

        if kind == "life_gauge":
            return int(self._ap_owned_life_target(d))

        if getattr(self, "_ap_shop_test_mode", False):
            if reward_addr == int(d["ADDR_BOOMY_TYPE"]):
                return 3
            if reward_addr == int(d["ADDR_BRACELET_BITFIELD"]):
                return 0xFF
            if reward_addr == int(d["ADDR_BOARD_LEVEL"]):
                return 2
            return 1

        def count(item_name: str | None) -> int:
            if not item_name:
                return 0
            item_id = d.get("ITEM_NAME_TO_ID", {}).get(item_name)
            return int(self._ap_item_counts.get(int(item_id), 0)) if item_id is not None else 0

        if reward_addr == int(d["ADDR_BOOMY_TYPE"]):
            # Do not equip a Boomy until the opening Wolfen whistle/rescue is
            # done. Afterwards Basic Boomy is a guaranteed vanilla baseline;
            # AP Progressive Boomy can upgrade it to level 2/3.
            if not self._ap_intro_wolfen_completed(d):
                return 0
            progressive = min(2, count(d.get("ITEM_PROGRESSIVE_BOOMY")))
            return min(3, 1 + progressive)

        if reward_addr == int(d["ADDR_BRACELET_BITFIELD"]):
            progressive = min(7, count(d.get("ITEM_PROGRESSIVE_BRACELET")))
            # White/default bracelet is vanilla baseline bit 0.
            return (1 << (progressive + 1)) - 1

        if reward_addr == int(d["ADDR_BOARD_LEVEL"]):
            return min(2, count(d.get("ITEM_PROGRESSIVE_BOARD")))

        # Boolean shop equipment (Bouncers, Gloves, Jamgut, Telescope).
        for item_name, address in d.get("ITEM_SCENARIO_FLAGS", {}).items():
            if int(address) == reward_addr:
                return 1 if count(item_name) > 0 else 0

        # Defensive fallback: a mapped shop reward should always hit one of the
        # branches above. Returning zero is safer than preserving a vanilla grant.
        return 0

    def _ap_reconcile_owned_inventory(self, pine: PineClient, d: dict) -> None:
        """Keep AP-owned Kya inventory authoritative over vanilla shop/story rewrites."""
        if not self._ap_joined or not self._ap_seed_build_verified:
            return
        if self._brazul_capture_guard.captive:
            # The Boomy MUST stay confiscated so Kya can whistle and the Wolfen
            # can break the cage. Never synthesize an AP shop/purchase hint here.
            return

        fixed = []
        shop_rewards = d.get("SHOP_VANILLA_REWARD_STATE", {})

        # One authoritative target per underlying player field. Several shop
        # locations share Boomy/Board/Bracelet fields, so deduplicate by address.
        targets: dict[int, tuple[int, str]] = {}
        for location_name, reward_spec in shop_rewards.items():
            addr = int(reward_spec["address"])
            target = int(self._ap_shop_authoritative_reward_target(location_name, reward_spec, d))
            existing = targets.get(addr)
            if existing is None:
                targets[addr] = (target, location_name)
            elif existing[0] != target:
                # Shared fields must resolve to the same AP-owned value. Use the
                # stronger value defensively and make the discrepancy visible.
                targets[addr] = (max(existing[0], target), existing[1])

        # A vanilla purchase can grant one of these boolean shop abilities only
        # briefly: AP inventory authority restores it BEFORE the Shop watcher polls.
        # Preserve the item identity as a short-lived hint. A Nooties spend with the
        # exact price, an unlocked shop, and an unchecked AP location are STILL
        # required before the Shop watcher is allowed to send a location check.
        # Addresses must be unique; shared/progressive reward fields are excluded.
        bool_shop_names_by_addr: dict[int, list[str]] = {}
        for shop_name, rule in d.get("SHOP_LIVE_REWARD_RULES", {}).items():
            if (str(rule.get("mode", "")) == "bool_gain"
                    and shop_name in shop_rewards):
                addr = int(rule["address"])
                bool_shop_names_by_addr.setdefault(addr, []).append(shop_name)

        for addr, (target, label) in targets.items():
            # During the opening tutorial Kya must be free to whistle. The
            # story owns this field until the first rescued Wolfen is checked;
            # do not replace vanilla 0/1 or a cutscene transition with AP data.
            if (addr == int(d["ADDR_BOOMY_TYPE"])
                    and not self._ap_intro_wolfen_completed(d)):
                continue
            current = int(pine.read32(addr))
            if current != target:
                # V0.8.15: capture exact vanilla downgrade BEFORE AP authority
                # restores the field. This is the missing correlation for cases like
                # Golden Boomy (3) -> Silver Boomy (2) and Speed Board (2) ->
                # Magic Board (1).  The hint is still Nooties-gated later.
                purchase_hint = None
                if (self._ap_current_zone or "") == "Nativs City":
                    if addr == int(d.get("ADDR_BOOMY_TYPE", -1)) and current < target:
                        if current == 1:
                            purchase_hint = "Nativs City - Shop - Basic Boomy"
                        elif current == 2 and target >= 3:
                            purchase_hint = "Nativs City - Shop - Silver Boomy"
                    elif addr == int(d.get("ADDR_BOARD_LEVEL", -1)) and current < target:
                        if current == 1 and target >= 2:
                            purchase_hint = "Nativs City - Shop - Magic Board"
                    elif addr == int(d.get("ADDR_LIFE_GAUGE", -1)) and current > target:
                        # Extra Energy Bar 1 / 2 have the SAME vanilla reward
                        # address, SAME native item ID (16) and SAME price.
                        # A life increase proves a bar transaction, NOT which one.
                        # Do not invent an "exact" hint from the first unchecked
                        # location: wait for the native shop-table context or an
                        # actual individual serialized-stock transition.
                        purchase_hint = None
                    elif current == 1 and target == 0:
                        # Telescope, Climbing Gloves, Magic Bouncers, Jamgut Birdcall.
                        # Shop grant 0->1 was seen, but AP immediately restored 0.
                        # Without this hint, an exact 30-Nootie Telescope spend
                        # remains unresolved (V0.9.22 live playtest 2026-10-12).
                        bool_names = bool_shop_names_by_addr.get(addr, [])
                        if len(bool_names) == 1:
                            bool_name = bool_names[0]
                            bool_lid = d.get("LOCATION_NAME_TO_ID", {}).get(bool_name)
                            if (bool_lid is not None
                                    and int(bool_lid) not in self._ap_checked
                                    and int(bool_lid) not in self._ap_pending_checks):
                                purchase_hint = bool_name
                if purchase_hint is not None:
                    hint_price = self._ap_shop_expected_price(purchase_hint)
                    if hint_price is not None:
                        hint_now = time.monotonic()
                        # Preserve both modified and vanilla price as viable hints.
                        # Hints only apply with a real observed money token and
                        # a unique, temporally correlated shop item identity.
                        for accepted_spend in self._ap_shop_allowed_spends(purchase_hint):
                            self._ap_shop_exact_reconcile_hints.append(
                                (hint_now, purchase_hint, int(accepted_spend))
                            )
                        self._ap_shop_exact_reconcile_hints = [
                            row for row in self._ap_shop_exact_reconcile_hints if hint_now - row[0] <= 3.0
                        ]
                        self._log_threadsafe(
                            f"Shop exact transition captured before AP restore: {purchase_hint} "
                            f"({current}->{target}; expected spend={hint_price}).",
                            "info",
                        )
                pine.write32(addr, target)
                verified = int(pine.read32(addr))
                fixed.append(f"{label.split(' - Shop - ')[-1]} {current}->{verified}")

                # Life Gauge also has runtime current/max HP mirrors.
                reward_spec = next((spec for name, spec in shop_rewards.items() if int(spec["address"]) == addr), {})
                if str(reward_spec.get("kind", "u32")) == "life_gauge":
                    player = self._ap_player_pointer(pine, d)
                    if player is not None:
                        max_addr = player + int(d["PLAYER_MAX_HP_OFFSET"])
                        hp_addr = player + int(d["PLAYER_HP_OFFSET"])
                        max_hp = float(target)
                        pine.write32(max_addr, self._ap_float_to_raw(max_hp))
                        hp = self._ap_raw_to_float(pine.read32(hp_addr))
                        if hp == hp and 0.0 <= hp < 10000.0 and hp > max_hp:
                            pine.write32(hp_addr, self._ap_float_to_raw(max_hp))

        # Non-shop AP progression that still needs replay/reload reconciliation.
        def count(name: str | None) -> int:
            if not name:
                return 0
            iid = d.get("ITEM_NAME_TO_ID", {}).get(name)
            return self._ap_item_counts.get(int(iid), 0) if iid is not None else 0

        # After the vanilla gear-return event the Runes NEVER come back. In
        # particular 6 AP Runes must NOT reset the story mana gauge from 1 to 7.
        # AP network ownership stays intact; only game-memory authority yields.
        after_brazul = self._brazul_capture_guard.recovered
        rune_count = 0
        if not after_brazul:
            for name, address in d.get("ITEM_RUNE_SCENARIO_VARS", {}).items():
                owned = count(name)
                rune_count += owned
                addr = int(address)
                cur = int(pine.read32(addr))
                if owned:
                    # AP owns this Rune; restore it after a savestate rollback.
                    self._ap_rune_rollback_due.pop(name, None)
                    if cur < 2:
                        pine.write32(addr, 2)
                        fixed.append(f"{name} {cur}->2 (AP reward)")
                elif cur == 2:
                    # Vanilla Rune pickup = AP *location*, never an AP *item*.
                    # Leave the flag intact until its corresponding check is ACKed,
                    # otherwise the special-check watcher can miss a 0->2 edge.
                    linked = d.get("ITEM_TO_SPECIAL_LOCATION", {}).get(name)
                    location_id = d.get("LOCATION_NAME_TO_ID", {}).get(linked)
                    if location_id is None or int(location_id) not in self._ap_checked:
                        self._ap_rune_rollback_due.pop(name, None)
                        continue
                    now_rune = time.monotonic()
                    due = self._ap_rune_rollback_due.setdefault(name, now_rune + 3.0)
                    if now_rune >= due:
                        pine.write32(addr, 0)
                        verified = int(pine.read32(addr))
                        fixed.append(f"{name} {cur}->{verified} (physical pickup, AP item not received)")
                        self._ap_rune_rollback_due.pop(name, None)
                else:
                    self._ap_rune_rollback_due.pop(name, None)

        # Non-shop boolean/key items (e.g. Blue Egg/Receptacle/Magic Regeneration).
        shop_addresses = set(targets)
        for name, address in d.get("ITEM_SCENARIO_FLAGS", {}).items():
            # Brazul's scripted return excludes the Receptacle; AP's earlier
            # reward must not resurrect it after the pickup cutscene.
            if after_brazul and name == "Receptacle":
                continue
            addr = int(address)
            if addr in shop_addresses:
                continue
            if count(name) > 0:
                cur = pine.read32(addr)
                if cur < 1:
                    pine.write32(addr, 1); fixed.append(f"{name} 0->1")

        # Six AP Rune rewards alone own maximum mana (50 + 50 per Rune).
        # Old seed Progressive Magic Gauge is reinterpreted as a one-shot
        # refill, not a seventh/eighth Rune or a permanent gauge upgrade.
        magic_target = min(10, 1 + rune_count)
        if self._ap_joined and self._ap_seed_build_verified and not after_brazul:
            addr = int(d["ADDR_MAGIC_GAUGE_LEVEL"]); cur = pine.read32(addr)
            # Exact AP authority: physical Rune pickups and old launcher writes cannot
            # grant permanent max magic unless the corresponding AP Rune was received.
            # Before all six Runes, Progressive Magic Gauge is banked so it cannot
            # bypass the vanilla 350-mana Wolfen City wall.
            if cur != magic_target:
                pine.write32(addr, magic_target); fixed.append(f"Magic Gauge {cur}->{magic_target} (AP runes only)")

        if fixed:
            # This guard suppresses only inventory/stock inference caused by our own
            # writes. V0.8.15 money sampling is independent and is never muted by it.
            self._ap_shop_live_ignore_until = max(self._ap_shop_live_ignore_until, time.monotonic() + 0.45)
            self._log_threadsafe("AP inventory authority reconciled: " + "; ".join(fixed), "ok")

    def _ap_suppress_shop_reward(self, pine: PineClient, location_id: int, pending: tuple[str, dict, int]) -> None:
        if location_id in self._ap_shop_suppressed:
            return
        name, reward_spec, _previous_reward = pending
        reward_addr = int(reward_spec["address"])
        target = int(self._ap_shop_authoritative_reward_target(name, reward_spec, self._ap_data))
        pine.write32(reward_addr, target)
        verified = int(pine.read32(reward_addr))

        if str(reward_spec.get("kind", "u32")) == "life_gauge":
            player = self._ap_player_pointer(pine, self._ap_data)
            if player is not None:
                max_addr = player + int(self._ap_data["PLAYER_MAX_HP_OFFSET"])
                hp_addr = player + int(self._ap_data["PLAYER_HP_OFFSET"])
                max_hp = float(target)
                pine.write32(max_addr, self._ap_float_to_raw(max_hp))
                hp = self._ap_raw_to_float(pine.read32(hp_addr))
                if hp == hp and 0.0 <= hp < 10000.0 and hp > max_hp:
                    pine.write32(hp_addr, self._ap_float_to_raw(max_hp))

        self._ap_shop_suppressed.add(location_id)
        self._ap_pending_shop_suppressions.pop(location_id, None)
        self._ap_shop_live_ignore_until = max(self._ap_shop_live_ignore_until, time.monotonic() + 1.0)
        self._log_threadsafe(
            f"Vanilla shop inventory mutation suppressed under AP authority: {name} "
            f"(0x{reward_addr:08X} -> {verified}).",
            "info",
        )

    def _apply_ap_item(self, pine: PineClient, item, *, replay: bool = False) -> None:
        d=self._ap_data
        ap_index = None
        if isinstance(item, dict) and item.get("_ap_index") is not None:
            try:
                ap_index = int(item.get("_ap_index"))
            except (TypeError, ValueError):
                ap_index = None
        effective_replay = bool(replay or (ap_index is not None and ap_index < self._ap_applied_item_cursor))
        # AP is about to touch Kya's inventory. Ignore live player-state shop
        # inference briefly so receiving an item can never validate its shop location.
        self._ap_shop_live_ignore_until = max(self._ap_shop_live_ignore_until, time.monotonic() + 0.85)
        item_id=int(item.get("item",-1)) if isinstance(item,dict) else int(item[0])
        source_location = int(item.get("location", -1)) if isinstance(item, dict) else -1
        pending_shop = self._ap_pending_shop_suppressions.get(source_location)
        if pending_shop is not None:
            self._ap_suppress_shop_reward(pine, source_location, pending_shop)
        pending_life = self._ap_pending_special_life_suppressions.get(source_location)
        if pending_life is not None:
            id_to_name_local = {int(v): k for k, v in d.get("LOCATION_NAME_TO_ID", {}).items()}
            self._ap_suppress_special_life_reward(
                pine, source_location, id_to_name_local.get(source_location, "Vanilla HP Up"), pending_life
            )
        name=self._ap_items.get(item_id,"Unknown item")
        if name == "Unknown item":
            self._log_threadsafe(f"ERROR: unrecognized Archipelago item id {item_id}. Reward NOT applied.", "error")
        self._ap_item_counts[item_id]=self._ap_item_counts.get(item_id,0)+1
        if (not effective_replay) and self.overlay_enabled:
            loc_name = {int(v): k for k, v in d.get("LOCATION_NAME_TO_ID", {}).items()}.get(source_location, f"Location {source_location}")
            loc_display = self._ap_public_location_name(loc_name)
            player_name = self.name_var.get().strip() or "Kya"
            self._overlay_notify_threadsafe(f"{player_name} found their {name}\n{loc_display}", "incoming")
            self._ap_overlay_recent_incoming[(item_id, source_location)] = time.monotonic()
        money_values = d.get("ITEM_MONEY_VALUES", {})
        hp_restores = d.get("ITEM_HP_RESTORE_AMOUNTS", {})
        magic_restores = d.get("ITEM_MAGIC_RESTORE_AMOUNTS", {})
        life_item = d.get("ITEM_PROGRESSIVE_LIFE_GAUGE")
        if effective_replay and (name in money_values or name in hp_restores or name in magic_restores):
            # These rewards are consumable. Replaying historical deliveries on
            # reconnect would grant duplicate currency or recovery.
            return
        self._log_threadsafe(f"ITEM <- Archipelago: {name}", "ok")
        # The AP server retains these rewards, but they are NOT a license to
        # bypass the vanilla Brazul captivity/escape and rune-seizure sequence.
        # Counts must still advance on full ReceivedItems replays.
        if self._brazul_capture_guard.defer_ap_item(name, d):
            self._log_threadsafe(
                f"BRAZUL STORY: {name} recorded by AP, game-memory grant deferred "
                f"({self._brazul_capture_guard.phase}).", "info")
            if ap_index is not None and ap_index >= self._ap_applied_item_cursor:
                self._ap_applied_item_cursor = ap_index + 1
                self._ap_save_item_cursor(d)
            return
        if name in money_values:
            base_amount = int(money_values[name])
            amount = self._ap_scale_percent(base_amount, self._ap_nooties_modifier_pct)
            address = int(d["ADDR_MONEY"])
            current = pine.read32(address)
            target = min(0xFFFFFFFF, current + amount)
            pine.write32(address, target)
            verified = pine.read32(address)
            modifier_note = (
                f"; base={base_amount}, modifier={self._ap_nooties_modifier_pct:+d}%"
                if self._ap_nooties_modifier_pct != 0 else ""
            )
            self._log_threadsafe(
                f"Nooties reward applied: +{amount} ({current} -> {verified}){modifier_note}",
                "ok" if verified == target else "warn",
            )
        elif name == life_item:
            self._ap_apply_progressive_life_gauge(pine, item_id, d, is_replay=effective_replay)
        elif name in hp_restores:
            amount = int(hp_restores[name])
            if not self._ap_restore_player_hp(pine, amount, d):
                self._ap_pending_hp_restore += amount
                self._log_threadsafe(f"HP recovery +{amount} queued until Kya's player data is available.", "info")
        elif name in magic_restores:
            amount = int(magic_restores[name])
            if not self._ap_restore_player_magic(pine, amount, d):
                self._ap_pending_magic_restore += amount
                self._log_threadsafe(f"Magic recovery +{amount} queued until Kya's magic data is available.", "info")
        elif name in d.get("ITEM_COMBAT_BONUSES", {}):
            spec = d["ITEM_COMBAT_BONUSES"][name]
            effect = spec.get("effect") if isinstance(spec, dict) else spec
            percent = self._ap_combat_bonus_percent(d, effect)
            self._log_threadsafe(
                f"{name} received: total {percent}% bonus armed "
                f"({'Wolfen damage' if effect == 'damage' else 'incoming damage reduction'}).",
                "ok",
            )
        elif name == d.get("ITEM_PROGRESSIVE_BOOMY"):
            count = min(2, self._ap_item_counts[item_id])
            if not self._ap_intro_wolfen_completed(d):
                # Item is stored in _ap_item_counts; inventory reconciliation
                # will apply it as soon as the first Wolfen rescue is checked.
                self._log_threadsafe(
                    f"Progressive Boomy {count}/2 banked until the first Wolfen rescue (whistle tutorial).",
                    "info",
                )
            else:
                address = int(d["ADDR_BOOMY_TYPE"])
                current = pine.read32(address)
                target = max(current, min(3, 1 + count))
                if target != current:
                    pine.write32(address, target)
                verified = pine.read32(address)
                self._log_threadsafe(f"Progressive Boomy applied: level {verified}/3", "ok" if verified >= target else "warn")
        elif name == d.get("ITEM_PROGRESSIVE_BRACELET"):
            count = min(7, self._ap_item_counts[item_id])
            address = int(d["ADDR_BRACELET_BITFIELD"])
            current = pine.read32(address)
            target = current | ((1 << (count + 1)) - 1)
            if target != current:
                pine.write32(address, target)
            verified = pine.read32(address)
            self._log_threadsafe(f"Progressive Bracelet applied: upgrade {count}/7, bitfield 0x{verified:02X}", "ok" if (verified & target) == target else "warn")
        elif name == d.get("ITEM_PROGRESSIVE_BOARD"):
            count = min(2, self._ap_item_counts[item_id])
            address = int(d["ADDR_BOARD_LEVEL"])
            current = pine.read32(address)
            target = max(current, count)
            if target != current:
                pine.write32(address, target)
            verified = pine.read32(address)
            self._log_threadsafe(f"Progressive Board applied: level {verified}/2", "ok" if verified >= target else "warn")
        elif name == d.get("ITEM_PROGRESSIVE_MAGIC_GAUGE"):
            # LEGACY 0.8.7 seeds can contain this item. It conflicted with
            # 'six Runes = 350 max mana'. Convert to a one-shot mana refill,
            # preserving replay semantics so reconnects never farm it.
            if effective_replay:
                return
            amount = 50
            if not self._ap_restore_player_magic(pine, amount, d):
                self._ap_pending_magic_restore += amount
            self._log_threadsafe(
                "Legacy Progressive Magic Gauge -> Magic Restore +50; "
                "max mana remains controlled by AP Runes only.", "info"
            )
        elif name == "Basic Boomy":
            # Compatibility with old seed/YAML items only. New technical-beta
            # seeds never give Basic Boomy at the start; the story awards it.
            if not self._ap_intro_wolfen_completed(d):
                self._log_threadsafe(
                    "Basic Boomy banked: whistle tutorial must finish before equipping it.",
                    "info",
                )
            else:
                address = int(d["ADDR_BOOMY_TYPE"])
                current = pine.read32(address)
                if current < 1:
                    pine.write32(address, 1)
                verified = pine.read32(address)
                self._log_threadsafe(f"Basic Boomy applied: ScenarioVar = {verified}", "ok" if verified >= 1 else "warn")
        elif name in ("Wolfen City Access", "The Fortress Access"):
            # The AP access items are runtime actor permissions, not
            # ScenarioVars. The 100ms actor guard releases the matching
            # persistent-key elevator, including after streaming/reload.
            self._ap_access_guard_next = 0.0
            self._log_threadsafe(
                f"AP elevator permission received: {name}; access guard will restore the vanilla lift.",
                "ok",
            )
        elif name.startswith("Progressive Rune: "):
            address = int(d["ITEM_RUNE_SCENARIO_VARS"][name])
            current = pine.read32(address)
            if current < 2:
                pine.write32(address, 2)
                verified = pine.read32(address)
                self._log_threadsafe(
                    f"Rune reward applied: {name} -> ScenarioVar 0x{address:08X} = 2 (readback={verified})",
                    "ok" if verified == 2 else "warn",
                )
            linked_location=d.get("ITEM_TO_SPECIAL_LOCATION",{}).get(name)
            if linked_location:
                self._ap_special_states[linked_location]=True
            rune_ids = [int(v) for n, v in d["ITEM_NAME_TO_ID"].items() if n.startswith("Progressive Rune: ")]
            rune_count = sum(self._ap_item_counts.get(rid, 0) for rid in rune_ids)
            gauge_name = d.get("ITEM_PROGRESSIVE_MAGIC_GAUGE")
            gauge_id = int(d["ITEM_NAME_TO_ID"].get(gauge_name, -1)) if gauge_name else -1
            gauge_count = self._ap_item_counts.get(gauge_id, 0) if gauge_id >= 0 else 0
            rune_total = len(rune_ids)
            active_gauge_bonus = gauge_count if rune_total > 0 and rune_count >= rune_total else 0
            target_level = min(10, 1 + rune_count + active_gauge_bonus)
            gauge_address = int(d["ADDR_MAGIC_GAUGE_LEVEL"])
            current_level = pine.read32(gauge_address)
            if current_level != target_level:
                pine.write32(gauge_address, target_level)
            verified_level = pine.read32(gauge_address)
            self._log_threadsafe(
                f"Rune mana authority: +50 per AP Rune ({rune_count}/{rune_total}) -> level {verified_level} "
                f"({verified_level * 50} max mana).",
                "ok" if verified_level == target_level else "warn",
            )
        elif name in d.get("ITEM_RUNE_SCENARIO_VARS", {}):
            address = int(d["ITEM_RUNE_SCENARIO_VARS"][name])
            current = pine.read32(address)
            if current < 2:
                pine.write32(address, 2)
                verified = pine.read32(address)
                self._log_threadsafe(
                    f"Rune reward applied: {name} -> 0x{address:08X} = 2 (readback={verified})",
                    "ok" if verified == 2 else "warn",
                )
        elif name in d.get("ITEM_SCENARIO_FLAGS", {}):
            address = int(d["ITEM_SCENARIO_FLAGS"][name])
            current = pine.read32(address)
            if current < 1:
                pine.write32(address, 1)
            verified = pine.read32(address)
            self._log_threadsafe(
                f"Ability/key item applied: {name} -> ScenarioVar 0x{address:08X} = {verified}",
                "ok" if verified >= 1 else "warn",
            )

        if ap_index is not None and ap_index >= self._ap_applied_item_cursor:
            self._ap_applied_item_cursor = ap_index + 1
            self._ap_save_item_cursor(d)

    @staticmethod
    def _ap_raw_to_float(raw: int) -> float:
        return struct.unpack("<f", struct.pack("<I", raw & 0xFFFFFFFF))[0]

    @staticmethod
    def _ap_float_to_raw(value: float) -> int:
        return struct.unpack("<I", struct.pack("<f", value))[0]

    @staticmethod
    def _ap_valid_pointer(value: int) -> bool:
        return 0x00100000 <= value < 0x02000000 and value % 4 == 0


    # ------------------------------------------------------------------
    # 0.8.24 Fast Travel beta runtime
    # ------------------------------------------------------------------
    def _ap_ft_enter_exclusive(self, route: dict, now: float) -> None:
        if self._ap_ft_exclusive:
            return
        self._ap_ft_exclusive = True
        self._ap_ft_exclusive_route_id = str(route.get("id", ""))
        self._ap_ft_exclusive_since = float(now)
        self._ap_ft_exclusive_confirmed_at = None
        self._ap_ft_defer_logged = False
        self._log_threadsafe(
            f"FAST TRAVEL EXCLUSIVE ON: {route.get('label', route.get('id', '?'))}. "
            "All non-FT game-memory writers are paused.",
            "ok",
        )

    def _ap_ft_leave_exclusive(self, *, success: bool, reason: str) -> None:
        if not self._ap_ft_exclusive:
            return
        route_id = self._ap_ft_exclusive_route_id or "?"
        queued = len(self._ap_ft_deferred_events)
        self._ap_ft_exclusive = False
        self._ap_ft_exclusive_route_id = None
        self._ap_ft_exclusive_since = 0.0
        self._ap_ft_exclusive_confirmed_at = None
        self._ap_ft_defer_logged = False
        self._log_threadsafe(
            f"FAST TRAVEL EXCLUSIVE OFF: {route_id} | "
            f"{'SUCCESS' if success else 'FAILSAFE'} | {reason} | "
            f"deferred AP events={queued}.",
            "ok" if success else "warn",
        )

    def _ap_ft_reset_runtime(self) -> None:
        # A savestate, PINE reconnect or new AP session invalidates any actors
        # retained by a suspended cleanroom step.  Never resume stale pointers.
        scan = getattr(self, "_ap_ft_sanctuary_generator", None)
        self._ap_ft_sanctuary_generator = None
        if scan is not None:
            scan.close()
        self._ap_ft_sanctuary_active = False
        self._ap_ft_nativ_loaded_last = False
        self._ap_ft_departure_pending = False
        self._ap_ft_departure_since = 0.0
        self._ap_ft_departure_route_id: str | None = None
        self._ap_ft_near_source_route_id: str | None = None
        self._ap_ft_near_source_seen = 0.0
        self._ap_ft_active_bridge = None
        self._ap_ft_next_runtime_scan = 0.0
        self._ap_ft_wind_triggered.clear()
        self._ap_ft_last_source_signature = None
        self._ap_ft_ft01_prepared_sources = {}
        # A new AP session starts outside a FT transaction. Do not discard any
        # already-deferred packets here; they are replayed on the next normal tick.
        self._ap_ft_exclusive = False
        self._ap_ft_exclusive_route_id = None
        self._ap_ft_exclusive_since = 0.0
        self._ap_ft_exclusive_confirmed_at = None
        self._ap_ft_defer_logged = False
        self._ap_ft_cleanroom_pending = False
        self._ap_ft_cleanroom_active = False
        self._ap_ft_waiting_for_nativ_exit = False
        self._ap_ft_session_departed = False
        self._ap_ft_room_far_since = 0.0
        self._ap_ft_cleanroom_continuation = None  # stale actor-generation provenance
        self._ap_ft_mana_stall_rescue = None
        self._ap_access_guard_next = 0.0

    def _ap_ft_route_location_id(self, route: dict, d: dict) -> int | None:
        name = str(route.get("location_name") or "")
        value = d.get("LOCATION_NAME_TO_ID", {}).get(name)
        return int(value) if value is not None else None

    def _ap_ft_enable_route(self, route: dict, reason: str) -> bool:
        try:
            source_key = int(route["source_key"])
            target_key = int(route["target_key"])
        except (KeyError, TypeError, ValueError):
            return False
        if any(int(r.get("source_key", -1)) == source_key for r in self._ap_starting_fast_travel_routes):
            return False
        copy = dict(route)
        self._ap_starting_fast_travel_routes.append(copy)
        self._ap_selected_target_keys.add(target_key)
        self._ap_ft_last_source_signature = None
        self._ap_ft_early_panels_done = False
        self._ap_ft_early_panels_retry_at = 0.0
        self._log_threadsafe(
            f"Fast Travel route enabled ({reason}): {copy.get('label', copy.get('id', '?'))}.",
            "ok",
        )
        return True

    def _ap_ft_restore_natural_routes(self, d: dict) -> None:
        if self._ap_fast_travel_progression != "archipelago":
            return
        present_sources = {int(r.get("source_key", -1)) for r in self._ap_starting_fast_travel_routes}
        for _zone, routes in d.get("FAST_TRAVEL_ALLOWED_ROUTES", {}).items():
            if bool(d.get("FAST_TRAVEL_ENTRY_ONLY_BETA", False)):
                routes = [r for r in routes if isinstance(r, dict) and int(r.get("source_index", -1)) == 0]
            for route in routes:
                try:
                    source_key = int(route["source_key"])
                except (KeyError, TypeError, ValueError):
                    continue
                if source_key in present_sources:
                    break
                lid = self._ap_ft_route_location_id(route, d)
                if lid is not None and lid in self._ap_checked:
                    if self._ap_ft_enable_route(route, "previously discovered"):
                        present_sources.add(source_key)
                    break

    def _ap_ft_unlock_route_for_location(self, location_name: str, d: dict) -> None:
        if self._ap_fast_travel_progression != "archipelago":
            return
        for _zone, routes in d.get("FAST_TRAVEL_ALLOWED_ROUTES", {}).items():
            if bool(d.get("FAST_TRAVEL_ENTRY_ONLY_BETA", False)):
                routes = [r for r in routes if isinstance(r, dict) and int(r.get("source_index", -1)) == 0]
            for route in routes:
                if str(route.get("location_name") or "") == str(location_name):
                    self._ap_ft_enable_route(route, "natural discovery")
                    return

    def _ap_ft_scan_keyed(self, pine: PineClient, d: dict, wanted_vtables: set[int]) -> dict[int, tuple[int, int]]:
        manager = int(pine.read32(int(d["ADDR_ACTOR_MANAGER_GLOBAL"])))
        if not self._ap_valid_pointer(manager):
            return {}
        active, count = pine.read32_many([
            manager + int(d["ACTOR_MANAGER_ACTIVE_LIST_OFFSET"]),
            manager + int(d["ACTOR_MANAGER_ACTIVE_COUNT_OFFSET"]),
        ])
        if not self._ap_valid_pointer(active) or count <= 0 or count > int(d["ACTOR_MANAGER_MAX_ACTIVE"]):
            return {}
        ptrs = pine.read32_many([active + i * 4 for i in range(count)])
        ptrs = [a for a in ptrs if self._ap_valid_pointer(a)]
        if not ptrs:
            return {}
        vts = pine.read32_many(ptrs)
        candidates = [(a, vt) for a, vt in zip(ptrs, vts) if int(vt) in wanted_vtables]
        if not candidates:
            return {}
        descs = pine.read32_many([a + int(d["FAST_TRAVEL_DESCRIPTOR_OFFSET"]) for a, _ in candidates])
        valid = [(a, vt, desc) for (a, vt), desc in zip(candidates, descs) if self._ap_valid_pointer(desc)]
        if not valid:
            return {}
        keys = pine.read32_many([desc + int(d["FAST_TRAVEL_KEY_OFFSET"]) for _, _, desc in valid])
        return {
            int(key) & 0xFFFFFFFF: (int(actor), int(vt))
            for (actor, vt, _), key in zip(valid, keys)
            if 0 < int(key) < 0x10000
        }

    def _ap_ft_footer_addr(self, pine: PineClient, actor: int, d: dict) -> int | None:
        table = int(pine.read32(actor + int(d["FAST_TRAVEL_ROUTE_TABLE_OFFSET"])))
        if not self._ap_valid_pointer(table):
            return None
        count = int(pine.read32(table))
        if count < 2 or count > 16:
            return None
        return table + 4 + count * 12 + 12

    def _ap_ft_write_if_needed(self, pine: PineClient, address: int, current: int, wanted: int) -> None:
        wanted &= 0xFFFFFFFF
        if int(current) != wanted:
            pine.write32(address, wanted)

    def _ap_ft_activate_wind(self, pine: PineClient, source_key: int, controller_actor: int, d: dict) -> bool:
        token = (int(source_key), int(controller_actor))
        flags, state, prev = pine.read32_many([
            controller_actor + int(d["ACTOR_FLAGS_OFFSET"]),
            controller_actor + int(d["ACTOR_STATE_OFFSET"]),
            controller_actor + int(d["ACTOR_PREV_STATE_OFFSET"]),
        ])
        if int(state) == 8 and int(prev) == 5 and (int(flags) & int(d["WIND_FLAG_SET_STAGE2"])):
            self._ap_ft_wind_triggered.add(token)
            return True
        if token in self._ap_ft_wind_triggered:
            # The same runtime address can be reused after a zone reload/savestate.
            # If vanilla no longer reports the active 8/5 state, this token is stale:
            # forget it and re-fire the real wind event instead of silently doing nothing.
            self._ap_ft_wind_triggered.discard(token)
        stage1 = (int(flags) & ~int(d["WIND_FLAG_CLEAR"])) | int(d["WIND_FLAG_SET_STAGE1"])
        stage2 = stage1 | int(d["WIND_FLAG_SET_STAGE2"])
        pine.write32(controller_actor + int(d["ACTOR_FLAGS_OFFSET"]), stage1)
        time.sleep(0.020)
        pine.write32(controller_actor + int(d["ACTOR_FLAGS_OFFSET"]), stage2)
        time.sleep(0.050)
        _flags2, state2, prev2 = pine.read32_many([
            controller_actor + int(d["ACTOR_FLAGS_OFFSET"]),
            controller_actor + int(d["ACTOR_STATE_OFFSET"]),
            controller_actor + int(d["ACTOR_PREV_STATE_OFFSET"]),
        ])
        ok = int(state2) == 8 and int(prev2) == 5
        if ok:
            self._ap_ft_wind_triggered.add(token)
            self._log_threadsafe(
                f"Fast Travel wind vanilla: source 0x{source_key:04X}, C540 actor=0x{controller_actor:08X}.",
                "ok",
            )
        return ok

    def _ap_ft_detector_chain_evidence(self, pine: PineClient, target_actor: int, d: dict) -> tuple[bool, str]:
        """Read-only evidence that the local FT discovery chain actually fired."""
        try:
            state, prev = [int(x) for x in pine.read32_many([
                int(target_actor) + int(d["ACTOR_STATE_OFFSET"]),
                int(target_actor) + int(d["ACTOR_PREV_STATE_OFFSET"]),
            ])]
        except Exception:
            state, prev = -1, -1
        parts = [f"target={state}/{prev & 0xFFFFFFFF:08X}"]
        # V0.9.15 detector-only rule: a generic target state=6 is NOT proof of
        # discovery because bootstrap/streaming can reach it.  Accept only the
        # characteristic local target 7/6 handoff or a live linked C540 chain.
        chain = bool(
            (state == 7 and prev in (5, 6))
            or (state == 6 and prev == 7)
        )
        try:
            controllers = self._ap_ft_target_route_wind_controllers(pine, int(target_actor), d)
        except Exception:
            controllers = []
        for off, ctrl, key in controllers:
            try:
                cs, cp = [int(x) for x in pine.read32_many([
                    int(ctrl) + int(d["ACTOR_STATE_OFFSET"]),
                    int(ctrl) + int(d["ACTOR_PREV_STATE_OFFSET"]),
                ])]
            except Exception:
                continue
            parts.append(f"C540+0x{int(off):03X}/0x{int(key):04X}={cs}/{cp & 0xFFFFFFFF:08X}")
            if cs in (8, 10) and cp in (5, 8, 10):
                chain = True
        return bool(chain), ", ".join(parts)

    def _ap_ft_detector_hold_remote_active_off(self, pine: PineClient, target_actor: int, target_key: int, d: dict, *, distance: float | None = None) -> bool:
        """Suppress only the bootstrap's remote +0x2A0 activation.

        +0x2A4, masks, indices, actor state and C540 are never written here.
        This is deliberately narrower than V0.9.13, whose available=0 write
        produced the all-grey button state reported by the tester.
        """
        # V0.9.17 Access-Only: destination FT actor is *strictly read-only*.
        # The old remote detector firewall wrote 1->0 to the game's active
        # flag, even in Access-Only mode. That violates vanilla ownership and
        # may race with zone streaming on second/subsequent transitions.
        # Keep the guard logic for legacy mode only.
        if bool(d.get("FAST_TRAVEL_ACCESS_ONLY_TEST", False)):
            if int(target_key) not in self._ap_ft_detector_remote_logged:
                self._ap_ft_detector_remote_logged.add(int(target_key))
                self._log_threadsafe(
                    f"FT ACCESS-ONLY READ-ONLY: target 0x{int(target_key):04X}; "
                    "remote active flag left to vanilla (no firewall write).",
                    "info",
                )
            return False
        active_addr = int(target_actor) + int(d["FAST_TRAVEL_ACTIVE_OFFSET"])
        try:
            active = int(pine.read32(active_addr))
        except Exception:
            return False
        if active == int(d["FAST_TRAVEL_STATE_OFF"]):
            return False
        try:
            pine.write32(active_addr, int(d["FAST_TRAVEL_STATE_OFF"]))
        except Exception:
            return False
        if int(target_key) not in self._ap_ft_detector_remote_logged:
            self._ap_ft_detector_remote_logged.add(int(target_key))
            try:
                avail = int(pine.read32(int(target_actor) + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"])))
            except Exception:
                avail = -1
            self._log_threadsafe(
                f"FT DETECTOR FIREWALL: remote FT01 active 0x{int(target_key):04X} forced 1->0 "
                f"at distance={distance if distance is not None else 'N/A'}m; available={avail} left untouched. "
                "No discovery/check/handoff until the player reaches the pad.",
                "warn",
            )
        return True

    def _ap_ft_route_detector_handoff(self, route: dict, d: dict) -> bool:
        """True only after a proximity-confirmed local FT01 discovery this session.

        Deliberately does NOT use Archipelago checked IDs.  The FT chain is a
        detector only: a bootstrap-generated remote 0->1 cannot change ownership.
        """
        if not bool(d.get("FAST_TRAVEL_ENTRY_ONLY_BETA", False)):
            return False
        if not bool(d.get("FAST_TRAVEL_DETECTOR_HANDOFF", True)):
            return False
        try:
            return int(route.get("source_index", -1)) == 0 and int(route.get("source_key", -1)) in self._ap_ft_detector_handoff_sources
        except (TypeError, ValueError):
            return False

    def _ap_ft_detector_handoff_source_keys(self) -> set[int]:
        return set(self._ap_ft_detector_handoff_sources)

    def _ap_ft_activate_nativ_source_winds(self, pine: PineClient, keyed: dict[int, tuple[int, int]], d: dict, *, only_source: int | None = None) -> None:
        if bool(d.get("FAST_TRAVEL_FT01_BAT_VALIDATED", True)) or not bool(d.get("FAST_TRAVEL_LOCAL_SOURCE_WIND_TEST", False)):
            return
        """Arm at most ONE AP-owned Nativ wind after an intentional approach.

        V0.9.15 never sweeps/re-fires Nativ winds on room load.  That sweep was
        the cause of the return-loop seen after Quarry: Kya spawned beside the
        source, the Launcher re-fired its C540 immediately, and the game sent her
        straight back out before the player could move.

        A detector-handed-off world is always skipped: its wind is 100% vanilla.
        """
        if not bool(d.get("FAST_TRAVEL_ENTRY_ONLY_BETA", False)):
            return
        if only_source is None:
            return
        source_key = int(only_source)
        selected_routes = {
            int(r.get("source_key", -1)): r
            for r in self._ap_starting_fast_travel_routes
            if isinstance(r, dict)
        }
        route = selected_routes.get(source_key)
        if route is None or self._ap_ft_route_detector_handoff(route, d):
            return
        wind_map = {int(k): int(v) for k, v in d.get("NATIV_WIND_CONTROLLER_KEYS", {}).items()}
        wind_key = wind_map.get(source_key)
        if wind_key is None:
            return
        row = keyed.get(int(wind_key))
        if not row or int(row[1]) != int(d["WIND_CONTROLLER_VTABLE"]):
            return
        try:
            self._ap_ft_activate_wind(pine, source_key, int(row[0]), d)
        except Exception:
            pass

    def _ap_ft_patch_nativ_sources(self, pine: PineClient, keyed: dict[int, tuple[int, int]], d: dict, armed_route: dict | None = None) -> None:
        """V0.9.21: the tested BAT 11/12/13 FT01 source preparation.

        This routine only writes *authorized, not-yet-discovered* Nativ City
        source actors. Test 10/11 showed that source index=0, index_copy=0,
        mask=0xFFFFFFFE, and the route footer ready bit are sufficient for
        vanilla to wake the source C540 and handle the wooden-elevator arrival.

        Crucially, DO NOT write source active/available, the C540 wind flags,
        remote destinations, or the discovery chain. The engine manages those.
        Unselected sources are untouched, as in BAT Test 12. A confirmed local
        FT01 discovery makes that source permanently read-only (Test 13).
        """
        if self._ap_fast_travel_progression != "archipelago":
            return
        ft_vt = int(d["FAST_TRAVEL_VTABLE"])
        index_off = int(d["FAST_TRAVEL_INDEX_OFFSET"])
        copy_off = int(d["FAST_TRAVEL_INDEX_COPY_OFFSET"])
        mask_off = int(d["FAST_TRAVEL_MASK_OFFSET"])
        ready_flag = int(d["FAST_TRAVEL_ROUTE_READY_FLAG"])
        mask_ft01 = 0xFFFFFFFE
        prepared = getattr(self, "_ap_ft_ft01_prepared_sources", {})
        if not isinstance(prepared, dict):
            prepared = {}
            self._ap_ft_ft01_prepared_sources = prepared

        # Validate the complete selected batch BEFORE any writes. A streaming
        # actor that is absent or has an invalid footer is retried on next tick.
        plan = []
        for route in self._ap_starting_fast_travel_routes:
            if not isinstance(route, dict):
                continue
            key = int(route.get("source_key", -1))
            if int(route.get("source_index", -1)) != 0:
                continue  # FT02+ not supported in the FT01 beta.
            if self._ap_ft_route_detector_handoff(route, d):
                continue
            row = keyed.get(key)
            if not row or int(row[1]) != ft_vt:
                return
            actor = int(row[0])
            footer = self._ap_ft_footer_addr(pine, actor, d)
            if footer is None:
                return
            if prepared.get(key) == (actor, footer):
                continue  # Like BAT 11: write once per Nativ room visit, not on every frame.
            values = pine.read32_many([
                actor + index_off, actor + copy_off,
                actor + mask_off, footer,
            ])
            plan.append((key, actor, footer, tuple(int(x) for x in values)))

        signature = []
        for key, actor, footer, (idx, copied, mask, footer_value) in plan:
            # The same four writes, and the same order, as successful BAT 11.
            self._ap_ft_write_if_needed(pine, actor + index_off, idx, 0)
            self._ap_ft_write_if_needed(pine, actor + copy_off, copied, 0)
            self._ap_ft_write_if_needed(pine, actor + mask_off, mask, mask_ft01)
            wanted_footer = footer_value | ready_flag
            self._ap_ft_write_if_needed(pine, footer, footer_value, wanted_footer)
            prepared[key] = (actor, footer)
            signature.append((key, actor, mask_ft01, bool(wanted_footer & ready_flag)))

        # Log only when the actor generation or the AP permission set changes.
        sig = (tuple(sorted((int(r["source_key"]), int(r.get("source_index", -1))) for r in self._ap_starting_fast_travel_routes)),
               tuple(sorted((k, v[0]) for k, v in prepared.items())),
               tuple(sorted(self._ap_ft_detector_handoff_sources)))
        if sig != self._ap_ft_last_source_signature:
            self._ap_ft_last_source_signature = sig
            authorized = {int(r["source_key"]) for r in self._ap_starting_fast_travel_routes}
            self._log_threadsafe(
                "FT01 BAT-VALIDATED SOURCES: "
                + (", ".join(f"0x{k:04X}" for k in sorted(prepared)) or "none awaiting vanilla")
                + "; vanilla handoff: "
                + (", ".join(f"0x{k:04X}" for k in sorted(authorized & self._ap_ft_detector_handoff_sources)) or "none")
                + "; NO wind/remote/discovery writes.",
                "ok",
            )


    def _ap_ft_find_plank_handlers(
        self,
        pine: PineClient,
        master_by_source_actor: dict[int, int],
        d: dict,
    ) -> dict[int, int]:
        """Resolve C2D0 condition objects by the proven reverse link.

        Ghidra FUN_00168820:
            C2D0 + 0x04 -> Master Event
            C2D0 + 0x14 = required freed-Wolfen count
            C2D0 + 0x18 = activation radius

        C2D0 objects are not Actor Manager actors, so the old V0.8.28
        Actor-Manager/proximity approach could never find them reliably.
        """
        handler_vt = int(d["NATIV_WOOD_HANDLER_VTABLE"])
        parent_off = int(d["NATIV_WOOD_MASTER_PTR_OFFSET"])

        resolved: dict[int, int] = {}
        wanted_by_master = {
            int(master_actor): int(source_key)
            for source_key, master_actor in master_by_source_actor.items()
        }

        # 1) Validate cached handlers first.
        for source_key, master_actor in master_by_source_actor.items():
            cached = self._ap_ft_plank_handler_cache.get(int(source_key))
            if cached is None:
                continue
            try:
                vt, parent = pine.read32_many([
                    int(cached),
                    int(cached) + parent_off,
                ])
                if int(vt) == handler_vt and int(parent) == int(master_actor):
                    resolved[int(source_key)] = int(cached)
            except Exception:
                pass

        # 2) Validate the historical PAL addresses. They are only hints:
        #    they are accepted exclusively when +0x04 points to the CURRENT
        #    Master actor, so this remains safe if runtime addresses move.
        legacy = {
            int(k): int(v)
            for k, v in d.get("NATIV_WOOD_LEGACY_HANDLER_HINTS", {}).items()
        }
        for source_key, master_actor in master_by_source_actor.items():
            if int(source_key) in resolved:
                continue
            handler = legacy.get(int(source_key))
            if handler is None:
                continue
            try:
                vt, parent = pine.read32_many([
                    handler,
                    handler + parent_off,
                ])
                if int(vt) == handler_vt and int(parent) == int(master_actor):
                    resolved[int(source_key)] = int(handler)
                    self._ap_ft_plank_handler_cache[int(source_key)] = int(handler)
            except Exception:
                pass

        missing_masters = {
            int(master_actor): int(source_key)
            for master_actor, source_key in wanted_by_master.items()
            if int(source_key) not in resolved
        }
        if not missing_masters:
            return resolved

        # 3) Fallback scan of the C2D0 runtime pool. This runs only while all
        #    eight Nativ kiosk Masters are loaded and only if hints/cache fail.
        scan_start = int(d.get("NATIV_WOOD_SCAN_START", 0x01900000))
        scan_end = int(d.get("NATIV_WOOD_SCAN_END", 0x01A00000))
        batch_words = int(d.get("NATIV_WOOD_SCAN_BATCH_WORDS", 2048))
        addr = scan_start

        while addr < scan_end and missing_masters:
            count = min(batch_words, max(0, (scan_end - addr) // 4))
            if count <= 0:
                break
            addrs = [addr + i * 4 for i in range(count)]
            values = pine.read32_many(addrs)

            candidates = [
                int(a)
                for a, value in zip(addrs, values)
                if int(value) == handler_vt
            ]

            for handler in candidates:
                try:
                    parent = int(pine.read32(handler + parent_off))
                except Exception:
                    continue

                source_key = missing_masters.get(parent)
                if source_key is None:
                    continue

                resolved[int(source_key)] = int(handler)
                self._ap_ft_plank_handler_cache[int(source_key)] = int(handler)
                missing_masters.pop(parent, None)

                self._log_threadsafe(
                    f"Fast Travel wooden kiosk backchain found: "
                    f"source 0x{int(source_key):04X} C2D0=0x{handler:08X} "
                    f"+0x04->Master=0x{parent:08X}.",
                    "info",
                )

            addr += count * 4

        return resolved

    def _ap_ft_open_selected_planks(
        self,
        pine: PineClient,
        actors: list[int],
        vtables: list[int],
        keyed: dict[int, tuple[int, int]],
        d: dict,
    ) -> None:
        """Open only the wooden kiosks belonging to AP-enabled Fast Travels.

        This routine is intentionally armed only when the complete Nativ City
        Fast Travel room is loaded (all eight kiosk Master Events present).
        It never writes Master state directly. It temporarily increases the
        exact paired C2D0 radius and lets FUN_00168820 perform vanilla 5->8.
        """
        if self._ap_fast_travel_progression != "archipelago":
            return

        master_key_by_source = {
            int(k): int(v)
            for k, v in d.get("NATIV_WOOD_MASTER_KEYS", {}).items()
        }
        all_master_keys = list(master_key_by_source.values())
        master_vt = int(d["MASTER_EVENT_VTABLE"])

        # Critical guard: do not touch the wood logic during partial streaming.
        # The dedicated Nativ FT room has all 8 kiosk Masters loaded together.
        room_masters: dict[int, int] = {}
        for source_key, master_key in master_key_by_source.items():
            mrow = keyed.get(int(master_key))
            if not mrow or int(mrow[1]) != master_vt:
                self._ap_ft_plank_room_logged = False
                return
            room_masters[int(source_key)] = int(mrow[0])

        if len(room_masters) != len(master_key_by_source) or len(room_masters) != 8:
            self._ap_ft_plank_room_logged = False
            return

        if not self._ap_ft_plank_room_logged:
            self._ap_ft_plank_room_logged = True
            self._log_threadsafe(
                "Nativ Fast Travel room detected: 8/8 wooden kiosk Masters loaded.",
                "info",
            )

        selected_sources = {
            int(route.get("source_key", -1))
            for route in self._ap_starting_fast_travel_routes
            if int(route.get("source_key", -1)) in room_masters
        }
        if not selected_sources:
            return

        selected_master_actors = {
            int(source_key): int(room_masters[source_key])
            for source_key in selected_sources
        }

        handlers = self._ap_ft_find_plank_handlers(
            pine,
            selected_master_actors,
            d,
        )

        parent_off = int(d["NATIV_WOOD_MASTER_PTR_OFFSET"])
        radius_off = int(d["NATIV_WOOD_RADIUS_OFFSET"])
        trigger_radius_raw = self._ap_float_to_raw(
            float(d.get("NATIV_WOOD_TRIGGER_RADIUS", 1000.0))
        )

        # Finalize successful vanilla opens and restore the original radius.
        for source_key in list(self._ap_ft_plank_patches):
            patch = self._ap_ft_plank_patches.get(source_key)
            if not patch:
                continue

            master_key = master_key_by_source.get(int(source_key))
            mrow = keyed.get(int(master_key)) if master_key is not None else None
            if not mrow or int(mrow[1]) != master_vt:
                continue

            master_actor = int(mrow[0])
            state, prev = pine.read32_many([
                master_actor + int(d["ACTOR_STATE_OFFSET"]),
                master_actor + int(d["ACTOR_PREV_STATE_OFFSET"]),
            ])
            if int(state) != 8:
                continue

            handler = int(patch["handler"])
            radius_raw = int(patch["radius_raw"])

            try:
                vt, parent = pine.read32_many([
                    handler,
                    handler + parent_off,
                ])
                if (
                    int(vt) == int(d["NATIV_WOOD_HANDLER_VTABLE"])
                    and int(parent) == master_actor
                ):
                    pine.write32(handler + radius_off, radius_raw)
            except Exception:
                pass

            self._ap_ft_plank_patches.pop(int(source_key), None)
            token = (int(source_key), master_actor)
            if token not in self._ap_ft_plank_open_logged:
                self._ap_ft_plank_open_logged.add(token)
                self._log_threadsafe(
                    f"Fast Travel wooden kiosk OPEN: source 0x{int(source_key):04X} "
                    f"(Master 0x{int(master_key):04X}, vanilla state=8 "
                    f"prev=0x{int(prev):08X}).",
                    "ok",
                )

        for source_key in sorted(selected_sources):
            if source_key in self._ap_ft_plank_patches:
                continue

            master_key = master_key_by_source[source_key]
            master_actor = room_masters[source_key]
            state, prev = pine.read32_many([
                master_actor + int(d["ACTOR_STATE_OFFSET"]),
                master_actor + int(d["ACTOR_PREV_STATE_OFFSET"]),
            ])

            if int(state) == 8:
                token = (source_key, master_actor)
                if token not in self._ap_ft_plank_open_logged:
                    self._ap_ft_plank_open_logged.add(token)
                    self._log_threadsafe(
                        f"Fast Travel wooden kiosk already OPEN: "
                        f"source 0x{source_key:04X} Master 0x{master_key:04X}.",
                        "info",
                    )
                continue

            if int(state) != 5:
                continue

            handler = handlers.get(source_key)
            if handler is None:
                token = (source_key, master_actor)
                if token not in self._ap_ft_plank_warned:
                    self._ap_ft_plank_warned.add(token)
                    self._log_threadsafe(
                        f"Fast Travel wooden kiosk: no exact C2D0->Master "
                        f"backchain for source 0x{source_key:04X}.",
                        "warn",
                    )
                continue

            # Revalidate exact reverse link immediately before touching radius.
            vt, parent, required_raw, radius_raw = pine.read32_many([
                handler,
                handler + parent_off,
                handler + int(d["NATIV_WOOD_REQUIRED_OFFSET"]),
                handler + radius_off,
            ])
            if (
                int(vt) != int(d["NATIV_WOOD_HANDLER_VTABLE"])
                or int(parent) != master_actor
            ):
                self._ap_ft_plank_handler_cache.pop(source_key, None)
                continue

            # Current Nativ kiosks have required=0. Do not alter it. If a future
            # build changes this field, fail safe instead of bypassing progression.
            if int(required_raw) != 0:
                token = (source_key, master_actor)
                if token not in self._ap_ft_plank_warned:
                    self._ap_ft_plank_warned.add(token)
                    self._log_threadsafe(
                        f"Fast Travel wooden kiosk source 0x{source_key:04X}: "
                        f"unexpected required={int(required_raw)}; not patched.",
                        "warn",
                    )
                continue

            self._ap_ft_plank_patches[source_key] = {
                "handler": int(handler),
                "radius_raw": int(radius_raw),
                "master_actor": master_actor,
            }

            if int(radius_raw) != int(trigger_radius_raw):
                pine.write32(handler + radius_off, int(trigger_radius_raw))

            self._log_threadsafe(
                f"Fast Travel wooden kiosk VANILLA trigger armed: "
                f"source 0x{source_key:04X} C2D0=0x{handler:08X} "
                f"+0x04->Master=0x{master_actor:08X} "
                f"radius {self._ap_raw_to_float(int(radius_raw)):g}->"
                f"{float(d.get('NATIV_WOOD_TRIGGER_RADIUS', 1000.0)):g}.",
                "info",
            )



    def _ap_ft_patch_destination(self, pine: PineClient, route: dict, keyed: dict[int, tuple[int, int]], d: dict) -> tuple[int | None, bool, int]:
        if bool(d.get("FAST_TRAVEL_ACCESS_ONLY_TEST", True)):
            return None, False, 0  # Never activate destination FT artificially.
        """Exact destination half of the working Sidecar bridge.

        Only the selected endpoint is touched: active=1, available=1 and footer
        ready. Sibling endpoints are left completely alone during the critical
        chain; suppressing them here was extra Launcher behavior absent from the
        standalone proof.
        """
        target_key = int(route["target_key"])
        row = keyed.get(target_key)
        if not row or int(row[1]) != int(d["FAST_TRAVEL_VTABLE"]):
            return None, False, 0

        actor = int(row[0])
        active_addr = actor + int(d["FAST_TRAVEL_ACTIVE_OFFSET"])
        available_addr = actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"])
        active, available = pine.read32_many([active_addr, available_addr])
        self._ap_ft_write_if_needed(pine, active_addr, int(active), 1)
        self._ap_ft_write_if_needed(pine, available_addr, int(available), 1)

        footer = self._ap_ft_footer_addr(pine, actor, d)
        if footer is None:
            return actor, False, 1
        old_footer = int(pine.read32(footer))
        wanted_footer = old_footer | int(d["FAST_TRAVEL_ROUTE_READY_FLAG"])
        self._ap_ft_write_if_needed(pine, footer, old_footer, wanted_footer)
        return actor, True, 1


    def _ap_ft_apply_access_locks(self, pine: PineClient, keyed: dict[int, tuple[int, int]], d: dict) -> None:
        bit = int(d["ACCESS_LOCK_DISABLE_BIT"])
        # Items are AP authority: never infer ownership from game memory.
        item_ids = d.get("ITEM_NAME_TO_ID", {})
        def received(name: str) -> bool:
            item_id = item_ids.get(name)
            return item_id is not None and self._ap_item_counts.get(int(item_id), 0) > 0

        specs = (
            ("Flying Forest elevator", int(d["FLYING_FOREST_ELEVATOR_KEY"]), int(d["ACCESS_HANDLER_VTABLE"]), bool(self._ap_lock_flying_forest)),
            ("The Root target", int(d["THE_ROOT_TARGET_KEY"]), int(d["MASTER_EVENT_VTABLE"]), bool(self._ap_lock_the_root)),
            ("Wolfen City elevator", int(d["WOLFEN_CITY_ELEVATOR_KEY"]), int(d["ACCESS_HANDLER_VTABLE"]),
             bool(self._ap_lock_wolfen_city) and not received("Wolfen City Access")),
            ("The Fortress elevator", int(d["FORTRESS_ELEVATOR_KEY"]), int(d["ACCESS_HANDLER_VTABLE"]),
             bool(self._ap_lock_the_fortress) and not received("The Fortress Access")),
        )
        for label, key, vt, should_lock in specs:
            row = keyed.get(key)
            if not row or int(row[1]) != vt:
                continue
            actor = int(row[0])
            # NEVER clear a bit owned by vanilla game events. Only undo a lock
            # that this Launcher explicitly wrote for this exact actor.
            if not should_lock and self._ap_access_owned_actors.get(label) != actor:
                continue
            flags = int(pine.read32(actor + int(d["ACTOR_FLAGS_OFFSET"])))
            wanted = (flags | bit) if should_lock else (flags & ~bit)
            if wanted != flags:
                pine.write32(actor + int(d["ACTOR_FLAGS_OFFSET"]), wanted)
                if should_lock:
                    self._ap_access_owned_actors[label] = actor
                else:
                    self._ap_access_owned_actors.pop(label, None)
                token = (label, actor, should_lock)
                if self._ap_access_lock_last.get(label) != token:
                    self._ap_access_lock_last[label] = token
                    self._log_threadsafe(
                        f"{label}: {'LOCKED' if should_lock else 'UNLOCKED'} (actor=0x{actor:08X}).",
                        "ok",
                    )

    def _ap_ft_access_guard_tick(self, pine: PineClient, d: dict, now: float | None = None) -> None:
        """Dedicated owner for runtime AP elevator and route access locks.

        It retries every 100 ms outside FT critical ownership so streaming cannot
        silently leave the Nativ->Flying elevator or The Root target enabled.
        """
        if not (self._ap_joined and self._ap_seed_build_verified):
            return
        if self._ap_ft_exclusive or self._ap_ft_cleanroom_pending or self._ap_ft_cleanroom_active:
            return
        if now is None:
            now = time.monotonic()
        if now < self._ap_access_guard_next:
            return
        self._ap_access_guard_next = now + 0.10
        try:
            keyed = self._ap_ft_scan_keyed(
                pine, d, {int(d["ACCESS_HANDLER_VTABLE"]), int(d["MASTER_EVENT_VTABLE"])}
            )
            self._ap_ft_apply_access_locks(pine, keyed, d)
        except Exception:
            return

    def _ap_ft_nativ_player_distance(self, pine: PineClient, d: dict) -> float | None:
        """Distance from Kya to the closest AP-selected Nativ FT source."""
        try:
            kya = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
            if not self._ap_valid_pointer(kya):
                return None
            kp = self._ap_ft_actor_pos(pine, kya, d)
            if kp is None:
                return None
            keyed = self._ap_ft_scan_keyed(pine, d, {int(d["FAST_TRAVEL_VTABLE"])})
            source_keys = {int(r["source_key"]) for r in self._ap_starting_fast_travel_routes}
            distances = []
            for source_key in source_keys:
                row = keyed.get(source_key)
                if not row or int(row[1]) != int(d["FAST_TRAVEL_VTABLE"]):
                    continue
                sp = self._ap_ft_actor_pos(pine, int(row[0]), d)
                if sp is None:
                    continue
                distances.append(((kp[0]-sp[0])**2 + (kp[1]-sp[1])**2 + (kp[2]-sp[2])**2) ** 0.5)
            return min(distances) if distances else None
        except Exception:
            return None

    def _ap_ft_world_guard(self, pine: PineClient, actors: list[int], vtables: list[int], d: dict) -> None:
        wanted_vts = {
            int(d["FAST_TRAVEL_VTABLE"]),
            int(d["WIND_CONTROLLER_VTABLE"]),
            int(d["MASTER_EVENT_VTABLE"]),
            int(d["ACCESS_HANDLER_VTABLE"]),
        }
        candidates = [(a, vt) for a, vt in zip(actors, vtables) if int(vt) in wanted_vts]
        if not candidates:
            return
        descs = pine.read32_many([a + int(d["FAST_TRAVEL_DESCRIPTOR_OFFSET"]) for a, _ in candidates])
        valid = [(a, vt, desc) for (a, vt), desc in zip(candidates, descs) if self._ap_valid_pointer(desc)]
        keys = pine.read32_many([desc + int(d["FAST_TRAVEL_KEY_OFFSET"]) for _, _, desc in valid]) if valid else []
        keyed = {
            int(key) & 0xFFFFFFFF: (int(actor), int(vt))
            for (actor, vt, _), key in zip(valid, keys)
            if 0 < int(key) < 0x10000
        }
        self._ap_ft_apply_access_locks(pine, keyed, d)
        if self._ap_fast_travel_progression != "archipelago":
            return
        # V0.8.45 ownership rule: with the cleanroom controller enabled, the
        # normal world guard is NEVER allowed to write Fast Travel source or
        # destination structures.  It may still enforce the two unrelated
        # access-lock bits outside a FT transaction.  All FT memory belongs to
        # the synchronous BAT-style cleanroom only.
        if self._ap_ft_sanctuary_enabled:
            return
        source_keys = {int(x) for x in d.get("NATIV_FAST_TRAVEL_SOURCE_KEYS", [])}
        if any(k in keyed and int(keyed[k][1]) == int(d["FAST_TRAVEL_VTABLE"]) for k in source_keys):
            self._ap_ft_patch_nativ_sources(pine, keyed, d)
            self._ap_ft_open_selected_planks(pine, actors, vtables, keyed, d)
        for route in self._ap_starting_fast_travel_routes:
            if int(route["target_key"]) in keyed:
                self._ap_ft_patch_destination(pine, route, keyed, d)

    @staticmethod
    def _ap_ft_float(raw: int) -> float:
        return struct.unpack("<f", struct.pack("<I", int(raw) & 0xFFFFFFFF))[0]

    def _ap_ft_actor_pos(self, pine: PineClient, actor: int, d: dict) -> tuple[float, float, float] | None:
        raw = pine.read32_many([
            actor + int(d["ACTOR_POS_X_OFFSET"]),
            actor + int(d["ACTOR_POS_Y_OFFSET"]),
            actor + int(d["ACTOR_POS_Z_OFFSET"]),
        ])
        xyz = tuple(self._ap_ft_float(x) for x in raw)
        if not all(abs(v) < 100000.0 and v == v for v in xyz):
            return None
        return xyz


    def _ap_ft_debug_warp_kya_to_target(
        self,
        pine: PineClient,
        route: dict,
        target_actor: int,
        d: dict,
    ) -> tuple[bool, float | None]:
        """DEBUG/SAFE fallback: place Kya on the resolved FT pad and keep her there.

        V0.8.33 proved that the persistent target key resolves the correct pad.
        V0.8.34 showed that leaving the selected FT fully vanilla can leave the
        destination pad/runtime insufficiently initialized and Kya can fall into
        the void.

        V0.8.40 FT-exclusive bridge does not use SafeWarp:
          1) selected target is canonicalized by _ap_ft_patch_destination;
          2) Kya is held at the target pad for a longer settle window;
          3) after release, a watchdog observes distance/vertical fall;
          4) if Kya escapes/falls, she is re-pinned automatically;
          5) success requires a stable post-release dwell near the target.

        This is intentionally a robust Archipelago fallback.  It does not touch
        the destination Master state and it does not claim to reproduce the
        native teleporter transition.
        """
        target_pos = self._ap_ft_actor_pos(pine, int(target_actor), d)
        if target_pos is None:
            self._log_threadsafe(
                f"SAFEWARP refused: invalid target position for {route.get('label')}.",
                "error",
            )
            return False, None

        kya = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
        if not self._ap_valid_pointer(kya):
            self._log_threadsafe(
                f"SAFEWARP refused: Kya actor unavailable for {route.get('label')}.",
                "error",
            )
            return False, None

        before = self._ap_ft_actor_pos(pine, kya, d)
        if before is None:
            self._log_threadsafe(
                f"SAFEWARP refused: Kya position invalid for {route.get('label')}.",
                "error",
            )
            return False, None

        y_offset = float(d.get("FAST_TRAVEL_SAFEWARP_Y_OFFSET", 1.25))
        wanted = (
            float(target_pos[0]),
            float(target_pos[1]) + y_offset,
            float(target_pos[2]),
        )
        raws = [self._ap_float_to_raw(v) for v in wanted]

        xoff = int(d["ACTOR_POS_X_OFFSET"])
        yoff = int(d["ACTOR_POS_Y_OFFSET"])
        zoff = int(d["ACTOR_POS_Z_OFFSET"])

        self._log_threadsafe(
            f"SAFEWARP start: {route.get('label')} | "
            f"Kya before=({before[0]:.3f},{before[1]:.3f},{before[2]:.3f}) | "
            f"target=({target_pos[0]:.3f},{target_pos[1]:.3f},{target_pos[2]:.3f}) | "
            f"landing=({wanted[0]:.3f},{wanted[1]:.3f},{wanted[2]:.3f}).",
            "warn",
        )

        def pin_for(seconds: float) -> int:
            deadline = time.monotonic() + float(seconds)
            writes = 0
            while time.monotonic() < deadline:
                kya_now = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
                if not self._ap_valid_pointer(kya_now):
                    time.sleep(0.01)
                    continue
                pine.write32(kya_now + xoff, raws[0])
                pine.write32(kya_now + yoff, raws[1])
                pine.write32(kya_now + zoff, raws[2])
                writes += 1
                time.sleep(float(d.get("FAST_TRAVEL_SAFEWARP_PIN_INTERVAL", 0.012)))
            return writes

        # Long initial settle.  V0.8.33 used 0.35 s; make this deliberately
        # conservative so streaming/collision has time to finish.
        writes = pin_for(float(d.get("FAST_TRAVEL_SAFEWARP_INITIAL_HOLD", 1.50)))

        watchdog_seconds = float(d.get("FAST_TRAVEL_SAFEWARP_WATCHDOG_SECONDS", 3.00))
        stable_required = float(d.get("FAST_TRAVEL_SAFEWARP_STABLE_SECONDS", 0.90))
        success_radius = float(d.get("FAST_TRAVEL_SAFEWARP_SUCCESS_RADIUS", 5.0))
        fall_margin = float(d.get("FAST_TRAVEL_SAFEWARP_FALL_MARGIN", 6.0))
        repin_seconds = float(d.get("FAST_TRAVEL_SAFEWARP_REPIN_SECONDS", 0.75))
        max_repins = int(d.get("FAST_TRAVEL_SAFEWARP_MAX_REPINS", 4))

        started = time.monotonic()
        stable_since = None
        repins = 0
        last_distance = None
        last_pos = None

        while time.monotonic() - started < watchdog_seconds:
            kya_now = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
            if not self._ap_valid_pointer(kya_now):
                stable_since = None
                time.sleep(0.02)
                continue

            last_pos = self._ap_ft_actor_pos(pine, kya_now, d)
            last_distance = self._ap_ft_arrival_distance(
                pine, int(target_actor), d
            )

            escaped = (
                last_pos is None
                or last_distance is None
                or last_distance > success_radius
                or (
                    last_pos is not None
                    and float(last_pos[1]) < float(target_pos[1]) - fall_margin
                )
            )

            if escaped:
                stable_since = None
                if repins >= max_repins:
                    break
                repins += 1
                self._log_threadsafe(
                    f"SAFEWARP recovery #{repins}: {route.get('label')} | "
                    f"distance={last_distance} pos={last_pos}.",
                    "warn",
                )
                writes += pin_for(repin_seconds)
                continue

            now = time.monotonic()
            if stable_since is None:
                stable_since = now
            elif now - stable_since >= stable_required:
                self._log_threadsafe(
                    f"SAFEWARP STABLE: {route.get('label')} | writes={writes} "
                    f"repins={repins} distance={last_distance} pos={last_pos}.",
                    "ok",
                )
                return True, last_distance

            time.sleep(0.02)

        self._log_threadsafe(
            f"SAFEWARP FAILED: {route.get('label')} | writes={writes} "
            f"repins={repins} distance={last_distance} pos={last_pos}.",
            "error",
        )
        return False, last_distance


    def _ap_ft_arrival_distance(self, pine: PineClient, target_actor: int, d: dict) -> float | None:
        kya = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
        if not self._ap_valid_pointer(kya):
            return None
        kp = self._ap_ft_actor_pos(pine, kya, d)
        tp = self._ap_ft_actor_pos(pine, target_actor, d)
        if kp is None or tp is None:
            return None
        return ((kp[0]-tp[0])**2 + (kp[1]-tp[1])**2 + (kp[2]-tp[2])**2) ** 0.5

    def _ap_ft_target_route_wind_controllers(
        self,
        pine: PineClient,
        target_actor: int,
        d: dict,
    ) -> list[tuple[int, int, int]]:
        """Resolve C540 wind/event controllers referenced by the target FT route table.

        The V0.8.36 forensic dump exposed the missing link directly inside
        target+0x2BC.  For Flying Forest FT01 the table points at C540 actors at
        table+0x50 and table+0x90.  Resolve this dynamically instead of hardcoding
        keys so the same path can be tested on every destination.

        Returns ``[(table_offset, actor, persistent_key), ...]``.
        """
        table = int(pine.read32(int(target_actor) + int(d["FAST_TRAVEL_ROUTE_TABLE_OFFSET"])))
        if not self._ap_valid_pointer(table):
            return []
        count = int(pine.read32(table))
        if count <= 0 or count > 32:
            return []

        scan_size = int(d.get("FAST_TRAVEL_TARGET_CHAIN_TABLE_SCAN", 0x120))
        scan_size = max(0x40, min(scan_size, 0x200))
        offsets = list(range(0, scan_size, 4))
        values = pine.read32_many([table + off for off in offsets])
        candidates = [(off, int(ptr)) for off, ptr in zip(offsets, values) if self._ap_valid_pointer(int(ptr))]
        if not candidates:
            return []
        vtables = pine.read32_many([ptr for _, ptr in candidates])
        found: list[tuple[int, int, int]] = []
        seen: set[int] = set()
        for (off, actor), vt in zip(candidates, vtables):
            if int(vt) != int(d["WIND_CONTROLLER_VTABLE"]) or actor in seen:
                continue
            seen.add(actor)
            key = 0
            desc = int(pine.read32(actor + int(d["FAST_TRAVEL_DESCRIPTOR_OFFSET"])))
            if self._ap_valid_pointer(desc):
                raw_key = int(pine.read32(desc + int(d["FAST_TRAVEL_KEY_OFFSET"])))
                if 0 < raw_key < 0x10000:
                    key = raw_key
            found.append((off, actor, key))
        return found

    def _ap_ft_commit_target_after_chain(
        self,
        pine: PineClient,
        route: dict,
        target_actor: int,
        d: dict,
    ) -> tuple[int, int, int]:
        """Last-resort commit after the route-linked chain has been fired.

        Unlike V0.8.36 this is never done before Kya reaches the pad and never done
        before the C540 controllers have been given their vanilla trigger flags.
        It exists only to prevent a softlock if the event chain animates but fails
        to persist the FT availability fields through PINE timing.
        """
        actor = int(target_actor)
        addrs = [
            actor + int(d["FAST_TRAVEL_INDEX_OFFSET"]),
            actor + int(d["FAST_TRAVEL_INDEX_COPY_OFFSET"]),
            actor + int(d["FAST_TRAVEL_MASK_OFFSET"]),
            actor + int(d["FAST_TRAVEL_ACTIVE_OFFSET"]),
            actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]),
        ]
        cur = [int(x) for x in pine.read32_many(addrs)]
        wanted = [0, 0, int(d["FAST_TRAVEL_DESTINATION_SINGLE_MASK"]), 1, 1]
        for addr, old_value, value in zip(addrs, cur, wanted):
            self._ap_ft_write_if_needed(pine, addr, old_value, value)
        footer = self._ap_ft_footer_addr(pine, actor, d)
        if footer is not None:
            old_footer = int(pine.read32(footer))
            self._ap_ft_write_if_needed(
                pine,
                footer,
                old_footer,
                old_footer | int(d["FAST_TRAVEL_ROUTE_READY_FLAG"]),
            )

        state_addr = actor + int(d["ACTOR_STATE_OFFSET"])
        prev_addr = actor + int(d["ACTOR_PREV_STATE_OFFSET"])
        state, prev = [int(x) for x in pine.read32_many([state_addr, prev_addr])]
        if state in (5, 7):
            # State 6 alone did not fix V0.8.36, but after the linked C540 chain
            # has fired it matches the known working FT actor signature.
            pine.write32(state_addr, 6)
            time.sleep(0.08)
        state2, active2, avail2 = [int(x) for x in pine.read32_many([
            state_addr,
            actor + int(d["FAST_TRAVEL_ACTIVE_OFFSET"]),
            actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]),
        ])]
        self._log_threadsafe(
            f"FT TARGET CHAIN fallback commit: {route.get('label')} | "
            f"state={state}->{state2} active={active2} available={avail2}. Master untouched.",
            "warn",
        )
        return state2, active2, avail2

    def _ap_ft_run_target_vanilla_chain(
        self,
        pine: PineClient,
        route: dict,
        target_actor: int,
        d: dict,
    ) -> bool:
        """Fire the route-linked wind/event chain only after Kya reached the target.

        Desired order for AP travel:
            Nativs City source -> destination zone -> Kya on target pad ->
            route-linked C540 chain -> FT becomes open/usable.

        The target endpoint is deliberately left vanilla (active=0/available=0 on
        an undiscovered pad) until this function runs.
        """
        actor = int(target_actor)
        state_addr = actor + int(d["ACTOR_STATE_OFFSET"])
        prev_addr = actor + int(d["ACTOR_PREV_STATE_OFFSET"])
        active_addr = actor + int(d["FAST_TRAVEL_ACTIVE_OFFSET"])
        avail_addr = actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"])
        mask_addr = actor + int(d["FAST_TRAVEL_MASK_OFFSET"])
        state0, prev0, active0, avail0, mask0 = [int(x) for x in pine.read32_many([
            state_addr, prev_addr, active_addr, avail_addr, mask_addr,
        ])]
        controllers = self._ap_ft_target_route_wind_controllers(pine, actor, d)
        controller_desc = ", ".join(
            f"+0x{off:03X}->0x{ctrl:08X}/key=0x{key:04X}"
            for off, ctrl, key in controllers
        ) or "NONE"
        self._log_threadsafe(
            f"FT TARGET CHAIN start: {route.get('label')} | "
            f"target state={state0} prev=0x{prev0:08X} active={active0} "
            f"available={avail0} mask=0x{mask0:08X} | C540={controller_desc}.",
            "info",
        )

        # If vanilla/save data already has the endpoint open, do not replay the
        # discovery animation.  Just leave it alone.
        if active0 == 1 and avail0 == 1:
            self._log_threadsafe(
                f"FT TARGET CHAIN already open: {route.get('label')} (vanilla/save state preserved).",
                "ok",
            )
            return True

        fired = 0
        target_key = int(route.get("target_key", 0))
        for off, ctrl, key in controllers:
            flags0, cstate0, cprev0 = [int(x) for x in pine.read32_many([
                ctrl + int(d["ACTOR_FLAGS_OFFSET"]),
                ctrl + int(d["ACTOR_STATE_OFFSET"]),
                ctrl + int(d["ACTOR_PREV_STATE_OFFSET"]),
            ])]
            ok = self._ap_ft_activate_wind(pine, target_key, ctrl, d)
            flags1, cstate1, cprev1 = [int(x) for x in pine.read32_many([
                ctrl + int(d["ACTOR_FLAGS_OFFSET"]),
                ctrl + int(d["ACTOR_STATE_OFFSET"]),
                ctrl + int(d["ACTOR_PREV_STATE_OFFSET"]),
            ])]
            if ok or (cstate1 == 8 and cprev1 == 5):
                fired += 1
            self._log_threadsafe(
                f"FT TARGET CHAIN C540 +0x{off:03X} key=0x{key:04X}: "
                f"flags 0x{flags0:08X}->0x{flags1:08X}, "
                f"state {cstate0}->{cstate1}, prev 0x{cprev0:08X}->0x{cprev1:08X}.",
                "ok" if (ok or (cstate1 == 8 and cprev1 == 5)) else "warn",
            )
            time.sleep(float(d.get("FAST_TRAVEL_TARGET_CHAIN_CONTROLLER_GAP", 0.12)))

        timeout = float(d.get("FAST_TRAVEL_TARGET_CHAIN_WAIT_SECONDS", 1.80))
        deadline = time.monotonic() + timeout
        last = (state0, active0, avail0)
        while time.monotonic() < deadline:
            state, active, avail = [int(x) for x in pine.read32_many([
                state_addr, active_addr, avail_addr,
            ])]
            last = (state, active, avail)
            if active == 1 and avail == 1:
                self._log_threadsafe(
                    f"FT TARGET CHAIN VANILLA OPEN: {route.get('label')} | "
                    f"state={state} active=1 available=1 | linked C540 fired={fired}/{len(controllers)}.",
                    "ok",
                )
                return True
            time.sleep(0.05)

        self._log_threadsafe(
            f"FT TARGET CHAIN did not persist availability by itself: {route.get('label')} | "
            f"last state={last[0]} active={last[1]} available={last[2]} | "
            f"linked C540 fired={fired}/{len(controllers)}. Applying anti-softlock commit AFTER chain.",
            "warn",
        )
        state2, active2, avail2 = self._ap_ft_commit_target_after_chain(
            pine, route, actor, d
        )
        # One final verification, including controller states, so the next test
        # tells us whether the missing piece was chain activation or persistence.
        time.sleep(0.20)
        ctrl_states = []
        for off, ctrl, key in controllers:
            cs, cp = [int(x) for x in pine.read32_many([
                ctrl + int(d["ACTOR_STATE_OFFSET"]),
                ctrl + int(d["ACTOR_PREV_STATE_OFFSET"]),
            ])]
            ctrl_states.append(f"+0x{off:03X}/0x{key:04X}:{cs}/{cp:08X}")
        self._log_threadsafe(
            f"FT TARGET CHAIN FINAL: {route.get('label')} | state={state2} "
            f"active={active2} available={avail2} | C540 "
            f"{', '.join(ctrl_states) if ctrl_states else 'NONE'}.",
            "ok" if (active2 == 1 and avail2 == 1 and fired > 0) else "warn",
        )
        return active2 == 1 and avail2 == 1

    def _ap_ft_arm_mana_stall_rescue(
        self,
        pine: PineClient,
        d: dict,
        label: str,
        now: float | None = None,
    ) -> None:
        """Arm a short post-Fast-Travel zero-mana stall detector.

        This is deliberately event-driven: no permanent proximity scanner.
        Kya may move normally during the window; the stationary timer restarts
        whenever she moves. Mana is written only after a continuous stationary
        dwell and only when authoritative runtime mana is exactly zero.
        """
        now = time.monotonic() if now is None else float(now)
        kya = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
        if not self._ap_valid_pointer(kya):
            return
        pos = self._ap_ft_actor_pos(pine, kya, d)
        if pos is None:
            return
        self._ap_ft_mana_stall_rescue = {
            "label": str(label),
            "armed_at": now,
            "expires_at": now + float(d.get("FAST_TRAVEL_MANA_STALL_WINDOW_SECONDS", 8.0)),
            "still_since": now,
            "anchor": tuple(pos),
            "next_sample": now,
        }
        self._log_threadsafe(
            f"FT MANA STALL GUARD armed: {label}; watching for zero-mana immobility.",
            "info",
        )

    def _ap_ft_mana_stall_rescue_tick(self, pine: PineClient, d: dict, now: float) -> None:
        rescue = self._ap_ft_mana_stall_rescue
        if not rescue:
            return
        if now >= float(rescue.get("expires_at", 0.0)):
            self._ap_ft_mana_stall_rescue = None
            return
        if now < float(rescue.get("next_sample", 0.0)):
            return
        rescue["next_sample"] = now + float(d.get("FAST_TRAVEL_MANA_STALL_SAMPLE_SECONDS", 0.10))

        try:
            kya = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
            if not self._ap_valid_pointer(kya):
                return
            pos = self._ap_ft_actor_pos(pine, kya, d)
            if pos is None:
                return
            anchor = rescue.get("anchor")
            if not anchor:
                rescue["anchor"] = tuple(pos)
                rescue["still_since"] = now
                return
            moved = ((pos[0]-anchor[0])**2 + (pos[1]-anchor[1])**2 + (pos[2]-anchor[2])**2) ** 0.5
            move_epsilon = float(d.get("FAST_TRAVEL_MANA_STALL_MOVE_EPSILON", 0.25))
            if moved > move_epsilon:
                rescue["anchor"] = tuple(pos)
                rescue["still_since"] = now
                return

            dwell = now - float(rescue.get("still_since", now))
            dwell_required = float(d.get("FAST_TRAVEL_MANA_STALL_DWELL_SECONDS", 2.0))
            if dwell < dwell_required:
                return

            player = self._ap_player_pointer(pine, d)
            if player is None:
                return
            magic_obj = player + int(d["PLAYER_MAGIC_OBJECT_OFFSET"])
            current_addr = magic_obj + int(d["MAGIC_CURRENT_OFFSET"])
            max_addr = magic_obj + int(d["MAGIC_MAX_OFFSET"])
            current = self._ap_raw_to_float(pine.read32(current_addr))
            maximum = self._ap_raw_to_float(pine.read32(max_addr))
            if not (0.0 <= current <= maximum and 0.0 < maximum <= float(d["MAGIC_MAX_CAP"])):
                return

            label = str(rescue.get("label", "Fast Travel"))
            if current <= 0.05:
                target = min(maximum, float(d.get("FAST_TRAVEL_MIN_RETURN_MANA", 3)))
                pine.write32(current_addr, self._ap_float_to_raw(target))
                verified = self._ap_raw_to_float(pine.read32(current_addr))
                if abs(verified - target) <= 0.05:
                    self._log_threadsafe(
                        f"FT MANA STALL RESCUE: {label} | Kya immobile {dwell:.2f}s and mana=0 -> {verified:g}.",
                        "ok",
                    )
                else:
                    self._log_threadsafe(
                        f"FT MANA STALL RESCUE write mismatch: {label} expected {target:g}, got {verified:g}.",
                        "warn",
                    )
            else:
                self._log_threadsafe(
                    f"FT MANA STALL GUARD cleared: {label} | Kya immobile {dwell:.2f}s but mana={current:g}; zero-only rescue not needed.",
                    "info",
                )
            self._ap_ft_mana_stall_rescue = None
        except Exception:
            # Keep the short window alive through transient streaming reads.
            return

    def _ap_ft_ensure_return_mana(self, pine: PineClient, d: dict) -> None:
        """Guarantee enough REAL runtime magic to use the return Fast Travel.

        0x004525D8 is only the integer HUD/cache mirror and is rewritten by
        the game from the player's runtime magic object. The authoritative
        current magic is float32 at:
            Read32(ADDR_PLAYER_POINTER)
            + PLAYER_MAGIC_OBJECT_OFFSET
            + MAGIC_CURRENT_OFFSET
        """
        minimum = float(d.get("FAST_TRAVEL_MIN_RETURN_MANA", 3))
        player = self._ap_player_pointer(pine, d)
        if player is None:
            self._log_threadsafe(
                "Fast Travel anti-softlock: player pointer unavailable; mana not changed.",
                "warn",
            )
            return

        magic_obj = player + int(d["PLAYER_MAGIC_OBJECT_OFFSET"])
        current_address = magic_obj + int(d["MAGIC_CURRENT_OFFSET"])
        max_address = magic_obj + int(d["MAGIC_MAX_OFFSET"])

        current = self._ap_raw_to_float(pine.read32(current_address))
        maximum = self._ap_raw_to_float(pine.read32(max_address))

        # The working BAT guarantees a *minimum* of 3 real runtime mana before
        # the destination wind chain is committed.  It is not an additive +3.
        # Accept a small negative depleted value too: some transition frames can
        # briefly expose mana debt before the HUD/runtime mirrors settle.
        debt_floor = -float(d.get("FAST_TRAVEL_MANA_DEBT_FLOOR", 12.0))
        if not (
            debt_floor <= current <= maximum
            and 0.0 < maximum <= float(d["MAGIC_MAX_CAP"])
        ):
            self._log_threadsafe(
                f"Fast Travel anti-softlock: invalid runtime magic "
                f"(current={current:g}, max={maximum:g}); mana not changed.",
                "warn",
            )
            return

        if current >= minimum - 0.05:
            return

        target = min(maximum, minimum)
        pine.write32(current_address, self._ap_float_to_raw(target))
        verified = self._ap_raw_to_float(pine.read32(current_address))

        if abs(verified - target) <= 0.05:
            self._log_threadsafe(
                f"Fast Travel anti-softlock: runtime mana {current:g} -> {verified:g}.",
                "ok",
            )
        else:
            self._log_threadsafe(
                f"Fast Travel anti-softlock write mismatch: "
                f"expected {target:g}, got {verified:g}.",
                "warn",
            )

    def _ap_ft_queue_arrival_check(self, route: dict, d: dict) -> None:
        link = self._ap_link
        if link is None or not self._ap_joined or not self._ap_seed_build_verified:
            return
        name = str(route.get("location_name") or "")
        lid = d.get("LOCATION_NAME_TO_ID", {}).get(name)
        if lid is None:
            return
        lid = int(lid)
        if lid in self._ap_checked or lid in self._ap_pending_checks:
            return
        self._ap_queue_location_check(link, lid, name, d)
        self._log_threadsafe(f"Fast Travel arrival CHECK queued -> Archipelago: {name} [id={lid}]", "ok")


    def _ap_ft_actor_has_identity(
        self,
        pine: PineClient,
        actor: int,
        expected_key: int,
        expected_vtable: int,
        d: dict,
    ) -> bool:
        if not self._ap_valid_pointer(actor):
            return False
        try:
            vt, desc = pine.read32_many([
                int(actor),
                int(actor) + int(d["FAST_TRAVEL_DESCRIPTOR_OFFSET"]),
            ])
            if int(vt) != int(expected_vtable) or not self._ap_valid_pointer(int(desc)):
                return False
            key = int(pine.read32(int(desc) + int(d["FAST_TRAVEL_KEY_OFFSET"]))) & 0xFFFFFFFF
            return key == int(expected_key)
        except Exception:
            return False

    def _ap_ft_refresh_route_identity(
        self,
        pine: PineClient,
        route: dict,
        d: dict,
    ) -> tuple[dict[int, tuple[int, int]], int | None, int | None]:
        keyed = self._ap_ft_scan_keyed(
            pine,
            d,
            {int(d["FAST_TRAVEL_VTABLE"]), int(d["MASTER_EVENT_VTABLE"])},
        )
        trow = keyed.get(int(route["target_key"]))
        mrow = keyed.get(int(route["master_key"]))
        if (
            not trow or not mrow
            or int(trow[1]) != int(d["FAST_TRAVEL_VTABLE"])
            or int(mrow[1]) != int(d["MASTER_EVENT_VTABLE"])
        ):
            return keyed, None, None
        return keyed, int(trow[0]), int(mrow[0])


    def _ap_ft_sanctuary_room_present(self, pine: PineClient, d: dict) -> bool:
        """Legacy weak probe kept only for diagnostics.

        Persistent keys are scene-local in Kya, so this MUST NOT be used to
        arm the cleanroom.  V0.8.47 uses _ap_ft_nativ_room_fingerprint().
        """
        try:
            keyed = self._ap_ft_scan_keyed(
                pine,
                d,
                {int(d["FAST_TRAVEL_VTABLE"]), int(d["MASTER_EVENT_VTABLE"])},
            )
        except Exception:
            return False
        master_vt = int(d["MASTER_EVENT_VTABLE"])
        ft_vt = int(d["FAST_TRAVEL_VTABLE"])
        for key in (int(v) for v in d.get("NATIV_FAST_TRAVEL_SOURCE_KEYS", [])):
            row = keyed.get(key)
            if row and int(row[1]) == ft_vt:
                return True
        for key in (int(v) for v in d.get("NATIV_WOOD_MASTER_KEYS", {}).values()):
            row = keyed.get(key)
            if row and int(row[1]) == master_vt:
                return True
        return False

    def _ap_ft_nativ_room_fingerprint(self, pine: PineClient, d: dict) -> bool:
        """Scene-specific proof that the real Nativ Fast Travel room is loaded.

        Actor persistent keys alone are insufficient because the same numeric
        keys can occur in other scenes.  The Nativ room also has eight fixed
        C2D0 wooden-kiosk handlers at known EE addresses.  Every handler must:
          * have the C2D0 vtable,
          * point through +0x04 to the expected runtime Master actor, and
          * retain required == 0.
        Together with all eight Master keys/vtables this is a strong room
        fingerprint and prevents destination-zone false positives.
        """
        try:
            keyed = self._ap_ft_scan_keyed(
                pine,
                d,
                {int(d["FAST_TRAVEL_VTABLE"]), int(d["MASTER_EVENT_VTABLE"])},
            )
        except Exception:
            return False

        master_vt = int(d["MASTER_EVENT_VTABLE"])
        handler_vt = int(d["NATIV_WOOD_HANDLER_VTABLE"])
        parent_off = int(d["NATIV_WOOD_MASTER_PTR_OFFSET"])
        # IMPORTANT V0.8.47: +0x14 (required freed-Wolfen count) is a MUTABLE
        # gameplay field, not part of the room identity. V0.8.46 incorrectly
        # required it to remain zero. After the first FT cycle vanilla can leave
        # a non-zero/transient value there when Nativs City streams back in,
        # which prevented the verified gate from ever re-arming. The visible
        # symptom was exactly: first FT works, Wolfen works, return to Nativs ->
        # every AP button stays grey.
        #
        # The immutable identity is already much stronger than scene-local keys:
        #   * all 8 expected Master keys with the Master vtable, AND
        #   * all 8 fixed C2D0 handler addresses with the C2D0 vtable, AND
        #   * each handler +0x04 points to its expected current runtime Master.
        # Eight fixed reverse-links are enough to prove the real Nativ FT room.
        # Do NOT gate room detection on +0x14.
        master_map = {int(k): int(v) for k, v in d.get("NATIV_WOOD_MASTER_KEYS", {}).items()}
        handler_hints = {int(k): int(v) for k, v in d.get("NATIV_WOOD_LEGACY_HANDLER_HINTS", {}).items()}
        if len(master_map) != 8 or len(handler_hints) < 8:
            return False

        resolved_masters: dict[int, int] = {}
        for source_key, master_key in master_map.items():
            row = keyed.get(master_key)
            if not row or int(row[1]) != master_vt:
                return False
            resolved_masters[source_key] = int(row[0])

        for source_key, master_actor in resolved_masters.items():
            handler = handler_hints.get(source_key)
            if handler is None:
                return False
            try:
                vt, parent = pine.read32_many([
                    handler,
                    handler + parent_off,
                ])
            except Exception:
                return False
            if int(vt) != handler_vt or int(parent) != int(master_actor):
                return False
        return True

    def _ap_ft_nativ_room_owner_present(self, pine: PineClient, d: dict) -> bool:
        """V0.8.49 structural Nativ Fast-Travel room ownership predicate.

        IMPORTANT: the normal zone watcher is Wolfen-key based.  After Nativs
        City's only mapped Wolfen has been freed, a later return may have no
        active Nativ Wolfen vote at all; _ap_current_zone can therefore remain
        stuck on the previous destination (for example Flying Forest).  V0.8.48
        required that stale hint to already equal ``Nativs City``, which is why
        the first trip worked but every AP source button stayed grey on return.

        Persistent keys are scene-local, so one or a few matching IDs are not
        enough either.  Instead prove the room structurally with the complete
        Nativ kiosk cluster:
          * all 8 wooden kiosk Master keys are live Master Events; and
          * every AP-selected source is a live Fast Travel actor; and
          * EITHER all 8 known Nativ FT source keys are live,
            OR at least 4 fixed C2D0 handlers currently reverse-link to their
            expected runtime Masters.

        The 16-key full cluster is absent from destination scans, while the
        partial C2D0 fallback tolerates late handler initialization on return.
        No Wolfen/zone hint participates in this decision.
        """
        try:
            keyed = self._ap_ft_scan_keyed(
                pine, d, {int(d["FAST_TRAVEL_VTABLE"]), int(d["MASTER_EVENT_VTABLE"])}
            )
        except Exception:
            return False

        ft_vt = int(d["FAST_TRAVEL_VTABLE"])
        master_vt = int(d["MASTER_EVENT_VTABLE"])
        master_map = {int(k): int(v) for k, v in d.get("NATIV_WOOD_MASTER_KEYS", {}).items()}
        source_keys = [int(v) for v in d.get("NATIV_FAST_TRAVEL_SOURCE_KEYS", [])]
        selected_sources = {int(r["source_key"]) for r in self._ap_starting_fast_travel_routes}
        if len(master_map) != 8 or len(source_keys) != 8 or not selected_sources:
            return False

        resolved_masters: dict[int, int] = {}
        for source_key, master_key in master_map.items():
            row = keyed.get(master_key)
            if not row or int(row[1]) != master_vt:
                return False
            resolved_masters[source_key] = int(row[0])

        # Every route that this AP seed exposes must exist as a real FT actor.
        for source_key in selected_sources:
            row = keyed.get(source_key)
            if not row or int(row[1]) != ft_vt:
                return False

        # Strongest / fastest proof: the complete 8-source + 8-Master cluster.
        live_source_count = sum(
            1 for source_key in source_keys
            if source_key in keyed and int(keyed[source_key][1]) == ft_vt
        )
        if live_source_count == len(source_keys):
            return True

        # Return-stream fallback: C2D0 links can initialize progressively.
        # Four independent fixed-address reverse links, on top of all 8 Masters
        # and all AP-selected source actors, are enough to distinguish the real
        # Nativ room without waiting for all eight links.
        handler_vt = int(d["NATIV_WOOD_HANDLER_VTABLE"])
        parent_off = int(d["NATIV_WOOD_MASTER_PTR_OFFSET"])
        handler_hints = {int(k): int(v) for k, v in d.get("NATIV_WOOD_LEGACY_HANDLER_HINTS", {}).items()}
        link_matches = 0
        for source_key, master_actor in resolved_masters.items():
            handler = handler_hints.get(source_key)
            if handler is None:
                continue
            try:
                vt, parent = pine.read32_many([handler, handler + parent_off])
            except Exception:
                continue
            if int(vt) == handler_vt and int(parent) == int(master_actor):
                link_matches += 1
        return link_matches >= 4

    def _ap_ft_sanctuary_room_loaded(self, pine: PineClient, d: dict) -> bool:
        """True only while the real Nativ City FT room is physically usable."""
        return self._ap_ft_nativ_room_owner_present(pine, d)

    def _ap_ft_resolve_wood_handler_quick(self, pine: PineClient, source_key: int,
                                          master_actor: int, d: dict, hints: dict[int, int]) -> int | None:
        """Resolve a wooden-panel C2D0 object using a VERIFIED runtime back-link.

        The historical PAL hint is an address, not an identity: savestates and
        scene streaming may move the object. Prefer the previously verified cache,
        then the original hint, then a deliberately bounded LOCAL pool search.
        No write is performed here. Never infer identity from proximity alone.
        """
        handler_vt = int(d["NATIV_WOOD_HANDLER_VTABLE"])
        parent_off = int(d["NATIV_WOOD_MASTER_PTR_OFFSET"])
        cache = getattr(self, "_ap_ft_plank_handler_cache", None)
        if not isinstance(cache, dict):
            cache = {}
            self._ap_ft_plank_handler_cache = cache
        candidates = [cache.get(int(source_key)), hints.get(int(source_key))]
        for candidate in candidates:
            if candidate is None:
                continue
            candidate = int(candidate)
            try:
                vt, parent = pine.read32_many([candidate, candidate + parent_off])
            except Exception:
                continue
            if int(vt) == handler_vt and int(parent) == int(master_actor):
                cache[int(source_key)] = candidate
                return candidate
        # Keep the critical Fast Travel room responsive. Search only a small
        # neighbourhood of the hint, at most once every 8s per source/master.
        hint = hints.get(int(source_key))
        if hint is None:
            return None
        probes = getattr(self, "_ap_ft_wood_probe_times", None)
        if not isinstance(probes, dict):
            probes = {}
            self._ap_ft_wood_probe_times = probes
        now = time.monotonic()
        token = (int(source_key), int(master_actor))
        if now - float(probes.get(token, -1e9)) < 8.0:
            return None
        probes[token] = now
        hint = int(hint)
        start = max(0x01000000, (hint - 0x1000) & ~3)
        end = min(0x02000000, (hint + 0x1000 + 4) & ~3)
        try:
            addrs = list(range(start, end, 4))
            values = pine.read32_many(addrs)
            matches = [int(a) for a, value in zip(addrs, values) if int(value) == handler_vt]
            for candidate in matches:
                if int(pine.read32(candidate + parent_off)) != int(master_actor):
                    continue
                cache[int(source_key)] = candidate
                self._log_threadsafe(
                    f"FT WOOD RELINK: source 0x{int(source_key):04X} "
                    f"C2D0=0x{candidate:08X} -> Master=0x{int(master_actor):08X} (verified).", "ok")
                return candidate
        except Exception:
            return None
        return None

    def _ap_ft_sanctuary_open_panels_exact(
        self,
        pine: PineClient,
        keyed: dict[int, tuple[int, int]],
        d: dict,
    ) -> dict[int, str]:
        """Exact synchronous wooden-panel opener used by the working sidecar."""
        selected_sources = {
            int(route["source_key"])
            for route in self._ap_starting_fast_travel_routes
        }
        master_keys = {
            int(k): int(v)
            for k, v in d.get("NATIV_WOOD_MASTER_KEYS", {}).items()
        }
        hints = {
            int(k): int(v)
            for k, v in d.get("NATIV_WOOD_LEGACY_HANDLER_HINTS", {}).items()
        }
        master_vt = int(d["MASTER_EVENT_VTABLE"])
        handler_vt = int(d["NATIV_WOOD_HANDLER_VTABLE"])
        parent_off = int(d["NATIV_WOOD_MASTER_PTR_OFFSET"])
        required_off = int(d["NATIV_WOOD_REQUIRED_OFFSET"])
        radius_off = int(d["NATIV_WOOD_RADIUS_OFFSET"])
        state_off = int(d["ACTOR_STATE_OFFSET"])
        prev_off = int(d["ACTOR_PREV_STATE_OFFSET"])
        trigger_raw = self._ap_float_to_raw(float(d.get("NATIV_WOOD_TRIGGER_RADIUS", 1000.0)))
        patches = []
        status: dict[int, str] = {}

        for source_key in sorted(selected_sources):
            master_key = master_keys.get(source_key)
            if master_key is None:
                continue
            mrow = keyed.get(master_key)
            if not mrow or int(mrow[1]) != master_vt:
                status[source_key] = "NOMASTER"
                continue
            master_actor = int(mrow[0])
            state, prev = pine.read32_many([master_actor + state_off, master_actor + prev_off])
            state = int(state)
            if state == 8:
                status[source_key] = "ALREADY"
                continue
            if state != 5:
                status[source_key] = f"WAIT({state})"
                continue
            handler = self._ap_ft_resolve_wood_handler_quick(
                pine, source_key, master_actor, d, hints)
            if handler is None:
                # Distinguish invalid/stale historical pointers from gameplay
                # progression conditions; neither is an excuse to force state 8.
                hint = hints.get(source_key)
                if hint is None:
                    status[source_key] = "NOHINT"
                else:
                    try:
                        vt_hint, parent_hint = pine.read32_many([int(hint), int(hint) + parent_off])
                        status[source_key] = (
                            "STALE_VTABLE" if int(vt_hint) != handler_vt
                            else "STALE_PARENT" if int(parent_hint) != master_actor
                            else "UNRESOLVED")
                    except Exception:
                        status[source_key] = "UNREADABLE_LINK"
                continue
            vt, parent, required, radius_raw = pine.read32_many([
                handler,
                handler + parent_off,
                handler + required_off,
                handler + radius_off,
            ])
            if int(vt) != handler_vt:
                status[source_key] = "STALE_VTABLE"
                continue
            if int(parent) != master_actor:
                status[source_key] = "STALE_PARENT"
                continue
            if int(required) != 0:
                # Vanilla conditions belong to the game. Keep read-only.
                status[source_key] = f"VANILLA_REQUIRED({int(required)})"
                continue

            # V0.9.11: NEVER fake Master state=8 here.  That made the log say
            # OPEN while the wooden mesh was still physically present.  The working
            # standalone BAT proved the correct path: enlarge the exact C2D0 handler
            # radius and let FUN_00168820 execute the normal 5->8 transition itself.
            # This updates both the event state and the visible wooden panel.
            patches.append((source_key, master_actor, handler, int(radius_raw)))
            if int(radius_raw) != int(trigger_raw):
                pine.write32(handler + radius_off, int(trigger_raw))
            status[source_key] = "VANILLA_ARMED"

        if patches:
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline and not self._camera_stop_event.is_set():
                pending = False
                for source_key, master_actor, _handler, _radius_raw in patches:
                    state, _prev = pine.read32_many([master_actor + state_off, master_actor + prev_off])
                    if int(state) == 8:
                        status[source_key] = "OPEN"
                    else:
                        pending = True
                if not pending:
                    break
                time.sleep(0.02)

        for _source_key, master_actor, handler, radius_raw in patches:
            try:
                vt, parent = pine.read32_many([handler, handler + parent_off])
                if int(vt) == handler_vt and int(parent) == master_actor:
                    pine.write32(handler + radius_off, radius_raw)
            except Exception:
                pass
        return status

    def _ap_ft_sanctuary_session(self, pine: PineClient, d: dict) -> bool:
        """Advance one cleanroom scan. True means the FT session has ended.

        Each call uses the *existing single PINE owner*.  The coroutine holds
        its approach, wood-panel and landing-guard state across calls; a regular
        heartbeat happens between scans.  Nothing else may write FT memory.
        """
        if self._ap_ft_sanctuary_generator is None:
            self._ap_ft_sanctuary_generator = self._ap_ft_sanctuary_steps(pine, d)
        try:
            next(self._ap_ft_sanctuary_generator)
            return False
        except StopIteration:
            self._ap_ft_sanctuary_generator = None
            return True
        except BaseException:
            # The generator's finally has already released the exclusive state.
            # A fresh PCSX2 session must never reuse its saved actor pointers.
            self._ap_ft_sanctuary_generator = None
            raise

    def _ap_ft_sanctuary_steps(self, pine: PineClient, d: dict):
        """Cooperative BAT cleanroom, with one PINE scan per service iteration.

        All historical transport safety conditions remain inside this generator.
        Unlike the old 120-second blocking loop, it yields control after every
        scan to allow a real game-signature heartbeat and UI responsiveness.
        """
        self._ap_ft_cleanroom_active = True
        self._ap_ft_sanctuary_active = True
        self._ap_ft_ft01_prepared_sources = {}  # Fresh room visit, exactly like BAT 11.
        self._log_threadsafe(
            "FT V0.9.21 BAT FT01 + EARLY PANELS: only Nativ source buttons are prepared; winds and destination discovery are vanilla-owned.",
            "ok",
        )

        all_selected_by_source = {
            int(route["source_key"]): route
            for route in self._ap_starting_fast_travel_routes
        }
        selected_by_source = {
            source_key: route
            for source_key, route in all_selected_by_source.items()
            if not self._ap_ft_route_detector_handoff(route, d)
        }
        handed_off = sorted(set(all_selected_by_source) - set(selected_by_source))
        if handed_off:
            self._log_threadsafe(
                "FT VANILLA OWNERSHIP active for Nativ sources: "
                + ", ".join(f"0x{x:04X}" for x in handed_off)
                + "; only those world(s) are now vanilla-owned.",
                "ok",
            )
        ft_vt = int(d["FAST_TRAVEL_VTABLE"])
        master_vt = int(d["MASTER_EVENT_VTABLE"])
        access_vt = int(d["ACCESS_HANDLER_VTABLE"])
        source_keys = {int(x) for x in d.get("NATIV_FAST_TRAVEL_SOURCE_KEYS", [])}
        near_route = None
        near_time = 0.0
        approach_wind_source = None  # Last successfully primed source, not a permanent lock
        pending_wind_source = None
        pending_wind_since = 0.0
        last_wind_attempt = 0.0
        last_quarry_probe = 0.0
        last_quarry_status = None
        last_quarry_report_at = 0.0
        last_nativ = False
        saw_nativ = False
        last_panel_attempt = 0.0
        last_panel_summary = None
        source_near_radius = float(d.get("FAST_TRAVEL_SOURCE_WIND_ARM_RADIUS", 6.5))
        wind_confirm_radius = float(d.get("FAST_TRAVEL_WIND_CONFIRM_RADIUS", 4.5))
        wind_confirm_seconds = float(d.get("FAST_TRAVEL_WIND_CONFIRM_SECONDS", 0.18))
        wind_retry_seconds = float(d.get("FAST_TRAVEL_WIND_SWITCH_COOLDOWN", 0.55))
        source_arm_window = 8.0
        room_yield_radius = 18.0
        room_yield_seconds = 0.80
        room_far_since = 0.0
        # V0.9.15: if a cleanroom starts with Kya already sitting on/next to a
        # Nativ source (typical return landing), no AP wind may fire and no route
        # may arm until Kya first walks clear of the pads.  This makes a return
        # physically inert instead of immediately launching the player again.
        # 0.9.56: The 120s watchdog may finish a perfectly stationary AFK
        # session. Re-arming a new cleanroom at 3m from the same source is NOT
        # evidence of a return landing. Preserve the old guard (including
        # True on a genuine return) only for the same streamed actor generation.
        continuity = getattr(self, "_ap_ft_cleanroom_continuation", None)
        self._ap_ft_cleanroom_continuation = None
        if (isinstance(continuity, tuple) and len(continuity) == 2
                and continuity[0] is not None
                and continuity[0] == self._ap_stream_last_valid_generation):
            return_wind_guard: bool | None = bool(continuity[1])
        else:
            return_wind_guard = None
        return_wind_guard_logged = False
        return_guard_block_radius = float(d.get("FAST_TRAVEL_RETURN_WIND_BLOCK_RADIUS", 7.0))
        return_guard_release_radius = float(d.get("FAST_TRAVEL_RETURN_WIND_RELEASE_RADIUS", 9.0))
        motion_last = None  # (timestamp, (x, y, z))
        motion_last_log = 0.0
        wait_deadline = time.monotonic() + 120.0

        try:
            while not self._camera_stop_event.is_set() and time.monotonic() < wait_deadline:
                now = time.monotonic()
                try:
                    keyed = self._ap_ft_scan_keyed(
                        pine, d, {ft_vt, master_vt, access_vt, int(d["WIND_CONTROLLER_VTABLE"])}
                    )
                except PineError:
                    # A dead PINE socket is NOT an actor-streaming hiccup.
                    # Previously it was retried here until the 120s cleanroom
                    # watchdog expired, delaying reconnection by minutes.
                    # Propagate to the sole PINE owner so it reconnects now.
                    raise
                except Exception as exc:
                    # Only transient game-scene scans are retried here.
                    self._log_threadsafe(f"FT TRUE CLEANROOM scene scan retry: {exc}", "warn")
                    # No blocking retry: next owner iteration can first verify
                    # the game signature and report a real PINE failure.
                    yield
                    continue

                # Once the cleanroom owns a *verified* Nativ room, use the
                # strong room fingerprint as the unload boundary.  We never let
                # a destination-zone key collision masquerade as Nativ again.
                nativ_loaded = self._ap_ft_nativ_room_owner_present(pine, d)

                if nativ_loaded:
                    saw_nativ = True

                    # V0.9.21: Keep AP lock decisions for the Root and Flying
                    # Forest elevators intact. Never clear their disable bits in
                    # the FT room; this contradicted Archipelago's route locks.

                    # V0.9.11: entry-fallback keeps AP one-bit masks permanently so secondary
                    # physical buttons never light. Full BAT source masks are used only
                    # by the postponed full Fast Travel mode.
                    armed_profile = (
                        near_route
                        if near_route is not None and (now - near_time <= source_arm_window)
                        else None
                    )
                    self._ap_ft_patch_nativ_sources(pine, keyed, d, armed_profile)

                    panel_retry = float(d.get("FAST_TRAVEL_PANEL_RETRY_SECONDS", 0.15))
                    if (not last_nativ) or (now - last_panel_attempt > panel_retry):
                        status = self._ap_ft_sanctuary_open_panels_exact(pine, keyed, d)
                        last_panel_attempt = time.monotonic()
                        summary = tuple(sorted(status.items()))
                        if status and summary != last_panel_summary:
                            last_panel_summary = summary
                            self._log_threadsafe(
                                "FT TRUE CLEANROOM PANELS: " + ", ".join(
                                    f"0x{k:04X}={v}" for k, v in sorted(status.items())
                                ),
                                "info",
                            )
                            if any(v == "VANILLA_ARMED" for v in status.values()):
                                self._log_threadsafe(
                                    "FT PANELS VANILLA TRIGGER: C2D0 radii temporarily enlarged; waiting for the game to remove the wooden panels itself.",
                                    "info",
                                )

                    try:
                        kya = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
                    except Exception:
                        kya = 0
                    kp = self._ap_ft_actor_pos(pine, kya, d) if self._ap_valid_pointer(kya) else None
                    if kp is not None:
                        if bool(d.get("FAST_TRAVEL_ACCESS_ONLY_TEST", True)):
                            if motion_last is not None:
                                prev_t, prev_p = motion_last
                                dt = max(0.001, now - prev_t)
                                delta = tuple(float(kp[j]) - float(prev_p[j]) for j in range(3))
                                travel = sum(v*v for v in delta) ** 0.5
                                if travel >= 0.4 and now - motion_last_log >= 1.5:
                                    self._log_threadsafe(
                                        f"FT MOTION READ-ONLY: ΔXYZ=({delta[0]:+.2f}, {delta[1]:+.2f}, {delta[2]:+.2f}) "
                                        f"over {dt:.2f}s; speed={travel/dt:.2f} m/s (vertical axis not assumed).",
                                        "info",
                                    )
                                    motion_last_log = now
                            motion_last = (now, tuple(kp))
                        best = None
                        best_dist = None
                        room_dist = None
                        for source_key, route in all_selected_by_source.items():
                            row = keyed.get(source_key)
                            if not row or int(row[1]) != ft_vt:
                                continue
                            actor = int(row[0])
                            sp = self._ap_ft_actor_pos(pine, actor, d)
                            if sp is None:
                                continue
                            dist = ((kp[0]-sp[0])**2 + (kp[1]-sp[1])**2 + (kp[2]-sp[2])**2) ** 0.5
                            if room_dist is None or dist < room_dist:
                                room_dist = dist

                            # A detector-handed-off world still participates in
                            # room ownership distance, but Launcher never arms or
                            # bridges its departure again.
                            if source_key not in selected_by_source:
                                continue

                            idx, idx_copy, avail = pine.read32_many([
                                actor + int(d["FAST_TRAVEL_INDEX_OFFSET"]),
                                actor + int(d["FAST_TRAVEL_INDEX_COPY_OFFSET"]),
                                actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]),
                            ])
                            if (
                                int(idx) != int(route["source_index"])
                                or int(idx_copy) != int(route["source_index"])
                                or int(avail) != 1
                            ):
                                continue
                            if best_dist is None or dist < best_dist:
                                best = route
                                best_dist = dist

                        # V0.8.50: the structural room may stay streamed while Kya
                        # walks back to Nativs shops. Do not freeze shop/Wolfen/access
                        # watchers for the whole scene. Yield once Kya is clearly
                        # outside the FT interaction area and no recently armed
                        # route still needs the departure window.
                        recent_arm = near_route is not None and (now - near_time <= source_arm_window)
                        if room_dist is not None and room_dist > room_yield_radius and not recent_arm:
                            if room_far_since <= 0.0:
                                room_far_since = now
                            elif now - room_far_since >= room_yield_seconds:
                                self._ap_ft_session_departed = False
                                self._ap_ft_cleanroom_continuation = None
                                self._log_threadsafe(
                                    f"FT ROOM OWNER YIELD: Kya left the FT interaction area ({room_dist:.2f}m); shops/Wolfen/access writers resume.",
                                    "info",
                                )
                                return
                        else:
                            room_far_since = 0.0

                        # Establish whether this cleanroom began on a return landing.
                        # On a normal/fresh approach Kya starts well outside the pads.
                        if return_wind_guard is None and room_dist is not None:
                            return_wind_guard = bool(room_dist <= return_guard_block_radius)
                            if return_wind_guard:
                                return_wind_guard_logged = True
                                self._log_threadsafe(
                                    f"FT RETURN LANDING GUARD: Kya entered Nativs City {room_dist:.2f}m from a source; "
                                    f"Launcher will NOT arm/refire any AP wind until Kya walks beyond {return_guard_release_radius:.1f}m.",
                                    "warn",
                                )
                        elif return_wind_guard and room_dist is not None and room_dist >= return_guard_release_radius:
                            return_wind_guard = False
                            near_route = None
                            near_time = 0.0
                            approach_wind_source = None
                            pending_wind_source = None
                            pending_wind_since = 0.0
                            self._log_threadsafe(
                                "FT RETURN LANDING GUARD CLEARED: player left the arrival pads; AP-owned routes may be armed again on a deliberate re-approach.",
                                "ok",
                            )

                        # AutoSave MUST continue running while the FT cleanroom
                        # owns the single PINE connection (up to 120 seconds).
                        # Save only outside the actual wind/arrival pads, with
                        # no recent AP arm, no pending local wind and a stable
                        # stream generation. Do not run during a departure.
                        recent_ft_arm = (near_route is not None and
                                         now - near_time <= source_arm_window)
                        if (room_dist is not None and room_dist >= return_guard_release_radius
                                and not recent_ft_arm and pending_wind_source is None
                                and not self._ap_stream_hold
                                and self._ap_stream_last_valid_generation is not None):
                            self._auto_save_tick(pine, safe_ft_room=True)

                        # Diagnostic only: Quarry button/controller and their live state.
                        # These reads never trigger FT discovery or modify route data.
                        if now - last_quarry_probe >= 1.0 and room_dist is not None and room_dist < 15.0:
                            last_quarry_probe = now
                            try:
                                qr = keyed.get(0x0244)
                                wr = keyed.get(0x0245)
                                if qr and wr:
                                    qa, wa = int(qr[0]), int(wr[0])
                                    qi, qc, qv = pine.read32_many([
                                        qa + int(d["FAST_TRAVEL_INDEX_OFFSET"]),
                                        qa + int(d["FAST_TRAVEL_INDEX_COPY_OFFSET"]),
                                        qa + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]),
                                    ])
                                    wf, ws, wp = pine.read32_many([
                                        wa + int(d["ACTOR_FLAGS_OFFSET"]),
                                        wa + int(d["ACTOR_STATE_OFFSET"]),
                                        wa + int(d["ACTOR_PREV_STATE_OFFSET"]),
                                    ])
                                    if qi or qc or ws == 8:
                                        # Hundreds of identical per-second read-only
                                        # traces hid useful crash/reconnect messages.
                                        status = (int(qi), int(qc), int(qv), int(wf),
                                                  int(ws), int(wp), approach_wind_source)
                                        if status != last_quarry_status or now - last_quarry_report_at >= 30.0:
                                            last_quarry_status = status
                                            last_quarry_report_at = now
                                            self._log_threadsafe(
                                                f"FT QUARRY TRACE: button 0x0244 idx={qi}/{qc} avail={qv}; "
                                                f"C540 0x0245 flags=0x{wf:08X} state={ws}/{wp}; "
                                                f"wind_owner={('0x%04X' % approach_wind_source) if approach_wind_source is not None else 'none'}",
                                                "info",
                                            )
                            except Exception:
                                pass

                        if (
                            not return_wind_guard
                            and best is not None
                            and best_dist is not None
                            and best_dist <= source_near_radius
                        ):
                            is_new_arm = near_route is None or str(near_route.get("id", "")) != str(best.get("id", ""))
                            source_key = int(best.get("source_key", -1))
                            if is_new_arm:
                                self._log_threadsafe(
                                    f"FT TRUE CLEANROOM ARM: {best.get('label', best.get('id','?'))} | distance source={best_dist:.2f}m",
                                    "ok",
                                )
                            # V0.9.20: proximity only proposes a candidate. It cannot
                            # permanently own the room. Confirm a close, stable approach
                            # before priming the corresponding *local* Nativ C540.
                            # The actual destination discovery chain remains read-only.
                            if best_dist <= wind_confirm_radius:
                                if pending_wind_source != source_key:
                                    pending_wind_source = source_key
                                    pending_wind_since = now
                                if (not bool(d.get("FAST_TRAVEL_FT01_BAT_VALIDATED", True))
                                        and bool(d.get("FAST_TRAVEL_LOCAL_SOURCE_WIND_TEST", False))
                                        and approach_wind_source != source_key
                                        and now - pending_wind_since >= wind_confirm_seconds
                                        and now - last_wind_attempt >= wind_retry_seconds):
                                    previous_source = approach_wind_source
                                    last_wind_attempt = now
                                    self._ap_ft_activate_nativ_source_winds(
                                        pine, keyed, d, only_source=source_key
                                    )
                                    # Record the source only when the underlying C540
                                    # confirms its active state; failed arms stay retryable.
                                    wind_key = int(best.get("wind_key", -1))
                                    # The wind helper maintains confirmed runtime tokens.
                                    if any(token[0] == source_key for token in self._ap_ft_wind_triggered):
                                        approach_wind_source = source_key
                                        if previous_source is not None and previous_source != source_key:
                                            self._log_threadsafe(
                                                f"FT WIND SWITCH: 0x{previous_source:04X} -> 0x{source_key:04X}; no remote writes.", "info"
                                            )
                                    else:
                                        self._log_threadsafe(
                                            f"FT WIND ARM PENDING: 0x{source_key:04X}; waiting for local C540 confirmation.", "warn"
                                        )
                            else:
                                pending_wind_source = None
                                pending_wind_since = 0.0
                            near_route = best
                            near_time = now

                        if best is None or best_dist is None or best_dist > source_near_radius:
                            pending_wind_source = None
                            pending_wind_since = 0.0

                elif saw_nativ and last_nativ:
                    # A real unload, unlike a 120s watchdog, ends room continuity.
                    self._ap_ft_cleanroom_continuation = None
                    recent = near_route is not None and (now - near_time <= source_arm_window)
                    if recent:
                        self._ap_ft_session_departed = True
                        route = near_route
                        self._log_threadsafe(
                            f"FT TRUE CLEANROOM DEPARTURE: {route.get('label', route.get('id','?'))}. Running V4 stable BAT-style critical loop.",
                            "ok",
                        )
                        if bool(d.get("FAST_TRAVEL_ACCESS_ONLY_TEST", True)):
                            self._log_threadsafe(
                                "FT ACCESS-ONLY: Nativ room unloaded; vanilla owns the transition. No bridge/target/chain writes.",
                                "ok",
                            )
                            return
                        ok, reason = self._ap_ft_blocking_bridge(pine, route, d, ultratight=True)
                        self._log_threadsafe(
                            f"FT TRUE CLEANROOM OFF: {'SUCCESS' if ok else 'FAIL'} | {reason}. Deferred Launcher work may resume.",
                            "ok" if ok else "error",
                        )
                        return
                    self._ap_ft_session_departed = True
                    self._log_threadsafe(
                        "FT TRUE CLEANROOM OFF: Nativ FT room unloaded without a recent AP-button arm.",
                        "warn",
                    )
                    return

                last_nativ = nativ_loaded
                # Keep the local FT state (including last_nativ, which is vital
                # for departure recognition), then return control to PINE's
                # heartbeat. This is not a return from the FT transaction.
                yield

            # Re-entering after an AFK watchdog must NOT invent a return.
            # Preserve both TRUE and FALSE guards; a genuine landing is still
            # blocked until Kya walks beyond the release radius.
            if (saw_nativ and last_nativ and not self._ap_ft_session_departed
                    and return_wind_guard is not None
                    and self._ap_stream_last_valid_generation is not None):
                self._ap_ft_cleanroom_continuation = (
                    self._ap_stream_last_valid_generation, bool(return_wind_guard)
                )
                self._log_threadsafe(
                    "FT WATCHDOG CONTINUITY: same Nativ room; retained arrival guard "
                    f"({'ON' if return_wind_guard else 'OFF'}); no fake landing on next scan.",
                    "info",
                )
            self._log_threadsafe(
                "FT TRUE CLEANROOM OFF: 120s debug watchdog reached without a completed departure.",
                "warn",
            )
        finally:
            if self._ap_ft_session_departed:
                self._ap_stream_hold = True
                self._ap_stream_departure_generation = self._ap_stream_last_valid_generation
                self._ap_stream_candidate = None
                self._ap_stream_ready_since = 0.0
                self._log_threadsafe(
                    "FT STREAM GUARD ON: Nativ FT departure; suspending all Launcher memory writers until destination actor list stabilizes.",
                    "warn",
                )
            self._ap_ft_cleanroom_active = False
            self._ap_ft_sanctuary_active = False

    def _ap_ft_entry_only_bridge(self, pine: PineClient, route: dict, d: dict) -> tuple[bool, str]:
        """V0.9.11 beta: use the FT source only to stream the destination, then
        deliberately let vanilla reject the inactive destination pad and place
        Kya at the zone's normal entry/fallback spawn.

        Critical differences from V0.9.9:
          * NEVER write destination active/available/footer/mask/index/state;
          * only release the destination Master 5 -> 6;
          * a landing close to FT01 is explicitly NOT success;
          * wait for a stable landing far from FT01 while the destination scene
            remains loaded;
          * do not activate FT01 after arrival. The player discovers FT01
            naturally, and that real 0->1 activation becomes the AP check.

        This intentionally trades full Fast Travel semantics for a small,
        deterministic beta surface and avoids the return-loop/corruption path.
        """
        label = str(route.get("label", route.get("id", "?")))
        target_key = int(route["target_key"])
        master_key = int(route["master_key"])
        ft_vt = int(d["FAST_TRAVEL_VTABLE"])
        master_vt = int(d["MASTER_EVENT_VTABLE"])
        state_off = int(d["ACTOR_STATE_OFFSET"])
        prev_off = int(d["ACTOR_PREV_STATE_OFFSET"])
        poll = float(d.get("FAST_TRAVEL_ENTRY_ONLY_POLL_SECONDS", 0.006))
        min_entry_distance = float(route.get(
            "entry_fallback_min_distance",
            d.get("FAST_TRAVEL_ENTRY_FALLBACK_MIN_DISTANCE", 20.0),
        ))

        self._log_threadsafe(
            f"FT ENTRY-FALLBACK START: {label} | target=0x{target_key:04X} Master=0x{master_key:04X}; "
            "destination FT stays undiscovered; only remote +0x2A0 bootstrap activation may be firewalled.",
            "info",
        )

        def resolve_pair():
            try:
                keyed = self._ap_ft_scan_keyed(pine, d, {ft_vt, master_vt})
            except Exception:
                return None, None
            trow = keyed.get(target_key)
            mrow = keyed.get(master_key)
            if not trow or not mrow:
                return None, None
            if int(trow[1]) != ft_vt or int(mrow[1]) != master_vt:
                return None, None
            return int(trow[0]), int(mrow[0])

        # Wait for the destination scene to stream.  No target write occurs here.
        target_actor = master_actor = None
        deadline = time.monotonic() + float(d.get("FAST_TRAVEL_ENTRY_ONLY_PAIR_TIMEOUT", 30.0))
        while time.monotonic() < deadline and not self._camera_stop_event.is_set():
            target_actor, master_actor = resolve_pair()
            if target_actor and master_actor:
                break
            time.sleep(poll)
        if not target_actor or not master_actor:
            return False, "entry-fallback target/Master not found"

        # Arm the destination firewall BEFORE releasing Master 5. The regular
        # watcher is paused by the cleanroom during this bridge, so without this
        # early guard vanilla can mark FT01 discovered before the watcher resumes.
        if bool(d.get("FAST_TRAVEL_DETECTOR_HANDOFF", True)):
            self._ap_ft_detector_guard_targets.add(int(target_key))
            self._ap_ft_detector_remote_logged.discard(int(target_key))
            self._ap_ft_detector_near_wait_logged.discard(int(target_key))

        self._ap_ft_ensure_return_mana(pine, d)
        tp = self._ap_ft_actor_pos(pine, target_actor, d)
        self._log_threadsafe(
            f"FT ENTRY-FALLBACK WINDOW: {label} target=0x{target_actor:08X} pos={tp} Master=0x{master_actor:08X}.",
            "info",
        )

        # The one write we keep from the proven bridge: release the destination
        # Master at state 5.  The FT endpoint itself is intentionally inactive so
        # vanilla has to choose its normal entry/fallback spawn.
        released = False
        last_state = None
        deadline = time.monotonic() + float(d.get("FAST_TRAVEL_ENTRY_ONLY_MASTER_TIMEOUT", 15.0))
        while time.monotonic() < deadline and not self._camera_stop_event.is_set():
            ta, ma = resolve_pair()
            if ta and ma:
                target_actor, master_actor = ta, ma
            if not target_actor or not master_actor:
                time.sleep(poll)
                continue
            try:
                state, prev = [int(x) for x in pine.read32_many([
                    master_actor + state_off,
                    master_actor + prev_off,
                ])]
            except Exception:
                time.sleep(poll)
                continue

            if state != last_state:
                last_state = state
                self._log_threadsafe(
                    f"FT ENTRY-FALLBACK Master 0x{master_key:04X}: state={state} prev=0x{prev:08X}.",
                    "info",
                )

            if state == 5:
                self._ap_ft_ensure_return_mana(pine, d)
                state_addr = master_actor + state_off
                # A couple of identical writes are enough to survive the same-frame
                # vanilla state update without continuously owning the structure.
                pine.write32(state_addr, 6)
                time.sleep(0.004)
                pine.write32(state_addr, 6)
                verified = int(pine.read32(state_addr))
                released = True
                self._log_threadsafe(
                    f">>> FT ENTRY-FALLBACK MASTER 5->0x{verified:08X}: {label}. "
                    "FT01 discovery chain untouched; waiting for normal zone-entry fallback. <<<",
                    "ok",
                )
                break

            if state in (6, 8):
                released = True
                self._log_threadsafe(
                    f"FT ENTRY-FALLBACK Master already {state}; waiting for normal entry.",
                    "warn",
                )
                break
            time.sleep(poll)

        if not released:
            return False, f"entry-fallback Master 5 not observed (last={last_state})"

        stable_required = float(d.get("FAST_TRAVEL_ENTRY_ONLY_STABLE_SECONDS", 0.80))
        landing_timeout = float(d.get("FAST_TRAVEL_ENTRY_FALLBACK_TIMEOUT", 18.0))
        move_eps = float(d.get("FAST_TRAVEL_ENTRY_ONLY_MOVE_EPSILON", 0.65))
        last_pos = None
        stable_since = None
        landing_pos = None
        landing_distance = None
        near_pad_logged = False
        pair_missing_since = None
        deadline = time.monotonic() + landing_timeout

        while time.monotonic() < deadline and not self._camera_stop_event.is_set():
            # Destination pair remaining live is our cheap proof that we did not
            # simply bounce all the way back to Nativs City.
            ta, ma = resolve_pair()
            if ta and ma:
                target_actor, master_actor = ta, ma
                pair_missing_since = None
            else:
                if pair_missing_since is None:
                    pair_missing_since = time.monotonic()
                elif time.monotonic() - pair_missing_since >= 0.75:
                    return False, "entry-fallback destination unloaded / bounced back before normal entry"

            kya = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
            pos = self._ap_ft_actor_pos(pine, kya, d) if self._ap_valid_pointer(kya) else None
            if pos is None:
                stable_since = None
                last_pos = None
                time.sleep(0.03)
                continue

            try:
                dist = self._ap_ft_arrival_distance(pine, int(target_actor), d)
            except Exception:
                dist = None

            # During the synchronous bridge the normal watcher cannot run. Keep
            # only +0x2A0 off while Kya is not physically at the destination pad.
            # Never touch +0x2A4/mask/index/state/C540 here.
            if (
                bool(d.get("FAST_TRAVEL_DETECTOR_HANDOFF", True))
                and (dist is None or float(dist) > float(d.get("FAST_TRAVEL_LOCAL_DISCOVERY_RADIUS", 5.5)))
            ):
                self._ap_ft_detector_hold_remote_active_off(
                    pine, int(target_actor), int(target_key), d, distance=dist
                )

            # The V0.9.9 bug is visible in the log: 1.26m from FT01 was accepted
            # as an "entry" and then we activated that FT, immediately creating a
            # return loop.  Being near the pad is now explicitly a transient state.
            if dist is not None and dist < min_entry_distance:
                if not near_pad_logged:
                    near_pad_logged = True
                    self._log_threadsafe(
                        f"FT ENTRY-FALLBACK transient pad landing: {label} distance={dist:.3f}m < "
                        f"{min_entry_distance:.1f}m; leaving endpoint untouched and waiting for vanilla fallback.",
                        "warn",
                    )
                stable_since = None
                last_pos = pos
                time.sleep(0.05)
                continue

            if last_pos is None:
                last_pos = pos
                stable_since = time.monotonic()
                time.sleep(0.05)
                continue
            moved = ((pos[0]-last_pos[0])**2 + (pos[1]-last_pos[1])**2 + (pos[2]-last_pos[2])**2) ** 0.5
            last_pos = pos
            if moved > move_eps:
                stable_since = time.monotonic()
            elif stable_since is None:
                stable_since = time.monotonic()

            if stable_since is not None and time.monotonic() - stable_since >= stable_required:
                landing_pos = pos
                landing_distance = dist
                break
            time.sleep(0.05)

        if landing_pos is None:
            return False, "entry-fallback normal zone entry never stabilized"

        self._log_threadsafe(
            f"FT ENTRY-FALLBACK LANDING: {label} pos=({landing_pos[0]:.3f},{landing_pos[1]:.3f},{landing_pos[2]:.3f}) "
            f"distance_to_FT01={landing_distance if landing_distance is not None else 'N/A'}; normal-entry fallback accepted.",
            "ok",
        )
        self._log_threadsafe(
            f"FT ENTRY-FALLBACK LOCAL FT01 LEFT VANILLA: {label}; no C540/state/active/available write. "
            "The real local activation will award the AP check.",
            "info",
        )
        if bool(d.get("FAST_TRAVEL_DETECTOR_HANDOFF", True)):
            self._log_threadsafe(
                f"FT DISCOVERY DETECTOR ARMED: {label} target 0x{target_key:04X}; "
                f"Launcher never sets destination active=1; remote bootstrap active is firewalled with +0x2A4 untouched until Kya is within "
                f"{float(d.get('FAST_TRAVEL_LOCAL_DISCOVERY_RADIUS', 5.5)):.1f}m, then target/C540 chain is read-only detector authority.",
                "info",
            )
        self._ap_ft_ensure_return_mana(pine, d)
        return True, (
            f"normal-entry fallback stable; local FT01 untouched; distance_to_target={landing_distance}"
        )

    def _ap_ft_blocking_bridge(self, pine: PineClient, route: dict, d: dict, *, ultratight: bool = True) -> tuple[bool, str]:
        if bool(d.get("FAST_TRAVEL_ENTRY_ONLY_BETA", False)):
            return self._ap_ft_entry_only_bridge(pine, route, d)

        """V0.9.8 destination bridge: V4 stable-target transaction mirrored from the working BAT.

        V0.8.43 proved that immediate Master 5->6 can work, but the second trip
        could still fall back to the wooden elevator.  The older V4 traces show
        why: vanilla can rewrite the destination FT while Master is in state 5.
        The robust recipe is therefore:

          AP-selected source -> temporary BAT legacy source preflight ->
          canonical target profile -> catch Master 5 -> keep target canonical
          for 0.20 s continuously -> ensure real mana -> write Master 5->6 ->
          hold only active/available/footer -> require vanilla Master 8 + arrival.

        No SafeWarp, no target-state write, no C540 forcing.
        """
        label = str(route.get("label", route.get("id", "?")))
        target_key = int(route["target_key"])
        master_key = int(route["master_key"])
        source_key = int(route.get("source_key", 0))
        ft_vt = int(d["FAST_TRAVEL_VTABLE"])
        master_vt = int(d["MASTER_EVENT_VTABLE"])
        state_off = int(d["ACTOR_STATE_OFFSET"])
        prev_off = int(d["ACTOR_PREV_STATE_OFFSET"])
        general_poll = 0.005
        stable_seconds = float(d.get("FAST_TRAVEL_TARGET_STABLE_SECONDS", 0.20))

        explicit_masks = {
            int(k): int(v)
            for k, v in d.get("FAST_TRAVEL_TARGET_LEGACY_MASKS", {}).items()
        }
        source_masks = {
            int(k): int(v)
            for k, v in d.get("NATIV_FAST_TRAVEL_LEGACY_MASKS", {}).items()
        }
        canonical_mask = explicit_masks.get(target_key, source_masks.get(source_key, 0xFFFFFFF0)) & 0xFFFFFFFF

        self._log_threadsafe(
            f"FT V4 STABLE START: {label} | target=0x{target_key:04X} Master=0x{master_key:04X} canonicalMask=0x{canonical_mask:08X}.",
            "info",
        )

        def read_target_profile(target_actor: int) -> tuple[int, int, int, int, int, bool]:
            idx, idx_copy, mask, active, avail = pine.read32_many([
                target_actor + int(d["FAST_TRAVEL_INDEX_OFFSET"]),
                target_actor + int(d["FAST_TRAVEL_INDEX_COPY_OFFSET"]),
                target_actor + int(d["FAST_TRAVEL_MASK_OFFSET"]),
                target_actor + int(d["FAST_TRAVEL_ACTIVE_OFFSET"]),
                target_actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]),
            ])
            footer = self._ap_ft_footer_addr(pine, target_actor, d)
            footer_ready = False
            if footer is not None:
                footer_ready = bool(int(pine.read32(footer)) & int(d["FAST_TRAVEL_ROUTE_READY_FLAG"]))
            return (
                int(idx), int(idx_copy), int(mask) & 0xFFFFFFFF,
                int(active), int(avail), footer_ready,
            )

        def profile_is_canonical(profile: tuple[int, int, int, int, int, bool]) -> bool:
            return (
                profile[0] == 0 and profile[1] == 0
                and profile[2] == canonical_mask
                and profile[3] == 1 and profile[4] == 1 and profile[5]
            )

        def patch_target_canonical(target_actor: int) -> tuple[int, int, int, int, int, bool]:
            # V4 canonical endpoint profile.  Index/copy are destination-local and
            # were 0/0 in the successful traces; the mask is the legacy zone/FT
            # profile, *not* the one-bit Nativ source-button mask.
            pine.write32(target_actor + int(d["FAST_TRAVEL_INDEX_OFFSET"]), 0)
            pine.write32(target_actor + int(d["FAST_TRAVEL_INDEX_COPY_OFFSET"]), 0)
            pine.write32(target_actor + int(d["FAST_TRAVEL_MASK_OFFSET"]), canonical_mask)
            pine.write32(target_actor + int(d["FAST_TRAVEL_ACTIVE_OFFSET"]), 1)
            pine.write32(target_actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]), 1)
            footer = self._ap_ft_footer_addr(pine, target_actor, d)
            if footer is not None:
                old = int(pine.read32(footer))
                pine.write32(footer, old | int(d["FAST_TRAVEL_ROUTE_READY_FLAG"]))
            return read_target_profile(target_actor)

        def hold_target_endpoint_only(target_actor: int) -> None:
            """Exact post-5->6 primitive used by the working BAT.

            Once Master=6 is written, vanilla must regain ownership of target
            index/copy/mask so it can finish camera, button and wind routing.
            We keep only active/available/footer alive until Master reaches 8.
            """
            pine.write32(target_actor + int(d["FAST_TRAVEL_ACTIVE_OFFSET"]), 1)
            pine.write32(target_actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]), 1)
            footer = self._ap_ft_footer_addr(pine, target_actor, d)
            if footer is not None:
                old = int(pine.read32(footer))
                pine.write32(footer, old | int(d["FAST_TRAVEL_ROUTE_READY_FLAG"]))

        # V0.9.5: runtime Actor addresses are ephemeral.  Persistent keys are the
        # identity; (Actor Manager, active-list, count) is the current generation.
        # A FT transition can replace that generation *while this blocking bridge
        # is still running*, so never trust one target/Master pointer for the
        # whole transaction.
        def manager_generation() -> tuple[int, int, int] | None:
            try:
                manager = int(pine.read32(int(d["ADDR_ACTOR_MANAGER_GLOBAL"])))
                if not self._ap_valid_pointer(manager):
                    return None
                active, count = pine.read32_many([
                    manager + int(d["ACTOR_MANAGER_ACTIVE_LIST_OFFSET"]),
                    manager + int(d["ACTOR_MANAGER_ACTIVE_COUNT_OFFSET"]),
                ])
                active = int(active); count = int(count)
                if not self._ap_valid_pointer(active) or count <= 0 or count > int(d["ACTOR_MANAGER_MAX_ACTIVE"]):
                    return None
                return manager, active, count
            except Exception:
                return None

        def actor_matches(actor: int | None, key: int, expected_vt: int) -> bool:
            if not actor or not self._ap_valid_pointer(int(actor)):
                return False
            try:
                vt, desc = pine.read32_many([
                    int(actor),
                    int(actor) + int(d["FAST_TRAVEL_DESCRIPTOR_OFFSET"]),
                ])
                if int(vt) != int(expected_vt) or not self._ap_valid_pointer(int(desc)):
                    return False
                actual_key = int(pine.read32(int(desc) + int(d["FAST_TRAVEL_KEY_OFFSET"]))) & 0xFFFFFFFF
                return actual_key == (int(key) & 0xFFFFFFFF)
            except Exception:
                return False

        def resolve_current_pair() -> tuple[int | None, int | None, tuple[int, int, int] | None]:
            # Require the Actor-Manager generation to be the same before/after
            # the keyed scan so target + Master always belong to one snapshot.
            before = manager_generation()
            if before is None:
                return None, None, None
            try:
                keyed_now = self._ap_ft_scan_keyed(pine, d, {ft_vt, master_vt})
            except Exception:
                return None, None, None
            after = manager_generation()
            if after is None or after != before:
                return None, None, after
            trow = keyed_now.get(target_key)
            mrow = keyed_now.get(master_key)
            if not trow or int(trow[1]) != ft_vt or not mrow or int(mrow[1]) != master_vt:
                return None, None, after
            ta = int(trow[0]); ma = int(mrow[0])
            if not actor_matches(ta, target_key, ft_vt) or not actor_matches(ma, master_key, master_vt):
                return None, None, after
            return ta, ma, after

        # Phase 1: wait for the destination target + Master to exist.
        start_time = time.monotonic()
        target_actor = None
        master_actor = None
        bound_generation = None
        while time.monotonic() - start_time < 90.0 and not self._camera_stop_event.is_set():
            target_actor, master_actor, bound_generation = resolve_current_pair()
            if target_actor and master_actor and bound_generation is not None:
                # BAT order matters: make the real runtime mana usable BEFORE we
                # start forcing the destination endpoint / wind chain.  Doing it
                # only at Master=5 can be too late if vanilla already sampled mana.
                self._ap_ft_ensure_return_mana(pine, d)
                try:
                    patch_target_canonical(target_actor)
                except Exception:
                    pass
                break
            time.sleep(general_poll)

        if not target_actor or not master_actor or bound_generation is None:
            return False, "V4 target/Master not found"

        tp = self._ap_ft_actor_pos(pine, target_actor, d)
        mp = self._ap_ft_actor_pos(pine, master_actor, d)
        self._log_threadsafe(
            f"FT V4 WINDOW: target 0x{target_key:04X}=0x{target_actor:08X} pos={tp} | "
            f"Master 0x{master_key:04X}=0x{master_actor:08X} pos={mp} | "
            f"generation manager=0x{bound_generation[0]:08X} list=0x{bound_generation[1]:08X} count={bound_generation[2]}.",
            "info",
        )

        state_addr = master_actor + state_off
        prev_addr = master_actor + prev_off
        critical_start = time.monotonic()
        last_state = None
        loops = 0
        caught = False
        stable_since = None
        stable_reads = 0
        vanilla_resets = 0
        last_profile = None
        last_vanilla_mask = None
        next_generation_check = 0.0
        rebinds = 0

        # Phase 2: catch Master=5, then require a continuously canonical target
        # for 0.20 s.  Any vanilla rewrite resets the timer and is repaired.
        while time.monotonic() - critical_start < 8.0 and not self._camera_stop_event.is_set():
            loops += 1
            now_critical = time.monotonic()
            if now_critical >= next_generation_check:
                next_generation_check = now_critical + 0.020
                current_generation = manager_generation()
                identity_ok = actor_matches(target_actor, target_key, ft_vt) and actor_matches(master_actor, master_key, master_vt)
                if current_generation != bound_generation or not identity_ok:
                    old_target = int(target_actor or 0)
                    old_master = int(master_actor or 0)
                    old_generation = bound_generation
                    new_target, new_master, new_generation = resolve_current_pair()
                    if not new_target or not new_master or new_generation is None:
                        stable_since = None
                        stable_reads = 0
                        time.sleep(general_poll)
                        continue
                    target_actor = new_target
                    master_actor = new_master
                    bound_generation = new_generation
                    state_addr = master_actor + state_off
                    prev_addr = master_actor + prev_off
                    stable_since = None
                    stable_reads = 0
                    last_state = None
                    rebinds += 1
                    self._log_threadsafe(
                        f"FT ACTOR REBIND #{rebinds}: {label} | "
                        f"generation {old_generation}->{bound_generation} | "
                        f"target 0x{old_target:08X}->0x{target_actor:08X} | "
                        f"Master 0x{old_master:08X}->0x{master_actor:08X}.",
                        "warn",
                    )
                    try:
                        patch_target_canonical(target_actor)
                    except Exception:
                        pass
                    continue
            try:
                # Read the target *before* repairing it.  This is important: it
                # lets us see vanilla's reset and restart the 0.20 s timer instead
                # of hiding the reset with our own write first.
                profile_before = read_target_profile(target_actor)
                state, prev = pine.read32_many([state_addr, prev_addr])
            except Exception:
                continue
            state = int(state); prev = int(prev)

            if state != last_state:
                self._log_threadsafe(
                    f"FT V4 Master 0x{master_key:04X}: state={state} prev=0x{prev:08X} loop={loops}.",
                    "info",
                )
                last_state = state

            if state != 5:
                stable_since = None
                stable_reads = 0
                try:
                    patch_target_canonical(target_actor)
                except Exception:
                    pass
                continue

            if not caught:
                caught = True
                self._log_threadsafe(
                    f">>> FT V4 MASTER 5 CAUGHT: {label} - TARGET STABILIZATION {stable_seconds:.2f}s <<<",
                    "ok",
                )

            if not profile_is_canonical(profile_before):
                vanilla_resets += 1
                stable_since = None
                stable_reads = 0
                # Preserve the last mask vanilla itself tried to install. The
                # full legacy mask (e.g. FFFFFFF0) is needed only during the
                # bridge; leaving it behind can visually/physically expose peer
                # Fast Travels in the destination zone.
                candidate_mask = int(profile_before[2]) & 0xFFFFFFFF
                if (candidate_mask & 0xFFFF0000) == 0xFFFF0000 and candidate_mask != canonical_mask:
                    last_vanilla_mask = candidate_mask
                if profile_before != last_profile:
                    self._log_threadsafe(
                        f"FT V4 TARGET VANILLA RESET #{vanilla_resets}: profile={profile_before}; restoring canonical mask 0x{canonical_mask:08X}.",
                        "warn",
                    )
                    last_profile = profile_before
                try:
                    repaired = patch_target_canonical(target_actor)
                    if profile_is_canonical(repaired):
                        self._log_threadsafe(
                            "FT V4 TARGET restored; stable timer restarted.",
                            "info",
                        )
                except Exception:
                    pass
                continue

            if stable_since is None:
                stable_since = time.monotonic()
                stable_reads = 1
                self._log_threadsafe(
                    f"FT V4 TARGET READY during Master 5 - stabilizing {stable_seconds:.2f}s...",
                    "info",
                )
            else:
                stable_reads += 1

            if time.monotonic() - stable_since >= stable_seconds:
                # One final no-write verification closes the race between the
                # last stable read and Master 5->6.
                try:
                    final_profile = read_target_profile(target_actor)
                except Exception:
                    final_profile = None
                if final_profile is None or not profile_is_canonical(final_profile):
                    vanilla_resets += 1
                    stable_since = None
                    stable_reads = 0
                    last_profile = final_profile
                    try:
                        patch_target_canonical(target_actor)
                    except Exception:
                        pass
                    continue

                # Last-moment ownership check.  If streaming replaced either
                # actor between the stable read and the state write, rebind and
                # rebuild the 0.20 s proof instead of writing to a stale object.
                current_generation = manager_generation()
                if (
                    current_generation != bound_generation
                    or not actor_matches(target_actor, target_key, ft_vt)
                    or not actor_matches(master_actor, master_key, master_vt)
                ):
                    new_target, new_master, new_generation = resolve_current_pair()
                    stable_since = None
                    stable_reads = 0
                    if new_target and new_master and new_generation is not None:
                        old_target = int(target_actor or 0); old_master = int(master_actor or 0)
                        target_actor = new_target; master_actor = new_master; bound_generation = new_generation
                        state_addr = master_actor + state_off; prev_addr = master_actor + prev_off
                        rebinds += 1
                        self._log_threadsafe(
                            f"FT ACTOR REBIND #{rebinds} BEFORE 5->6: {label} | "
                            f"target 0x{old_target:08X}->0x{target_actor:08X} | "
                            f"Master 0x{old_master:08X}->0x{master_actor:08X}.",
                            "warn",
                        )
                        try:
                            patch_target_canonical(target_actor)
                        except Exception:
                            pass
                    continue

                self._log_threadsafe(
                    f">>> FT V4 TARGET STABLE ({stable_reads} reads, {time.monotonic()-stable_since:.3f}s, resets={vanilla_resets}, rebinds={rebinds}) - MANA GUARD + MASTER 5->6 <<<",
                    "ok",
                )
                self._ap_ft_ensure_return_mana(pine, d)
                for _ in range(4):
                    pine.write32(state_addr, 6)
                break
            # Deliberately no sleep: the V4 trace made ~240-250 reads in 0.20 s.

        if not caught:
            return False, f"V4 Master state 5 not caught (last={last_state}, loops={loops})"
        if stable_since is None or time.monotonic() - stable_since < stable_seconds:
            return False, f"V4 target never stayed canonical for {stable_seconds:.2f}s (resets={vanilla_resets})"

        # Phase 3: mirror the working BAT exactly.  After Master 5->6, stop
        # writing index/copy/mask.  Keep ONLY active/available/footer ready while
        # vanilla completes the native chain to Master=8.  This is the critical
        # distinction between a physically-near arrival and a fully initialized
        # return wind/camera/button state.
        arrival_timeout = float(route.get("arrival_timeout", 8.0))
        deadline = time.monotonic() + arrival_timeout
        final_state = None
        final_prev = None
        final_loops = 0
        near_since = None
        native_tail_stable = float(d.get("FAST_TRAVEL_NATIVE_TAIL_STABLE_SECONDS", 0.60))
        arrival_radius = float(route.get("arrival_radius", d.get("FAST_TRAVEL_ARRIVAL_RADIUS", 7.0)))
        completed_by = None
        master8_wait_logged = False
        require_master8 = bool(route.get("require_master8", True))
        tail_hold_endpoint = bool(route.get("tail_hold_endpoint", True))
        tail_hold_logged = False
        fallback_dwell = float(route.get(
            "native_tail_fallback_dwell_seconds",
            d.get("FAST_TRAVEL_NATIVE_TAIL_FALLBACK_DWELL_SECONDS", 2.0),
        ))
        next_tail_generation_check = 0.0
        while time.monotonic() < deadline and not self._camera_stop_event.is_set():
            final_loops += 1
            now_tail_probe = time.monotonic()
            if now_tail_probe >= next_tail_generation_check:
                next_tail_generation_check = now_tail_probe + 0.020
                current_generation = manager_generation()
                identity_ok = actor_matches(target_actor, target_key, ft_vt) and actor_matches(master_actor, master_key, master_vt)
                if current_generation != bound_generation or not identity_ok:
                    old_target = int(target_actor or 0)
                    old_master = int(master_actor or 0)
                    old_generation = bound_generation
                    new_target, new_master, new_generation = resolve_current_pair()
                    if not new_target or not new_master or new_generation is None:
                        final_state = None; final_prev = None
                        near_since = None
                        time.sleep(0.002)
                        continue
                    target_actor = new_target
                    master_actor = new_master
                    bound_generation = new_generation
                    state_addr = master_actor + state_off
                    prev_addr = master_actor + prev_off
                    near_since = None
                    rebinds += 1
                    self._log_threadsafe(
                        f"FT ACTOR REBIND #{rebinds} DURING TAIL: {label} | "
                        f"generation {old_generation}->{bound_generation} | "
                        f"target 0x{old_target:08X}->0x{target_actor:08X} | "
                        f"Master 0x{old_master:08X}->0x{master_actor:08X}.",
                        "warn",
                    )
            try:
                if tail_hold_endpoint:
                    hold_target_endpoint_only(target_actor)
                    if not tail_hold_logged:
                        tail_hold_logged = True
                        self._log_threadsafe(
                            f"FT V4 BAT TAIL HOLD: {label} keeps only active/available/footer ready; vanilla owns index/copy/mask until Master=8.",
                            "info",
                        )
                final_state, final_prev = pine.read32_many([state_addr, prev_addr])
                final_state = int(final_state); final_prev = int(final_prev)
            except Exception:
                final_state = None; final_prev = None
            distance = self._ap_ft_arrival_distance(pine, target_actor, d)
            now_tail = time.monotonic()

            # Master=8 is only a protocol milestone, not proof that Kya has
            # physically reached the correct Fast Travel pad. Hunters FT01 proved
            # this: Master hit 8 at ~7.96 m while Kya was still at the wooden
            # elevator. Keep the cleanroom alive until the route-specific physical
            # arrival radius is actually reached and stable.
            if final_state == 8 and distance is not None and distance > arrival_radius and not master8_wait_logged:
                master8_wait_logged = True
                self._log_threadsafe(
                    f"FT V4 MASTER 8 EARLY: {label} distance={distance:.3f}m > arrival radius={arrival_radius:.3f}m; waiting final vanilla placement.",
                    "warn",
                )

            if distance is not None and distance <= arrival_radius:
                if near_since is None:
                    near_since = now_tail
                else:
                    dwell = now_tail - near_since
                    # Prefer the complete vanilla protocol.  The previous 0.60 s
                    # Master=6 early-exit was enough to place Kya near a target,
                    # but not always enough to finish wind/button/camera routing.
                    if final_state == 8 and dwell >= native_tail_stable:
                        completed_by = f"Master=8 + physical dwell {dwell:.3f}s"
                        break
                    # Production AP must not call Master=6 a success merely because
                    # Kya happens to be physically near the pad: that exact state
                    # produced missing winds / half-initialized buttons.  Retain the
                    # old fallback only as an opt-in diagnostic route flag.
                    if (not require_master8) and dwell >= fallback_dwell:
                        completed_by = f"physical fallback dwell {dwell:.3f}s (Master={final_state})"
                        break
            else:
                near_since = None

            time.sleep(0.005)

        distance = self._ap_ft_arrival_distance(pine, target_actor, d)
        success = bool(
            distance is not None and distance <= arrival_radius and completed_by is not None
        )
        self._log_threadsafe(
            f"FT V4 RESULT: {label} | Master={final_state} prev=0x{int(final_prev or 0):08X} | "
            f"distance={distance if distance is not None else 'N/A'} | critical_loops={loops} "
            f"stable_reads={stable_reads} resets={vanilla_resets} rebinds={rebinds} final_loops={final_loops} "
            f"arrival_radius={arrival_radius:.3f}m native_tail={completed_by or 'TIMEOUT'}.",
            "ok" if success else "error",
        )

        # V0.9.3: preserve V0.9.1 cleanup everywhere. Quarry routes alone
        # may override the transient vanilla mask after CONFIRMED success, because
        # Quarry FT02 exposed a stray final pad with vanilla mask 0xFFFFFFF6.
        # Only the mask is touched; active/available/footer remain vanilla-owned.
        cleanup_mask = None
        cleanup_reason = "last vanilla profile"
        if success and route.get("destination_cleanup_mask") is not None:
            cleanup_mask = int(route["destination_cleanup_mask"]) & 0xFFFFFFFF
            cleanup_reason = "AP Quarry single-route mask"
        elif success and last_vanilla_mask is not None:
            cleanup_mask = int(last_vanilla_mask) & 0xFFFFFFFF
        if cleanup_mask is not None:
            try:
                pine.write32(target_actor + int(d["FAST_TRAVEL_MASK_OFFSET"]), cleanup_mask)
                self._log_threadsafe(
                    f"FT DESTINATION CLEANUP: target 0x{target_key:04X} mask 0x{canonical_mask:08X}->0x{cleanup_mask:08X} ({cleanup_reason}).",
                    "info",
                )
            except Exception as exc:
                self._log_threadsafe(f"FT DESTINATION CLEANUP warning: {exc}", "warn")

        if success:
            # Keep the proven bridge zero-mana guard, but post-arrival recovery
            # itself is stationary + zero-only. This also covers a player who
            # immediately uses a local destination Fast Travel.
            self._ap_ft_ensure_return_mana(pine, d)
            try:
                self._ap_ft_arm_mana_stall_rescue(pine, d, str(label), time.monotonic())
            except Exception:
                pass
            self._ap_ft_queue_arrival_check(route, d)
            return True, f"V4 stable arrival {distance:.3f}m (Master={final_state}, {completed_by})"

        # Focused diagnostics for routes that complete the Master protocol but
        # still leave Kya at a vanilla wooden-elevator arrival. No extra writes.
        try:
            vals = [int(x) for x in pine.read32_many([
                target_actor + int(d["ACTOR_STATE_OFFSET"]),
                target_actor + int(d["ACTOR_PREV_STATE_OFFSET"]),
                target_actor + int(d["FAST_TRAVEL_MASK_OFFSET"]),
                target_actor + int(d["FAST_TRAVEL_ACTIVE_OFFSET"]),
                target_actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]),
                target_actor + 0x2AC,
                target_actor + 0x2B0,
            ])]
            self._log_threadsafe(
                f"FT ARRIVAL DIAG: {label} target state={vals[0]} prev=0x{vals[1]:08X} "
                f"mask=0x{vals[2]:08X} active={vals[3]} avail={vals[4]} "
                f"+2AC=0x{vals[5]:08X} +2B0=0x{vals[6]:08X} distance={distance} radius={arrival_radius:.3f}.",
                "warn",
            )
        except Exception as exc:
            self._log_threadsafe(f"FT ARRIVAL DIAG unavailable: {exc}", "warn")
        return False, f"V4 wrong physical arrival distance={distance} radius={arrival_radius:.3f} Master={final_state} resets={vanilla_resets}"

    def _ap_ft_bridge_tick(self, pine: PineClient, d: dict, now: float) -> None:
        """Runtime bridge using the sequence proven by the standalone BAT.

        Nativ source -> zone stream -> selected target prepared -> Master state 5
        -> real runtime mana guard -> Master 5->6 -> vanilla engine arrival.

        No SafeWarp, no target-state write, no destination C540 forcing.
        """
        if self._ap_fast_travel_progression != "archipelago" or not self._ap_starting_fast_travel_routes:
            return

        # Hard failsafe: even an unexpected streaming edge must never leave the
        # rest of the Launcher paused forever. Normal bridge timeouts are much
        # shorter; 45s is only the final safety net.
        if (
            self._ap_ft_exclusive
            and self._ap_ft_exclusive_since > 0.0
            and now - self._ap_ft_exclusive_since > 45.0
        ):
            self._log_threadsafe(
                "FAST TRAVEL EXCLUSIVE watchdog: 45s limit reached; releasing Launcher writers.",
                "error",
            )
            self._ap_ft_active_bridge = None
            self._ap_ft_departure_pending = False
            self._ap_ft_departure_route_id = None
            self._ap_ft_leave_exclusive(success=False, reason="45s hard watchdog")
            return

        # The successful standalone bridge polls at ~5 ms in the critical window.
        interval = 0.005 if (self._ap_ft_departure_pending or self._ap_ft_active_bridge is not None) else 0.060
        if now < self._ap_ft_next_runtime_scan:
            return
        self._ap_ft_next_runtime_scan = now + interval

        keyed = self._ap_ft_scan_keyed(
            pine,
            d,
            {int(d["FAST_TRAVEL_VTABLE"]), int(d["MASTER_EVENT_VTABLE"])},
        )
        source_keys = {int(x) for x in d.get("NATIV_FAST_TRAVEL_SOURCE_KEYS", [])}
        nativ_loaded = any(
            key in keyed and int(keyed[key][1]) == int(d["FAST_TRAVEL_VTABLE"])
            for key in source_keys
        )

        if nativ_loaded:
            self._ap_ft_nativ_loaded_last = True
            if self._ap_ft_active_bridge is None:
                self._ap_ft_departure_pending = False
                self._ap_ft_departure_route_id = None

            # Arm only the AP-selected source route Kya is actually standing near.
            kya = int(pine.read32(int(d["ADDR_KYA_ACTOR_GLOBAL"])))
            kp = self._ap_ft_actor_pos(pine, kya, d) if self._ap_valid_pointer(kya) else None
            if kp is not None:
                best = None
                best_distance = None
                for route in self._ap_starting_fast_travel_routes:
                    row = keyed.get(int(route["source_key"]))
                    if not row or int(row[1]) != int(d["FAST_TRAVEL_VTABLE"]):
                        continue
                    actor = int(row[0])
                    idx, avail = pine.read32_many([
                        actor + int(d["FAST_TRAVEL_INDEX_OFFSET"]),
                        actor + int(d["FAST_TRAVEL_AVAILABLE_OFFSET"]),
                    ])
                    if int(idx) != int(route["source_index"]) or int(avail) != 1:
                        continue
                    sp = self._ap_ft_actor_pos(pine, actor, d)
                    if sp is None:
                        continue
                    dist = ((kp[0]-sp[0])**2 + (kp[1]-sp[1])**2 + (kp[2]-sp[2])**2) ** 0.5
                    if best_distance is None or dist < best_distance:
                        best = route
                        best_distance = dist
                if best is not None and best_distance is not None and best_distance <= float(d.get("FAST_TRAVEL_SOURCE_ARM_RADIUS", 10.0)):
                    self._ap_ft_near_source_route_id = str(best.get("id", ""))
                    self._ap_ft_near_source_seen = now
            return

        if self._ap_ft_nativ_loaded_last:
            self._ap_ft_nativ_loaded_last = False
            recent_id = self._ap_ft_near_source_route_id
            recent = bool(recent_id) and (now - float(self._ap_ft_near_source_seen) <= float(d.get("FAST_TRAVEL_SOURCE_ARM_WINDOW", 6.0)))
            if recent:
                self._ap_ft_departure_pending = True
                self._ap_ft_departure_route_id = str(recent_id)
                self._ap_ft_departure_since = now
                route_for_lock = next(
                    (r for r in self._ap_starting_fast_travel_routes if str(r.get("id", "")) == str(recent_id)),
                    {"id": str(recent_id), "label": str(recent_id)},
                )
                self._ap_ft_enter_exclusive(route_for_lock, now)
                self._log_threadsafe(
                    f"AP Fast Travel departure detected from {recent_id}; BLOCKING bridge takes exclusive PINE ownership now.",
                    "info",
                )

                # V0.8.41 legacy path: do NOT return to the 20 ms camera/AP service loop. Run
                # the proven bridge synchronously until success/failure. This is
                # the key behavioral difference from V0.8.40.
                ultratight = "--ft-ultratight" in sys.argv
                ok, reason = self._ap_ft_blocking_bridge(pine, route_for_lock, d, ultratight=ultratight)
                self._ap_ft_active_bridge = None
                self._ap_ft_departure_pending = False
                self._ap_ft_departure_route_id = None
                self._ap_ft_leave_exclusive(success=ok, reason=reason)
                return
            else:
                self._ap_ft_departure_pending = False
                self._ap_ft_departure_route_id = None

        bridge = self._ap_ft_active_bridge
        if bridge is None and self._ap_ft_departure_pending:
            for route in self._ap_starting_fast_travel_routes:
                if self._ap_ft_departure_route_id and str(route.get("id", "")) != self._ap_ft_departure_route_id:
                    continue
                trow = keyed.get(int(route["target_key"]))
                mrow = keyed.get(int(route["master_key"]))
                if not trow or not mrow:
                    continue
                if int(trow[1]) != int(d["FAST_TRAVEL_VTABLE"]) or int(mrow[1]) != int(d["MASTER_EVENT_VTABLE"]):
                    continue

                state = int(pine.read32(int(mrow[0]) + int(d["ACTOR_STATE_OFFSET"])))
                bridge = {
                    "route": route,
                    "target_actor": int(trow[0]),
                    "master_actor": int(mrow[0]),
                    "seen_preinit": state == 0xFFFFFFFF,
                    "released_at": None,
                    "last_state": None,
                    "caught_state5": False,
                }
                self._ap_ft_active_bridge = bridge
                tp = self._ap_ft_actor_pos(pine, int(trow[0]), d)
                mp = self._ap_ft_actor_pos(pine, int(mrow[0]), d)
                self._log_threadsafe(
                    f"LEGACY FT bridge armed: {route.get('label')} | "
                    f"target 0x{int(route['target_key']):04X}=0x{int(trow[0]):08X} pos={tp} | "
                    f"Master 0x{int(route['master_key']):04X}=0x{int(mrow[0]):08X} pos={mp} "
                    f"first state=0x{state:08X}.",
                    "info",
                )
                break

            if bridge is None:
                if now - self._ap_ft_departure_since > 25.0:
                    self._ap_ft_departure_pending = False
                    self._ap_ft_departure_route_id = None
                    self._ap_ft_leave_exclusive(
                        success=False, reason="target/Master not found within 25s"
                    )
                return

        if bridge is None:
            return

        route = bridge["route"]
        target_key = int(route["target_key"])
        master_key = int(route["master_key"])
        trow = keyed.get(target_key)
        mrow = keyed.get(master_key)

        if not trow or not mrow:
            # Streaming can briefly remove the Actor Manager list.  Keep waiting
            # unless the post-release transition has clearly timed out.
            if bridge.get("released_at") is not None and now - float(bridge["released_at"]) > 10.0:
                self._log_threadsafe(
                    f"LEGACY FT bridge timeout after Master release: {route.get('label')}.",
                    "warn",
                )
                self._ap_ft_active_bridge = None
                self._ap_ft_departure_pending = False
                self._ap_ft_departure_route_id = None
                self._ap_ft_leave_exclusive(
                    success=False, reason="streaming lost target/Master after release"
                )
            return

        if int(trow[1]) != int(d["FAST_TRAVEL_VTABLE"]) or int(mrow[1]) != int(d["MASTER_EVENT_VTABLE"]):
            return

        bridge["target_actor"] = int(trow[0])
        bridge["master_actor"] = int(mrow[0])

        # This is patch_target_endpoint() from the working bridge: selected FT
        # active/available + footer ready, repeated continuously while state 5 is
        # being awaited so vanilla resets cannot win the race.
        target_actor, ready, loaded = self._ap_ft_patch_destination(pine, route, keyed, d)
        if target_actor is None:
            return

        state, prev = pine.read32_many([
            int(mrow[0]) + int(d["ACTOR_STATE_OFFSET"]),
            int(mrow[0]) + int(d["ACTOR_PREV_STATE_OFFSET"]),
        ])
        state = int(state)
        prev = int(prev)

        if bridge.get("last_state") != state:
            bridge["last_state"] = state
            self._log_threadsafe(
                f"LEGACY FT Master 0x{master_key:04X}: state={state} prev=0x{prev:08X} "
                f"target_ready={'YES' if ready else 'NO'} loaded={loaded}.",
                "info",
            )

        if state == 0xFFFFFFFF:
            bridge["seen_preinit"] = True
            return

        if bridge.get("released_at") is None and state == 5:
            self._log_threadsafe(
                f">>> LEGACY STATE 5 CAUGHT: {route.get('label')} - MANA GUARD THEN MASTER 5->6 <<<",
                "ok",
            )

            # Keep the exact endpoint armed immediately before the transition.
            for _ in range(4):
                self._ap_ft_patch_destination(pine, route, keyed, d)

            self._ap_ft_ensure_return_mana(pine, d)

            master_state_addr = int(mrow[0]) + int(d["ACTOR_STATE_OFFSET"])
            for _ in range(4):
                pine.write32(master_state_addr, 6)

            verified = int(pine.read32(master_state_addr))
            bridge["released_at"] = time.monotonic()
            bridge["caught_state5"] = True
            self._log_threadsafe(
                f"LEGACY Master 0x{master_key:04X}: 5->0x{verified:08X}; vanilla continuation released.",
                "ok" if verified in (6, 8) else "warn",
            )
            return

        if bridge.get("released_at") is None:
            # We deliberately do nothing else.  In particular, no SafeWarp and
            # no target/C540 state forcing while waiting for vanilla state 5.
            if now - self._ap_ft_departure_since > 25.0:
                self._log_threadsafe(
                    f"LEGACY FT bridge never saw Master state 5: {route.get('label')} "
                    f"(last={state}, prev=0x{prev:08X}).",
                    "error",
                )
                self._ap_ft_active_bridge = None
                self._ap_ft_departure_pending = False
                self._ap_ft_departure_route_id = None
                self._ap_ft_leave_exclusive(
                    success=False, reason="Master state 5 not observed within 25s"
                )
            return

        # After 5->6, vanilla should advance the Master to 8 AND place Kya at
        # the selected target. V0.8.40 keeps exclusive ownership until both are
        # true, then waits a short settle window (the gameplay exit/countdown
        # phase) before normal Launcher writers resume.
        distance = self._ap_ft_arrival_distance(pine, int(target_actor), d)
        arrived = distance is not None and distance <= 8.0
        vanilla_done = state == 8

        if arrived and vanilla_done:
            if bridge.get("confirmed_at") is None:
                bridge["confirmed_at"] = now
                self._ap_ft_ensure_return_mana(pine, d)
                self._log_threadsafe(
                    f"LEGACY FT VANILLA COMPLETE: {route.get('label')} | Master=8 | "
                    f"distance={distance:.3f}m. Holding exclusive mode for 0.75s settle window.",
                    "ok",
                )
                return

            if now - float(bridge["confirmed_at"]) < 0.75:
                return

            self._ap_ft_ensure_return_mana(pine, d)
            self._ap_ft_queue_arrival_check(route, d)
            self._log_threadsafe(
                f"LEGACY FT ARRIVAL CONFIRMED: {route.get('label')} | "
                f"Master state={state} prev=0x{prev:08X} | distance={distance:.3f}m.",
                "ok",
            )
            self._ap_ft_active_bridge = None
            self._ap_ft_departure_pending = False
            self._ap_ft_departure_route_id = None
            self._ap_ft_leave_exclusive(
                success=True, reason="Master 8 + target arrival + settle window"
            )
            return

        if now - float(bridge["released_at"]) > 10.0:
            self._log_threadsafe(
                f"LEGACY FT post-release timeout: {route.get('label')} | "
                f"Master state={state} prev=0x{prev:08X} | "
                f"distance={distance if distance is not None else 'N/A'}.",
                "error",
            )
            self._ap_ft_active_bridge = None
            self._ap_ft_departure_pending = False
            self._ap_ft_departure_route_id = None
            self._ap_ft_leave_exclusive(
                success=False, reason=f"post-release timeout state={state} distance={distance}"
            )

    def _ap_player_pointer(self, pine: PineClient, d: dict) -> int | None:
        pointer = pine.read32(int(d["ADDR_PLAYER_POINTER"]))
        return pointer if self._ap_valid_pointer(pointer) else None

    def _ap_owned_life_target(self, d: dict) -> int:
        base = int(d.get("LIFE_GAUGE_BASE", 50))
        step = int(d["LIFE_GAUGE_STEP"])
        cap = int(d["LIFE_GAUGE_CAP"])
        life_name = d.get("ITEM_PROGRESSIVE_LIFE_GAUGE")
        life_id = d.get("ITEM_NAME_TO_ID", {}).get(life_name) if life_name else None
        count = self._ap_item_counts.get(int(life_id), 0) if life_id is not None else 0
        return min(cap, base + max(0, int(count)) * step)

    def _ap_suppress_special_life_reward(
        self, pine: PineClient, location_id: int, location_name: str, target: int
    ) -> None:
        d = self._ap_data
        address = int(d["ADDR_LIFE_GAUGE"])
        target = int(target)
        pine.write32(address, target)
        verified = int(pine.read32(address))
        player = self._ap_player_pointer(pine, d)
        if player is not None:
            max_addr = player + int(d["PLAYER_MAX_HP_OFFSET"])
            hp_addr = player + int(d["PLAYER_HP_OFFSET"])
            pine.write32(max_addr, self._ap_float_to_raw(float(target)))
            hp = self._ap_raw_to_float(pine.read32(hp_addr))
            if hp == hp and 0.0 <= hp < 10000.0 and hp > float(target):
                pine.write32(hp_addr, self._ap_float_to_raw(float(target)))
        self._ap_pending_special_life_suppressions.pop(location_id, None)
        self._ap_shop_live_ignore_until = max(self._ap_shop_live_ignore_until, time.monotonic() + 1.0)
        self._log_threadsafe(
            f"Vanilla HP Up suppressed: {location_name} -> AP-owned max HP restored to {verified}.",
            "info",
        )

    def _ap_apply_progressive_life_gauge(
        self, pine: PineClient, item_id: int, d: dict, *, is_replay: bool = False
    ) -> None:
        """Make AP Progressive Life Gauge the sole authority for max HP.

        Vanilla HP Ups and Energy Bars are locations/checks only.  The persistent
        Life Gauge and runtime max HP are always derived from the number of
        Progressive Life Gauge items received from Archipelago:
            0/1/2/3/4 -> 50/100/150/200/250 HP.
        """
        address = int(d["ADDR_LIFE_GAUGE"])
        base = int(d.get("LIFE_GAUGE_BASE", 50))
        step = int(d["LIFE_GAUGE_STEP"])
        cap = int(d["LIFE_GAUGE_CAP"])
        count = max(0, int(self._ap_item_counts.get(item_id, 0)))
        target = min(cap, base + count * step)
        valid_values = set(range(base, cap + 1, step))

        current = int(pine.read32(address))
        # Loading/cutscene transitions can briefly expose garbage values at this
        # address. Never write through such a transient value, even for a live AP
        # delivery; the received item count is already recorded and the regular
        # reconciliation pass will apply the target once the ScenarioVar is sane.
        if current not in valid_values:
            if not is_replay:
                self._log_threadsafe(
                    f"Progressive Life Gauge delayed: transient readback {current}; AP target remains {target}.",
                    "warn",
                )
            return

        persistent_changed = current != target
        if persistent_changed:
            pine.write32(address, target)
        verified = int(pine.read32(address))
        if verified != target:
            self._log_threadsafe(
                f"Life Gauge write failed: requested {target}, readback={verified}.",
                "warn",
            )
            return

        runtime_changed = False
        hp_change = None
        player = self._ap_player_pointer(pine, d)
        if player is not None:
            max_addr = player + int(d["PLAYER_MAX_HP_OFFSET"])
            hp_addr = player + int(d["PLAYER_HP_OFFSET"])
            runtime_max = self._ap_raw_to_float(pine.read32(max_addr))
            hp = self._ap_raw_to_float(pine.read32(hp_addr))

            if runtime_max == runtime_max and 0.0 < runtime_max < 10000.0 and abs(runtime_max - float(target)) > 0.05:
                pine.write32(max_addr, self._ap_float_to_raw(float(target)))
                runtime_readback = self._ap_raw_to_float(pine.read32(max_addr))
                runtime_changed = abs(runtime_readback - float(target)) <= 0.05

            if hp == hp and 0.0 <= hp < 10000.0:
                new_hp = hp
                if hp > float(target):
                    new_hp = float(target)
                elif (not is_replay) and target > current and current in valid_values:
                    new_hp = min(float(target), hp + float(target - current))
                if abs(new_hp - hp) > 0.001:
                    pine.write32(hp_addr, self._ap_float_to_raw(new_hp))
                    hp_readback = self._ap_raw_to_float(pine.read32(hp_addr))
                    hp_change = f"HP {hp:g}->{hp_readback:g}"

        new_state = {"count": count, "expected_max": target}
        if self._ap_life_gauge_progress.get(self._ap_life_gauge_key) != new_state:
            self._ap_life_gauge_progress[self._ap_life_gauge_key] = new_state
            cfg = load_config()
            cfg["ap_life_gauge_progress"] = self._ap_life_gauge_progress
            save_config_data(cfg)

        if persistent_changed or runtime_changed:
            details = []
            if runtime_changed:
                details.append(f"runtime max={target}")
            if hp_change:
                details.append(hp_change)
            suffix = "; " + ", ".join(details) if details else ""
            action = "reconciled" if is_replay else "applied"
            self._log_threadsafe(
                f"Progressive Life Gauge {action}: {current}->{verified} max HP{suffix}.",
                "ok",
            )

    def _ap_restore_player_hp(self, pine: PineClient, amount: int, d: dict) -> bool:
        player = self._ap_player_pointer(pine, d)
        if player is None:
            return False
        max_hp = float(pine.read32(int(d["ADDR_LIFE_GAUGE"])))
        hp_address = player + int(d["PLAYER_HP_OFFSET"])
        hp = self._ap_raw_to_float(pine.read32(hp_address))
        if not (0.0 < max_hp <= float(d["LIFE_GAUGE_CAP"]) and 0.0 <= hp <= max_hp):
            return False
        target = min(max_hp, hp + amount)
        pine.write32(hp_address, self._ap_float_to_raw(target))
        verified = self._ap_raw_to_float(pine.read32(hp_address))
        if abs(verified - target) > 0.05:
            self._log_threadsafe(f"HP recovery readback mismatch: expected {target:g}, got {verified:g}.", "warn")
            return False
        self._ap_player_last_hp = verified
        self._log_threadsafe(f"HP recovery applied: +{amount} ({hp:g}->{verified:g}, max={max_hp:g}).", "ok")
        return True

    def _ap_restore_player_magic(self, pine: PineClient, amount: int, d: dict) -> bool:
        player = self._ap_player_pointer(pine, d)
        if player is None:
            return False
        object_address = player + int(d["PLAYER_MAGIC_OBJECT_OFFSET"])
        current_address = object_address + int(d["MAGIC_CURRENT_OFFSET"])
        max_address = object_address + int(d["MAGIC_MAX_OFFSET"])
        current = self._ap_raw_to_float(pine.read32(current_address))
        maximum = self._ap_raw_to_float(pine.read32(max_address))
        if not (0.0 <= current <= maximum <= float(d["MAGIC_MAX_CAP"]) and maximum > 0.0):
            return False
        target = min(maximum, current + amount)
        pine.write32(current_address, self._ap_float_to_raw(target))
        verified = self._ap_raw_to_float(pine.read32(current_address))
        if abs(verified - target) > 0.05:
            self._log_threadsafe(f"Magic recovery readback mismatch: expected {target:g}, got {verified:g}.", "warn")
            return False
        self._log_threadsafe(f"Magic recovery applied: +{amount} ({current:g}->{verified:g}, max={maximum:g}).", "ok")
        return True

    def _ap_apply_pending_recovery(self, pine: PineClient) -> None:
        d = self._ap_data
        if self._ap_pending_hp_restore:
            amount = self._ap_pending_hp_restore
            if self._ap_restore_player_hp(pine, amount, d):
                self._ap_pending_hp_restore = 0
        if self._ap_pending_magic_restore:
            amount = self._ap_pending_magic_restore
            if self._ap_restore_player_magic(pine, amount, d):
                self._ap_pending_magic_restore = 0

    def _ap_combat_bonus_percent(self, d: dict, effect: str) -> int:
        total = 0
        for item_name, spec in d.get("ITEM_COMBAT_BONUSES", {}).items():
            if isinstance(spec, dict):
                item_effect = str(spec.get("effect", ""))
                each = int(spec.get("percent", d.get("ITEM_COMBAT_BONUS_PERCENT", 5)))
            else:
                item_effect = str(spec)
                each = int(d.get("ITEM_COMBAT_BONUS_PERCENT", 5))
            if item_effect != effect:
                continue
            iid = d.get("ITEM_NAME_TO_ID", {}).get(item_name)
            if iid is not None:
                total += self._ap_item_counts.get(int(iid), 0) * each
        return min(int(d.get("ITEM_COMBAT_BONUS_CAP_PERCENT", 25)), total)

    def _ap_monitor_player_protection(self, pine: PineClient, d: dict) -> None:
        percent = self._ap_combat_bonus_percent(d, "protection")
        player = self._ap_player_pointer(pine, d)
        if player is None:
            self._ap_player_last_hp = None
            return
        hp_address = player + int(d["PLAYER_HP_OFFSET"])
        current = self._ap_raw_to_float(pine.read32(hp_address))
        if not (0.0 <= current <= float(d["LIFE_GAUGE_CAP"])):
            self._ap_player_last_hp = None
            return
        previous = self._ap_player_last_hp
        if previous is None or current >= previous - 0.001:
            self._ap_player_last_hp = current
            return
        damage = previous - current
        if percent <= 0 or current <= 0.0:
            self._ap_player_last_hp = current
            return
        reduction = min(0.75, percent / 100.0)
        target = max(0.0, previous - damage * (1.0 - reduction))
        pine.write32(hp_address, self._ap_float_to_raw(target))
        verified = self._ap_raw_to_float(pine.read32(hp_address))
        if abs(verified - target) <= 0.05:
            self._ap_player_last_hp = verified
            if not self._ap_protection_effect_logged:
                self._log_threadsafe(f"Protection bonus active: reduced this hit by {reduction:.0%}.", "ok")
                self._ap_protection_effect_logged = True
        else:
            self._ap_player_last_hp = verified
            self._log_threadsafe("Protection bonus write did not verify against Kya's HP field.", "warn")

    def _ap_monitor_wolfen_damage(self, pine: PineClient, actors: list[int], states: list[int], d: dict) -> None:
        percent = self._ap_combat_bonus_percent(d, "damage")
        if percent <= 0:
            self._ap_damage_last_hp.clear()
            return
        present = int(d["WOLFEN_STATE_PRESENT"])
        hp_offset = int(d["WOLFEN_HP_OFFSET"])
        active = [actor for actor, state in zip(actors, states) if state == present]
        raw_values = pine.read32_many([actor + hp_offset for actor in active]) if active else []
        active_set = set(active)
        for actor in set(self._ap_damage_last_hp) - active_set:
            self._ap_damage_last_hp.pop(actor, None)
        bonus = min(0.75, percent / 100.0)
        for actor, raw in zip(active, raw_values):
            current = self._ap_raw_to_float(raw)
            if not (0.0 <= current <= 100000.0):
                self._ap_damage_last_hp.pop(actor, None)
                continue
            previous = self._ap_damage_last_hp.get(actor)
            if previous is None or current > previous + 0.001:
                self._ap_damage_last_hp[actor] = current
                continue
            if current < previous - 0.001:
                damage = previous - current
                target = max(0.0, previous - damage * (1.0 + bonus))
                pine.write32(actor + hp_offset, self._ap_float_to_raw(target))
                verified = self._ap_raw_to_float(pine.read32(actor + hp_offset))
                self._ap_damage_last_hp[actor] = verified
                if abs(verified - target) <= 0.05 and not self._ap_damage_effect_logged:
                    self._log_threadsafe(f"Attack bonus active: scaled Wolfen damage by +{bonus:.0%}.", "ok")
                    self._ap_damage_effect_logged = True
                elif abs(verified - target) > 0.05:
                    self._log_threadsafe("Attack bonus write did not verify against the Wolfen HP field.", "warn")
            else:
                self._ap_damage_last_hp[actor] = current

    def _debug_tick(self, pine: PineClient) -> None:
        """Apply audit-runner style cheats through the launcher's single PINE owner."""
        if not (self._debug_infinite_life or self._debug_infinite_mana or self._debug_one_shot):
            return
        d = self._ap_data

        # Kya life / mana locks use the validated dynamic player pointer.
        try:
            player = self._ap_player_pointer(pine, d)
            if player is not None and self._debug_infinite_life:
                hp_addr = player + int(d["PLAYER_HP_OFFSET"])
                max_addr = player + int(d.get("PLAYER_MAX_HP_OFFSET", 0x2DC))
                maximum = self._ap_raw_to_float(pine.read32(max_addr))
                if 1.0 <= maximum <= 5000.0:
                    pine.write32(hp_addr, self._ap_float_to_raw(maximum))
            if player is not None and self._debug_infinite_mana:
                magic_obj = player + int(d["PLAYER_MAGIC_OBJECT_OFFSET"])
                cur_addr = magic_obj + int(d["MAGIC_CURRENT_OFFSET"])
                max_addr = magic_obj + int(d["MAGIC_MAX_OFFSET"])
                maximum = self._ap_raw_to_float(pine.read32(max_addr))
                if 0.0 < maximum <= 5000.0:
                    pine.write32(cur_addr, self._ap_float_to_raw(maximum))
        except Exception:
            pass

        if not self._debug_one_shot:
            return
        now = time.monotonic()
        if now < self._debug_next_actor_scan:
            return
        self._debug_next_actor_scan = now + 0.05
        try:
            manager = pine.read32(int(d["ADDR_ACTOR_MANAGER_GLOBAL"]))
            if not self._ap_valid_pointer(manager):
                self._debug_wolfen_hp.clear(); return
            active, count = pine.read32_many([
                manager + int(d["ACTOR_MANAGER_ACTIVE_LIST_OFFSET"]),
                manager + int(d["ACTOR_MANAGER_ACTIVE_COUNT_OFFSET"]),
            ])
            if not self._ap_valid_pointer(active) or count > int(d["ACTOR_MANAGER_MAX_ACTIVE"]):
                self._debug_wolfen_hp.clear(); return
            slots = pine.read32_many([active + i * 4 for i in range(count)]) if count else []
            actors = sorted({a for a in slots if self._ap_valid_pointer(a)})
            if not actors:
                self._debug_wolfen_hp.clear(); return
            vtables = pine.read32_many(actors)
            wolfens = [a for a, vt in zip(actors, vtables) if vt == int(d["WOLFEN_VTABLE"])]
            current_set = set(wolfens)
            for old in list(self._debug_wolfen_hp):
                if old not in current_set:
                    self._debug_wolfen_hp.pop(old, None)
            if not wolfens:
                return
            raw_hp = pine.read32_many([a + int(d["WOLFEN_HP_OFFSET"]) for a in wolfens])
            states = pine.read32_many([a + int(d["WOLFEN_STATE_OFFSET"]) for a in wolfens])
            for actor, raw, state in zip(wolfens, raw_hp, states):
                hp = self._ap_raw_to_float(raw)
                previous = self._debug_wolfen_hp.get(actor)
                if previous is not None and state == int(d["WOLFEN_STATE_PRESENT"]):
                    if 0.0 < hp < previous - 0.01:
                        pine.write32(actor + int(d["WOLFEN_HP_OFFSET"]), self._ap_float_to_raw(0.0))
                self._debug_wolfen_hp[actor] = hp
        except Exception:
            pass

    def _ap_lava_worm_witness_tick(self, pine: PineClient, d: dict,
                                   actors: list[int], vtables: list[int],
                                   actor_list: int, now: float) -> None:
        """0.9.59: a *live* scenario edge plus a subsequent actor-death edge.

        User's read-only PINE capture (2026-11-03): ScenarioVar[4] at
        0x004253F4: 0->1, followed ~0.37s later by vtable 0x00441500
        actor state 0x03->0x11. The scenario variable also participates in
        Frank's conditions, so it alone must NEVER send an AP check.
        This is a guarded *beta hypothesis* pending live PCSX2 validation.
        """
        zone = self._ap_current_zone
        if actor_list != self._ap_lava_actor_generation:
            self._ap_lava_actor_generation = actor_list
            self._ap_lava_actor_address = None
            self._ap_lava_actor_last_state = None
            self._ap_lava_last_var = None
            self._ap_lava_pending_at = None
        target_name = 'Flying Forest - Lava Worm Defeated'
        build = str(self._ap_slot_data.get('prototype_version', ''))
        if (not self._ap_joined or not self._ap_seed_build_verified
                or build not in ('0.8.13-lava-witness-map-zoom', '0.8.14-ft-safe-shop-audit')
                or target_name not in d.get('LOCATION_NAME_TO_ID', {})):
            return
        if self._ap_stream_hold or zone != 'Flying Forest' or now < self._ap_reload_pause_until:
            # Keep baselines neutral across scene transitions/savestates.
            self._ap_lava_pending_at = None
            self._ap_lava_last_var = None
            self._ap_lava_actor_last_state = None
            return
        candidates = [a for a, vt in zip(actors, vtables) if int(vt) == 0x00441500]
        if len(candidates) != 1:
            self._ap_lava_pending_at = None
            self._ap_lava_last_var = None
            self._ap_lava_actor_last_state = None
            return
        actor = candidates[0]
        if actor != self._ap_lava_actor_address:
            self._ap_lava_actor_address = actor
            self._ap_lava_last_var = None
            self._ap_lava_actor_last_state = None
            self._ap_lava_pending_at = None
        flag, frank, actor_state = map(int, pine.read32_many([
            0x004253F4, 0x00425584, actor+0x104]))
        prev_flag = self._ap_lava_last_var
        prev_state = self._ap_lava_actor_last_state
        self._ap_lava_last_var = flag
        self._ap_lava_actor_last_state = actor_state
        if frank != 0:
            self._ap_lava_pending_at = None
            return
        if prev_flag == 0 and flag == 1 and prev_state is not None and prev_state != 0x11:
            self._ap_lava_pending_at = now
            self._log_threadsafe(
                f'LAVA WORM WITNESS: ScenarioVar[4] 0->1 in Flying Forest; '
                f'actor=0x{actor:08X} vtable=0x00441500 state={prev_state}->{actor_state}; '
                'awaiting post-boss state 0x11 (no check yet).', 'info')
        pending = self._ap_lava_pending_at
        if pending is None:
            return
        if now - pending > 8.0 or flag != 1:
            self._ap_lava_pending_at = None
            self._log_threadsafe('LAVA WORM WITNESS EXPIRED: no safe double-edge check.', 'info')
            return
        if prev_state is None or prev_state == 0x11 or actor_state != 0x11:
            return
        self._ap_lava_pending_at = None
        lid = int(d['LOCATION_NAME_TO_ID'][target_name])
        if lid in self._ap_checked or lid in self._ap_pending_checks:
            return
        self._ap_queue_location_check(self._ap_link, lid, target_name, d)
        self._log_threadsafe(
            f'LAVA WORM LIVE CHECK queued: ScenarioVar[4] 0->1 + '
            f'actor state {prev_state}->0x11 in same scene, '
            f'actor=0x{actor:08X}; Frank flag=0.', 'ok')

    def _ap_log_actor_manager_state(self, state: tuple, message: str) -> None:
        """Log actor-manager diagnostics only when its pointer state changes."""
        if state != self._ap_actor_manager_state:
            self._ap_actor_manager_state = state
            self._log_threadsafe(message, "info")

    # ------------------------------------------------------------------
    # PCSX2 session fault / recovery (single PINE owner; never a second socket)
    # ------------------------------------------------------------------
    def _reset_after_pcsx2_state_change(self) -> None:
        """Forget transient game-memory baselines, NOT AP server progress."""
        # Loading a savestate can change ScenarioVars in a single frame.  It is
        # NOT a witnessed real-time credits edge; reset the goal baselines.
        self._ap_goal_last_value = None
        self._ap_goal_credits_last_value = None
        self._ap_goal_auto_candidate_at = None
        self._ap_goal_auto_candidate_samples = 0
        self._ap_goal_fortress_since = None
        self._ap_goal_boss_witness_at = None
        self._ap_reload_pause_until = time.monotonic() + 6.0
        self._map_guard_recovery.reset()
        self._ap_baselined = False
        self._ap_special_baselined = False
        self._ap_fast_travel_baselined = False
        self._ap_validation_probes_baselined = False
        self._ap_actor_states.clear()
        self._ap_actor_keys.clear()
        self._ap_actor_descriptors.clear()
        self._ap_wolfen_states.clear()
        self._ap_special_states.clear()
        self._ap_first_brazul_last_value = None
        self._ap_first_brazul_zone_since = None
        self._ap_first_brazul_next_poll = 0.0
        self._ap_lava_last_var = None
        self._ap_lava_actor_generation = None
        self._ap_lava_actor_address = None
        self._ap_lava_actor_last_state = None
        self._ap_lava_pending_at = None
        self._ap_fast_travel_states.clear()
        self._ap_fast_travel_keys.clear()
        self._ap_shop_baselined = False
        self._ap_shop_states.clear()
        self._ap_shop_live_baselined = False
        self._ap_shop_live_reward_states.clear()
        self._ap_shop_money_last = None
        self._ap_shop_purchase_tokens.clear()
        self._ap_shop_native.reset()
        self._ap_shop_sold_observer.reset()
        self._ap_shop_native_sold_state_last = {}
        self._ap_ft_reset_runtime()
        self._ap_current_zone = None
        self._ap_stream_hold = True
        self._ap_stream_candidate = None
        self._ap_stream_ready_since = 0.0
        self._ap_stream_departure_generation = None
        self._ap_next_inventory_reconcile = 0.0
        self._auto_save_controller.previous = None

    def _on_pcsx2_pine_lost(self, reason: str) -> None:
        if not self._pine_was_online or self._pine_lost_at is not None:
            return
        self._pine_lost_at = time.monotonic()
        self._pine_last_heartbeat_at = 0.0
        self._camera_ready_event.clear()
        self._pine_auto_restore_pending = None
        self._pine_recovery_candidate = None
        self._ap_first_brazul_last_value = None
        self._ap_first_brazul_zone_since = None
        self._ap_first_brazul_next_poll = 0.0
        # A PCSX2 crash/restart invalidates live credit-transition evidence.
        self._ap_goal_last_value = None
        self._ap_goal_credits_last_value = None
        self._ap_goal_auto_candidate_at = None
        self._ap_goal_auto_candidate_samples = 0
        self._ap_goal_fortress_since = None
        self._ap_goal_boss_witness_at = None
        if self._auto_recover_enabled and self._ap_joined and self._ap_seed_build_verified:
            identity = self._ap_pending_storage_key(self._ap_data)
            if identity and self._ap_link is not None and self._ap_link.connected_event.is_set():
                self._pine_recovery_candidate = self._auto_save_controller.latest_current_session(identity)
            if self._pine_recovery_candidate is None:
                self._log_threadsafe(
                    'AUTO RECOVERY unavailable: no CONFIRMED AutoSave for this Launcher session and AP seed. '
                    'Automatic load cannot use an older session state.', 'warn')
        self._log_threadsafe('PCSX2/PINE OFFLINE: ' + reason +
                             '. Waiting for Kya to reconnect. AP server stays independent.', 'warn')

    def _restore_after_pcsx2_reconnect(self, pine: PineClient) -> None:
        """Stage same-session AutoSave recovery; never load into a streaming VM."""
        lost_at = self._pine_lost_at
        self._pine_lost_at = None
        candidate = self._pine_recovery_candidate
        self._pine_recovery_candidate = None
        self._reset_after_pcsx2_state_change()
        self._log_threadsafe('PCSX2/PINE RECONNECTED: Kya signature verified. Waiting for stable scene.', 'ok')
        if not self._auto_recover_enabled or candidate is None or lost_at is None:
            return
        if time.monotonic() - lost_at < 5.0:
            self._log_threadsafe('AUTO RECOVERY skipped: disconnect was brief (<5s).', 'info')
            return
        self._pine_auto_restore_pending = candidate
        self._pine_auto_restore_started = time.monotonic()
        self._log_threadsafe('AUTO RECOVERY queued: verified same-session AutoSave; waiting for stable Kya scene.', 'info')

    def _pine_auto_restore_tick(self, pine: PineClient) -> bool:
        """Delay automatic recovery until safe, without running AP memory writers.

        The AP stream guard may inspect actors here, but other AP writes and
        AutoSaves are suspended until the saved state was loaded (or aborted).
        """
        candidate = self._pine_auto_restore_pending
        if candidate is None:
            return False
        # This is a real response from PCSX2 via MemoryCore, not just a live
        # proxy socket. Failure propagates to the reconnection owner thread.
        if int(pine.read32(SIG_ADDRS[0])) != int(SIG_VALUES[0]):
            raise RuntimeError('PCSX2 game changed during automatic restoration')
        self._pine_last_heartbeat_at = time.monotonic()
        now = time.monotonic()
        if now - self._pine_auto_restore_started > 120.0:
            self._pine_auto_restore_pending = None
            self._log_threadsafe('AUTO RECOVERY expired: no stable scene within 120s; manual reload is available.', 'warn')
            return True
        if now < self._ap_reload_pause_until:
            return True
        if not (self._ap_joined and self._ap_seed_build_verified and
                self._ap_link is not None and self._ap_link.connected_event.is_set()):
            return True
        identity = self._ap_pending_storage_key(self._ap_data)
        if not (getattr(self._ap_link, 'room_seed', '') == self._ap_seed_name and
                bool(self._ap_seed_name) and identity and identity == candidate.get('ap_identity')):
            self._pine_auto_restore_pending = None
            self._log_threadsafe('AUTO RECOVERY refused: wrong AP seed/slot identity.', 'warn')
            return True
        # PCSX2 LoadState replaces emulator state and can safely load from the
        # title screen: do NOT require a populated game actor list here. The
        # actor stream guard still blocks ordinary AP writes AFTER the load.
        if not self._pine_vm_ready_for_savestate_load(pine):
            return True
        # Never restore an unverified old or overwritten state.
        self._pine_auto_restore_pending = None
        try:
            slot = int(candidate['slot'])
            path = self._auto_save_controller.verify_reload_slot(slot)
            stat = path.stat()
            if (path.name != candidate.get('filename') or
                    stat.st_size != candidate.get('size') or
                    stat.st_mtime_ns != candidate.get('mtime_ns') or
                    not self._auto_save_controller.matches_current_session(slot, identity)):
                raise RuntimeError('AutoSave changed after disconnect or belongs to another session')
            response = pine._packet(bytes((0x0A, slot)))
            if response:
                raise RuntimeError('Unexpected PCSX2 LoadState response')
            self._reset_after_pcsx2_state_change()
            self._log_threadsafe(f'AUTO RECOVERY: PCSX2 reloaded verified slot {slot} ({path.name}).', 'ok')
        except Exception as exc:
            self._log_threadsafe(f'AUTO RECOVERY refused/failed: {type(exc).__name__}: {exc}', 'error')
        return True

    # ------------------------------------------------------------------
    # Integrated camera service
    # ------------------------------------------------------------------
    def _camera_service_loop(self) -> None:
        announced = False

        while not self._camera_stop_event.is_set():
            self._camera_ready_event.clear()

            try:
                with PineClient(PINE_HOST, PINE_PORT, timeout=8.0) as pine:
                    sig = tuple(int(v) for v in pine.read32_many(SIG_ADDRS, batch_size=8))
                    if sig != SIG_VALUES:
                        self._camera_last_error = (
                            f"Unsupported/unknown game signature: {sig}"
                        )
                        self._on_pcsx2_pine_lost(self._camera_last_error)
                        time.sleep(0.75)
                        continue

                    self._camera_last_error = ""
                    if self._pine_lost_at is not None:
                        self._restore_after_pcsx2_reconnect(pine)
                    self._pine_was_online = True
                    self._pine_last_heartbeat_at = time.monotonic()
                    self._last_pine_service_error = ""
                    self._camera_ready_event.set()

                    if not announced:
                        announced = True
                        self._log_threadsafe(self.tr["camera_active"], "ok")
                        self._log_threadsafe(
                            "Modular MemoryCore active: Launcher -> 127.0.0.1:28111 -> PCSX2 PINE 127.0.0.1:28011. One upstream PINE owner.",
                            "ok",
                        )
                        self._log_threadsafe(
                            "External data modules loaded: core / wolfen / fast_travel / shops / access / items / zones.",
                            "info",
                        )

                    if DIAGNOSTIC_DISABLE_ALL_CAMERA_ROUTE_WRITES:
                        self._log_threadsafe(
                            "MENU-SAFE DIAG active: camera input route writes DISABLED. "
                            "Camera inversion sliders are suspended in this build.",
                            "warn",
                        )
                    # V0.9.46: MAP/AMBER diagnostic guard removed. The state bit
                    # 0x00451ABC is shared with regeneration ambers and caused
                    # catastrophic AP check/Goal starvation during cutscenes.
                    # The independent FT actor-generation guard is retained.
                    self._log_threadsafe(
                        "MAP/AMBER BLOCKING DISABLED: AP checks continue normally; "
                        "FT scene-streaming protection stays active.", "ok")

                    valid_routes = {
                        build_gameplay_route("vanilla", "vanilla"),
                        build_gameplay_route("inverted", "vanilla"),
                        build_gameplay_route("vanilla", "inverted"),
                        build_gameplay_route("inverted", "inverted"),
                    }

                    last_zoom_route_mode = None
                    last_zoom_route_diag_at = 0.0
                    while not self._camera_stop_event.is_set():
                        # Maintain a real PINE heartbeat with the single PINE owner.
                        # A prolonged watcher cycle is UI-BUSY, never an
                        # unproven disconnect.
                        self._pine_service_stage = 'PINE heartbeat'
                        pine.read32(SIG_ADDRS[0])
                        self._pine_last_heartbeat_at = time.monotonic()
                        self._pine_service_stage = 'AP preflight'
                        if self._pine_auto_restore_tick(pine):
                            time.sleep(0.10)
                            continue
                        if self._auto_save_reload_tick(pine):
                            time.sleep(0.10)
                            continue
                        if time.monotonic() < self._ap_reload_pause_until:
                            time.sleep(0.10)
                            continue
                        # The final fight may unload Kya's actor. Observe the
                        # live Brazul transition before the stream guard;
                        # 0x0044982C is diagnostic only (false positive proved).
                        self._ap_goal_read_only_tick(pine)
                        # First Brazul may complete while the actor list is
                        # unavailable. Monitor the live edge before stream guard.
                        self._ap_first_brazul_read_only_tick(pine)
                        # UI requests must be processed on this one PINE owner.
                        # If MAP is open or a FT is streaming, never take a state.
                        self._auto_save_tick(pine)
                        # V0.9.46: Always run AP checks. Do not infer that MAP
                        # is open from 0x00451ABC, actor movement or availability.
                        # _ap_tick itself retains the independent FT stream guard.
                        self._pine_service_stage = 'AP watchers / FT / shops'
                        self._ap_tick(pine)
                        # 0.9.55: the FT cleanroom now yields every iteration.
                        # Do NOT run the unrelated camera/input route writer in
                        # those gaps: preserve BAT-style exclusive FT ownership.
                        if self._ap_ft_cleanroom_active:
                            self._pine_service_stage = 'FT cleanroom yield / PINE heartbeat'
                            time.sleep(0.02)
                            continue
                        self._pine_service_stage = 'camera/route update'
                        if self._ap_stream_hold:
                            time.sleep(0.05)
                            continue
                        # BETA CLEAN: no manual cheats, test grants, shop demo,
                        # FT forensic scanner or 0-mana write in normal play.
                        horizontal = self.camera_horizontal
                        vertical = self.camera_vertical

                        # 0.9.62: input-route candidate only. Camera submode 3
                        # is a zoom handler, NOT proof that the MAP UI is open.
                        # The ambiguous MAP/amber bit never gates AP checks,
                        # shop recovery, autosaves or Fast Travel transitions.
                        # Emit actual table traces for the remaining zoom issue.
                        map_flag, camera_submode = map(int, pine.read32_many([
                            MAP_STATE_ADDR, MAP_ZOOM_CAMERA_MODE_ADDR]))
                        zoom_route_mode = bool(map_flag == 1 or camera_submode == MAP_ZOOM_CAMERA_MODE)
                        target = select_camera_input_route(
                            horizontal, vertical, camera_submode, map_flag)

                        if DIAGNOSTIC_DISABLE_ALL_CAMERA_ROUTE_WRITES:
                            # This isolates the camera/MAP route patch from the
                            # AP gameplay loop without altering vanilla controls.
                            time.sleep(0.05)
                            continue

                        # Preflight every input-object route BEFORE writing any
                        # one of them. A zero/partially unloaded camera table
                        # belongs to the streaming engine, not to our patcher.
                        existing_routes = [(obj, read_route(pine, obj)) for obj in INPUT_OBJECTS]
                        # Unknown routes are common while native map/menu and
                        # scene loaders own the input objects. NEVER treat an
                        # unfamiliar table as permission to overwrite memory,
                        # and do not disconnect the AP socket for this case.
                        transient_route = any(before not in valid_routes
                                              for _, before in existing_routes)
                        if transient_route and zoom_route_mode and last_zoom_route_mode is not True:
                            self._log_threadsafe(
                                f'MAP ZOOM ROUTE SKIPPED: input tables transient '
                                f'[map_flag={map_flag}, camera_mode={camera_submode}]; no unsafe writes.', 'warn')
                            last_zoom_route_mode = True
                        if not transient_route:
                            for obj, before in existing_routes:
                                if before != target:
                                    write_route(pine, obj, target)
                                after = read_route(pine, obj)
                                if after != target:
                                    # Game may take back the table mid-frame;
                                    # it is safer to retry on the next tick.
                                    transient_route = True
                                    break
                            # Real-device instrumentation of MAP input routing.
                            # 0x00451ABC also changes near ambers and a log saying
                            # 'vanilla' does NOT prove the on-screen zoom direction.
                            # Sample both tables before/after; no extra RAM writes.
                            camera_diag_now = time.monotonic()
                            if zoom_route_mode and (camera_diag_now - last_zoom_route_diag_at >= 4.0):
                                actual = [read_route(pine, obj) for obj in INPUT_OBJECTS]
                                self._log_threadsafe(
                                    f'MAP CAMERA VERIFY: flag={map_flag}, submode={camera_submode}, '
                                    f'vertical_preference={vertical}, expected={target}, '
                                    f'before={[route for _obj,route in existing_routes]}, '
                                    f'actual={actual}, transient={transient_route}. '
                                    'This verifies memory routing, NOT visual zoom direction.', 'info')
                                last_zoom_route_diag_at = camera_diag_now
                            if not transient_route and zoom_route_mode != last_zoom_route_mode:
                                # No noisy logs for the initial gameplay read.
                                if zoom_route_mode:
                                    self._log_threadsafe(
                                        f'MAP ZOOM ROUTE: vanilla zoom/dezoom (C/D) [map_flag={map_flag}, camera_mode={camera_submode}]; '
                                        'gameplay camera preference preserved.', 'info')
                                elif last_zoom_route_mode is True:
                                    self._log_threadsafe(
                                        'MAP ZOOM ROUTE: gameplay vertical inversion restored (no map/zoom hint).', 'info')
                                last_zoom_route_mode = zoom_route_mode

                        time.sleep(0.05 if transient_route else 0.02)

            except Exception as exc:
                self._pine_service_stage = 'PINE error'
                # Never let a Python-side watcher regression die silently.
                # Keep the service alive and surface the exact exception in the UI.
                raw_error = f"{type(exc).__name__}: {exc}"
                if raw_error != self._last_pine_service_error:
                    self._last_pine_service_error = raw_error
                    self._log_threadsafe(f"PINE watcher read failed: {raw_error}", "error")
                if "timed out" in raw_error.lower():
                    self._camera_last_error = self.tr["pine_busy_hint"]
                else:
                    self._camera_last_error = raw_error
                self._on_pcsx2_pine_lost(raw_error)
                self._pine_last_heartbeat_at = 0.0
                self._camera_ready_event.clear()
                time.sleep(0.75)
            finally:
                self._camera_ready_event.clear()



if __name__ == "__main__":
    try:
        _core_started, _core_desc = ensure_memory_core()
    except Exception as _core_exc:
        try:
            messagebox.showerror("Kya MemoryCore", str(_core_exc))
        except Exception:
            pass
        raise SystemExit(str(_core_exc))

    try:
        KyaLauncher().mainloop()
    finally:
        stop_owned_memory_core()
