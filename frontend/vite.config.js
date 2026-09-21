import { resolve } from "path";
import { defineConfig } from "vite";

export default defineConfig({
  root: "./",
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
