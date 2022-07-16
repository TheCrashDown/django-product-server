from django.test import TestCase

from .models import ShopUnit, ShopUnitType


class GetSalesTestCase(TestCase):
    # TESTING /sales/ api

    def setUp(self):
        pass

    def testValidDate(self):
        # valid date format
        response = self.client.get('/api/sales?date=2021-05-28T21:12:01.000Z')

        self.assertEqual(response.status_code, 200)

        
    def testInvalidDate(self): 
        # invalid date format
        response = self.client.get('/api/sales?date=05-28-2022-22:00')

        self.assertEqual(response.status_code, 400)


class getNodesTestCase(TestCase):
    # TESTING /nodes/{id} api

    def setUp(self):
        ShopUnit.objects.create(id="3fa85f64-5717-4562-b3fc-2c963f66a222",
                                name="OFF1",
                                price=234,
                                type=ShopUnitType.OFFER,
                                date="2021-05-28T21:12:01.000Z")
    
    def testGetExistingItem(self):
        # item exists
        response = self.client.get('/api/nodes/3fa85f64-5717-4562-b3fc-2c963f66a222')

        self.assertEqual(response.status_code, 200)

    def testGetUnexistingItem(self):
        # item with such id doesnt exist
        response = self.client.get('/api/nodes/3fa85f64-5717-4562-b3fc-2c963f63a210')

        self.assertEqual(response.status_code, 404)
    
    def testGetInvalidId(self):
        # invalid uuid
        response = self.client.get('/api/nodes/3fawererwa210')
        
        self.assertEqual(response.status_code, 400)


