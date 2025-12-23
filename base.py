from django.db.models import Model
from django.forms import ModelForm
from django.forms.models import model_to_dict
from django.db.models import QuerySet
from typing import List
from django.db.models.fields.files import FieldFile

class BaseOperationMixins:
    """
        Veritabanindan bilgi cekme ve filtreleme
        cektigi verileri json veri turune donusturme
    """
    
    # Kullanicilar child classta verilecek
    form: ModelForm = None
    model: Model = None
    table_excluded_fields: List = None
    table_included_fields: List = None
    
    def __get_instance__(self, model=None, **kwargs):
        if model:
            self.model = model
        elif not self.model and self.form:
            self.model = self.form._meta.model
        # QuerySet veri tipinde tek bir instance doner
        verbose_name = self.model._meta.verbose_name.lower()
        try:
            return self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            raise Exception(f"Bu parametrelere göre {verbose_name} bulunamadı")
    
    def __get__(self, model=None, **kwargs):
        if model:
            self.model = model
        elif not self.model and self.form:
            self.model = self.form._meta.model
        # QuerySet veri tipine gore cekilmis veriyi
        # serialize eder
        try:
            instance = self.__get_instance__(**kwargs)
            return self.__serialize_instance__(
                instance=instance,
                fields=self.table_included_fields,
                exclude=self.table_excluded_fields)
        except Exception as exception:
            return {"message": str(exception)}
    
    def __all_qs__(self, model=None, **kwargs) -> QuerySet:
        # Verilen modele ait tum verileri filtresiz doner
        if model:
            self.model = model
        else:
            self.model = self.form._meta.model
            
        return self.model.objects.all()
        
    def __all__(self, model=None, **kwargs):
        # Filtresiz bir sekilde gelen tum QuerySet
        # tipinde veriyi sozluk veri tipine donusturur
        qs = self.__all_qs__(model=model)
        return self.__serialize__(
            query_set=qs,
            fields=self.table_included_fields,
            exclude=self.table_excluded_fields)
    
    def __filtered_qs__(self, order_by="id", model=None, **kwargs) -> QuerySet:
        # Filtrelenmis bir veri seti doner
        # Filtereleme queryleri **kwargs icerisindediler
        # Sete dahil ve haric edilecek alanlar **kwargs icerisinde verilir
        if model:
            self.model = model
        else:
            self.model = self.form._meta.model
        
        return self.model.objects.filter(**kwargs).order_by(order_by)
    
    def __filter__(self, model=None, order_by="id", **kwargs):
        # Filtrelenmis Query Set yine kendi metodu olan
        # __filtered_qs__'den gelir
        if model:
            self.model = model
        else:
            self.model = self.form._meta.model
            
        filtered_data = self.__filtered_qs__(model=model,order_by=order_by, **kwargs)
        return self.__serialize__(
            query_set=filtered_data,
            fields=self.table_included_fields,
            exclude=self.table_excluded_fields)
    
    def __excluded_qs__(self, model=None, **kwargs) -> QuerySet:
        # Filtrelenmis bir veri seti doner
        # Filtereleme queryleri **kwargs icerisindediler
        # Sete dahil ve haric edilecek alanlar **kwargs icerisinde verilir
        if model:
            self.model = model
        else:
            self.model = self.form._meta.model
        
        return self.model.objects.exclude(**kwargs)
    
    def __exclude__(self, model=None, *kwargs):
        if model:
            self.model = model
        else:
            self.model = self.form._meta.model
        
        excluded_data = self.__excluded_qs__(model=model, **kwargs)
        return self.__serialize__(
            query_set=excluded_data,
            fields=self.table_included_fields,
            exclude=self.table_excluded_fields)
    
    def __serialize_instance__(self, instance, **kwargs):
        try:
            if not instance:
                instance = self.__get_instance__(**kwargs)
                
            data = model_to_dict(
                instance=instance,
                fields=self.table_included_fields,
                exclude=self.table_excluded_fields)
            
            for field_name, value in data.items():
                # Eğer değer bir dosya objesiyse (ImageFieldFile veya FieldFile)
                if isinstance(value, FieldFile):
                    # Dosya mevcutsa URL'ini al, yoksa None dön
                    data[field_name] = value.url if value else None
                    
            return data

        except Exception as exception:
            return {"message": str(exception)}
        
    def __serialize__(self, query_set, **kwargs):
        return [
            self.__serialize_instance__(
                instance=instance,
                fields=self.table_included_fields,
                exclude=self.table_excluded_fields)
            for instance in query_set
        ]
    
    def __errors__(self, form):
        return next(iter(form.errors.values()))[0] if form.errors else "Bir hata oluştu"
