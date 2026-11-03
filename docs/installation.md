# Kya: Dark Lineage Archipelago — player setup guide

**Release:** `9.0.0-beta1` (Launcher implementation `0.9.63`, APWorld implementation `0.8.14`)

**Supported game:** *Kya: Dark Lineage*, PAL PlayStation 2, serial **`SLES-51473`**. Other regional releases are not supported by the current memory mappings.

This integration runs alongside the original game in PCSX2. It does **not** ship a game ISO, and it does not require distributing a patched game image.

## 1. Downloads and prerequisites

- Your own legally obtained copy of the supported PAL PS2 game.
- A recent [PCSX2](https://pcsx2.net/) installation with **PINE** support.
- [Archipelago](https://archipelago.gg/) **0.6.7 or newer**, with its Generator installed if you plan to generate a multiworld locally.
- The following files from this project's GitHub **Releases** page:
  - `Launcher.zip` — Windows executables, runtime data, and optional tools.
  - `kya_dark_lineage.apworld` — the custom Archipelago world.
  - `Kya_Dark_Lineage.yaml` — an example player configuration.

Windows players running the compiled Launcher and MemoryCore **do not need to install Python**. Kya Color Studio is optional and has its own Python/Pillow requirements.

## 2. Confirm your game version

In PCSX2, select the game and check its **Properties / Summary / Serial**. It must read **`SLES-51473`**. The memory addresses in this integration were researched for this PAL release; a different serial is not interchangeable.

## 3. Configure PCSX2 graphics (important for textures)

Open **PCSX2 → Settings → Graphics → Rendering** and find the **Renderer** setting.

1. If **Software** or **Software Renderer** is selected, change it to **Vulkan** (spelled *Vulkan*, not *Vulcan*).
2. Keep Vulkan selected as the **hardware renderer**. This is especially important for the provided texture replacements. Vulkan requires a compatible graphics card and reasonably current graphics drivers.
3. Open **Settings → Graphics → Texture Replacement** (the wording may be singular or plural in different PCSX2 builds).
4. Enable **Load Textures** / **Load Texture Replacements**. You can leave asynchronous loading enabled if your PCSX2 version provides it.
5. Restart the game if an already loaded texture does not refresh.

For systems that cannot run Vulkan, another supported **hardware renderer** may work, but Vulkan is the recommended tested configuration here. The PCSX2 project's [graphics documentation](https://pcsx2.net/docs/configuration/general/) explains the differences between software and hardware modes.

### Optional replacement textures

For a standard Windows installation, the replacement folder is commonly:

```text
Documents\PCSX2\textures\SLES-51473\replacements\
```

Check **PCSX2 → Settings → Folders** to confirm the actual textures directory; portable installations may use a different location. Back up existing replacements before overwriting anything. Texture recolors are optional and should not be installed over a customized Kya Color Studio palette unless you want to replace it.

The Launcher may install its Archipelago branding texture at startup. That is separate from optionally applying a character recolor.

## 4. Enable the PINE connection

1. In PCSX2, enable advanced settings if they are hidden (in some versions: **Tools → Show Advanced Settings**).
2. Open **Settings → Advanced → PINE Settings**. In some layouts the path starts with **System → Settings**.
3. Enable PINE and use TCP port **`28011`**.
4. Start *Kya: Dark Lineage* in PCSX2. Keep PCSX2 running while using the Launcher.

The Launcher communicates locally with PCSX2 through **`127.0.0.1:28011`**. This is **not** the same as the Archipelago multiworld server address/port.

## 5. Install the APWorld

1. In the Archipelago Launcher, choose **Install APWorld** and select `kya_dark_lineage.apworld`.
2. Alternatively, use the official custom-world installation method for your Archipelago installation.
3. The included game ID should be shown as **`Kya: Dark Lineage`**.

If generating a seed locally, every person generating the world must use a compatible APWorld. Archipelago's [official setup guide](https://archipelago.gg/tutorial/Archipelago/setup_en) explains installing custom worlds.

## 6. Edit your YAML and generate a seed

1. Open `Kya_Dark_Lineage.yaml` in a plain-text editor (Notepad or VS Code).
2. Change `name: Kya` to **your exact Archipelago slot/player name**; it must match the name in the generated room.
3. Keep the game field as `game: 'Kya: Dark Lineage'` and edit the game-specific options if desired. See [configuration.md](configuration.md) for the supported values.
4. Save the YAML into Archipelago's **`Players`** directory alongside the YAML files for other players.
5. Use **Generate** / `ArchipelagoGenerate.exe` to generate a new multiworld locally, then host the resulting room using the normal Archipelago workflow.

Because this is a custom APWorld, you should not assume the public web generator has Kya installed. Generating locally is the reliable route for this beta.

## 7. Extract the Launcher and play

1. Extract `Launcher.zip` into a normal folder, for example `C:\Games\Kya-Archipelago\`.
2. Keep **`Kya_Archipelago_Launcher.exe`**, **`Kya_MemoryCore.exe`** and the **`data/`** directory together in the extracted folder.
3. Start PCSX2 and boot the supported game.
4. Run `Kya_Archipelago_Launcher.exe`.
5. Connect to your Archipelago room with the server address (for example `archipelago.gg:PORT`), your **slot name**, and the room password **if one is set**.
6. Verify that the Launcher detects PCSX2/PINE and that the Archipelago connection is established before collecting checks.

The exact Launcher UI labels may change between beta versions. Keep the current Launcher and APWorld together; do not mix arbitrary old builds with a freshly generated seed.

## 8. Optional Kya Color Studio

The extra Color Studio can be launched with `tools/Kya_Color_Studio_v4_3_3/START_KYA_COLOR_STUDIO.bat`. It requires Python 3 and Pillow and is **not required** for normal Archipelago gameplay. Back up any existing texture customizations before using it.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Launcher cannot see PCSX2 | Supported PAL `SLES-51473`, PINE enabled, port `28011`, game actually running |
| Texture replacements do not appear | Set **Graphics → Rendering → Renderer → Vulkan**, enable **Texture Replacement → Load Textures**, check the `SLES-51473/replacements` directory, then restart the game |
| Archipelago says the slot is missing | YAML `name` must match the generated multiworld's player name exactly |
| Generation does not recognize Kya | Install the `.apworld` into the **same Archipelago installation used for generation**, then regenerate |
| A Fast Travel or cinematic location has not checked | Some checks depend on live transitions and may not recover from a completed vanilla save; consult [known issues](known_issues.md) |
| Color Studio does not start | Check Python 3 and Pillow installation; this optional tool is separate from the precompiled Launcher |

**Known limits:** [known_issues.md](known_issues.md). **Credits and tools:** [CREDITS.md](../CREDITS.md).
