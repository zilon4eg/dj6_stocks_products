from rest_framework import serializers

from logistic.models import Product, StockProduct, Stock


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']
    pass


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['address', 'positions']
    # настройте сериализатор для склада

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        # здесь вам надо заполнить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions

        for position in positions:
            StockProduct.objects.create(
                stock=stock,
                # product=Product.objects.get(id=position['product']),
                product=position['product'],
                quantity=position['quantity'],
                price=position['price'],
            ).save()

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        # здесь вам надо обновить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions
        for position in positions:
            # если product с номером для обновления есть на складе, обновляем
            stock_product = StockProduct.objects.filter(product=position['product'])
            if stock_product:
                stock_product.update(
                    stock=stock,
                    product=position['product'],
                    quantity=position['quantity'],
                    price=position['price'],
                )
            else:
                # если нет добавляем
                StockProduct.objects.create(
                    stock=stock,
                    product=position['product'],
                    quantity=position['quantity'],
                    price=position['price'],
                ).save()

        return stock
