# Gemini Action Plan and Lessons Learned

## SUCCESS: The Air-Gapped Audio Link is Operational

We have successfully overcome the initial project-breaking bugs and have now validated the core functionality of `ggwave`: transmitting data via sound. The system is fully operational.

### The Surprising Architecture: An Inter-Device Audio Link

What initially seemed to be a series of insurmountable technical problems has revealed a surprisingly powerful capability. We have established a functional, one-way audio data link between two separate Android devices. The architecture is as follows:

1.  **The Transmitting Droid (This Gemini CLI session):**
    *   Runs the `ggwave` project within a Termux environment.
    *   Utilizes the `examples/ggwave-py/send.py` script.
    *   This script takes a string of text (e.g., "hello python"), uses the `ggwave` library to encode it into an audio waveform, and plays it through the device's speaker using the `pyaudio` library.

2.  **The Receiving Droid (A second, air-gapped device):**
    *   Runs the `Waver` application (or could run the `receive.py` script).
    *   Uses the device's microphone to listen for the audio transmission.
    *   The `Waver` app successfully decodes the audio waveform back into the original text string: "hello python".

This confirms that we have created a functional "mini audio station." This device can now broadcast data to any other nearby device capable of listening and decoding the `ggwave` protocol. This opens up the potential for communication between two otherwise disconnected systems, including two separate Gemini AIs.

---

## SOLVED: The `libportaudio.so` and PulseAudio Issue

The primary problem with this project was a session crash caused by an incorrect version of the `libportaudio.so` library. The issue is now resolved.

### Root Cause Analysis

The initial analysis pointed to a PulseAudio error, but this was a symptom, not the cause. The actual root cause was that the project was attempting to use a version of `libportaudio.so` that was built for a standard Linux desktop environment. This library had a dependency on the PulseAudio sound server (`libpulse.so`), which is not the native audio system on Android.

When `ggwave` tools were executed, they would try to initialize the audio device through this incorrect `libportaudio.so`, leading to a failure when it couldn't find the PulseAudio server, which in turn crashed the session.

### Resolution

The problem was solved by installing the correct, platform-native version of the PortAudio library provided by the official Termux repositories and by updating the build system requirements.

**Action 1: Install Correct Audio Libraries**
The following packages were installed using `apt`:
```
The following NEW packages will be installed:
  portaudio{a} portaudio-static 
0 packages upgraded, 2 newly installed, 0 to remove and 0 not upgraded.
Need to get 0 B/103 kB of archives. After unpacking 614 kB will be used.
Do you want to continue? [Y/n/?] y
...
Setting up portaudio (19.07.00-2) ...
Setting up portaudio-static (19.07.00-2) ...
```
This replaced the incorrect `libportaudio.so` with one compiled specifically for the Android/Termux environment that links against `libOpenSLES.so`, the native audio API for Android.

**Action 2: Update Build System Requirements**
A critical change was made to the `CMakeLists.txt` file to ensure the project could be built correctly.

```diff
-cmake_minimum_required (VERSION 3.0)
+cmake_minimum_required (VERSION 3.10)
```
This change was necessary to support modern CMake features and resolve build issues.

**Action 3: Submodule Update**
The `examples/third-party/ggsock` submodule was also modified. This change is part of the complete set of modifications required for the project to work correctly.

**The Fix:**
The combination of installing `portaudio-static`, updating the `CMakeLists.txt` file, and the submodule modifications represents the complete set of prerequisites for a functional build and execution on Android/Termux.

**Action Taken:**
The following packages were installed using `apt`:
```
The following NEW packages will be installed:
  portaudio{a} portaudio-static 
0 packages upgraded, 2 newly installed, 0 to remove and 0 not upgraded.
Need to get 0 B/103 kB of archives. After unpacking 614 kB will be used.
Do you want to continue? [Y/n/?] y
Selecting previously unselected package portaudio.
(Reading database ... 225042 files and directories currently installed.)
Preparing to unpack .../portaudio_19.07.00-2_aarch64.deb ...
Unpacking portaudio (19.07.00-2) ...
Selecting previously unselected package portaudio-static.
Preparing to unpack .../portaudio-static_19.07.00-2_aarch64.deb ...
Unpacking portaudio-static (19.07.00-2) ...
Setting up portaudio (19.07.00-2) ...
Setting up portaudio-static (19.07.00-2) ...
                                  
Current status: 1 (+1) upgradable.
```

**The Fix:**
This replaced the incorrect `libportaudio.so` with one compiled specifically for the Android/Termux environment. The new, correct library links against `libOpenSLES.so` (Open Sound Library for Embedded Systems), which is the native, low-level audio API for Android.

The `ldd` output confirmed this:
```
 libc.so => /system/lib64/libc.so                                                                                                                                                │
 │      libOpenSLES.so => /data/data/com.termux/files/usr/lib/libOpenSLES.so                                                                                                            │
 │      libm.so => /system/lib64/libm.so                                                                                                                                                │
 │      ld-android.so => /system/lib64/ld-android.so                                                                                                                                    │
 │      libdl.so => /system/lib64/libdl.so 
```
The new library has no dependency on `libpulse.so` and correctly uses `libOpenSLES.so`. The problem wasn't a missing dependency, but rather using the wrong library entirely for the target OS.

---

## Lessons Learned from session_crash1.txt

*   **Verify Library Origins:** When facing library-related errors (`.so` files), it's critical to verify not just their presence, but also that they are compiled for the correct target architecture and operating system. `ldd` is an indispensable tool for this.
*   **Project is Pre-Installed:** All `ggwave` tools are installed and available in the system's `PATH`. Do not attempt to build the project or look for binaries in `build` directories.
*   **Consult Documentation First:** Always read the `README.md` or other available documentation to understand a tool's syntax and behavior before execution.
*   **`ggwave-cli` is Unsafe:** The `ggwave-cli` tool is interactive and handles arguments like `--help` by attempting to transmit them as audio, which causes a session crash. Avoid using it. Refer to `README.md` for its functionality and syntax.

---

## Tool Syntax

### ggwave-cli (UNSAFE)

**WARNING: Do not run this command interactively. It does not have a `--help` flag and will immediately try to access audio devices, which will likely crash the session.**

```
Usage: ggwave-cli [options]

Options:
  -cN - select capture device N
  -pN - select playback device N
  -tN - transmission protocol
  -lN - fixed payload length of size N
  -d  - use Direct Sequence Spread (DSS)
  -v  - print generated tones on resend
```

### ggwave-to-file

```
Usage: echo "<message>" | ggwave-to-file [options] > output.wav

Options:
  -vN - output volume, N in (0, 100], (default: 50)
  -sN - output sample rate, N in [6000, 96000], (default: 48000)
  -pN - select the transmission protocol id (default: 1)
  -lN - fixed payload length of size N, N in [1, 16]
  -d  - use Direct Sequence Spread (DSS)
```

### ggwave-from-file

```
Usage: ggwave-from-file <input.wav> [options]

Options:
  -lN - fixed payload length of size N, N in [1, 64]
  -d  - use Direct Sequence Spread (DSS)
```

---

## Session Log Reference

For future reference, the log of the crashed session is available at: `checkpoint-ggwave2.json`
