# GSD MCH

A chore-tracking app. Wrapped with Capacitor for iOS and Android distribution.

## Local setup

```
npm install
npx cap add ios
npx cap sync
```

The web app itself lives in `www/index.html` — a single self-contained file, no build step.

## App icons and splash screen

`resources/icon.png` (1024×1024) and `resources/splash.png` (2732×2732) are the source images. Generate every platform-specific size from them with:

```
npm install @capacitor/assets --save-dev
npx capacitor-assets generate --iconBackgroundColor '#180b2e' --splashBackgroundColor '#180b2e'
```

Run this after `npx cap add ios` (so the `ios/` folder exists for it to populate) and again any time `resources/icon.png` or `resources/splash.png` changes. Then run `npx cap sync` to make sure Xcode picks up the update.

## Privacy policy

`privacy.html` is a standalone privacy policy page required by Apple for App Store submission, even though this app collects no data. It needs to be hosted at a public URL before it can be linked in App Store Connect — the easiest option is GitHub Pages, since this repo is already on GitHub:

1. On GitHub, go to this repo's **Settings** → **Pages**
2. Under **Source**, choose **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)` → **Save**
4. After a minute or two, the policy will be live at `https://kaybra.github.io/GetStuffDone/privacy.html`

That URL is what goes in App Store Connect's "Privacy Policy URL" field.

## Android

The `android/` folder is the Capacitor Android project (package `com.getstuffdone.gsdmch`, same as iOS). It targets Android 16 / API 36, which Google Play requires for new apps from 31 August 2026.

- **Build:** the `GSD MCH - Android (Play .aab)` workflow in `codemagic.yaml` produces a signed `.aab` (Play needs an AAB, not an APK). It is started manually from Codemagic.
- **Version:** `versionName` is `package.json`'s `version` (same as iOS); `versionCode` is Codemagic's `$BUILD_NUMBER`.
- **Icons and splash:** regenerate with `pip install pillow && python generate-android-icons.py` after changing anything in `icons/` or `resources/`. It also writes the Play Store icon and feature graphic to `store/android/`.
- **Home-screen icon choice:** the in-app "App Icon" setting works on Android through three `<activity-alias>` entries in `AndroidManifest.xml` and `AppIconPlugin.java`.
- **Signing keys** (`*.jks`, `*.keystore`) are git-ignored. Keep the upload keystore and its passwords somewhere safe, outside this repo.
- After changing `www/index.html`, run `npx cap sync android` before building locally.
