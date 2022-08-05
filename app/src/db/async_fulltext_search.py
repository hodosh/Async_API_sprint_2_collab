from abc import ABC, abstractmethod
from typing import Coroutine, Any


class FullTextSearch(ABC):
    @abstractmethod
    async def get(self,
                  index: Any,
                  id: Any,
                  doc_type: Any = None,
                  params: Any = None,
                  headers: Any = None) -> Coroutine[Any, Any, bool]:
        pass

    # получение документов по запросу
    @abstractmethod
    async def search(self,
                     body: Any = None,
                     index: Any = None,
                     doc_type: Any = None,
                     params: Any = None,
                     headers: Any = None) -> Coroutine[Any, Any, bool]:
        pass
