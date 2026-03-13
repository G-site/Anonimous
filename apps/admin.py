import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)


from apps.database import check_admin, get_all_users


admin_router = Router()


admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сообщить о тех-перерыве', callback_data='message1')],
    [InlineKeyboardButton(text='Попросить поделиться с другом', callback_data='message2')],
    [InlineKeyboardButton(text='Попросить подписаться на тгк', callback_data='message3')]
    ])
subscribe_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔔 Подписаться', url='https://t.me/+kKVb9YkgDF03ZDdi')]])
share_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔗 Поделиться', url="https://t.me/share/url?url=t.me/Anonim_Messssage_Bot")]])


@admin_router.message(Command('admin'))
async def admin(message: Message):
    status = await check_admin(message.from_user.id)
    if status == 'M':
        name = message.from_user.first_name
        await message.answer(f"Добро пожаловать в админ-панель, <b>{name}</b>!", reply_markup=admin_menu, parse_mode="HTML")
    else:
        await message.answer(text="⚠️ <b>Упс!</b>\n\nТы <i>не являешься администратором</i> этого бота 🚫\nДоступ к этой функции ограничен только для администраторов 🛡\n\nЕсли ты считаешь, что это ошибка, обратись в нашу <b>поддержку</b> 🛠", parse_mode="HTML")


@admin_router.callback_query(F.data == 'message3')
async def subscribe(callback: CallbackQuery):
    users = await get_all_users()
    sent = 0
    for id in users:
        try:
            await callback.bot.send_message(
                chat_id=id,
                text="📢 <b>Будь в курсе всех новостей!</b>\n\nЧтобы не пропускать обновления и новые функции, подпишись на наш <b>Telegram-канал</b> 💌\nТам ты найдёшь интересные анонсы, советы и сюрпризы для участников нашего чата 🎁",
                parse_mode="HTML",
                reply_markup=subscribe_menu
            )
            sent += 1
            await asyncio.sleep(0.5)
        except TelegramAPIError:
            pass
    await callback.message.answer(f"✅ Отправлено {sent} пользователям!")


@admin_router.callback_query(F.data == 'message2')
async def share(callback: CallbackQuery):
    users = await get_all_users()
    sent = 0
    for id in users:
        try:
            await callback.bot.send_message(
                chat_id=id,
                text="🤝 <b>Поделись с другом!</b>\n\nХочешь получать больше анонимных сообщений и сюрпризов? 🎁\nОтправь свою секретную ссылку другу и пусть он тоже попробует наш бот 💌\n\n📤 Чем больше друзей — тем веселее и интереснее! 😎",
                parse_mode="HTML",
                reply_markup=share_menu
            )
            sent += 1
            await asyncio.sleep(0.5)
        except TelegramAPIError:
            pass
    await callback.message.answer(f"✅ Отправлено {sent} пользователям!")


@admin_router.callback_query(F.data == 'message1')
async def tech(callback: CallbackQuery):
    users = await get_all_users()
    sent = 0
    for id in users:
        try:
            await callback.bot.send_message(
                chat_id=id,
                text="🛠 <b>Внимание!</b>\n\nЗавтра у нас планируется <i>технический перерыв</i> ⏳\nВо время него бот может быть недоступен или работать с перебоями ⚡\n\n🙏 Пожалуйста, имей это в виду и не переживай — после перерыва мы снова будем рады принимать твои анонимные сообщения 💌",
                parse_mode="HTML"
            )
            sent += 1
            await asyncio.sleep(0.5)
        except TelegramAPIError:
            pass
    await callback.message.answer(f"✅ Отправлено {sent} пользователям!")
