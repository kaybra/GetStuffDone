# v0.38 patch for www/index.html.
#
# Two things in this patch:
#
# 1. THE ACTUAL FIX for "sheet is invisible but tappable" (both the
#    single-chore add button and the multi-chore add button): opening a
#    sheet removed the `hidden` attribute and, one requestAnimationFrame
#    later, added a `.show` class that CSS uses to transition opacity
#    from 0 to 1. Inside WKWebView (the iOS app's web engine), those two
#    changes can get coalesced into a single style recalculation with no
#    reflow in between, which means the transition never gets a proper
#    starting frame -- and the element can be left stuck at its
#    pre-transition opacity (0) forever. It's still fully laid out and
#    clickable, which is exactly why tapping blindly where the buttons
#    should be "registered" for you. The fix forces a layout flush
#    (reading offsetHeight) between removing `hidden` and adding `.show`,
#    and uses a double requestAnimationFrame instead of a single one, so
#    the browser is guaranteed to paint the "before" state first.
#
# 2. An always-on-screen debug HUD (small green monospace text, top-left
#    corner) that logs button taps, both sheets' hidden/show state, and
#    the keyboard plugin's status live. There's no way to attach a
#    debugger to the wrapped app without a Mac, so this is the
#    replacement: screenshot it any time something looks wrong and that
#    tells us exactly what state the app thinks it's in.
#
# Run this from the root of your project (same folder as www/, next to
# capacitor.config.json) with: python3 apply_debug_hud_and_sheet_fix.py

path = "www/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# 1. Insert #debugHud markup right after <body>.
old1 = '<body>\n<div class="app">'
new1 = '''<body>
<!-- Temporary on-device debug HUD -- see apply_debug_hud_and_sheet_fix.py
     for why this exists. Remove once the app is confirmed stable. -->
<div id="debugHud" style="position:fixed;top:2px;left:2px;z-index:999999;background:rgba(0,0,0,0.82);color:#7CFC9A;font:9px/1.35 monospace;padding:5px 7px;border-radius:6px;max-width:280px;white-space:pre-wrap;pointer-events:none;"></div>
<div class="app">'''
if old1 in content:
    content = content.replace(old1, new1); changes += 1
else:
    print("WARNING: marker 1 (body/app) not found")

old2 = """  const STORAGE_KEY = 'chores:list';"""
new2 = """  const STORAGE_KEY = 'chores:list';
  // --- Debug HUD ---------------------------------------------------
  const debugHud = document.getElementById('debugHud');
  const debugLines = [];
  function debugLog(msg){
    const t = new Date();
    const ts = String(t.getHours()).padStart(2,'0') + ':' + String(t.getMinutes()).padStart(2,'0') + ':' + String(t.getSeconds()).padStart(2,'0');
    debugLines.push(ts + ' ' + msg);
    if(debugLines.length > 8) debugLines.shift();
    renderDebugHud();
  }
  function sheetState(el){
    if(!el) return 'missing';
    return 'hidden=' + el.hidden + ' show=' + el.classList.contains('show');
  }
  function renderDebugHud(){
    if(!debugHud) return;
    const capPresent = !!window.Capacitor;
    const kbPluginPresent = !!(window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Keyboard);
    const kbInset = document.documentElement.style.getPropertyValue('--kb-inset') || '(unset)';
    const snapshot = [
      'Capacitor: ' + capPresent + ' | Keyboard plugin: ' + kbPluginPresent,
      'kb-inset: ' + kbInset,
      'addSheet: ' + sheetState(document.getElementById('addSheet')),
      'multiSheet: ' + sheetState(document.getElementById('multiSheet'))
    ].join('\\n');
    debugHud.textContent = snapshot + '\\n---\\n' + debugLines.join('\\n');
  }
  debugLog('script started');"""
if old2 in content:
    content = content.replace(old2, new2); changes += 1
else:
    print("WARNING: marker 2 (STORAGE_KEY) not found")

old3 = """    const capKeyboard = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Keyboard;
    if(capKeyboard){
      capKeyboard.addListener('keyboardWillShow', (info) => {
        applyInset(info && info.keyboardHeight || 0, 'capacitor');
      });
      capKeyboard.addListener('keyboardDidShow', (info) => {
        applyInset(info && info.keyboardHeight || 0, 'capacitor');
      });
      capKeyboard.addListener('keyboardWillHide', () => applyInset(0, 'capacitor'));
      capKeyboard.addListener('keyboardDidHide', () => applyInset(0, 'capacitor'));
      if(dbg) dbg.textContent = 'kb-inset: 0px (source: capacitor, waiting for keyboard)';
      return;
    }

    const vv = window.visualViewport;
    if(!vv){
      if(dbg) dbg.textContent = 'kb-inset: unavailable (no Capacitor plugin, no visualViewport)';
      return;
    }
    function update(){
      applyInset(window.innerHeight - vv.height - vv.offsetTop, 'visualViewport');
    }
    vv.addEventListener('resize', update);
    vv.addEventListener('scroll', update);
    update();
  }
  setupKeyboardAvoidance();"""
new3 = """    const capKeyboard = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Keyboard;
    debugLog('setupKeyboardAvoidance: Capacitor=' + !!window.Capacitor + ' KeyboardPlugin=' + !!capKeyboard);
    if(capKeyboard){
      capKeyboard.addListener('keyboardWillShow', (info) => {
        debugLog('keyboardWillShow height=' + (info && info.keyboardHeight));
        applyInset(info && info.keyboardHeight || 0, 'capacitor');
        renderDebugHud();
      });
      capKeyboard.addListener('keyboardDidShow', (info) => {
        debugLog('keyboardDidShow height=' + (info && info.keyboardHeight));
        applyInset(info && info.keyboardHeight || 0, 'capacitor');
        renderDebugHud();
      });
      capKeyboard.addListener('keyboardWillHide', () => { debugLog('keyboardWillHide'); applyInset(0, 'capacitor'); renderDebugHud(); });
      capKeyboard.addListener('keyboardDidHide', () => { debugLog('keyboardDidHide'); applyInset(0, 'capacitor'); renderDebugHud(); });
      if(dbg) dbg.textContent = 'kb-inset: 0px (source: capacitor, waiting for keyboard)';
      return;
    }

    const vv = window.visualViewport;
    if(!vv){
      if(dbg) dbg.textContent = 'kb-inset: unavailable (no Capacitor plugin, no visualViewport)';
      debugLog('no visualViewport either -- no keyboard avoidance available');
      return;
    }
    function update(){
      applyInset(window.innerHeight - vv.height - vv.offsetTop, 'visualViewport');
      renderDebugHud();
    }
    vv.addEventListener('resize', update);
    vv.addEventListener('scroll', update);
    update();
  }
  setupKeyboardAvoidance();"""
if old3 in content:
    content = content.replace(old3, new3); changes += 1
else:
    print("WARNING: marker 3 (setupKeyboardAvoidance body) not found")

old4 = """  function openSheet(sheetEl, focusEl){
    openSheetEl = sheetEl;
    sheetBackdrop.hidden = false;
    sheetEl.hidden = false;
    window.requestAnimationFrame(() => {
      sheetBackdrop.classList.add('show');
      sheetEl.classList.add('show');
    });
    if(focusEl){
      window.setTimeout(() => focusEl.focus(), SHEET_TRANSITION_MS + 20);
    }
  }
  function closeSheet(){
    if(!openSheetEl) return;
    const el = openSheetEl;
    openSheetEl = null;
    el.classList.remove('show');
    sheetBackdrop.classList.remove('show');
    window.setTimeout(() => {
      el.hidden = true;
      sheetBackdrop.hidden = true;
    }, SHEET_TRANSITION_MS);
  }

  fabBtn.addEventListener('click', () => openSheet(addSheet, addInput));
  fabMultiBtn.addEventListener('click', () => openSheet(multiSheet, multiTitle));
  sheetBackdrop.addEventListener('click', () => closeSheet());"""
new4 = """  function openSheet(sheetEl, focusEl){
    debugLog('openSheet ' + (sheetEl && sheetEl.id));
    openSheetEl = sheetEl;
    sheetBackdrop.hidden = false;
    sheetEl.hidden = false;
    // Force a synchronous style/layout flush BEFORE the .show class is
    // added -- see the big comment at the top of this file for why.
    void sheetBackdrop.offsetHeight;
    void sheetEl.offsetHeight;
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        sheetBackdrop.classList.add('show');
        sheetEl.classList.add('show');
        debugLog('applied .show to ' + (sheetEl && sheetEl.id));
        renderDebugHud();
      });
    });
    if(focusEl){
      window.setTimeout(() => focusEl.focus(), SHEET_TRANSITION_MS + 20);
    }
    renderDebugHud();
  }
  function closeSheet(){
    if(!openSheetEl) return;
    debugLog('closeSheet ' + openSheetEl.id);
    const el = openSheetEl;
    openSheetEl = null;
    el.classList.remove('show');
    sheetBackdrop.classList.remove('show');
    window.setTimeout(() => {
      el.hidden = true;
      sheetBackdrop.hidden = true;
      renderDebugHud();
    }, SHEET_TRANSITION_MS);
    renderDebugHud();
  }

  fabBtn.addEventListener('click', () => { debugLog('fabBtn clicked'); openSheet(addSheet, addInput); });
  fabMultiBtn.addEventListener('click', () => { debugLog('fabMultiBtn clicked'); openSheet(multiSheet, multiTitle); });
  sheetBackdrop.addEventListener('click', () => closeSheet());"""
if old4 in content:
    content = content.replace(old4, new4); changes += 1
else:
    print("WARNING: marker 4 (openSheet/closeSheet/FAB listeners) not found")

if '<p class="version-tag">v0.37</p>' in content:
    content = content.replace('<p class="version-tag">v0.37</p>', '<p class="version-tag">v0.38</p>')
    changes += 1
else:
    print("WARNING: version tag v0.37 not found (may already be a different version -- check manually)")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Applied {changes}/5 patches to {path}")
