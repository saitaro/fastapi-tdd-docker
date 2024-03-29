import nltk
from newspaper import Article

from app.models.tortoise import TextSummary


async def generate_summary(summary_id, url: str):
    article = Article(url)
    article.download()
    article.parse()

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    finally:
        article.nlp()

    await TextSummary.filter(id=summary_id).update(summary=article.summary)
