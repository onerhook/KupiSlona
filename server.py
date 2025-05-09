from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    
    handle_dialog(request.json, response)
    
    logging.info(f'Response: {response!r}')
    
    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    
    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'elephant_count': 0
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return
    
    user_response = req['request']['original_utterance'].lower()
    
    if user_response in ['ладно', 'куплю', 'покупаю', 'хорошо', 'да', 'ок']:
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return
    
    sessionStorage[user_id]['elephant_count'] += 1
    count = sessionStorage[user_id]['elephant_count']
    
    if count == 1:
        res['response']['text'] = f"Все говорят '{user_response}', а ты купи слона!"
    elif count == 2:
        res['response']['text'] = f"Ну пожалуйста! Купи слона!"
    else:
        res['response']['text'] = f"Я не отстану! Купи слона!"
    
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]
    
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]
    
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })
    
    return suggests

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
