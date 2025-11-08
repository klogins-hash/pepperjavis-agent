"""
FastAPI server for PepperJarvis Agent with observability.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import observability
from opentelemetry import metrics, trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from pepperjavis.agent import PepperJarvisAgent
from pepperjavis.config import AgentConfig


# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)


# ============== Observability Setup ==============

def setup_tracing():
    """Configure Jaeger tracing."""
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv('JAEGER_AGENT_HOST', 'localhost'),
        agent_port=int(os.getenv('JAEGER_AGENT_PORT', 6831)),
    )

    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

    # Instrument libraries
    FastAPIInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()


# ============== Metrics ==============

request_counter = Counter(
    'pepperjavis_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'pepperjavis_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

agent_requests = Counter(
    'pepperjavis_agent_requests_total',
    'Total agent requests',
    ['status']
)

agent_errors = Counter(
    'pepperjavis_agent_errors_total',
    'Total agent errors',
    ['error_type']
)


# ============== Database & Cache ==============

def get_database_url():
    """Get database URL from environment."""
    return os.getenv(
        'DATABASE_URL',
        'postgresql://pepperjavis:pepperjavis_secure_pass@localhost:5432/pepperjavis'
    )


def get_redis_url():
    """Get Redis URL from environment."""
    return os.getenv(
        'REDIS_URL',
        'redis://localhost:6379/0'
    )


# Initialize database
engine = None
SessionLocal = None
redis_client = None


async def init_dependencies():
    """Initialize database and cache connections."""
    global engine, SessionLocal, redis_client

    try:
        engine = create_engine(
            get_database_url(),
            echo=os.getenv('LOG_LEVEL') == 'DEBUG'
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("✓ Database connection established")
    except Exception as e:
        logger.error(f"✗ Failed to connect to database: {e}")
        raise

    try:
        redis_client = redis.from_url(
            get_redis_url(),
            decode_responses=True
        )
        redis_client.ping()
        logger.info("✓ Redis connection established")
    except Exception as e:
        logger.error(f"✗ Failed to connect to Redis: {e}")
        raise


async def shutdown_dependencies():
    """Shutdown database and cache connections."""
    global engine, redis_client

    if engine:
        engine.dispose()
        logger.info("✓ Database connection closed")

    if redis_client:
        redis_client.close()
        logger.info("✓ Redis connection closed")


# ============== Agent Management ==============

agent = None


async def init_agent():
    """Initialize the PepperJarvis Agent."""
    global agent

    try:
        config = AgentConfig()
        agent = PepperJarvisAgent(config=config)
        logger.info(f"✓ Agent initialized: {config.agent_name}")
    except Exception as e:
        logger.error(f"✗ Failed to initialize agent: {e}")
        raise


# ============== Request Models ==============

class MessageRequest(BaseModel):
    """Request model for agent messages."""
    session_id: str
    message: str
    temperature: float = 0.7


class MessageResponse(BaseModel):
    """Response model for agent messages."""
    session_id: str
    message: str
    status: str


# ============== Lifespan ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("🚀 Starting PepperJarvis Agent Server...")
    setup_tracing()
    await init_dependencies()
    await init_agent()
    logger.info("✓ Server startup complete")

    yield

    # Shutdown
    logger.info("🛑 Shutting down PepperJarvis Agent Server...")
    await shutdown_dependencies()
    logger.info("✓ Server shutdown complete")


# ============== FastAPI App ==============

app = FastAPI(
    title="PepperJarvis Agent API",
    description="Chief of Staff & JARVIS Combined AI Agent",
    version="0.1.0",
    lifespan=lifespan
)


# ============== Health Check ==============

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "pepperjavis-agent",
        "agent_ready": agent is not None,
        "database_ready": engine is not None,
        "cache_ready": redis_client is not None,
    }


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Kubernetes readiness check."""
    if agent is None or engine is None or redis_client is None:
        raise HTTPException(status_code=503, detail="Dependencies not ready")
    return {"ready": True}


# ============== Metrics ==============

@app.get("/metrics", tags=["observability"])
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()


# ============== Agent Endpoints ==============

@app.post("/v1/messages", response_model=MessageResponse, tags=["agent"])
async def send_message(request: MessageRequest):
    """Send a message to the agent."""
    agent_requests.labels(status='started').inc()

    try:
        with request_duration.labels(
            method='POST',
            endpoint='/v1/messages'
        ).time():
            # Process message
            response = await process_agent_message(
                session_id=request.session_id,
                message=request.message,
                temperature=request.temperature
            )

        agent_requests.labels(status='completed').inc()

        return MessageResponse(
            session_id=request.session_id,
            message=response,
            status="success"
        )

    except Exception as e:
        logger.exception(f"Error processing message: {e}")
        agent_errors.labels(error_type=type(e).__name__).inc()
        agent_requests.labels(status='failed').inc()
        raise HTTPException(status_code=500, detail=str(e))


async def process_agent_message(session_id: str, message: str, temperature: float) -> str:
    """Process a message through the agent."""
    # Store message in database
    if SessionLocal:
        session = SessionLocal()
        try:
            # Insert message into messages table
            # This is a stub - implement based on your ORM models
            pass
        finally:
            session.close()

    # Cache in Redis
    if redis_client:
        cache_key = f"session:{session_id}:last_message"
        redis_client.setex(cache_key, 3600, message)

    # Process through agent
    response = agent(message)
    return response


@app.get("/v1/sessions/{session_id}", tags=["agent"])
async def get_session(session_id: str):
    """Get session details."""
    try:
        # Retrieve from database
        if SessionLocal:
            session = SessionLocal()
            try:
                # Query session from database
                # This is a stub - implement based on your ORM models
                pass
            finally:
                session.close()

        return {
            "session_id": session_id,
            "status": "active",
        }
    except Exception as e:
        logger.exception(f"Error retrieving session: {e}")
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/v1/capabilities", tags=["agent"])
async def get_capabilities():
    """Get agent capabilities."""
    return agent.get_capabilities()


# ============== Error Handlers ==============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============== Startup Events ==============

@app.on_event("startup")
async def startup_event():
    """Startup event."""
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    logger.info("Application shutdown complete")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "pepperjavis.server:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv('ENVIRONMENT') == 'development'
    )
