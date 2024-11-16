@app.on_message(filters.command("tag") & filters.group)
async def tag(client, message):
    if is_user_blocked(message.from_user.id):
        await message.reply("**Üzgünüm, bu komutu kullanma yetkiniz engellendi.** 🚫")
        return
        
    if message.chat.type == 'private':
        await message.reply("❗ Bu komutu sadece gruplarda kullanabilirsiniz!")
        return

    admins = []
    async for member in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
        admins.append(member.user.id)

    if message.from_user.id not in admins:
        await message.reply("❗ Bu komutu kullanmak için yönetici olmalısınız!")
        return

    args = message.command

    if len(args) > 1:
        msg_content = " ".join(args[1:])
    elif message.reply_to_message:
        msg_content = message.reply_to_message.text
        if msg_content is None:
            await message.reply("❗ Eski mesajı göremiyorum!")
            return
    else:
        msg_content = ""

    total_members = 0
    async for member in client.get_chat_members(message.chat.id):
        user = member.user
        if not user.is_bot and not user.is_deleted:
            total_members += 1
    user = message.from_user
    chat = message.chat
    
    await client.send_message(LOG_CHANNEL, f"""

Etiket işlemi bildirimi.

Kullanan : {user.mention} [`{user.id}`]
Etiket Tipi : Tekli Tag

Grup : {chat.title}
Grup İD : `{chat.id}`

Sebep : {message.text}
"""
 )
    
    num = 1
    estimated_time = (total_members // num) * 5

    start_msg = await message.reply(f"""
**Üye etiketleme işlemi başlıyor.**

**Silinen hesapları ve botları atlayacak**

👥 __Toplam Etiketlenecek Üye Sayısı: {total_members}__
⏳ __Tahmini Süre: {estimated_time // 60} dakika__
""")
    
    rose_tagger[message.chat.id] = start_msg.id
    nums = 1
    usrnum = 0
    skipped_bots = 0
    skipped_deleted = 0
    total_tagged = 0
    usrtxt = ""
    
    async for member in client.get_chat_members(message.chat.id):
        user = member.user
        if user.is_bot:
            skipped_bots += 1
            continue
        if user.is_deleted:
            skipped_deleted += 1
            continue
        usrnum += 1
        total_tagged += 1
        usrtxt += f"• [{user.first_name}](tg://user?id={user.id})"
        if message.chat.id not in rose_tagger or rose_tagger[message.chat.id] != start_msg.id:
            return
        if usrnum == nums:
            await client.send_message(message.chat.id, f" **{msg_content}**\n\n{usrtxt}")
            usrnum = 0
            usrtxt = ""
            await asyncio.sleep(5)

    await client.send_message(message.chat.id, f"""
**Üye etiketleme işlemi tamamlandı** ✅

👥 __Etiketlenen üye: {total_tagged}__
🤖 __Atlanılan Bot Sayısı: {skipped_bots}__
💣 __Atlanılan Silinen Hesap Sayısı: {skipped_deleted}__
""")