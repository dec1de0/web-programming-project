"""TODO: typed dictionaries keyed by UUID for projects, audits and findings.

Create one store per FastAPI application through app.state, not global dictionaries.
Protect multi-resource writes with a lock. Run a single worker: data is ephemeral.
"""
