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

## Technologies Used

- **Backend**:
  - Flask (Python web framework)
  - SQLAlchemy (ORM)
  - JWT for API authentication
  - pdf2image for PDF processing

- **Frontend**:
  - Bootstrap 5 (Dark theme)
  - turn.js for flipbook effects
  - Chart.js for analytics visualization
  - Vanilla JavaScript

- **Database**:
  - PostgreSQL

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Tardextrad/pdf-flipbook-saas.git
cd pdf-flipbook-saas
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
FLASK_SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://username:password@host:port/database
```

4. Initialize the database:
```bash
python migrations.py
```

5. Start the server:
```bash
python main.py
```

The application will be available at `http://localhost:8080`

## Usage Guide

### Creating a Flipbook

1. Register/Login to your account
2. Navigate to the dashboard
3. Click "Create New Flipbook"
4. Upload your PDF file and provide a title
5. Wait for conversion to complete
6. Access your flipbook from the dashboard

### Viewing and Sharing

1. Open any flipbook from your dashboard
2. Use arrow keys or click arrows to navigate pages
3. Use zoom controls to adjust view
4. Click "Share" to copy the sharing link
5. Click "Embed" to get the embed code for your website

### Analytics

1. Navigate to the Analytics dashboard
2. View total views for each flipbook
3. Check the 7-day view history chart
4. Monitor user engagement metrics

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

## Environment Variables

Required environment variables:

- `FLASK_SECRET_KEY`: Secret key for Flask session and JWT
- `DATABASE_URL`: PostgreSQL database URL
- `PORT`: Server port (default: 8080)

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
