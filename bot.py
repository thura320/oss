import requests
import telebot
from telebot import types
import os
from gatet import Tele, get_proxy
import time

token = '7431401185:AAEWnMVfCxE7a7midTkYw2WmQh76fuErq2g'
bot = telebot.TeleBot(token, parse_mode="HTML")
subscriber = '6473717870'

def current_ip(proxy, retries=30, timeout=5):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get("https://api.ipify.org?format=json", proxies=proxy, timeout=timeout)
            print(f"Successfully fetched IP: {response.json().get('ip')}")
            return response.json().get("ip")
        except requests.exceptions.Timeout:
            print(f"Timeout error with proxy {proxy}. Retrying ({attempt + 1}/{retries})...")
            attempt += 1
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"Request error with proxy {proxy}: {e}")
            return "Unknown"
    print(f"Failed to fetch IP after {retries} attempts with proxy {proxy}. Skipping this proxy.")
    return "Unknown"

@bot.message_handler(commands=["start"])
def start(message):
    if str(message.chat.id) != subscriber:
        bot.reply_to(message, "Uhhh")
        return
    bot.reply_to(message, "Send the file now")

@bot.message_handler(content_types=["document"])
def main(message):
    if str(message.chat.id) != subscriber:
        bot.reply_to(message, "Uhmm")
        return
    
    dd = 0  # Declined cards count
    live = 0  # Live cards count
    insu = 0  # Insufficient funds cards count
    ko = bot.reply_to(message, "Checking Your Cards...⌛").message_id
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open("combo.txt", "wb") as w:
        w.write(downloaded_file)
    
    try:
        with open("combo.txt", 'r') as file:
            cards = file.readlines()
            total = len(cards)
            for cc in cards:
                if os.path.exists("stop.stop"):
                    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='𝗦𝗧𝗢𝗣𝗣𝗘𝗗 ✅\n𝗕𝗢𝗧 𝗕𝗬 ➜ @Thura')
                    os.remove("stop.stop")
                    return
                
                # Initialize proxy and IP
                proxy = None
                ip = "Unknown"
                while ip == "Unknown":
                    try:
                        proxy = get_proxy()
                        ip = current_ip(proxy)
                        if ip != "Unknown":
                            break
                    except Exception as e:
                        print(f"Error with proxy: {e}")
                    time.sleep(2)

                if ip == "Unknown":
                    dd += 1
                    continue

                try:
                    result, proxy_ip = Tele(cc.strip(), proxy)
                    print(f"Result from Tele for card {cc.strip()}: {result}")

                    # Add conditions for different results
                    if 'error' in result:
                        if 'declined' in result['error']:
                            status = f"{result}"
                            result_message = result['errors']
                            dd += 1
                        elif 'insufficient funds' in result['errors']:
                            status = "INSU FUNDS ✅"
                            result_message = "Insufficient funds"
                            insu += 1
                        elif 'security code is incorrect' in result or 'security code is invalid' in result['errors']:
                            status = "CCN LIVE ✅"
                            result_message = "Insufficient funds"
                            live += 1
                        elif 'your card does not support this type of purchase' in result['errors']:
                            status = "CVV LIVE ✅"
                            result_message = "Insufficient funds"
                            live += 1
                        elif 'success' in result or 'successfully' in result:
                            status = "APPROVED ✓"
                            result_message = "CVV CHARGED Ѳ.➂💲"
                            live += 1
                        else:
                            status = "ERROR ❌"
                            result_message = "Unknown error"
                    else:
                        # No errors, check if it's a live card
                        status = f"{result}"
                        result_message = "result"
                        dd += 1  # Count live cards

                except Exception as e:
                    status = "ERROR ❌"
                    result_message = "Processing failed"
                    dd += 1

                data = {}
                try:
                    bin_response = requests.get(f'https://lookup.binlist.net/{cc[:6]}')
                    if bin_response.status_code == 200:
                        data = bin_response.json()
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching BIN data: {e}")

                bank = data.get('bank', {}).get('name', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
                emj = data.get('country', {}).get('emoji', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
                cn = data.get('country', {}).get('name', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
                dicr = data.get('scheme', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
                typ = data.get('type', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')

                msg = f'''✮ 𝑪𝑨𝑹𝑫  ➜ {cc.strip()} 
✮ 𝑺𝑻𝑨𝑻𝑼𝑺 ➜ {status}
✮ 𝑹𝑬𝑺𝑼𝑳𝑻 ➜ {result_message}
✮ 𝑮𝑨𝑻𝑬𝑾𝑨𝑌 ➜ Stripe Charge
━━━━━━━━━━━━━━━━━
✮ 𝑩𝑰𝑵 ➜ {cc[:6]} - {dicr} - {typ}
✮ 𝑪𝑶𝑼𝑵𝑻𝑹𝒀 ➜ {cn} - {emj} 
✮ 𝑩𝑨𝑵𝑲 ➜ {bank}
━━━━━━━━━━━━━━━━━
✮ 𝑩𝒀: @Thura
✮ 𝑷𝑹𝑶𝑿𝒀𝑺 : {ip} ✅'''

                # Send live card messages only
                if status == "LIVE ✅":  # Send live cards
                    bot.reply_to(message, msg)

                # Update inline buttons with updated counts for live, declined, and insufficient funds
                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"Card: {cc.strip()}", callback_data='info')
                cm2 = types.InlineKeyboardButton(f"Status: {status}", callback_data='status')
                cm3 = types.InlineKeyboardButton(f"Approved ✅ : {live}", callback_data='approved')
                cm4 = types.InlineKeyboardButton(f"Declined  📛 : {dd}", callback_data='declined')
                cm5 = types.InlineKeyboardButton(f"Insufficient Funds 💳 : {insu}", callback_data='insufficient')
                cm6 = types.InlineKeyboardButton(f"Total ☣️ : {total}", callback_data='total')
                cm7 = types.InlineKeyboardButton(f"IP: {ip}", callback_data='ip')
                stop_btn = types.InlineKeyboardButton("STOP", callback_data='stop')
                mes.add(cm1, cm2, cm3, cm4, cm5, cm6, cm7, stop_btn)

                # Edit message with inline buttons
                bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text="Processing...⌛", reply_markup=mes)

    except Exception as e:
        print(f"Error processing the card file: {e}")
    
    # After all cards are processed, display the final message
    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='𝗕𝗘𝗘𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 ✅\n𝗕𝗢𝗧 𝗕𝗬 ➜ Thura')

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_bot(call):
    with open("stop.stop", "w") as f:
        pass

print("+-----------------------------------------------------------------+")
bot.polling(none_stop=True)  # Ensure the bot keeps polling for updates
