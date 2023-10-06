from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/pay', methods=['POST'])
def pay_order():
    try:
        data = request.get_json()
        order_number = data.get('order_number')
        card_number = data.get('card_number')
        quantity = data.get('quantity')

        if order_number % 2 == 0 and str(card_number)[-1] != '0':
            response = {'status': 'success', 'message': 'Оплата подтверждена'}
        elif order_number % 2 != 0 and str(card_number)[-1] == '0':
            raise Exception('Ошибка оплаты: случайная ошибка оплаты')
        else:
            response = {'status': 'success', 'message': 'Оплата подтверждена'}

        return jsonify(response)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
