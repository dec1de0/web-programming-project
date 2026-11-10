from fastapi import APIRouter

router = APIRouter(prefix="/projects", tags=["Projects"])

# Add project CRUD handlers here; delegate business rules to services/projects.py.
