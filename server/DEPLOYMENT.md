# IFC Processing Server - Deployment Guide

## Deployment Options

### Option 1: Heroku with Docker Container Registry (Recommended)

Heroku supports Docker containers, which gives you more control over the environment and dependencies.

#### Prerequisites
- Heroku CLI installed (`heroku login`)
- Docker installed (`docker`)
- Git repository initialized

#### Steps

1. **Create a Heroku app:**
   ```bash
   heroku create your-app-name
   ```

2. **Login to Heroku Container Registry:**
   ```bash
   heroku container:login
   ```

3. **Build and push Docker image:**
   ```bash
   heroku container:push web --app=your-app-name
   ```

4. **Release the image:**
   ```bash
   heroku container:release web --app=your-app-name
   ```

5. **View logs:**
   ```bash
   heroku logs --tail --app=your-app-name
   ```

6. **Configure environment variables (optional):**
   ```bash
   heroku config:set BACKEND=fileBased --app=your-app-name
   ```

#### All-in-One Commands
```bash
# Create app and deploy
heroku create your-app-name
heroku container:login
heroku container:push web --app=your-app-name
heroku container:release web --app=your-app-name

# View app
heroku open --app=your-app-name
```

### Option 2: Heroku with Traditional Buildpack

If you prefer not to use Docker, Heroku can build from source code using buildpacks.

#### Prerequisites
- Heroku CLI installed
- Git repository initialized

#### Steps

1. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

2. **Set buildpack (optional, will auto-detect Python):**
   ```bash
   heroku buildpacks:set heroku/python --app=your-app-name
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

4. **Scale the app:**
   ```bash
   heroku ps:scale web=1 --app=your-app-name
   ```

5. **View logs:**
   ```bash
   heroku logs --tail --app=your-app-name
   ```

### Option 3: Docker Container (Local Development or Self-Hosted)

#### Build
```bash
docker build -t ifc-server .
```

#### Run
```bash
docker run -p 5000:5000 \
  -e BACKEND=fileBased \
  -v $(pwd)/dataStores/fileBased/data:/app/dataStores/fileBased/data \
  -v $(pwd)/uploads:/app/uploads \
  ifc-server
```

#### Run with Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - BACKEND=fileBased
      - FLASK_ENV=production
    volumes:
      - ./dataStores/fileBased/data:/app/dataStores/fileBased/data
      - ./uploads:/app/uploads
```

Then run:
```bash
docker-compose up
```

## Important Notes for Heroku Deployment

### 1. **Ephemeral Filesystem**
Heroku has an ephemeral filesystem that's replaced on each dyno restart. For file-based storage:
- **Option A:** Use MongoDB-based backend instead
- **Option B:** Store files on AWS S3 or similar external storage
- **Option C:** Run with `--backend mongodbBased` and set MongoDB connection string

### 2. **Environment Variables**
Set these on Heroku:
```bash
heroku config:set BACKEND=fileBased --app=your-app-name
heroku config:set FLASK_ENV=production --app=your-app-name
```

### 3. **Port Binding**
- The server automatically reads `$PORT` environment variable
- Default is 5000, but Heroku assigns dynamically
- Already configured in Procfile and Dockerfile

### 4. **Log Viewing**
```bash
# Real-time logs
heroku logs --tail --app=your-app-name

# View specific number of lines
heroku logs -n 100 --app=your-app-name

# View logs from specific dyno
heroku logs --dyno web --app=your-app-name
```

### 5. **Scaling**
```bash
# View current dynos
heroku ps --app=your-app-name

# Scale to multiple instances
heroku ps:scale web=2 --app=your-app-name

# Scale down
heroku ps:scale web=1 --app=your-app-name
```

## Database Integration

For persistent file storage, consider using MongoDB:

```bash
# Create MongoDB Atlas account (https://cloud.mongodb.com)
# Get your connection string: mongodb+srv://user:password@cluster.mongodb.net/database

# Set on Heroku
heroku config:set MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/database --app=your-app-name

# Deploy with MongoDB backend
heroku container:release web --app=your-app-name
```

Then modify your start command to use MongoDB backend:
```bash
--backend mongodbBased
```

## Troubleshooting

### App crashes on startup
```bash
# Check logs
heroku logs --tail --app=your-app-name

# Restart dyno
heroku restart --app=your-app-name
```

### Port binding issues
- Ensure you're using `0.0.0.0` as host (✓ already configured)
- Ensure you're binding to `$PORT` environment variable (✓ already configured)

### Dependencies not installed
```bash
# Rebuild push
heroku container:push web --app=your-app-name
heroku container:release web --app=your-app-name
```

## Web App URLs

After deployment:
- **Admin Dashboard:** `https://your-app-name.herokuapp.com/`
- **Viewer:** `https://your-app-name.herokuapp.com/viewer`
- **API Base:** `https://your-app-name.herokuapp.com/api`

## Cost Considerations

- **Free tier:** Sleeps after 30 min of inactivity (eco dynos)
- **Paid tiers** start at $5-10/month for always-on dynos
- Docker container deployments are supported on paid plans
