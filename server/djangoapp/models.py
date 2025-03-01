from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator

class CarMake(models.Model):
    Name = models.CharField(max_length=100)
    Description = models.TextField()
    Color = models.CharField(max_length=100)

    def __str__(self): #method to print a car make object
        return self.Name

class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE) #Many-to-one relationship to CarMake model (One car make can have many car models, using a ForeignKey field)
    #Dealer_Id = models.IntegerField(default=0)
    Name = models.CharField(max_length=100)
    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        # Add more choices as required
    ]
    type = models.CharField(max_length=10, choices=CAR_TYPES, default='SUV') #(CharField with a choices argument to provide limited choices such as Sedan, SUV, and Wagon)
    year = models.IntegerField(default=2023,
        validators=[
            MaxValueValidator(2023),
            MinValueValidator(2015)
        ])

    def __str__(self):
        return self.Name