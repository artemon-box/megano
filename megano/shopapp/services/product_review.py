from shopapp.models import ProductReview


class ProductReviewService:
    @classmethod
    def get_reviews_for_product(cls, product):
        """
        Получение списка всех отзывов для конкретного товара.

        :param product: Продукт, для которого нужно получить отзывы.
        :return: Queryset с требуемым продуктом.
        """
        reviews = ProductReview.objects.filter(product=product)

        return reviews

    @classmethod
    def add_review_for_product(cls, product, user_id, review_text):
        """
        Добавление отзыва к товару от конкретного пользователя.

        :param product: Продукт, для которого нужно добавить отзыв.
        :param user_id: Пользователь, который добавляет отзыв.
        :param review_text: Текст отзыва.
        """

        ProductReview.objects.create(product=product, user_id=user_id, text=review_text)

    @classmethod
    def get_reviews_count(cls, product):
        """
        Получить количество отзывов для товара

        :param product: Продукт, для которого нужно получить количество отзывов.
        :return: Количество отзывов для данного продукта.
        """
        reviews_count = ProductReview.objects.filter(product=product).order_by("-created_at").count()

        return reviews_count
