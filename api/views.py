from datetime import timedelta
from django.utils.dateparse import parse_datetime
import uuid
from django.forms import ValidationError
from rest_framework import views, generics, mixins
from rest_framework.response import Response
from rest_framework import status

from .models import (
    ShopUnit,
    ShopUnitType,
    ShopUnitStatisticUnit,
    ShopUnitStatisticResponse,
)
from .serializers import (
    ShopUnitSerializer,
    ShopUnitImportRequestSerializer,
    ShopUnitStatisticResponseSerializer,
)


class ShopUnitGetAllView(views.APIView):
    """
    A view for retrieving all shop units.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve all shop units.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A Response object containing serialized shop unit data.
        """
        shop_units = ShopUnit.objects.all()
        serializer = ShopUnitSerializer(shop_units, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopUnitGetItemView(views.APIView):
    """
    View class for retrieving a shop unit by its ID.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieves a shop unit by its ID and returns the serialized data.

        Args:
            request: The HTTP request object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments, containing the 'pk' parameter.

        Returns:
            A Response object with the serialized data of the shop unit if it exists,
            or a 404 response if the item doesn't exist.

        Raises:
            ValidationError: If the 'pk' parameter is not a valid UUID.
        """
        pk = kwargs.get("pk")
        try:
            shop_unit = ShopUnit.objects.get(id=pk)
            serializer = ShopUnitSerializer(shop_unit)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except ShopUnit.DoesNotExist:
            return Response(
                {"message": "Such item doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError:
            return Response(
                {"message": "{} is not a valid UUID".format(pk)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ShopUnitCreateView(generics.CreateAPIView):
    """
    A view for creating new shop units.
    """

    serializer_class = ShopUnitImportRequestSerializer

    def updateItem(shop_unit, item, date):
        """
        Updates an item in a shop unit if it exists.

        Parameters:
            shopUnit (ShopUnit): The shop unit to update the item in.
            item (dict): The item to update.
            date (datetime): The date to set for the shop unit.

        Returns:
            None: If the update is successful.

        Raises:
            Response: If the item type is different from the shop unit type.
        """

        if item["type"] != shop_unit.type:
            return Response(
                {"message": "Forbidden to change type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update shop unit properties
        shop_unit.name = item["name"]
        shop_unit.date = date
        shop_unit.parent_id = item.get("parentId")
        if shop_unit.type == ShopUnitType.OFFER:
            shop_unit.price = item.get("price", 0)
        else:
            shop_unit.price = None

        # Save the changes to shop unit
        shop_unit.save()

        # Create record in statistics table
        shop_unit_statistic_unit = ShopUnitStatisticUnit(
            id=shop_unit.id,
            stat_id=uuid.uuid4(),
            name=shop_unit.name,
            parent_id=shop_unit.parent_id,
            type=shop_unit.type,
            date=date,
            price=shop_unit.price,
        )
        shop_unit_statistic_unit.save()

    def post(self, request, *args, **kwargs):
        """
        Handles a POST request to create multiple items.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response indicating the result of the request.
        """
        items = request.data["items"]
        date = request.data["updateDate"]

        for item in items:
            item_id = item.get("id") or uuid.uuid4()

            shop_unit = ShopUnit.objects.filter(id=item_id).first()
            if shop_unit:
                resp = ShopUnitCreateView.updateItem(shop_unit, item, date)
                if resp is not None:
                    return resp
                continue

            item_name = item["name"]
            parent_id = item.get("parentId")
            parent = None

            if parent_id != "null":
                parent = ShopUnit.objects.filter(id=parent_id)
                if not parent:
                    return Response(
                        {"message": "Parent does not exist"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if parent[0].type == ShopUnitType.OFFER:
                    return Response(
                        {"message": "Parent must be a category"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            item_type = {
                ShopUnitType.OFFER: ShopUnitType.OFFER,
                ShopUnitType.CATEGORY: ShopUnitType.CATEGORY,
            }.get(item["type"])

            if item_type is None:
                return Response(
                    {"message": "No such type"}, status=status.HTTP_400_BAD_REQUEST
                )

            shop_unit = ShopUnit(id=item_id, name=item_name, date=date, type=item_type)
            if item_type == ShopUnitType.OFFER:
                shop_unit.price = item.get("price", 0)
            else:
                shop_unit.price = None

            if parent_id is not None:
                shop_unit.parentId = parent_id

            shop_unit.save()

            if parent_id is not None:
                parent = parent[0]
                parent.children.add(shop_unit)

            statistic_unit = ShopUnitStatisticUnit(
                statid=uuid.uuid4(),
                name=item_name,
                parentId=shop_unit.parentId,
                type=item_type,
                date=date,
                price=shop_unit.price,
            )
            statistic_unit.save()

        return Response(status=status.HTTP_201_CREATED)


class ShopUnitStatisticsGetView(views.APIView):
    """
    A view that shows statistics for a shop unit by its id.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieves a specific ShopUnitStatisticUnit object by its ID and returns the corresponding ShopUnitStatisticResponse object.

        Args:
            request (HttpRequest): The HTTP request object.
            **kwargs: Arbitrary keyword arguments containing pk.

        Returns:
            Response: The serialized ShopUnitStatisticResponse object or an error response.

        Raises:
            ValidationError: If the ID is not a valid UUID.
        """
        pk = kwargs.get("pk")

        try:
            queryset = ShopUnitStatisticUnit.objects.filter(id=pk)

            if queryset:
                # create statistic_response object
                response = ShopUnitStatisticResponse()
                response.save()
                response.items.add(queryset)
                # return it
                serializer = ShopUnitStatisticResponseSerializer(
                    [response], many=True
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            # if statistic is not found
            return Response(
                {"message": "Such item doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )

        except ValidationError:
            return Response(
                {"message": "{} is not a valid UUID".format(pk)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ShopUnitSalesView(views.APIView):
    # view showing statistics about units with sales during 24h from date in request

    def get(self, request, *args, **kwargs):
        date = request.GET.get("date")

        date_end = parse_datetime(date)

        if date_end is None:
            return Response(
                {"message": "Incorrect data format"}, status=status.HTTP_400_BAD_REQUEST
            )

        date_start = date_end - timedelta(hours=24)
        queryset = ShopUnitStatisticUnit.objects.filter(
            date__range=[date_start, date_end], type=ShopUnitType.OFFER
        )

        # create statistic_response object
        shopUnitStatisticResponse = ShopUnitStatisticResponse(id=uuid.uuid4())
        shopUnitStatisticResponse.save()
        for stat in queryset.all():
            shopUnitStatisticResponse.items.add(stat)
        # return it
        serializer = ShopUnitStatisticResponseSerializer(
            [shopUnitStatisticResponse], many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopUnitDeleteView(generics.GenericAPIView):
    # view to delete a shop unit by id

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            queryset = ShopUnit.objects.filter(id=pk)

            if queryset:
                ShopUnit.delete_recursive(queryset[0])
                return Response(
                    {"message": "deleted succesfully"}, status=status.HTTP_200_OK
                )
            return Response(
                {"message": "such item doesnt exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError:
            return Response(
                {"message": "{} is not a valid uuid".format(pk)},
                status=status.HTTP_400_BAD_REQUEST,
            )
