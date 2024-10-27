# PDF Flipbook SaaS

A modern web application that transforms PDF documents into interactive digital flipbooks with customization options, analytics, and sharing capabilities.

## Features

- **PDF to Flipbook Conversion**: 
  - Upload PDFs and convert them into interactive flipbooks
  - Support for multiple page PDFs
  - Automatic image conversion and optimization

- **Interactive Viewer**: 
  - Smooth page turning animations using turn.js
  - Zoom controls for better readability
  - Keyboard navigation support
  - Responsive design for various screen sizes

- **User Management**:
  - Secure authentication system
  - User registration and login
  - JWT-based API authentication
  - Refresh token functionality

- **Customization Options**:
  - Custom logos
  - Background color customization
  - CSS customization capabilities
  - Responsive layout options

- **Analytics Dashboard**:
  - View count tracking
  - 7-day view history chart
  - Per-flipbook statistics
  - Page-level analytics

- **Sharing and Embedding**:
  - Share links for easy distribution
  - Embed code generation
  - Iframe support for external websites
  - Toast notifications for user feedback

## Deployment on Replit

1. Fork the project on Replit:
   - Visit [Replit](https://replit.com)
   - Create a new repl
   - Choose "Import from GitHub"
   - Enter the repository URL: `https://github.com/Tardextrad/pdf-flipbook-saas.git`

2. Set up environment variables in Replit:
   - Go to the "Secrets" tab in your repl
   - Add the following environment variables:
     - `FLASK_SECRET_KEY`: A secure random string for session encryption
     - `DATABASE_URL`: PostgreSQL database URL (automatically set by Replit)
     - `PORT`: Server port (default: 8080)

3. Install Dependencies:
   - The project will automatically install required dependencies on first run
   - Dependencies are managed through the Replit packager system
   - If needed, you can manually install packages using the Packages tab

4. Database Setup:
   - The PostgreSQL database is automatically provisioned by Replit
   - Run migrations to set up the database schema:
     ```bash
     python migrations.py
     ```

5. Start the Application:
   - Click the "Run" button in Replit
   - The server will start automatically on port 8080
   - Your application will be available at your Replit URL

6. Continuous Deployment:
   - Replit automatically detects changes and restarts the application
   - The application uses Replit's always-on feature to maintain uptime
   - Database connections are automatically managed by Replit

7. Monitoring:
   - Use Replit's built-in console to monitor logs
   - Check the "Shell" tab for any error messages
   - Monitor database status in the "Database" tab

8. Troubleshooting:
   - If the application fails to start, check the console for error messages
   - Verify all required secrets are set in the Secrets tab
   - Ensure the database is properly initialized
   - Use the "Stop" and "Run" buttons to restart the application if needed

## API Documentation

### Authentication

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password"
}
```

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "username",
    "email": "user@example.com",
    "password": "password"
}
```

#### Refresh Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
    "refresh_token": "your_refresh_token"
}
```

### Flipbooks

#### List Flipbooks
```http
GET /api/flipbooks
Authorization: Bearer your_access_token
```

#### Get Flipbook
```http
GET /api/flipbooks/<unique_id>
Authorization: Bearer your_access_token
```

## Screenshots

### Home Page
![Home Page](static/screenshots/home.png)
- Clean, minimalist landing page
- Quick access to registration and login
- Dark theme for better readability

### Dashboard
![Dashboard](static/screenshots/dashboard.png)
- Overview of all flipbooks
- Statistics and analytics
- Easy access to create new flipbooks

### Flipbook Viewer
![Flipbook Viewer](static/screenshots/viewer.png)
- Interactive page turning
- Zoom controls
- Sharing and embedding options

### Analytics Dashboard
![Analytics](static/screenshots/analytics.png)
- View count tracking
- 7-day view history chart
- Per-flipbook statistics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [turn.js](https://www.turnjs.com/) for the flipbook effect
- [Chart.js](https://www.chartjs.org/) for analytics visualization
- [Bootstrap](https://getbootstrap.com/) for UI components
- [Flask](https://flask.palletsprojects.com/) for the web framework
