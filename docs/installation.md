# Installation Guide

Setting up web automation on Android can be tricky due to the differences between standard Linux environments and Termux. This guide will walk you through the process of setting up `playwright-termux` correctly.

## 1. Install Termux

If you haven't already, install Termux. **Do not install Termux from the Google Play Store**, as those versions are outdated and deprecated.

Instead, install it from **F-Droid** or download the latest APK directly from the [Termux GitHub Releases](https://github.com/termux/termux-app/releases).

## 2. Update System Packages

Once inside Termux, ensure all your base packages are up to date:

```bash
pkg update
pkg upgrade
```

## 3. Install Requirements

You need Python and the official Chromium browser package compiled specifically for Termux.

```bash
pkg install python chromium-browser
```

*Note: Standard Playwright installs its own browser binaries. We rely entirely on the Termux `chromium-browser` package, which is heavily patched to run under Android's Bionic libc.*

## 4. Install playwright-termux

Now you can install the library directly from PyPI via `pip`:

```bash
pip install playwright-termux
```

## 5. (Optional) Set Up Termux:X11 for Headed Mode

If you only want to scrape or run background tasks, you can stop here and use `headless=True`.

However, if you want to visually see the browser executing your code, you must set up an X11 server on Android.

1. Install the `Termux:X11` companion app from its [GitHub Releases](https://github.com/termux/termux-x11/releases) (or via the F-Droid Termux repository).
2. Inside the Termux terminal, install the X11 packages:
   ```bash
   pkg install x11-repo
   pkg install termux-x11-nightly
   ```
3. Start the Termux:X11 app on your phone.
4. In your Termux terminal, export the display variable before running your python script:
   ```bash
   export DISPLAY=:0
   python your_script.py
   ```
   *Make sure your script initializes `Chromium(headless=False)`.*

## Troubleshooting

- **Browser fails to launch:** Ensure `chromium-browser` is installed (`pkg install chromium-browser`).
- **"Headed Chromium requires an X11 display" error:** You attempted to run `headless=False` without setting the `DISPLAY` environment variable. Refer to step 5.
- **CDP Connection Timeouts:** If the browser launches but your script times out connecting, it might be due to a slow device. Ensure you aren't running out of RAM, as Chromium is very heavy.
