import re

class PreprocessingService:
    @staticmethod
    def preprocess_query(text: str) -> str:
        """
        Cleans and normalizes the raw user query before it enters the NLP pipeline.
        """
        if not text:
            return ""
            
        # 1. Strip surrounding whitespace
        cleaned = text.strip()
        
        # 2. Strip surrounding literal quotation marks (handles nested quotes like '"Help"')
        while cleaned.startswith(('"', "'")) and cleaned.endswith(('"', "'")) and len(cleaned) > 1:
            cleaned = cleaned[1:-1].strip()
            
        # 3. Remove unwanted special signs/symbols but KEEP unicode words, spaces, and basic punctuation
        # \w = any word character (including Arabic, Chinese, etc.)
        # \s = spaces
        # \.,!\?'"\(\)- = basic punctuation needed for emotion/context
        cleaned = re.sub(r'[^\w\s\.,!\?\'"\(\)-]', '', cleaned)
            
        # 4. Normalize multiple whitespaces/newlines into a single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned
