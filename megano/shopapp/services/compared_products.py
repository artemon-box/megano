from config import settings
from shopapp.models import ProductSeller, FeatureValue, ProductFeature


class ComparedProductsService:

    def __init__(self, request):
        """инициализировать список сравнения"""
        self.session = request.session
        compare_list = self.session.get(settings.COMPARE_LIST_SESSION_ID)
        if not compare_list:
            # сохранить пустой список в сеансе
            compare_list = self.session[settings.COMPARE_LIST_SESSION_ID] = []
        self.compare_list = compare_list

    def get_compared_products(self, max_items=3):
        """
        получение списка сравниваемых товаров
        (с возможностью ограничить количество, по умолчанию максимум ― три первых добавленных)
        """
        return self.compare_list[:max_items]

    def add_to_compared_products(self, product_id):
        """
        добавление товара в список сравниваемых
        """
        if product_id not in self.compare_list:
            self.compare_list.append(product_id)
            if self.compare_list.__len__() > 1:
                first_product = ProductSeller.objects.get(id=self.compare_list[0]).product
                current_product = ProductSeller.objects.get(id=product_id).product
                if first_product.category == current_product.category:
                    first_product_features = [feature.feature for feature in first_product.features.all()]
                    current_product_features = [feature.feature for feature in current_product.features.all()]
                    if first_product_features != current_product_features:
                        for feature in first_product_features:
                            if feature not in current_product_features:
                                value, created = FeatureValue.objects.get_or_create(feature=feature, value='-')
                                ProductFeature.objects.create(
                                    product=current_product,
                                    category=current_product.category,
                                    feature=feature,
                                    value=value
                                )
                        for feature in current_product_features:
                            if feature not in first_product_features:
                                value, created = FeatureValue.objects.get_or_create(feature=feature, value='-')
                                ProductFeature.objects.create(
                                    product=first_product,
                                    category=first_product.category,
                                    feature=feature,
                                    value=value
                                )
            self.save()

    def remove_from_compared_products(self, product_id):
        """
        удаление товара из списка сравниваемых
        """
        if product_id in self.compare_list:
            self.compare_list.remove(product_id)
            self.save()

    def clear(self):
        """
        очистить список сравниваемых товаров
        """
        self.compare_list.clear()
        self.save()

    def __len__(self):
        """
        получение количество товаров в списке сравнения
        """
        return len(self.compare_list)

    def save(self):
        """
        пометить сеанс как "измененный", чтобы обеспечить его сохранение
        """
        self.session.modified = True
