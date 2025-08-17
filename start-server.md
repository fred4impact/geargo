# 🚀 GearGo - Server Startup Guide

This guide contains all the commands needed to start and manage the GearGo application using Docker Compose and Makefile.

## 📋 Prerequisites

Make sure you have the following installed:
- Docker
- Docker Compose
- Make

## 🛠️ Initial Setup (First Time Only)

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd geargo
```

### 2. Build Docker Images
```bash
make build
```

### 3. Set Up the Application
```bash
make setup
```

This command will:
- Start all services (web, database, redis, celery)
- Run database migrations
- Create initial data (categories, test users)
- Set up email templates

## 🚀 Daily Startup Commands

### Start All Services
```bash
make up
```

### Alternative: Start with Logs
```bash
make up-logs
```

## 🛑 Stopping the Application

### Stop All Services
```bash
make down
```

### Stop and Remove Volumes (Clean Slate)
```bash
make clean
```

## 🔄 Restart Services

### Restart All Services
```bash
make restart
```

### Restart Specific Service
```bash
# Restart web service only
docker-compose restart web

# Restart database only
docker-compose restart db

# Restart redis only
docker-compose restart redis

# Restart celery only
docker-compose restart celery
```

## 👤 User Management

### Create Superuser
```bash
make superuser
```

### Create Test User
```bash
make testuser
```

## 🗄️ Database Operations

### Run Migrations
```bash
make migrate
```

### Reset Database (Dangerous!)
```bash
make reset
```

## 📊 Monitoring

### View Logs
```bash
make logs
```

### View Specific Service Logs
```bash
# Web service logs
docker-compose logs web

# Database logs
docker-compose logs db

# Redis logs
docker-compose logs redis

# Celery logs
docker-compose logs celery
```

### Follow Logs (Real-time)
```bash
make logs-follow
```

## 🔧 Development Commands

### Access Django Shell
```bash
make shell
```

### Run Tests
```bash
make test
```

### Collect Static Files
```bash
make collectstatic
```

### Check Service Status
```bash
make status
```

## 🌐 Access Points

Once the application is running, you can access:

- **Main Application**: http://127.0.0.1:8000
- **Admin Interface**: http://127.0.0.1:8000/admin
- **API Endpoints**: http://127.0.0.1:8000/api/

## 🔑 Default Credentials

### Admin User
- **Email**: admin@geargo.com
- **Password**: adminpass123

### Test User
- **Email**: test@geargo.com
- **Password**: testpass123

## 🚨 Troubleshooting

### If Services Won't Start
```bash
# Check if ports are in use
make check-ports

# Clean everything and start fresh
make clean
make build
make setup
```

### If Database Issues
```bash
# Reset database
make reset

# Or manually recreate
docker-compose down -v
docker-compose up -d db
make migrate
make setup
```

### If Images Not Loading
```bash
# Check media directory permissions
docker-compose exec web chmod -R 755 /app/media

# Restart web service
docker-compose restart web
```

### If Celery Not Working
```bash
# Restart celery service
docker-compose restart celery

# Check celery logs
docker-compose logs celery
```

## 📝 Quick Reference

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make restart` | Restart all services |
| `make logs` | View logs |
| `make setup` | Initial setup |
| `make superuser` | Create admin user |
| `make reset` | Reset everything |
| `make clean` | Clean up containers |

## 🎯 Typical Workflow

1. **Start the application**:
   ```bash
   make up
   ```

2. **Check if everything is running**:
   ```bash
   make status
   ```

3. **View logs if needed**:
   ```bash
   make logs
   ```

4. **Access the application**:
   - Open http://127.0.0.1:8000 in your browser

5. **Stop when done**:
   ```bash
   make down
   ```

## 🔄 Development Workflow

For active development:

1. **Start with logs**:
   ```bash
   make up-logs
   ```

2. **Make your changes** (files are mounted as volumes)

3. **Restart web service** (if needed):
   ```bash
   docker-compose restart web
   ```

4. **Run migrations** (if model changes):
   ```bash
   make migrate
   ```

5. **Stop when done**:
   ```bash
   make down
   ```

---

**Note**: All commands should be run from the project root directory (`/Users/mac/Documents/geargo`).
