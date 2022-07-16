from datetime import timedelta
from django.utils.dateparse import parse_datetime
import uuid
from django.forms import ValidationError
from rest_framework import views, generics, mixins
from rest_framework.response import Response
from rest_framework import status

from .models import ShopUnit, ShopUnitType, ShopUnitStatisticUnit, ShopUnitStatisticResponse
from .serializers import ShopUnitSerializer, ShopUnitImportRequestSerializer, \
    ShopUnitStatisticResponseSerializer



class ShopUnitGetAllView(views.APIView):
    # view showing all elements

    def get(self, request, *args, **kwargs):
        queryset = ShopUnit.objects.all()
        serializer = ShopUnitSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopUnitGetItemView(views.APIView):
    # view showing element by id

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            queryset = ShopUnit.objects.filter(id=pk)
            serializer = ShopUnitSerializer(queryset, many=True)

            if queryset:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'message' : 'such item doesnt exist'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            return Response({'message' : '{} is not a valid uuid'.format(pk)}, status=status.HTTP_400_BAD_REQUEST)



class ShopUnitCreateView(generics.CreateAPIView):
    # general view to import new items
    
    serializer_class = ShopUnitImportRequestSerializer

    def updateItem(shopUnit, item, date):
        # function to update item if it exists

        if item['type'] != shopUnit.type:
            return Response({'message' : 'forbidden to change type'},status=status.HTTP_400_BAD_REQUEST)
        
        shopUnit.name=item['name']
        shopUnit.date=date
        if item['parentId'] != 'null':
            shopUnit.parentId=item['parentId']
        shopUnit.price=item['price']
        shopUnit.save()


        ShopUnit.updatePrice(shopUnit)

        # create record in statistics table
        shopUnitStatisticUnit = ShopUnitStatisticUnit(id=shopUnit.id,
                                                      statid=uuid.uuid4(),
                                                      name=shopUnit.name, 
                                                      parentId=shopUnit.parentId,
                                                      type=shopUnit.type,
                                                      date=date,
                                                      price=shopUnit.price)
        shopUnitStatisticUnit.save()

        return None

    def post(self, request, *args, **kwargs):
        items = request.data['items']
        date = request.data['updateDate']

        # handle all items in request
        for item in items:
            id = item['id'] or uuid.uuid4()
            
            # check if such id already exists
            existing_id = ShopUnit.objects.filter(id=id)
            if existing_id:
                shopUnit = existing_id[0]
                resp = ShopUnitCreateView.updateItem(shopUnit, item, date)
                if resp != None:
                    return resp
                continue

            # if not exist => we create it now
            name = item['name']
            parentId = item['parentId']
            parent = ""
            
            if parentId != 'null':
                # check if parent is correct
                parent = ShopUnit.objects.filter(id=parentId)
                if not parent:
                    return Response({'message' : 'Parent not exist'}, status=status.HTTP_400_BAD_REQUEST)
                if parent[0].type == ShopUnitType.OFFER:
                    return Response({'message' : 'Parent must be a category'}, status=status.HTTP_400_BAD_REQUEST)

            # switch item type
            # case offer
            if item['type'] == ShopUnitType.OFFER:
                type = ShopUnitType.OFFER
            # case category
            elif item['type'] == ShopUnitType.CATEGORY:
                type = ShopUnitType.CATEGORY
            # else == bad data
            else:
                 return Response({'message' : 'No such type'}, status=status.HTTP_400_BAD_REQUEST)
            
            shopUnit = ShopUnit(id=id,
                                name=name,
                                date=date,
                                type=type)
            if type == ShopUnitType.OFFER:
                shopUnit.price = item['price'] or 0
            else:
                shopUnit.price = ShopUnit.calculatePrice(shopUnit)
            if parentId != 'null':
                shopUnit.parentId = parentId

            shopUnit.save()

            # update parent's children list and price
            if parentId != 'null':
                parent = parent[0]
                parent.children.add(shopUnit)
                parent.price = ShopUnit.calculatePrice(parent)
                parent.save()


            ShopUnit.updatePrice(shopUnit)
            
            # create record in statistics table
            shopUnitStatisticUnit = ShopUnitStatisticUnit(id=id,
                                                          statid=uuid.uuid4(),
                                                          name=name, 
                                                          parentId=shopUnit.parentId,
                                                          type=type,
                                                          date=date,
                                                          price=shopUnit.price)
            shopUnitStatisticUnit.save()
        

        return Response(status=status.HTTP_201_CREATED) 


class ShopUnitStatisticsGetView(views.APIView):
    # view showing statistics for a shop unit by id

    def get(self, request, *args, **kwargs):
        
        pk = kwargs.get('pk')
        
        try:
            queryset = ShopUnitStatisticUnit.objects.filter(id=pk)

            if queryset:
                # create statistic_response object
                shopUnitStatisticResponse = ShopUnitStatisticResponse()
                shopUnitStatisticResponse.save()
                for stat in queryset.all():
                    shopUnitStatisticResponse.items.add(stat)
                # return it
                serializer = ShopUnitStatisticResponseSerializer([shopUnitStatisticResponse], many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            # if statistic is not found
            return Response({'message' : 'such item doesnt exist'}, status=status.HTTP_404_NOT_FOUND)
        
        except ValidationError:
            return Response({'message' : '{} is not a valid uuid'.format(pk)}, status=status.HTTP_400_BAD_REQUEST)


class ShopUnitSalesView(views.APIView):
    # view showing statistics about units with sales during 24h from date in request
    
    def get(self, request, *args, **kwargs):

        date = request.GET.get('date')
        
        date_end = parse_datetime(date)

        if date_end is None:
            return Response({'message' : 'incorrect data format'}, status=status.HTTP_400_BAD_REQUEST)

        date_start = date_end - timedelta(hours=24)
        queryset = ShopUnitStatisticUnit.objects.filter(date__range=[date_start, date_end], 
                                                        type=ShopUnitType.OFFER)

        # create statistic_response object
        shopUnitStatisticResponse = ShopUnitStatisticResponse(id=uuid.uuid4())
        shopUnitStatisticResponse.save()
        for stat in queryset.all():
            shopUnitStatisticResponse.items.add(stat)
        # return it
        serializer = ShopUnitStatisticResponseSerializer([shopUnitStatisticResponse], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ShopUnitDeleteView(generics.GenericAPIView):
    # view to delete a shop unit by id

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            queryset = ShopUnit.objects.filter(id=pk)

            if queryset:
                ShopUnit.deleteRecursive(queryset[0])
                return Response({'message' : 'deleted succesfully'}, status=status.HTTP_200_OK)
            return Response({'message' : 'such item doesnt exist'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            return Response({'message' : '{} is not a valid uuid'.format(pk)}, status=status.HTTP_400_BAD_REQUEST)


