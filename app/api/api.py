from fastapi import APIRouter



api_router = APIRouter()

@api_router.get('/health')
async def health_check():
    return {"message": "API is working"}

@api_router.get('/new')
async def health_check():
    return {"message": "Added to test ci/cd auto deployment"}
