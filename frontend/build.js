const fs = require("fs");
const path = require("path");

const rootDir = __dirname;
const distDir = path.join(rootDir, "dist");

function copyDir(src, dest) {
  if (!fs.existsSync(src)) return;
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// 1. Clean dist directory
if (fs.existsSync(distDir)) {
  fs.rmSync(distDir, { recursive: true, force: true });
}
fs.mkdirSync(distDir, { recursive: true });

// 2. Copy all HTML files to dist
const rootEntries = fs.readdirSync(rootDir, { withFileTypes: true });
for (const entry of rootEntries) {
  if (entry.isFile() && entry.name.endsWith(".html")) {
    fs.copyFileSync(path.join(rootDir, entry.name), path.join(distDir, entry.name));
    console.log(`Copied HTML: ${entry.name}`);
  }
}

// 3. Copy css, js, and images directories
copyDir(path.join(rootDir, "css"), path.join(distDir, "css"));
copyDir(path.join(rootDir, "js"), path.join(distDir, "js"));
copyDir(path.join(rootDir, "images"), path.join(distDir, "images"));

console.log("✓ Production static build completed successfully in dist/");
