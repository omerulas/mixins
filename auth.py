import json
from django.forms import ModelForm
from django.contrib.auth import login, logout
from mixins.base import BaseOperationMixins

class AuthMixin(BaseOperationMixins):
    
    authentication_form: ModelForm = None
    
    def get_anonymous_user(self):
        return {
            "is_authenticated": False,
            "is_active": False,
            "is_superuser": False,
            "email": None,
            "corporate": None
        }
    
    def get_user_data(self, user):
        
        if user.is_authenticated:
            return {
                "is_authenticated": user.is_authenticated,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "email": user.email,
            }
            
        return self.get_anonymous_user()
    
    def login_process(self, request):
        data = json.loads(request.body)
        form = self.authentication_form(data=data)
        
        if form.is_valid():
            user = form.get_user()
            login(request=request, user=user)
            user_data = self.get_user_data(user=user)
            return {"data": user_data}

        return {"message": self.__errors__(form), "status": 400}
    
    def logout_process(self, request):
        logout(request=request)
        return {"message": "Oturum başarıyla kapatıldı"}