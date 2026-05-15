# Gemini Action Plan and Lessons Learned (Finalized)

## STATUS: PRODUCTION READY

We have fully stabilized the `ggwave` project. The core C++ library, the CLI tools, and the Python bindings are now robustly integrated and verified across multiple environments (Linux Desktop and Android/Termux).

### The "One Workflow" Installation

The project has been engineered so that a standard build and install process works everywhere, handling tool name collisions and missing dependencies automatically.

**Prerequisites:**
```bash
# Ubuntu/Debian
sudo apt install cmake make build-essential libsdl2-dev python3-dev python3-pip

# Python tools (for Git-based development)
pip install cython cogapp --user
```

**Standard Installation:**
```bash
# 1. Configure with all features enabled
cmake . -DGGWAVE_SUPPORT_PYTHON=ON

# 2. Build everything as a regular user
make

# 3. System-wide installation
sudo make install
```

### Key Technical Resolutions

1.  **`ggwave-cli` Pipe Support:**
    *   Patched `main.cpp` to detect EOF (End of File) when reading from a pipe.
    *   Implemented a graceful exit that waits for the audio buffer to finish playing before terminating.
    *   Example: `echo "All is done" | ggwave-cli`

2.  **Python Binding Stability:**
    *   Fixed a critical syntax error in `setup-tmpl.py` regarding `long_description`.
    *   Robustified the `Makefile` to prioritize `python3 -m cogapp`, avoiding collisions with the Replicate `cog` CLI.
    *   Documented the need for `--no-build-isolation` when building from source.

3.  **Termux/Android Portability:**
    *   **Imgui Paths:** Fixed build failures on Termux by using `${CMAKE_CURRENT_SOURCE_DIR}` for `imgui-extra` source paths to ensure absolute resolution.
    *   **Build Environment:** Recommended using a custom build wrapper (like the user's `cmakeinstall`) to pass `CMAKE_INSTALL_PREFIX` and `CXXFLAGS` correctly in non-standard environments.
    *   **Permissions:** Always build in a local directory as a regular user, and only use `sudo` for the final `make install` step to prevent ownership conflicts.

---

## Lessons Learned

*   **Packaging vs. Source:** Consumers should favor `pip install`, but developers using the Git repo must use the `make ggwave` syncing step to bring C++ sources into the Python environment.
*   **Tool Collisions:** System-level binaries (like `cog`) can shadow Python modules. Always favor `python3 -m <module>` for build scripts.
*   **Termux Compatibility:** Android/Termux environments require careful handling of paths in CMake (`CMAKE_CURRENT_SOURCE_DIR`) and environment-specific libraries (`libOpenSLES.so` vs `libpulse.so`).
*   **Unix Philosophy:** Tools should handle pipes gracefully. Always check `isatty()` and handle EOF to avoid infinite loops in CLI utilities.
*   **Build First, Sudo Later:** Always perform the compilation as a regular user to preserve environment context, using `sudo` only for the final `cp` (install) phase.
