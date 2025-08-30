# Frontend Setup Guide

This directory contains the React frontend for the Repo Insight Generator.

## Prerequisites

- Node.js 16.x or higher
- npm or yarn package manager

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Create environment variables file (optional):
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set:
   ```
   REACT_APP_API_URL=http://localhost:8000/api
   ```

## Development

Start the development server:
```bash
npm start
# or
yarn start
```

The application will be available at http://localhost:3000

## Building for Production

Create a production build:
```bash
npm run build
# or
yarn build
```

The built files will be in the `build/` directory.

## Project Structure

```
src/
├── components/         # Reusable React components
│   ├── Header.js      # Navigation header
│   ├── Footer.js      # Page footer
│   ├── LoadingSpinner.js
│   ├── StatusBadge.js
│   ├── ExportButtons.js
│   └── RepositoryCard.js
├── pages/             # Main page components
│   ├── Home.js        # Repository analysis form
│   ├── AnalysisResult.js # Analysis results display
│   └── History.js     # Analysis history
├── services/          # API and utility services
│   └── api.js        # Backend API integration
├── App.js            # Main application component
├── index.js          # Application entry point
└── index.css         # Global styles (Tailwind CSS)
```

## Key Features

- **Repository Analysis Form**: Input field for GitHub URLs with validation
- **Real-time Analysis**: Live updates during analysis process
- **Results Display**: Comprehensive visualization of analysis results
- **Export Options**: Download analysis in multiple formats
- **History Management**: View and manage past analyses
- **Responsive Design**: Works on desktop and mobile devices

## API Integration

The frontend communicates with the Django backend through REST APIs:

- `POST /api/analyze/` - Analyze repository
- `GET /api/analysis/{id}/` - Get analysis results
- `POST /api/export/{format}/{id}/` - Export analysis
- `GET /api/download/{format}/{id}/` - Download exported file
- `GET /api/analyses/` - List all analyses

## Styling

The application uses:
- **Tailwind CSS** for utility-first styling
- **Custom CSS classes** for component-specific styles
- **Responsive design** with mobile-first approach
- **Dark/light mode** support (can be added in future)

## Error Handling

- Form validation for repository URLs
- API error handling with user-friendly messages
- Loading states for better user experience
- Toast notifications for feedback

## Development Tips

1. **Hot Reload**: Changes to source files automatically refresh the browser
2. **API Proxy**: Development server proxies API requests to `http://localhost:8000`
3. **Console Logging**: Check browser console for debugging information
4. **Network Tab**: Monitor API requests in browser developer tools

## Troubleshooting

### Common Issues

1. **API Connection Errors**:
   - Ensure Django backend is running on port 8000
   - Check CORS configuration in Django settings
   - Verify API URL in environment variables

2. **Build Errors**:
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check for syntax errors in React components
   - Ensure all imports are correct

3. **Styling Issues**:
   - Rebuild Tailwind CSS: `npm run build:css`
   - Check for conflicting CSS classes
   - Verify Tailwind configuration

### Performance Optimization

- Use React.memo() for expensive components
- Implement code splitting with React.lazy()
- Optimize images and assets
- Use production build for deployment

## Deployment

### Using Nginx

1. Build the application:
   ```bash
   npm run build
   ```

2. Configure Nginx to serve static files:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       root /path/to/build;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Using Docker

Create a Dockerfile:
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npx", "serve", "-s", "build", "-l", "3000"]
```

## Contributing

1. Follow React best practices
2. Use functional components with hooks
3. Write descriptive component and function names
4. Add PropTypes for component props
5. Test components thoroughly