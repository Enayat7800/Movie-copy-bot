from telethon import TelegramClient, events, sync
import os
import asyncio

# अपने Telegram API क्रेडेंशियल्स यहाँ डालें
api_id = int(os.environ.get("TELEGRAM_API_ID"))
api_hash = os.environ.get("TELEGRAM_API_HASH")

# Telethon क्लाइंट शुरू करें
client = TelegramClient('bot_session', api_id, api_hash)

source_channel = None
destination_channel = None
is_copying = False

@client.on(events.NewMessage(pattern='/set_source'))
async def set_source_channel(event):
    global source_channel
    try:
        channel_username = event.text.split(' ', 1)[1]
        source_channel = await client.get_entity(channel_username)
        await event.respond(f"सोर्स चैनल सेट किया गया: {source_channel.title} ({source_channel.id})")
    except Exception as e:
        await event.respond(f"सोर्स चैनल सेट करने में त्रुटि: {e}. कृपया /set_source <चैनल_यूजरनेम_या_ID> का उपयोग करें।")

@client.on(events.NewMessage(pattern='/set_destination'))
async def set_destination_channel(event):
    global destination_channel
    try:
        channel_username = event.text.split(' ', 1)[1]
        destination_channel = await client.get_entity(channel_username)
        await event.respond(f"डेस्टिनेशन चैनल सेट किया गया: {destination_channel.title} ({destination_channel.id})")
    except Exception as e:
         await event.respond(f"डेस्टिनेशन चैनल सेट करने में त्रुटि: {e}. कृपया /set_destination <चैनल_यूजरनेम_या_ID> का उपयोग करें।")

@client.on(events.NewMessage(pattern='/startcopy'))
async def start_copying(event):
    global is_copying
    if source_channel is None or destination_channel is None:
      await event.respond("पहले सोर्स और डेस्टिनेशन चैनल सेट करें। /set_source और /set_destination कमांड का उपयोग करें।")
      return
    if is_copying:
        await event.respond("कॉपी पहले से ही चल रही है।")
        return
    is_copying = True
    await event.respond("वीडियो कॉपी करना शुरू किया जा रहा है...")
    try:
       async for message in client.iter_messages(source_channel):
            if message.video:
                try:
                    await client.send_file(destination_channel, file=message.video, caption=message.text)
                    print(f"वीडियो कॉपी किया गया: {message.id}")
                except Exception as e:
                    print(f"वीडियो कॉपी करने में त्रुटि (मैसेज ID: {message.id}): {e}")
    except Exception as e:
        print(f"कॉपी करने के दौरान एक सामान्य त्रुटि: {e}")
        await event.respond(f"कॉपी करने के दौरान एक सामान्य त्रुटि: {e}")
    finally:
       is_copying=False
       await event.respond("वीडियो कॉपी करना समाप्त हो गया।")

async def main():
    await client.start()
    print("बॉट चालू हो गया है!")

    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
