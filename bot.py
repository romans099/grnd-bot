import requests
import json
import time
import re
import ast

TELEGRAM_TOKEN = '7419880072:AAHFbjYLT5s8GBHd5XykgJ6RjVwQo5KLwWE'

# КОМУ ОТПРАВЛЯТЬ (личка + группа)
CHAT_IDS = [
    '1812692747',           # Твой ID
    '-1004469277708',       # Группа "grnd bot"
]

API_LIST_URL = 'https://api-site.grnd.gg/admin/complaints'
API_DETAIL_URL = 'https://api-site.grnd.gg/admin/complaints/ru/'

PARAMS = {
    'status': '0',
    'server': '{"ru":[33]}',
    '_': str(int(time.time() * 1000))
}

COOKIES = {
    'i18n_redirected': 'ru',
    'grnd_sid': 's%3AjTOM2sRvbUd86iyR-uVlPTp6VUBddcGa.xxJVyVibF8VMqHluGzzIl6p9SFlEw%2FlV2cQh7I7HEmg',
    'filters:/admin/complaints:region': '%5B%22ru%22%5D',
    'filters:/admin/complaints:server': '%7B%22ru%22%3A%5B33%5D%7D',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
    'Referer': 'https://grnd.gg/admin/complaints',
}

def send_telegram(message, photo_url=None):
    for target in CHAT_IDS:
        if photo_url:
            try:
                img_data = requests.get(photo_url, timeout=10).content
                files = {'photo': ('complaint.jpg', img_data)}
                data = {'chat_id': target, 'caption': message, 'parse_mode': 'HTML'}
                requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto', data=data, files=files, timeout=15)
                continue
            except:
                pass
        try:
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': target, 'text': message, 'parse_mode': 'HTML'}, timeout=10)
        except:
            pass

def get_last():
    try:
        with open('last.txt', 'r') as f:
            return f.read().strip()
    except:
        return None

def save_last(x):
    with open('last.txt', 'w') as f:
        f.write(str(x))

def get_complaint_details(complaint_id):
    try:
        url = f'{API_DETAIL_URL}{complaint_id}'
        r = requests.get(url, headers=HEADERS, cookies=COOKIES, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data[0]
    except:
        pass
    return None

def check():
    print('🔄 Проверка...')
    try:
        r = requests.get(API_LIST_URL, params=PARAMS, headers=HEADERS, cookies=COOKIES, timeout=15)
        print(f'📡 Статус: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            complaints = data.get('complaints', [])
            print(f'📋 Найдено жалоб: {len(complaints)}')
            if complaints:
                new = complaints[-1]
                new_id = str(new.get('id'))
                old = get_last()
                if old != new_id:
                    details = get_complaint_details(new_id) or new
                    msg = "🆕 <b>НОВАЯ ЖАЛОБА!</b>\n\n"
                    msg += f"<b>Номер:</b> #{new_id}\n"
                    msg += f"<b>Время:</b> {details.get('createdAt', 'Не указано')}\n"
                    msg += f"<b>От:</b> {details.get('from_user_name', 'Неизвестно')}\n"
                    msg += f"<b>На:</b> {details.get('to_user_name', 'Неизвестно')}\n\n"
                    msg += f"<b>Текст:</b>\n{details.get('text', 'Не указан')[:500]}\n\n"
                    msg += f"🔗 <a href='https://grnd.gg/admin/complaints/ru/{new_id}'>Открыть жалобу</a>"
                    
                    photo_url = None
                    images = details.get('images', '')
                    if images:
                        try:
                            img_list = ast.literal_eval(images)
                            if img_list and isinstance(img_list, list):
                                photo_url = img_list[0]
                        except:
                            if isinstance(images, str) and images.startswith('http'):
                                photo_url = images
                    
                    send_telegram(msg, photo_url)
                    save_last(new_id)
                    print('✅ Новая жалоба #', new_id)
                else:
                    print('ℹ️ Новых нет. Последняя:', old)
            else:
                print('ℹ️ Жалоб нет')
        else:
            print('❌ Ошибка HTTP:', r.status_code)
    except Exception as e:
        print('❌ Ошибка:', e)

if __name__ == '__main__':
    check()
