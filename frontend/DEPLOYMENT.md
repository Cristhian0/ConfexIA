# Frontend Deployment Guide

## Vercel Configuration

This Angular application is configured to deploy on Vercel with the following setup:

### Key Files:
- `vercel.json` - Build and routing configuration
- `angular.json` - Build output path: `dist/pati-confeccion`
- `.env.production` - API URL configuration

### Deployment Steps:

1. **Push changes to repository**
```bash
git add .
git commit -m "message"
git push
```

2. **Deploy to Vercel**
- Go to https://vercel.com/dashboard
- Click "Add New" → "Project"
- Import the repository
- Framework: Angular
- Root Directory: `frontend/`
- Build Command: `npm run build`
- Install Command: `npm install`
- Leave other settings as default
- Click "Deploy"

3. **Configure API Connection**
- Once deployed, Vercel will provide the frontend URL
- Update backend environment variable `FRONTEND_URL` with this URL
- Backend at: https://confecciones-zsoi.vercel.app

### Important Notes:

- The frontend automatically routes API calls to `/api/:path*` which proxies to the backend
- All routes not matching `/api` are redirected to `/index.html` for Angular routing
- API calls use the URL: `https://confecciones-zsoi.vercel.app/api/v1`

### If you get 404 error:

1. Check that `outputDirectory` in `vercel.json` matches `angular.json` build output path
2. Verify `npm run build` completes successfully locally
3. Check that `index.html` exists in the built output: `dist/pati-confeccion/index.html`
4. Ensure rewrites in `vercel.json` are correctly configured for SPA routing

### Local Development:

```bash
npm install
ng serve
# Navigate to http://localhost:4200
```

