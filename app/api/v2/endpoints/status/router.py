from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_status() -> str:
    """Health check endpoint for v2."""
    return "Server Up (/v2)"
