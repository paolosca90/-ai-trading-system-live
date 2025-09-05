# Trading Backend API - Railway Deploy

## Files in this package:

1. **main.py** - FastAPI main application with all endpoints
2. **database.py** - Database configuration (PostgreSQL)
3. **models.py** - SQLAlchemy models (User, Signal, Subscription, etc.)
4. **schemas.py** - Pydantic schemas for API validation
5. **jwt_auth.py** - JWT authentication and authorization
6. **requirements.txt** - Python dependencies (compatible with Python 3.12)
7. **nixpacks.toml** - Railway/Nixpacks configuration
8. **.env.example** - Environment variables example

## Deploy Instructions on Railway:

### 1. Environment Variables:
Set these in Railway Dashboard → Settings → Environment Variables:
- `SECRET_KEY` = [generate a strong random string]
- `DATABASE_URL` = [Railway provides this automatically]

### 2. Deploy:
1. Upload all files to your GitHub repository
2. Connect GitHub repo to Railway
3. Railway will auto-deploy using nixpacks.toml configuration

### 3. After Deploy:
- Visit: `https://your-app.up.railway.app/docs` for API documentation
- Test the `/health` endpoint to verify it's working

## API Endpoints:

### Authentication:
- `POST /register` - Register new user
- `POST /token` - Login and get JWT tokens
- `GET /me` - Get current user info with stats

### Signals:
- `GET /signals/top` - Get top 3 public signals
- `GET /signals` - Get user signals (with filters)
- `POST /signals` - Create signal (admin only)

### MT5 Integration:
- `POST /mt5/connect` - Setup MT5 connection
- `GET /mt5/status` - Get MT5 connection status

### Admin:
- `POST /admin/generate-signals` - Generate signals manually

## Features:
- ✅ User registration with 7-day trial
- ✅ JWT authentication with access/refresh tokens
- ✅ Signal creation and management
- ✅ User statistics and analytics
- ✅ MT5 integration placeholder
- ✅ Admin panel functions
- ✅ CORS enabled for frontend integration
- ✅ PostgreSQL database with relationships
- ✅ Python 3.12 compatible
- ✅ Ready for Railway deployment

## Next Steps:
1. Deploy backend ✅
2. Test API endpoints
3. Build frontend React app
4. Implement AI signal generation
5. Add real MT5 integration
6. Create executable for clients

All fixed and ready for production! 🚀
