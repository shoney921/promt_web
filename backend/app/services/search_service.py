from typing import Optional, List, Dict
from langchain_community.tools.tavily_search import TavilySearchResults
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """검색 서비스 - Tavily Search를 사용한 웹 검색"""
    
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.is_enabled = bool(self.api_key)
        
        if not self.is_enabled:
            logger.warning("Tavily API Key가 설정되지 않았습니다. 검색 기능이 비활성화됩니다.")
            self.search_tool = None
        else:
            try:
                self.search_tool = TavilySearchResults(
                    api_key=self.api_key,
                    max_results=5,  # 최대 검색 결과 수
                    search_depth="advanced"  # 기본 또는 고급 검색
                )
                logger.info("Tavily Search 서비스가 초기화되었습니다.")
            except Exception as e:
                logger.error(f"Tavily Search 초기화 실패: {str(e)}")
                self.search_tool = None
                self.is_enabled = False
    
    def get_search_tool(self):
        """검색 툴 반환 (Langchain Tool)"""
        if not self.is_enabled or not self.search_tool:
            return None
        return self.search_tool
    
    def get_tools(self) -> List:
        """사용 가능한 검색 툴 목록 반환"""
        tool = self.get_search_tool()
        if tool:
            return [tool]
        return []
    
    async def search(self, query: str) -> List[Dict]:
        """
        직접 검색 실행 (비동기)
        
        Args:
            query: 검색 쿼리
            
        Returns:
            검색 결과 리스트
        """
        if not self.is_enabled or not self.search_tool:
            return []
        
        try:
            # Tavily Search는 동기 함수이므로 run_in_executor 사용
            import asyncio
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self.search_tool.invoke,
                query
            )
            return results if isinstance(results, list) else []
        except Exception as e:
            logger.error(f"검색 실행 중 오류 발생: {str(e)}")
            return []


# 싱글톤 인스턴스
search_service = SearchService()
