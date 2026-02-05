from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.fsm.context import FSMContext
import os
from dotenv import load_dotenv
from hashids import Hashids


from apps.database import set_user, get_my_hash


router = Router()


load_dotenv()
HASHLIB_KEY = os.getenv("HASHLIB_KEY")
hashids = Hashids(salt=HASHLIB_KEY, min_length=8)


start_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ О нас', callback_data='about')],
    [InlineKeyboardButton(text='❓ FAQ', callback_data='instruction')],
    [InlineKeyboardButton(text='📝 Отправить сообщение', callback_data='send')]
    ])
about_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📣 Telegram-канал', url='https://t.me/+hOyJbBMC508xMzIy')],
    [InlineKeyboardButton(text='🛠 Поддержка', url='https://t.me/orlovurasuper')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='start')]
    ])
instruction_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝 Отправить сообщение', callback_data='send')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='start')]
    ])


@router.message(CommandStart())
async def start(message: Message, command: Command, state: FSMContext):
    await set_user(message.from_user.id, message.from_user.username,  message.from_user.first_name)
    args = command.args
    if not args:
        hash = await get_my_hash(message.from_user.id)
        await message.answer(text=f"👋 <b>Привет!</b>\nРад видеть тебя в нашем анонимном чате 💌\n\n🔗 <b>Твоя секретная ссылка:</b> <i>https://t.me/Anonim_Messssage_Bot?start={hash}</i>\n📤 <b><a href='https://t.me/share/url?url=По этой ссылке можно отправить мне анонимное сообщение👉t.me/Anonim_Messssage_Bot?start={hash}'>Поделись ею с друзьями:</a></b> <i>чтобы они могли отправлять тебе анонимные сообщения</i>\n\nВыбери действие ниже ⬇️", reply_markup=start_menu, parse_mode="HTML", disable_web_page_preview=True)
    elif message.from_user.id == hashids.decode(args)[0]:
        await message.answer(text="🤔 <b>Хм...</b>\nПохоже, ты нажал на <i>свою собственную ссылку</i> 💌\n\n📢 Анонимные сообщения можно отправлять другим людям, а не себе 😅\nПопробуй поделиться своей ссылкой с друзьями и получай секретные послания! 🔗", reply_markup=start_menu, parse_mode="HTML")
    else:
        from apps.message import send_by_args
        await send_by_args(args, message, state)


@router.message(Command('about'))
async def about(message: Message):
    await message.answer(text="💌 <b>О нас</b>\n\nМы создаём пространство для анонимных сообщений между друзьями и знакомыми 🤫\nЗдесь можно делиться секретами, поддерживать друзей и получать неожиданные послания 💖\n\n📢 Подписывайся на наш <b>Telegram-канал</b> для новостей и обновлений\n🛠 Нужна помощь? Наша <b>поддержка</b> всегда готова ответить на твои вопросы 🙌", reply_markup=about_menu, parse_mode="HTML")


@router.callback_query(F.data == 'about')
async def about2(callback: CallbackQuery):
    await callback.message.edit_text(text="💌 <b>О нас</b>\n\nМы создаём пространство для анонимных сообщений между друзьями и знакомыми 🤫\nЗдесь можно делиться секретами, поддерживать друзей и получать неожиданные послания 💖\n\n📢 Подписывайся на наш <b>Telegram-канал</b> для новостей и обновлений\n🛠 Нужна помощь? Наша <b>поддержка</b> всегда готова ответить на твои вопросы 🙌", reply_markup=about_menu, parse_mode="HTML")
    await callback.answer("ℹ️ О нас")


@router.callback_query(F.data == 'instruction')
async def instruction(callback: CallbackQuery):
    await callback.message.edit_text(text="❓ <b>FAQ — Часто задаваемые вопросы</b>\n\n💌 <b>Как отправить анонимное сообщение?</b>\nПросто скопируй секретную ссылку друга и отправь ей сообщение через нашего бота. Он останется полностью анонимным 🤫\n\n📬 <b>Как получить сообщение?</b>\nВсе сообщения приходят прямо в бота. Ты увидишь уведомление и сможешь прочитать послание в любое время 🕒\n\n💡 <b>Можно ли поделиться своей ссылкой?</b>\nКонечно! Делись с друзьями, чтобы получать больше анонимных сообщений и сюрпризов 🎁", reply_markup=instruction_menu, parse_mode="HTML")
    await callback.answer("❓ FAQ")


@router.callback_query(F.data == 'start')
async def start2(callback: CallbackQuery):
    hash = await get_my_hash(callback.message.from_user.id)
    await callback.message.edit_text(text=f"👋 <b>Привет!</b>\nРад видеть тебя в нашем анонимном чате 💌\n\n🔗 <b>Твоя секретная ссылка:</b> <i>https://t.me/Anonim_Messssage_Bot?start={hash}</i>\n📤 <b><a href='https://t.me/share/url?url=По этой ссылке можно отправить мне анонимное сообщение👉t.me/Anonim_Messssage_Bot?start={hash}'>Поделись ею с друзьями:</a></b> <i>чтобы они могли отправлять тебе анонимные сообщения</i>\n\nВыбери действие ниже ⬇️", reply_markup=start_menu, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer("📋 Меню")


@router.message(Command('instruction'))
async def instruction2(message: Message):
    await message.answer(text="❓ <b>FAQ — Часто задаваемые вопросы</b>\n\n💌 <b>Как отправить анонимное сообщение?</b>\nПросто скопируй секретную ссылку друга и отправь ей сообщение через нашего бота. Он останется полностью анонимным 🤫\n\n📬 <b>Как получить сообщение?</b>\nВсе сообщения приходят прямо в бота. Ты увидишь уведомление и сможешь прочитать послание в любое время 🕒\n\n💡 <b>Можно ли поделиться своей ссылкой?</b>\nКонечно! Делись с друзьями, чтобы получать больше анонимных сообщений и сюрпризов 🎁", reply_markup=instruction_menu, parse_mode="HTML")
