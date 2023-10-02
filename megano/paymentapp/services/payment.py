class FakePaymentService:
    """
        Фиктивный сервис для оплаты заказа
    """

    def pay_order(self, order_id, card_number, amount):
        if card_number % 2 == 0 and str(card_number)[-1] != '0':
            return True, "Оплата успешно подтверждена."
        else:
            return False, "Ошибка: Неверный пин-код."

