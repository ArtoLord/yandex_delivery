from django.db import models
from django.db.models import Avg, Min
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
    assigned_now = models.BooleanField(default=False)

    __type_to_max_weight_dict = {
        CourierTypes.FOOT: 10,
        CourierTypes.BIKE: 15,
        CourierTypes.CAR: 50
    }

    @property
    def current_assignation(self):
        if self.assigned_now:
            return self.assignations.order_by('-assign_time').first()
        return None

    @property
    def max_weight(self):
        return self.__type_to_max_weight_dict[CourierTypes(self.courier_type)]

    @property
    def rating(self):
        if not self.completed_orders:
            return None
        rating = self.completed_orders.values('region').annotate(
            avg=Avg('delivery_time')
        ).aggregate(Min('avg')).get('avg_min', 0)
        return (60 * 60 - min(rating, 60 * 60))/(60 * 60) * 5

    __type_to_c_dict = {
        CourierTypes.FOOT: 2,
        CourierTypes.BIKE: 5,
        CourierTypes.CAR: 9
    }

    @property
    def earnings(self):
        n = self.assignations.exclude(pk=self.current_assignation.pk if self.assigned_now else -1).count()
        return n * 500 * self.__type_to_c_dict[CourierTypes(self.courier_type)]

    @property
    def completed_orders(self):
        return Order.objects.filter(
            complete_time__isnull=False,
            assigned_to__courier=self
        )


class Assignation(models.Model):
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, related_name="assignations")
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
    delivery_time = models.DurationField(null=True, default=None)
