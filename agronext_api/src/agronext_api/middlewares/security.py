from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware


__all__ = ["CORSMiddleware", "HTTPSRedirectMiddleware", "TrustedHostMiddleware"]

# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])
# app.add_middleware(HTTPSRedirectMiddleware)
# app.add_middleware(ProxyHeadersMiddleware)
# app.add_middleware(CorrelationIdMiddleware)
# app.add_middleware(AuthenticationMiddleware, backend=SimpleBackend())
# app.add_middleware(SessionMiddleware, secret_key="...")
# app.add_middleware(GZipMiddleware, minimum_size=500)
