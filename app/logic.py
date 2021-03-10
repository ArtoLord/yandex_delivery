from .models import Order, Assignation, Courier
from sortedcontainers import SortedList


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


def get_possible_orders(courier):
    try:
        var = courier.assignation
        return []
    except Assignation.DoesNotExist:
        pass

    orders = Order.objects.filter(
        region__in=courier.regions.all(),
        weight__lte=courier.max_weight,
        assigned_to=None
    )

    courier_times = TimeRange(courier.working_hours)
    return [order for order in orders if courier_times.intersect(TimeRange(order.delivery_hours))]


def assign_to(courier, orders):
    assign, created = Assignation.objects.get_or_create(courier=courier)
    if not created:
        return assign
    for order in orders:
        order.assigned_to = assign
        order.save()
    return assign
