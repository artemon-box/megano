from shopapp.models import ProductReview


class ProductReviewService:
    def get_reviews_for_product(self, product):
        """
        Получение списка всех отзывов для конкретного товара
        """
        reviews = ProductReview.objects.filter(product=product)

        return reviews

    def add_review_for_product(self, product, user_id, review_text):
        """
        Добавление отзыва к товару от конкретного пользователя
        """
        ProductReview.objects.create(product=product, user_id=user_id, text=review_text)

    def get_reviews_count(self, product):
        """
        Получить количество отзывов для товара
        """
        reviews_count = ProductReview.objects.filter(product=product).count()


        return reviews_count
