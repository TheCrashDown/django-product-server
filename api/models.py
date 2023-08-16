import uuid
from django.db import models


class ShopUnitType(models.TextChoices):
    OFFER = "OFFER"
    CATEGORY = "CATEGORY"


class ShopUnit(models.Model):
    """
    Basic model with information about products
    """

    # required fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=225)
    date = models.DateTimeField()
    type = models.CharField(
        max_length=10, choices=ShopUnitType.choices, default=ShopUnitType.OFFER
    )

    # properties
    parentId = models.UUIDField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    children = models.ManyToManyField("self", symmetrical=False, blank=True)

    def __str__(self) -> str:
        """
        Convert the object to a string representation.

        Returns:
            str: The string representation of the object.
        """
        return f"{self.name} {str(self.id)}"

    def delete_statistics(self) -> None:
        """
        Deletes the statistics for the shop unit.

        Returns:
            None
        """
        # Retrieve the statistics for the shop unit
        statistics = ShopUnitStatisticUnit.objects.filter(id=self.id)

        # Check if there are any statistics
        if not statistics.exists():
            return

        # Delete each statistic
        for stat in statistics:
            stat.delete()

    def delete_recursive(self):
        """
        Recursively deletes an item and its subcategories.
        """
        if self.type == ShopUnitType.OFFER:
            self.delete_statistics()
            self.delete()
            return

        if self.children.count() == 0:
            self.delete()
            return

        for child in self.children.all():
            child.delete_recursive()

        self.delete_statistics()
        self.delete()


class ShopUnitImport(models.Model):
    """
    Model to import data from requests
    """

    # required fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=225)
    type = models.CharField(
        max_length=10, choices=ShopUnitType.choices, default=ShopUnitType.OFFER
    )

    # properties
    parentId = models.UUIDField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        """
        Convert the object to a string representation.

        Returns:
            str: The string representation of the object.
        """
        return self.name


class ShopUnitImportRequest(models.Model):
    """
    Request to import multiple ShopUnitImport's
    """

    items = models.ManyToManyField(ShopUnitImport)
    updateDate = models.DateTimeField


class ShopUnitStatisticUnit(models.Model):
    """
    Unit providing statistics for ShopUnit
    """

    statid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    # required fields
    id = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=225)
    type = models.CharField(
        max_length=10, choices=ShopUnitType.choices, default=ShopUnitType.OFFER
    )
    date = models.DateTimeField()

    # properties
    parentId = models.UUIDField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:
        """
        Convert the object to a string representation.

        Returns:
            str: The string representation of the object.
        """
        return f"{self.name} {str(self.date)}"


class ShopUnitStatisticResponse(models.Model):
    """
    Response for statistics request
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    items = models.ManyToManyField(ShopUnitStatisticUnit)
