# Maintainer release procedure

The full source belongs in the **repository**. The three player downloads belong to a GitHub **Release** tagged `9.0.0-beta1`.

1. Review published source code, docs, research data, third-party attributions and rights.
2. Verify the chosen source license and credits.
3. Run the private `BUILD_RELEASE_ON_WINDOWS.bat` from this preparation package on Windows.
4. Check the resulting `Release_Assets/Launcher.zip` contains `Kya_Archipelago_Launcher.exe`, `Kya_MemoryCore.exe`, `data/` and Color Studio.
5. Validate opening the Launcher and connecting to a real test room with PCSX2.
6. Publish the source tree (`Github/` contents) as the repository and attach **exactly three** files from `Release_Assets/` to the beta release.

Do not upload ISO images, disk extracts, savestates, memory dumps or proprietary game files just to make a bigger repository.
