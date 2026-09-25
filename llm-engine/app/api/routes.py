from fastapi import APIRouter, Depends, HTTPException, status
from app.config import settings
from app.providers import get_llm_provider, LLMProvider
from app.schemas.query import ParseQueryRequest, SeatSearchQuery

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "provider": settings.LLM_PROVIDER,
        "service": "llm-engine",
    }


@router.post("/api/v1/parse-query", response_model=SeatSearchQuery)
async def parse_query(
    payload: ParseQueryRequest,
    provider: LLMProvider = Depends(get_llm_provider),
):
    try:
        result = await provider.parse_query(payload.query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse query: {str(e)}",
        )
