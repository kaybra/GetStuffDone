// One-off fixer: splices the real celebration GIF into www/index.html,
// replacing the CELEBRATE_GIF_BASE64 placeholder string.
//
// Usage (from the repo root, with celebrate.gif sitting next to this script
// or path passed as an argument):
//   node fix-celebrate-gif.js [path/to/celebrate.gif] [path/to/www/index.html]

const fs = require('fs');
const path = require('path');

const gifPath = process.argv[2] || path.join(__dirname, 'celebrate.gif');
const htmlPath = process.argv[3] || path.join(__dirname, 'www', 'index.html');

if (!fs.existsSync(gifPath)) {
  console.error(`GIF not found at ${gifPath}`);
  process.exit(1);
}
if (!fs.existsSync(htmlPath)) {
  console.error(`index.html not found at ${htmlPath}`);
  process.exit(1);
}

const gifBuffer = fs.readFileSync(gifPath);
const base64 = gifBuffer.toString('base64');

let html = fs.readFileSync(htmlPath, 'utf8');

const placeholderPattern = /CELEBRATE_GIF_BASE64\s*=\s*"REPLACE_WITH_ACTUAL_GIF_BASE64"/;
const alreadyDonePattern = /CELEBRATE_GIF_BASE64\s*=\s*"[A-Za-z0-9+/=]{100,}"/;

if (placeholderPattern.test(html)) {
  html = html.replace(
    placeholderPattern,
    `CELEBRATE_GIF_BASE64 = "${base64}"`
  );
  fs.writeFileSync(htmlPath, html, 'utf8');
  console.log(`Done. Spliced ${gifBuffer.length} bytes of GIF data into ${htmlPath}.`);
} else if (alreadyDonePattern.test(html)) {
  console.log('Looks like the placeholder is already replaced with real data — nothing to do. (Delete this check and re-run if you actually want to overwrite it.)');
} else {
  console.error('Could not find CELEBRATE_GIF_BASE64 in the expected format. Check the file by hand.');
  process.exit(1);
}
