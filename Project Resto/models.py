from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=13, null=True)
    def __str__(self):
        return self.restaurant_name


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact= models.CharField(max_length=13, null=True)
    location = models.CharField(max_length=50, null=True)
    def __str__(self):
        return self.user.username


class Menu(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)  # Updated field
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE)
    description= models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    contact = models.CharField(max_length=13,null=True)
    location = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=50, default='pending')
    date=models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Order {self.id}: {self.menu.name} - {self.client.user.username}"
     
    class Meta:
        db_table = "Orders"
        verbose_name_plural = "Orders"