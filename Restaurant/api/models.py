from django.db import models

STATUS = (
    ("DELIVERED", "Delivered"),
    ("IN_TRANSIT", "In Transit"),
    ("IN_PROGRESS", "In Progress"),
    ("NOT_FOUND", "Not Found")
)



class Products(models.Model):
    name = models.CharField(max_length=200, unique=True)
    price = models.PositiveIntegerField(null=False, default=200)

    def __str__(self):
        return self.name


    
class Orders(models.Model):
    order_key = models.IntegerField(blank=False, null=False, default=230584)
    session_id = models.CharField(max_length=300, default="Alakada")

    

    def __str__(self):
        return str(self.id)
    def get_total_amount(self):
        total = 0
        order_items = self.orderitem_set.all()
        for item in order_items:
            total += item.quantity * item.product.price
        return total
    
    @property
    def item_names(self):
        return [(item.id ,item.product.name, item.quantity, item.product.price) for item in self.orderitem_set.all()]
    



class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order} - {self.product} - {self.quantity}"
    
class Tracking(models.Model):
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=15, choices=STATUS, default = "NOT_FOUND"
    )
