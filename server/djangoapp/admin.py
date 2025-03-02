from django.contrib import admin
from .models import CarMake, CarModel


# Register your models here.
admin.site.register(CarMake)
admin.site.register(CarModel)

# register the CarMake/CarModel on the admin site 
# so you can conveniently manage their content
