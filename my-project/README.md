# DataViz Pro - Modern Data Visualization Dashboard

A modern, interactive data visualization platform built with **React**, **Vite**, **Tailwind CSS**, and **FastAPI**.

## 🚀 Tech Stack

### Frontend
- **React 19.1.1** - Modern UI library
- **Vite 7.1.7** - Fast build tool
- **Tailwind CSS 3.4.18** - Modern utility-first CSS
- **React Router DOM 6** - Client-side routing
- **Axios** - HTTP client with interceptors
- **Recharts** - Beautiful chart library
- **Lucide React** - Modern icon library

### Backend
- **FastAPI 0.109.0** - High-performance Python API
- **Firebase Admin SDK 6.4.0** - Authentication & Firestore
- **Pandas 2.1.4** - Data processing
- **JWT Authentication** - Secure token-based auth

## ✨ Features

- 📊 **Interactive Charts** - Bar, Line, and Pie charts with Recharts
- 📋 **Smart Tables** - Sortable, searchable, paginated data tables
- 📁 **File Upload** - Drag-and-drop CSV/Excel file uploads
- 🌓 **Dark Mode** - Toggle between light and dark themes
- 🔐 **Authentication** - Secure JWT-based auth with Firebase
- 📱 **Responsive Design** - Works on all devices
- ⚡ **Fast Performance** - Backend processing with Vite builds

## 🛠️ Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Firebase project with Firestore enabled

### Backend Setup

1. Navigate to backend directory:
```bash
cd ../backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure `.env` file exists with:
```
SECRET_KEY=your-secret-key-here
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
```

4. **Enable Firestore Database** in Firebase Console:
   - Go to https://console.firebase.google.com
   - Select project: **sparelens-afb9c**
   - Click "Firestore Database"
   - Click "Create Database"
   - Choose production/test mode
   - Select a location
   - Click "Enable"

5. Start the backend:
```bash
uvicorn main:app --reload --port 8000
```

Backend runs on: **http://localhost:8000**

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Ensure `.env` file exists with:
```
VITE_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

Frontend runs on: **http://localhost:5174** (or 5173)

## 📖 Usage Guide

### 1. Sign Up
- Navigate to http://localhost:5174
- Click "Sign Up"
- Enter email, password, select role
- Create account

### 2. Upload Data
- Click "Upload" in navbar
- Drag and drop CSV/Excel file
- Click "Upload File"

### 3. View Dashboard
- Click "Dashboard" in navbar
- Select dataset from sidebar
- Toggle between **Table View** and **Chart View**
- Use search, sort, and pagination

## 📂 Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── Navbar.jsx
│   ├── DataTable.jsx
│   ├── ChartView.jsx
│   └── PrivateRoute.jsx
├── pages/            # Page components
│   ├── Home.jsx
│   ├── Signup.jsx
│   ├── Signin.jsx
│   ├── Dashboard.jsx
│   └── Upload.jsx
├── context/          # React Context providers
│   ├── AuthContext.jsx
│   └── ThemeContext.jsx
├── services/         # API service layer
│   ├── api.js
│   ├── authService.js
│   └── dataService.js
├── App.jsx           # Main app with routing
└── main.jsx          # Entry point
```

## 🔑 API Endpoints

### Authentication
- `POST /auth/signup` - Create account
- `POST /auth/token` - Login
- `GET /auth/users/me` - Get current user

### Data Management
- `POST /upload/` - Upload file
- `GET /data/datasets` - List datasets
- `GET /data/{id}` - Get dataset data
- `DELETE /data/{id}` - Delete dataset

## ⚠️ Important Notes

1. **Firestore Database** must be enabled before signup works
2. Backend must run on port **8000**
3. Environment variables use **VITE_** prefix
4. Supported files: **CSV, XLS, XLSX** (max 50MB)

## 🎯 Building for Production

```bash
npm run build
```

Output in `dist/` folder.

## 📝 License

MIT
