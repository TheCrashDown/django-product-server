import uuid
from django.db import models

class ShopUnitType(models.TextChoices):
    OFFER = "OFFER"
    CATEGORY = "CATEGORY"

class ShopUnit(models.Model):
    # basic model with information about products

    # required fields
    id = models.UUIDField(primary_key=True, 
                          default=uuid.uuid4(),
                          editable=False)
    name = models.CharField(max_length=225)
    date = models.DateTimeField()
    type = models.CharField(max_length=10, 
                            choices=ShopUnitType.choices, 
                            default=ShopUnitType.OFFER)

    # properties
    parentId = models.UUIDField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    children = models.ManyToManyField("self", 
                                      symmetrical=False, 
                                      blank=True)
    
    def __str__(self):
        return self.name + " " + str(self.id)

    def calculatePrice(shopUnit):
        # function to calculate category price
        if shopUnit.type == ShopUnitType.OFFER:
            return shopUnit.price
        
        if shopUnit.children.count() == 0:
            return 0
        
        sum = 0.0
        for child in shopUnit.children.all():
            sum += ShopUnit.calculatePrice(child)
        return sum / shopUnit.children.count()

    def updatePrice(shopUnit):
        # function to recursively update parent category price when item is updated

        if shopUnit.parentId == 'null':
            return

        if shopUnit.type == ShopUnitType.CATEGORY:
            shopUnit.price = ShopUnit.calculatePrice(shopUnit)
            shopUnit.save()
        
        parent = ShopUnit.objects.filter(id=shopUnit.parentId)
        
        if parent:
            ShopUnit.updatePrice(parent[0])
    
    def deleteStatistics(shopUnit):
        # function to delete statistics of deleted shopUnit
        statistics = ShopUnitStatisticUnit.objects.filter(id=shopUnit.id)
        if not statistics:
            return
        for stat in statistics.all():
            stat.delete()

    def deleteRecursive(shopUnit):
        # function to recursively delete item and its subcategories
        if shopUnit.type == ShopUnitType.OFFER:
            ShopUnit.deleteStatistics(shopUnit)
            shopUnit.delete()
            return
        if shopUnit.children.count() == 0:
            shopUnit.delete()
            return
        for child in shopUnit.children.all():
            ShopUnit.deleteRecursive(child)
        
        ShopUnit.deleteStatistics(shopUnit)
        shopUnit.delete()
        return




class ShopUnitImport(models.Model):
    # model to import data from requests

    # required fields
    id = models.UUIDField(primary_key=True, 
                          default=uuid.uuid4(),
                          editable=False)
    name = models.CharField(max_length=225)
    type = models.CharField(max_length=10, 
                            choices=ShopUnitType.choices, 
                            default=ShopUnitType.OFFER)

    # properties
    parentId = models.UUIDField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.name



class ShopUnitImportRequest(models.Model):
    items = models.ManyToManyField(ShopUnitImport)
    updateDate = models.DateTimeField



class ShopUnitStatisticUnit(models.Model):
    statid = models.UUIDField(primary_key=True, 
                              default=uuid.uuid4(), 
                              editable=False)
    # required fields
    id = models.UUIDField(default=uuid.uuid4(),
                          editable=False)
    name = models.CharField(max_length=225)
    type = models.CharField(max_length=10, 
                            choices=ShopUnitType.choices, 
                            default=ShopUnitType.OFFER)
    date = models.DateTimeField()

    # properties
    parentId = models.UUIDField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
        
    def __str__(self):
        return self.name + " " + str(self.date)

class ShopUnitStatisticResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    items = models.ManyToManyField(ShopUnitStatisticUnit)
