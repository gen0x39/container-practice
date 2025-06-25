from pydantic import BaseModel
from typing import Optional

class TweetRequest(BaseModel):
    content: str
    author: str = "ユーザー"
    category: str = "ユーザー投稿"
    ascii_content: Optional[str] = None  # アスキーアート本体 
