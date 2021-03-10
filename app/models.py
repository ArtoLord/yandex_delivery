from django.db import models
from django.contrib.postgres.fields import ArrayField, RangeField


class CourierTypes(models.TextChoices):
    FOOT = "foot"
    BIKE = "bike"
    CAR = "car"


class Region(models.Model):
    region_id = models.IntegerField(primary_key=True, unique=True)

    def __repr__(self):
        return str(self.region_id)


class Courier(models.Model):

    courier_id = models.IntegerField(primary_key=True, unique=True)
    courier_type = models.CharField(
        choices=CourierTypes.choices,
        max_length=4
    )
    working_hours = ArrayField(models.CharField(max_length=16))
    regions = models.ManyToManyField(Region, related_name="couriers")
    rating = models.FloatField(default=0)
    earnings = models.IntegerField(default=0)

    __type_to_max_weight_dict = {
        CourierTypes.FOOT: 10,
        CourierTypes.BIKE: 15,
        CourierTypes.CAR: 50
    }

    @property
    def max_weight(self):
        return self.__type_to_max_weight_dict[CourierTypes(self.courier_type)]


class Assignation(models.Model):
    courier = models.OneToOneField(Courier, on_delete=models.CASCADE, related_name="assignation")
    assign_time = models.DateTimeField(auto_now=True)

    @property
    def not_completed_orders(self):
        return self.orders.filter(complete_time=None)


class Order(models.Model):
    assigned_to = models.ForeignKey(Assignation, on_delete=models.SET_NULL, null=True, related_name="orders")
    complete_time = models.DateTimeField(null=True, default=None)
    order_id = models.IntegerField(primary_key=True, unique=True)
    weight = models.FloatField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="orders")
    delivery_hours = ArrayField(models.CharField(max_length=16))

