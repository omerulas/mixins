import json
from main.mixins.base import BaseOperationMixins

class ModelFormMixin(BaseOperationMixins):
    """
        Devamlı tekrar eden crud islemleri (olusturma, guncelleme,
        silme) islemlerini tek bir catida evrensellestirir.
    """
    
    def __data__(self, request):
        """
        Body'den güvenli bir şekilde veri çeker.
        Öncelik sırası:
        1. Multipart (Dosya + 'data' key içinde JSON string)
        2. Standart Form POST (request.POST.dict())
        3. Raw JSON Body
        """
        data = {}
        files = request.FILES or None

        # 1. Durum: Form Data veya Multipart (Dosya varsa veya POST doluysa)
        if request.POST or request.FILES:
            # Frontend: formData.append('data', JSON.stringify({...})) gönderdiyse:
            raw_data = request.POST.get("data")
            
            if raw_data:
                try:
                    data = json.loads(raw_data)
                except (json.JSONDecodeError, TypeError):
                    # 'data' anahtarı var ama JSON değilse olduğu gibi almayalım, hata loglayabilirsin.
                    pass
            else:
                # 'data' anahtarı yoksa, tüm POST verisini sözlük yapıp dönelim (Standard Form)
                data = request.POST.dict()

        # 2. Durum: Raw JSON Body (POST boşsa ve Body varsa)
        else:
            try:
                if request.body:
                    data = json.loads(request.body)
            except json.JSONDecodeError:
                pass

        return data, files
    
    def create(self, model=None, data={}, files=None, **kwargs):
        if model:
            self.model = model
        elif not self.model and self.form:
            self.model = self.form._meta.model
        
        try:
            form = self.form(data=data, files=files)
            
            if form.is_valid():
                form.save()
                verbose_name = self.form._meta.model._meta.verbose_name
                message = f"{verbose_name} başarıyla oluşturuldu"
                return {"message": message}
            
            return {"message": self.__errors__(form), "status": 400}
        
        except TypeError:
            message = "View seviyesinde model veya form tanınmlanmamış olabilir"
            return {"message": message, "status": 500}

        except Exception as exception:
            return {"message": staticmethod(exception), "status": 500}
    
    def update(self, model=None, data={}, files=None, **kwargs):
        if model:
            self.model = model
        elif not self.model and self.form:
            self.model = self.form._meta.model
        
        try:
            instance = self.__get_instance__(**kwargs)
            form = self.form(instance=instance, data=data, files=files)
            
            if form.is_valid():
                form.save()
                verbose_name = self.model._meta.verbose_name
                message = f"{verbose_name} başarıyla güncellendi"
                return {"message": message}
            
            message = self.__errors__(form)
            return {"message": message, "status": 400}
        
        except TypeError:
            message = "View seviyesinde model veya form tanınmlanmamış olabilir"
            return {"message": message, "status": 500}

        except Exception as exception:
            return {"message": str(exception), "status": 500}
    
    def destroy(self, model=None, **kwargs):
        if model:
            self.model = model
        elif not self.model and self.form:
            self.model = self.form._meta.model
        
        try:
            verbose_name = self.model._meta.verbose_name
            instance = self.__get_instance__(**kwargs)
            instance.delete()
            return {"message": f"{verbose_name} başarıyla silindi"}
        except Exception as exception:
            return {"message": str(exception)}