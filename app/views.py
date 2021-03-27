from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.views import Response
from .serializers import CourierSerializer, UpdateCourierSerializer, OrderSerializer, AssignationSerializer
from .models import Courier, Order, Assignation
from rest_framework.decorators import action
from .logic import get_possible_orders, assign_to, complete
from django.utils.timezone import datetime


class CourierViewSet(ModelViewSet):
    queryset = Courier.objects.all()

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return UpdateCourierSerializer
        return CourierSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get('data')
        couriers_to_save = []
        errors = []
        if not data or not isinstance(data, list):
            raise serializers.ValidationError('Data not present or is not a list')
        for courier_data in data:
            courier = CourierSerializer(data=courier_data)
            if courier.is_valid():
                couriers_to_save.append(courier)
                continue
            errors.append({'id': courier_data.get('courier_id'), 'errors': {**courier.errors}})

        if errors:
            raise serializers.ValidationError({"validation_error": {"couriers": errors}})
        for courier in couriers_to_save:
            courier.save()
        return Response({"couriers": [{"id": courier.data['courier_id']} for courier in couriers_to_save]}, status=201)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(["POST"], detail=False)
    def complete(self, request):
        courier = Courier.objects.filter(courier_id=request.data.get('courier_id'))
        order = Order.objects.filter(order_id=request.data.get('order_id'))
        complete_time = request.data.get('complete_time')
        if not complete_time or not courier or not order:
            return Response(status=400)
        courier = courier.first()
        order = order.first()

        if courier != order.assigned_to.courier:
            return Response(status=400)

        if order.complete_time:
            return Response({"order_id": order.order_id})

        complete(order, courier, complete_time)

        return Response({"order_id": order.order_id})

    @action(["POST"], detail=False)
    def assign(self, request):
        courier_id = request.data.get("courier_id")
        courier = Courier.objects.filter(courier_id=courier_id)
        if not courier:
            return Response({"error": "wrong courier id"}, status=400)
        courier = courier.first()
        orders = get_possible_orders(courier)
        assign = assign_to(courier, orders)
        if not assign.orders.all():
            return Response({"orders": []})
        return Response(AssignationSerializer(assign).data)

    def create(self, request, *args, **kwargs):
        data = request.data.get('data')
        orders_to_save = []
        errors = []
        if not data or not isinstance(data, list):
            raise serializers.ValidationError('Data not present or is not a list')
        for order_data in data:
            order = OrderSerializer(data=order_data)
            if order.is_valid():
                orders_to_save.append(order)
                continue
            errors.append({'id': order_data.get('order_id'), 'errors': {**order.errors}})

        if errors:
            raise serializers.ValidationError({"validation_error": {"orders": errors}})
        for order in orders_to_save:
            order.save()
        return Response({"orders": [{"id": order.data['order_id']} for order in orders_to_save]}, status=201)
