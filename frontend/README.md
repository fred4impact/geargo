# GearGo Frontend

Modern React + TypeScript frontend for the GearGo rental marketplace, built with Vite.

## Features

- ⚡ **Fast Development** - Vite for instant HMR
- 🎨 **Modern UI** - Clean, responsive design with GearGo branding
- 🔐 **Authentication** - Token and session-based auth
- 📱 **Responsive** - Works on all devices
- 🚀 **Production Ready** - Optimized build with Nginx

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **TanStack Query** - Data fetching and caching
- **Nginx** - Production web server

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file (optional):
```env
VITE_API_URL=http://localhost:8000/api
```

3. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Production

### Docker

The frontend is containerized with a multi-stage Docker build:

1. Build stage: Compiles the React app
2. Production stage: Serves with Nginx

To build and run:
```bash
docker-compose up frontend
```

The frontend will be available at `http://localhost:3000`

### Manual Build

1. Build the app:
```bash
npm run build
```

2. Serve the `dist` folder with any static file server

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client and endpoints
│   ├── components/    # Reusable components
│   ├── context/       # React context providers
│   ├── pages/         # Page components
│   ├── types/         # TypeScript type definitions
│   ├── App.tsx        # Main app component
│   └── main.tsx       # Entry point
├── public/            # Static assets
├── Dockerfile         # Production Docker image
├── nginx.conf         # Nginx configuration
└── vite.config.ts     # Vite configuration
```

## API Integration

The frontend communicates with the Django backend API at `/api/`. All API calls are handled through:

- `src/api/client.ts` - Axios instance with interceptors
- `src/api/endpoints.ts` - API endpoint functions
- `src/context/AuthContext.tsx` - Authentication context

## Features Implemented

- ✅ User authentication (login/logout)
- ✅ Item browsing and search
- ✅ Item detail view
- ✅ Create new items
- ✅ Booking management
- ✅ User dashboard
- ✅ Profile management
- ✅ Responsive design
- ✅ Category filtering

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000/api`)

## Notes

- The frontend uses session-based authentication with fallback to token auth
- All API requests include credentials for CORS
- The production build is optimized and served via Nginx
- The frontend proxies API requests in development via Vite
