from fastapi import APIRouter
from generator.base_generator import MediaBasedContentGenerator 
router = APIRouter()


@router.post("/generate_content")
def generate_content(idea: str, target_audience: str, platform: str, post_category: str):
    """
    Main function to be called from your FastAPI endpoint
    
    Args:
        idea: Content idea/topic
        target_audience: Target audience description
        platform: Platform context (though content is generated for both)
        post_category: Category/theme of the post
    
    Returns:
        Dict with structure: {"linkedin": {"long": "...", "medium": "...", "small": "..."}, "x": {...}}
    """

    generator = MediaBasedContentGenerator()
    return generator.generate_all_content(idea, target_audience, platform, post_category)

