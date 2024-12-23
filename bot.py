import logging
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telethon import TelegramClient, events, sync
import asyncio

# टेलीग्राम बॉट टोकन
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# टेलीग्राम API क्रेडेंशियल्स (यह बॉट के लिए आवश्यक नहीं है, लेकिन यदि आप Telethon का उपयोग करना चाहते हैं तो आपको इसकी आवश्यकता होगी)
api_id = int(os.environ.get("TELEGRAM_API_ID"))
api_hash = os.environ.get("TELEGRAM_API_HASH")

# Telethon client
telethon_client = TelegramClient('bot_session', api_id, api_hash)

# Source channel ID aur destination channel ID variable
source_channel_id = None
destination_channel_id = None
is_copying = False

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="मैं एक वीडियो कॉपी करने वाला बॉट हूँ। /set_source और /set_destination कमांड का उपयोग करके सोर्स और डेस्टिनेशन चैनल सेट करें, और फिर /startcopy कमांड का उपयोग करके कॉपी करना शुरू करें।")

async def set_source_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global source_channel_id
    try:
        source_channel_id = int(context.args[0])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"सोर्स चैनल सेट किया गया: {source_channel_id}")
    except (IndexError, ValueError):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="कृपया सही सोर्स चैनल ID दें। उदाहरण: /set_source -100123456789")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"सोर्स चैनल सेट करने में त्रुटि: {e}")


async def set_destination_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global destination_channel_id
    try:
        destination_channel_id = int(context.args[0])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"डेस्टिनेशन चैनल सेट किया गया: {destination_channel_id}")
    except (IndexError, ValueError):
       await context.bot.send_message(chat_id=update.effective_chat.id, text="कृपया सही डेस्टिनेशन चैनल ID दें। उदाहरण: /set_destination -100987654321")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"डेस्टिनेशन चैनल सेट करने में त्रुटि: {e}")

async def start_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
     global is_copying
     if source_channel_id is None or destination_channel_id is None:
          await context.bot.send_message(chat_id=update.effective_chat.id, text="पहले सोर्स और डेस्टिनेशन चैनल सेट करें। /set_source और /set_destination कमांड का उपयोग करें।")
          return
     if is_copying:
         await context.bot.send_message(chat_id=update.effective_chat.id, text="कॉपी पहले से ही चल रही है।")
         return
     is_copying = True
     await context.bot.send_message(chat_id=update.effective_chat.id, text="वीडियो कॉपी करना शुरू किया जा रहा है...")
     try:
         async for message in telethon_client.iter_messages(source_channel_id):
           if message.video:
                try:
                   await telethon_client.send_file(destination_channel_id, file=message.video, caption=message.text)
                   print(f"वीडियो कॉपी किया गया: {message.id}")
                except Exception as e:
                   print(f"वीडियो कॉपी करने में त्रुटि (मैसेज ID: {message.id}): {e}")
     except Exception as e:
           print(f"कॉपी करने के दौरान एक सामान्य त्रुटि: {e}")
           await context.bot.send_message(chat_id=update.effective_chat.id, text=f"कॉपी करने के दौरान एक सामान्य त्रुटि: {e}")
     finally:
           is_copying = False
           await context.bot.send_message(chat_id=update.effective_chat.id, text="वीडियो कॉपी करना समाप्त हो गया।")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """Log the error and send a telegram message"""
  logging.error(f"Exception while handling an update: {context.error}")
  try:
      await context.bot.send_message(chat_id=update.effective_chat.id,text="ओह! एक त्रुटि हुई।")
  except Exception as e:
        logging.error(f"Failed to send message. {e}")

async def main():
    await telethon_client.start()
    print("Telethon Client चालू हो गया है!")

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_source", set_source_channel))
    application.add_handler(CommandHandler("set_destination", set_destination_channel))
    application.add_handler(CommandHandler("startcopy", start_copy))
    application.add_error_handler(error_handler)
    
    
    print("Telegram Bot चालू हो गया है!")
    await application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
