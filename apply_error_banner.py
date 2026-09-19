path = "www/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

old1 = "(function(){\n  const STORAGE_KEY = 'chores:list';"
new1 = """(function(){
  // Everything below runs inside this try/catch so that if anything
  // throws, the failure is visible on screen as a red banner instead of
  // silently leaving every button unresponsive.
  try{
  const STORAGE_KEY = 'chores:list';"""
if old1 in content:
    content = content.replace(old1, new1); changes += 1
else:
    print("WARNING: marker 1 (start of IIFE) not found")

old2 = "  load();\n})();\n</script>"
new2 = """  load();
  } catch(err){
    try{
      var errBanner = document.createElement('div');
      errBanner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:#c0392b;color:#fff;padding:10px 14px;font:12px/1.4 monospace;white-space:pre-wrap;max-height:45vh;overflow:auto;';
      errBanner.textContent = 'JS ERROR: ' + ((err && (err.stack || err.message)) || err);
      document.body.appendChild(errBanner);
    }catch(err2){}
  }
})();
</script>"""
if old2 in content:
    content = content.replace(old2, new2); changes += 1
else:
    print("WARNING: marker 2 (end of IIFE) not found")

if '<p class="version-tag">v0.35</p>' in content:
    content = content.replace('<p class="version-tag">v0.35</p>', '<p class="version-tag">v0.36</p>')
else:
    print("WARNING: version tag v0.35 not found (may already be a different version — check manually)")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Applied {changes}/2 patches to {path}")
