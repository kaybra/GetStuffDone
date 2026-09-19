import re

path = "www/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

old1 = "    --line: rgba(243,236,255,0.12);\n    --radius: 14px;\n  }"
new1 = "    --line: rgba(243,236,255,0.12);\n    --radius: 14px;\n    --kb-inset: 0px;\n  }"
if old1 in content:
    content = content.replace(old1, new1); changes += 1
else:
    print("WARNING: marker 1 (--kb-inset var) not found")

old2 = "  .sheet{\n    position: fixed;\n    left: 50%;\n    bottom: 0;\n    transform: translateX(-50%) translateY(16px);"
new2 = "  .sheet{\n    position: fixed;\n    left: 50%;\n    bottom: var(--kb-inset, 0px);\n    transform: translateX(-50%) translateY(16px);"
if old2 in content:
    content = content.replace(old2, new2); changes += 1
else:
    print("WARNING: marker 2 (.sheet bottom) not found")

old3 = "  let hideCompleted = false;\n\n  // Floating add buttons"
new3 = """  let hideCompleted = false;

  // Keeps the bottom sheets above the on-screen keyboard on iPad/iPhone
  // Safari (fixes: sheet opens but is hidden under the keyboard).
  function setupKeyboardAvoidance(){
    const vv = window.visualViewport;
    if(!vv) return;
    function update(){
      const inset = Math.max(0, window.innerHeight - vv.height - vv.offsetTop);
      document.documentElement.style.setProperty('--kb-inset', inset + 'px');
    }
    vv.addEventListener('resize', update);
    vv.addEventListener('scroll', update);
    update();
  }
  setupKeyboardAvoidance();

  // Floating add buttons"""
if old3 in content:
    content = content.replace(old3, new3); changes += 1
else:
    print("WARNING: marker 3 (setupKeyboardAvoidance) not found")

content = re.sub(r'<p class="version-tag">v[\d.]+</p>', '<p class="version-tag">v0.35</p>', content)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Applied {changes}/3 patches to {path}")
