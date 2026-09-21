import fs from "fs";
import path, { resolve } from "path";
import { defineConfig } from "vite";

function copyStaticAssets() {
  return {
    name: "copy-static-assets",
    closeBundle() {
      const copyDir = (src, dest) => {
        if (!fs.existsSync(src)) return;
        fs.mkdirSync(dest, { recursive: true });
        for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
          const srcPath = path.join(src, entry.name);
          const destPath = path.join(dest, entry.name);
          if (entry.isDirectory()) {
            copyDir(srcPath, destPath);
          } else {
            fs.copyFileSync(srcPath, destPath);
          }
        }
      };
      copyDir(resolve(__dirname, "js"), resolve(__dirname, "dist/js"));
      copyDir(resolve(__dirname, "images"), resolve(__dirname, "dist/images"));
      copyDir(resolve(__dirname, "css"), resolve(__dirname, "dist/css"));
    },
  };
}

export default defineConfig({
  root: "./",
  plugins: [copyStaticAssets()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    reportCompressedSize: false,
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
        login: resolve(__dirname, "login.html"),
        dashboard: resolve(__dirname, "dashboard.html"),
        users: resolve(__dirname, "users.html"),
        results: resolve(__dirname, "results.html"),
        materials: resolve(__dirname, "materials.html"),
        attendance: resolve(__dirname, "attendance.html"),
        courses: resolve(__dirname, "courses.html"),
        events: resolve(__dirname, "events.html"),
        notices: resolve(__dirname, "notices.html"),
        profile: resolve(__dirname, "profile.html"),
        settings: resolve(__dirname, "settings.html"),
        doc: resolve(__dirname, "doc.html"),
      },
    },
  },
});
