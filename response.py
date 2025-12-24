from django.http import JsonResponse
from typing import Any, Optional

class ExtendedJsonResponse(JsonResponse):
    
    def __init__(
            self,
            data: Optional[Any] = None,
            message: Optional[str] = "",
            status: int =200,
            **kwargs
        ):
        
        payload = {
            "data": data,
            "message": message,
        }
        
        super().__init__(data=payload, status=status, **kwargs)