from fastapi import APIRouter

from .auth import router as auth_router
from .partners import router as partners_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(partners_router)
