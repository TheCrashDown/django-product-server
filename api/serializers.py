from rest_framework import serializers
from .models import ShopUnit, ShopUnitImport, ShopUnitImportRequest, \
    ShopUnitStatisticUnit, ShopUnitStatisticResponse

class ShopUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUnit
        fields = ('__all__')


class ShopUnitImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUnitImport
        fields = ('__all__')


class ShopUnitImportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUnitImportRequest
        fields = ('__all__')


class ShopUnitStatisticUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUnitStatisticUnit
        fields = ['id', 'name', 'date', 'parentId', 'price', 'type']


class ShopUnitStatisticResponseSerializer(serializers.ModelSerializer):
    items = ShopUnitStatisticUnitSerializer(many=True)
    class Meta:
        model = ShopUnitStatisticResponse
        fields = ['items']

