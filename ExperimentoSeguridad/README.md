# 🔐 Experimento Seguridad - JWT + RBAC Microservice

A comprehensive security microservice implementing JWT RS256 with RBAC (Role-Based Access Control) for architecture experiments. This service provides authentication, authorization, token management, and observability features.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client        │───▶│   FastAPI App    │───▶│   SQLite DB     │
│  (Postman/Web)  │    │  + JWT Middleware│    │  (users.db)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌──────────────────┐
                       │    Redis         │
                       │ (Token Revocation)│
                       └──────────────────┘
                               │
                               ▼
                       ┌──────────────────┐
                       │   Prometheus     │
                       │   + Grafana      │
                       └──────────────────┘
```

## ✨ Features

- **JWT RS256 Authentication** with key rotation
- **RBAC Authorization** (admin/user roles)
- **Token Revocation** with Redis fallback to SQLite
- **Comprehensive Metrics** with Prometheus
- **Health Checks** and observability
- **Docker Support** for easy deployment
- **Comprehensive Test Suite** with pytest

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Postman (for API testing)

### Running with Docker (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   cd ExperimentoSeguridad
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Wait for services to be ready (30 seconds):**
   ```bash
   docker-compose logs -f app
   ```

4. **Verify the service is running:**
   ```bash
   curl http://localhost:8000/health
   ```

### Access Points

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics
- **Grafana Dashboard**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090

## 🧪 Running Tests

### Prerequisites for Testing

```bash
# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Run Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest tests/test_auth_integration.py  # Run integration tests
```

### Test Categories

- **Authentication Tests**: Login, token validation, revocation
- **Authorization Tests**: RBAC permissions, role-based access
- **Integration Tests**: End-to-end API workflows
- **Metrics Tests**: Prometheus metrics validation

## 📊 API Usage

### Authentication Flow

1. **Create User:**
   ```bash
   curl -X POST "http://localhost:8000/users/" \
        -H "Content-Type: application/json" \
        -d '{
          "email": "user@example.com",
          "password": "password123",
          "full_name": "Test User",
          "role": "user"
        }'
   ```

2. **Login:**
   ```bash
   curl -X POST "http://localhost:8000/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=user@example.com&password=password123"
   ```

3. **Access Protected Resource:**
   ```bash
   curl -X GET "http://localhost:8000/users/me" \
        -H "Authorization: Bearer YOUR_TOKEN"
   ```

### Key Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/users/` | POST | Create user | No |
| `/token` | POST | Login | No |
| `/users/me` | GET | Get current user | Yes |
| `/auth/revoke` | POST | Revoke token | Yes |
| `/auth/refresh` | POST | Refresh token | Yes |
| `/auth/blacklist` | GET | View blacklist | Admin only |
| `/auth/rotate-keys` | POST | Rotate keys | Admin only |
| `/.well-known/jwks.json` | GET | Public keys | No |
| `/metrics` | GET | Prometheus metrics | No |
| `/health` | GET | Health check | No |

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./users.db` | Database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `JWT_ISS` | `experimento-seguridad` | JWT issuer |
| `JWT_AUD` | `api-users` | JWT audience |
| `PROMETHEUS_ENABLED` | `true` | Enable Prometheus metrics |
| `WEB_CONCURRENCY` | `1` | Number of workers (dev) |
| `PROMETHEUS_MULTIPROC_DIR` | - | Multiprocess metrics dir (prod) |

### Development vs Production

**Development (Docker Compose):**
- Single worker (`WEB_CONCURRENCY=1`)
- SQLite database
- Single-process Prometheus metrics

**Production:**
- Multiple workers
- PostgreSQL database
- Multiprocess Prometheus metrics (set `PROMETHEUS_MULTIPROC_DIR`)

## 📈 Monitoring and Metrics

### Prometheus Metrics

- `jwt_validation_seconds`: JWT validation latency
- `jwt_validation_failures_total`: Validation failures by reason
- `jwt_validation_success_total`: Successful validations
- `redis_connection_status`: Redis availability

### Grafana Dashboard

Access the pre-configured dashboard at http://localhost:3000:
- Username: `admin`
- Password: `admin123`

Dashboard includes:
- JWT validation latency (p50, p95, p99)
- Error rates by endpoint
- Redis connection status
- Token revocation metrics

## 🔒 Security Features

### JWT RS256 Implementation

- **Asymmetric encryption** with RSA keys
- **Key rotation** support with `kid` header
- **Clock skew tolerance** (±60 seconds)
- **Comprehensive validation** (issuer, audience, expiration)

### RBAC (Role-Based Access Control)

| Role | Users | Auth |
|------|-------|------|
| `admin` | read, create, update, delete | rotate_keys, view_blacklist |
| `user` | read, update | - |

### Token Management

- **Revocation** with Redis + SQLite fallback
- **Refresh** functionality
- **Blacklist** viewing (admin only)
- **Fail-closed** security model

## 🐳 Docker Configuration

### Development

```bash
# Single worker for development
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Production

```bash
# Enable multiprocess metrics
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir

# Use PostgreSQL
export DATABASE_URL=postgresql://user:pass@host:port/db

# Scale workers
export WEB_CONCURRENCY=4

docker-compose up -d
```

## 🧪 Experiment Scenarios

This microservice is designed for architecture experiments testing:

1. **Key Rotation**: Measure availability during key rotation
2. **Redis Failure**: Test fallback to SQLite
3. **Token Revocation**: Verify revocation effectiveness
4. **RBAC Enforcement**: Test role-based access control
5. **Performance**: Measure latency under load

### Using Postman Collection

Import `Docs/UserService.postman_collection.json` into Postman to run comprehensive tests:

1. **Setup**: Create admin and user accounts
2. **Authentication**: Test login flows
3. **Authorization**: Test RBAC permissions
4. **Token Management**: Test revocation and refresh
5. **Metrics**: Verify Prometheus metrics

## 🛠️ Development

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
ruff check app/ tests/

# Run all quality checks
pre-commit run --all-files
```

### Project Structure

```
ExperimentoSeguridad/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── routes/              # API routes
│   ├── middleware/          # JWT middleware
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   └── utils/               # Utilities (auth, rbac, etc.)
├── tests/                   # Test suite
├── docs/                    # Documentation
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Container definition
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test suite for usage examples