import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import { sentryVitePlugin } from "@sentry/vite-plugin";
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    server: {
      port: 3000,
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    },
    plugins: [
      react(),
      sentryVitePlugin({
        org: process.env.SENTRY_ORG, // Configure via .env
        project: process.env.SENTRY_PROJECT, // Configure via .env
        authToken: process.env.SENTRY_AUTH_TOKEN, // Configure via .env
      })
    ],
    define: {
      'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      }
    }
  };
});
