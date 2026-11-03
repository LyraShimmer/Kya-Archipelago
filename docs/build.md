# Building from source

The complete **Python source** and the `.spec` files live in [`launcher/`](../launcher/). They are published so contributors can inspect and reproduce the executable.

The maintainer's one-click release BAT is stored in the **private preparation package**, not in the repository. Contributors may build the components on Windows with Python 3, PyInstaller and Pillow:

```powershell
cd launcher
py -3 -m pip install pyinstaller pillow
py -3 -m PyInstaller --noconfirm --clean KyaMemoryCore.spec
py -3 -m PyInstaller --noconfirm --clean KyaArchipelagoLauncher.spec
```

After compiling, package both EXEs, the entire `launcher/data/` folder and the optional Color Studio `launcher/tools/` folder. Include any required visual resources and verify that the compiled launcher starts a separate MemoryCore without needing source Python on the target computer.

**Important:** Reproducibility depends on external Python dependencies and the Windows environment. Version pinning and additional verification are recommended before a stable release.
