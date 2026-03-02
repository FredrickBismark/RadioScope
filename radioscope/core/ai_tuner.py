"""AI-powered station recommendation using Anthropic Claude.

Acts as an intelligent radio tuner — translates natural language mood/activity
descriptions into search queries for the station aggregator. Not an algorithm,
just a knowledgeable guide to human-curated radio.
"""
import json
import asyncio
from dataclasses import dataclass

from core.config import ANTHROPIC_API_KEY, AI_MODEL, AI_MAX_TOKENS

SYSTEM_PROMPT = """You are a knowledgeable internet radio curator and enthusiast. \
The user will describe a mood, activity, memory, or music preference. Your job is to \
recommend search terms that will find great stations in internet radio directories \
like radio-browser.info and SomaFM.

You are NOT an algorithm. You are a radio nerd helping someone find the right dial position. \
Think like a record store clerk or college radio DJ — you know the obscure stuff, the deep \
genre tags, the specific station names that most people don't know about.

Respond ONLY in this JSON format with no additional text, no markdown fences:
{"explanation": "Your brief, warm explanation of why these searches will work (2-3 sentences max)", "searches": ["term1", "term2", "term3", "term4"], "somafm_channels": ["channel-id-if-relevant"]}

Guidelines:
- Provide 3-5 search terms that work as genre tags in radio-browser.info
- Use specific genre tags (e.g. "dark ambient" not just "ambient", "bebop" not just "jazz")
- If SomaFM has a relevant channel, include its ID (e.g. "dronezone", "groovesalad", "defcon")
- Consider the time of day, energy level, and activity implied by the request
- Be opinionated — pick the BEST matches, not everything that could possibly work
- Keep explanation conversational and brief"""


@dataclass
class AIRecommendation:
    explanation: str = ""
    searches: list = None
    somafm_channels: list = None
    error: str = ""

    def __post_init__(self):
        if self.searches is None:
            self.searches = []
        if self.somafm_channels is None:
            self.somafm_channels = []


async def get_recommendation(prompt: str) -> AIRecommendation:
    """Get AI station recommendations for a natural language prompt."""
    if not ANTHROPIC_API_KEY:
        return AIRecommendation(
            error="No API key configured. Set ANTHROPIC_API_KEY in .env file."
        )

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

        message = await client.messages.create(
            model=AI_MODEL,
            max_tokens=AI_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        text = ""
        for block in message.content:
            if block.type == "text":
                text += block.text

        # Clean and parse JSON
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(text)

        return AIRecommendation(
            explanation=data.get("explanation", ""),
            searches=data.get("searches", []),
            somafm_channels=data.get("somafm_channels", []),
        )

    except json.JSONDecodeError:
        return AIRecommendation(error="AI response wasn't valid JSON. Try rephrasing.")
    except Exception as e:
        return AIRecommendation(error=f"AI request failed: {e}")


# Convenience wrapper for use from Qt (which needs sync calls bridged to async)
def get_recommendation_sync(prompt: str) -> AIRecommendation:
    """Synchronous wrapper for use from Qt threads."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(get_recommendation(prompt))
    finally:
        loop.close()
