from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from controllers.mawaqitController import router as mawaqitRouter
from config.settings import settings


def create_app() -> FastAPI:
    # Disable default docs to add custom ones with Vercel Analytics
    app = FastAPI(title='Mawaqit Api', debug=False, read_root="/", docs_url=None, redoc_url=None)

    if settings.ENABLE_REDIS:
        storage_uri = settings.REDIS_URI
        limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT], storage_uri=storage_uri)
    else:
        limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    return app


app = create_app()
app.include_router(router=mawaqitRouter)


# Custom docs endpoints with Vercel Web Analytics
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI documentation with Vercel Analytics integration."""
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
    )
    # Inject Vercel Analytics script
    html_content = html.body.decode('utf-8')
    analytics_script = '<script defer src="https://cdn.vercel-insights.com/v1/script.js"></script>'
    modified_html = html_content.replace('</head>', f'{analytics_script}</head>')
    return HTMLResponse(content=modified_html)


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    """Custom ReDoc documentation with Vercel Analytics integration."""
    html = get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
    )
    # Inject Vercel Analytics script
    html_content = html.body.decode('utf-8')
    analytics_script = '<script defer src="https://cdn.vercel-insights.com/v1/script.js"></script>'
    modified_html = html_content.replace('</head>', f'{analytics_script}</head>')
    return HTMLResponse(content=modified_html)
