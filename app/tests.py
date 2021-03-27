from rest_framework.test import APITestCase
from django.test import Client
import json
from .logic import TimeRange


class CourierApiTestCase(APITestCase):
    def setUp(self):
        self.client = Client()

    def test_creation(self):
        data = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "car",
                    "regions": [
                        1, 2
                    ],
                    "working_hours": [
                        "10:20-11:30"
                    ]
                },
                {
                    "courier_id": 2,
                    "courier_type": "foot",
                    "regions": [
                        3, 4
                    ],
                    "working_hours": [
                    ]
                }
            ]
        }

        response = self.client.post(
            '/couriers',
            json.dumps(data),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content), {
            "couriers": [
                {
                    "id": 1
                },
                {
                    "id": 2
                }
            ]
        })

    def test_not_unique_id(self):
        data = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "car",
                    "regions": [],
                    "working_hours": []
                },
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [],
                    "working_hours": []
                }
            ]
        }
        response = self.client.post(
            '/couriers',
            json.dumps(data),
            content_type='application/json')
        self.assertEquals(response.status_code, 400)

    def test_wrong_time_format(self):
        data = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "car",
                    "regions": [],
                    "working_hours": ["abc"]
                }
            ]
        }
        response = self.client.post(
            '/couriers',
            json.dumps(data),
            content_type='application/json')
        self.assertEquals(response.status_code, 400)

    def test_get(self):
        data = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "car",
                    "regions": [1],
                    "working_hours": []
                }
            ]
        }
        response = self.client.post(
            '/couriers',
            json.dumps(data),
            content_type='application/json')
        self.assertEquals(response.status_code, 201)
        response = self.client.get('/couriers/1')
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/couriers/2')
        self.assertEquals(response.status_code, 404)

    def test_patch(self):
        data = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "car",
                    "regions": [1],
                    "working_hours": []
                }
            ]
        }

        response = self.client.post(
            '/couriers',
            json.dumps(data),
            content_type='application/json')
        self.assertEquals(response.status_code, 201)
        response = self.client.patch(
            '/couriers/1',
            json.dumps(
                {
                    "courier_type": "bike",
                    "regions": [1, 3, 4],
                    "working_hours": ["10:20-11:30"]
                }
            ),
            content_type='application/json'
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(
            {
                "courier_id": 1,
                "courier_type": "bike",
                "regions": [1, 3, 4],
                "working_hours": ["10:20-11:30"]
            },
            json.loads(response.content)
        )


class TimeRangeTestCase(APITestCase):
    def test_intersect(self):
        data1 = ["10:20-10:40", "10:45-10:50"]
        data2 = ["10:25-10:35"]
        self.assertTrue(TimeRange(data1).intersect(TimeRange(data2)))

        data2 = ["10:40-10:44"]
        self.assertTrue(TimeRange(data1).intersect(TimeRange(data2)))

        data2 = ["10:41-10:45"]
        self.assertTrue(TimeRange(data1).intersect(TimeRange(data2)))

        data2 = ["10:41-10:44"]
        self.assertFalse(TimeRange(data1).intersect(TimeRange(data2)))


class OrderTestCase(APITestCase):
    def setUp(self):
        self.client = Client()

    def couriers_setUp(self):
        couriers = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [100],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [1, 12],
                    "working_hours": ["09:00-18:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [12, 22, 23, 33],
                    "working_hours": []
                }
            ]
        }

        self.client.post(
            '/couriers',
            json.dumps(couriers),
            content_type='application/json'
        )

    def orders_SetUp(self):
        orders = {
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        }

        self.client.post(
            "/orders",
            json.dumps(orders),
            content_type='application/json'
        )

    def test_creation(self):
        data = {
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        }
        response = self.client.post("/orders", json.dumps(data),
                                    content_type='application/json')

        self.assertEquals(response.status_code, 201)
        self.assertEquals(json.loads(response.content), {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]})

    def test_assign(self):
        self.couriers_setUp()
        self.orders_SetUp()

        data = {
            "courier_id": 2
        }

        response = self.client.post(
            "/orders/assign",
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            json.loads(response.content)['orders'],
            [{"id": 1}, {"id": 2}]
        )

        self.assertIn("assign_time", json.loads(response.content).keys())

    def test_complete(self):
        self.test_assign()
        data = {
            "courier_id": 2,
            "order_id": 2,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }
        response = self.client.post(
            "/orders/complete",
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            json.loads(response.content),
            {
                "order_id": 2
            }
        )

    def test_assign_wrong_courier(self):
        self.orders_SetUp()
        self.couriers_setUp()

        data = {
            "courier_id": 110
        }

        response = self.client.post(
            "/orders/assign",
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_assign_not_found(self):
        self.orders_SetUp()
        self.couriers_setUp()

        data = {
            "courier_id": 1
        }

        response = self.client.post(
            "/orders/assign",
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            json.loads(response.content),
            {
                "orders": []
            }
        )
