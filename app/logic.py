from .models import Order, Assignation, Courier
from sortedcontainers import SortedList
from django.utils.dateparse import parse_datetime
from django.utils.timezone import datetime

from django.db.models.signals import pre_save
from django.dispatch import receiver


class TimeRange:

    @staticmethod
    def __parse_time(timerange):
        time1 = int(timerange[:2]) * 60 + int(timerange[3:5])
        timerange = timerange[6:]
        time2 = int(timerange[:2]) * 60 + int(timerange[3:5])
        return time1, time2

    def __init__(self, times):
        self.times = SortedList()
        for time1, time2 in map(self.__parse_time, times):
            self.times.update([(time1, -1), (time2, 1)])

    def intersect(self, other):
        new = SortedList()
        new.update(self.times)  # copy times
        count = [0, 0]
        for time, typ in other.times:
            new.add((time, 2 * typ))
        for time, typ in new:
            count[typ % 2] += typ
            if count[0] * count[1] != 0:
                return True
        return False


def get_possible_orders(courier, assigned_to=None):
    if courier.assigned_now and not assigned_to:
        return []

    orders = Order.objects.filter(
        region__in=courier.regions.all(),
        weight__lte=courier.max_weight,
        assigned_to=assigned_to
    )

    courier_times = TimeRange(courier.working_hours)
    return [order for order in orders if courier_times.intersect(TimeRange(order.delivery_hours))]


def assign_to(courier, orders):

    if courier.assigned_now:
        return courier.current_assignation

    if not orders:
        if not courier.assigned_now:
            return Assignation(courier=courier, assign_time=datetime.now())

    assign = Assignation.objects.create(courier=courier)

    for order in orders:
        order.assigned_to = assign
        order.save()
    courier.assigned_now = True
    courier.save()
    return assign


def complete(order, courier, complete_time):
    time = parse_datetime(complete_time)
    orders = courier.completed_orders.order_by('-complete_time')
    if not orders:
        order.delivery_time = time - courier.current_assignation.assign_time
        order.complete_time = time
        order.save()
        return order
    order.delivery_time = time - orders.first().complete_time
    order.complete_time = complete_time
    order.save()
    courier.assigned_now = bool(courier.current_assignation.not_completed_orders)
    courier.save()
    return order


@receiver(pre_save, sender=Courier)
def courier_post_save(sender, instance, *args, **kwargs):
    if assignation := instance.current_assignation:
        orders = get_possible_orders(instance, assigned_to=assignation)
        for order in assignation.orders.all():
            if order not in orders:
                order.assigned_to = None
                order.save()
        if assignation.orders.count() == 0:
            assignation.delete()
            instance.assigned_now = False
