# Media Forensics Frontend

This directory contains the React/Vite client for the Media Forensics Platform. It provides a small analyst workspace for uploading images, reviewing forensic results, and switching between scans from the current browser session.

The backend service must be running separately from the repository root. See the [root project README](../README.md) for full setup instructions.

## What It Does

- Shows a client-side demo login screen
- Accepts image files through the upload control
- Sends images to `POST http://127.0.0.1:8000/upload`
- Displays metadata, AI-generation signals, ELA manipulation results, and the combined verdict
- Keeps scan history in memory while the page is open
- Provides dashboard totals for scanned and flagged files

The login is only a frontend demo gate. It does not create accounts or authenticate against the backend.

## Setup

From this directory:

```bash
npm install
```

Start the development server:

```bash
npm run dev -- --host 0.0.0.0 --port 5173
```

Then open `http://localhost:5173`.

The demo credentials are displayed on the login screen. The backend must be available at `http://127.0.0.1:8000` for analysis requests to succeed.

## Scripts

| Command | Purpose |
| --- | --- |
| `npm run dev` | Start the Vite development server with hot reload |
| `npm run build` | Create a production build in `dist/` |
| `npm run lint` | Run ESLint against the frontend source |
| `npm run preview` | Preview the production build locally |

## Main Files

- `src/App.jsx`: login flow, upload request, scan history, and result rendering
- `src/App.css`: dashboard and login-page styles
- `src/index.css`: global styles and typography defaults
- `src/main.jsx`: React application entry point
- `vite.config.js`: Vite configuration

## Configuration Notes

The API URL is currently defined directly in `src/App.jsx` as `http://127.0.0.1:8000/upload`. Update that URL when connecting the frontend to a different backend host or deployment environment.

This client does not persist uploaded files or scan history. Refreshing the page clears the current investigation session.
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
