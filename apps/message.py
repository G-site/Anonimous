from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButtonRequestUser, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import os
from dotenv import load_dotenv
from hashids import Hashids


from apps.database import get_my_hash, get_name_by_id
from bot_instance import bot


message_router = Router()


load_dotenv()
HASHLIB_KEY = os.getenv("HASHLIB_KEY")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
hashids = Hashids(salt=HASHLIB_KEY, min_length=8)


send_menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Выбрать", request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False))],
        [KeyboardButton(text="❌ Отмена")]
        ], resize_keyboard=True, one_time_keyboard=True)
share_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить', url='https://t.me/share/url?url=')]
    ])
close_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❌ Отмена', callback_data='close')]
    ])


class MessageStates(StatesGroup):
    user = State()
    text = State()


@message_router.message(Command('send'))
async def send_by_command(message: Message, state: FSMContext):
    await message.answer(text="📬 <b>Кому хочешь отправить анонимное сообщение?</b>\n\n👤 Выбери пользователя из списка ниже, чтобы отправить своё послание 🤫", reply_markup=send_menu, parse_mode="HTML")
    await state.set_state(MessageStates.user)


@message_router.callback_query(F.data == 'send')
async def send_by_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="📬 <b>Кому хочешь отправить анонимное сообщение?</b>\n\n👤 Выбери пользователя из списка ниже, чтобы отправить своё послание 🤫", reply_markup=send_menu, parse_mode="HTML")
    await state.set_state(MessageStates.user)


async def send_by_args(args, message: Message, state: FSMContext):
    user_id = hashids.decode(args)[0]
    await state.update_data(user=user_id)
    await message.answer(text="✏️ <b>Напиши своё анонимное послание</b>\n\nТы можешь отправить текст, фото, стикер или любое другое сообщение 🤫\nКогда будешь готов, просто отправь его в чат.", reply_markup=close_menu, parse_mode="HTML")
    await state.set_state(MessageStates.text)


@message_router.message(MessageStates.user)
async def get_message(message: Message, state: FSMContext):
    user_id = message.user_shared.user_id
    if not user_id:
        await message.edit_reply_markup(reply_markup=None)
        await state.clear()
    else:
        await state.update_data(user=user_id)
        await message.answer(text="✏️ <b>Напиши своё анонимное послание</b>\n\nТы можешь отправить текст, фото, стикер или любое другое сообщение 🤫\nКогда будешь готов, просто отправь его в чат.", reply_markup=close_menu, parse_mode="HTML")
        await state.set_state(MessageStates.text)


@message_router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await message.answer(text="Отменено! ✅", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@message_router.message(MessageStates.text)
async def send_message(message: Message, state: FSMContext):
    data = await state.get_data()
    my_id = message.from_user.id
    try:
        user = data["user"]
        recipient_menu = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='💬 Ответить', callback_data=f'answer_{my_id}')],
            [InlineKeyboardButton(text='🕵️‍♂️ Узнать кто это (20 ⭐)', callback_data=f'who_{my_id}')]
        ])
        await bot.send_message(text="🔔 <b>У тебя новое анонимное сообщение!</b>", chat_id=user, parse_mode="HTML")
        await bot.copy_message(
            chat_id=user,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=recipient_menu
        )
    except Exception as e:
        print(e)
    finally:
        await message.answer(text="✅ <b>Сообщение отправлено!</b>", reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
        await state.clear()


@message_router.callback_query(F.data == 'close')
async def about2(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


@message_router.callback_query(F.data.startswith("answer_"))
async def answer(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.data[len("answer_"):]
    await state.update_data(user=user_id)
    await callback.message.answer(text="✏️ <b>Напиши своё анонимное послание</b>\n\nТы можешь отправить текст, фото, стикер или любое другое сообщение 🤫\nКогда будешь готов, просто отправь его в чат.", reply_markup=close_menu, parse_mode="HTML")
    await state.set_state(MessageStates.text)


@message_router.callback_query(F.data.startswith("who_"))
async def who(callback: CallbackQuery):
    user_id = callback.data[len("who_"):]
    user = user_id
    prices = [LabeledPrice(label="🕵️‍♂️ Узнай, кто отправил сообщение!", amount=20)]
    print(user)
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="🕵️‍♂️ Узнай, кто отправил сообщение!",
        description="🕵️‍♂️ Узнай, кто отправил сообщение!",
        payload=user,
        currency="XTR",
        prices=prices,
        start_parameter="buy_stars_product"
    )


@message_router.pre_checkout_query()
async def pre_checkout(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)


@message_router.message(F.successful_payment)
async def handle_payment(message: Message):
    comment = message.successful_payment.invoice_payload
    name = await get_name_by_id(comment)
    await message.answer(f"✅ <b>Оплата прошла успешно!</b>\n\n💬 Сообщение было отправлено пользователем <b><a href='tg://openmessage?user_id={comment}'>{name}</a></b>🤫", parse_mode="HTML")
