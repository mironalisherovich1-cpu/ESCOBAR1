#!/usr/bin/env python3
"""
ESCOBAR SHOP - Telegram Bot (RUS)
"""
import os
import logging
import uuid
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

from database import db
from keyboards import main_menu, products_keyboard, product_detail_keyboard, back_to_main

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
STORE_NAME = "ESCOBAR SHOP"

# Создаем папку для товаров
os.makedirs("products", exist_ok=True)

# ==================== КОМАНДЫ ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Добавляем пользователя в БД
    await db.add_user(user.id, user.username, user.full_name)
    
    text = (
        f"👋 Привет, {user.first_name}!\n\n"
        f"🛍 **Добро пожаловать в {STORE_NAME}!**\n\n"
        "Здесь вы можете покупать товары за Litecoin (LTC).\n"
        "Выберите раздел ниже:"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu(), parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu(), parse_mode='Markdown')

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /admin для администраторов"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет доступа к админ-панели.")
        return
    
    text = "🛠 **Админ-панель**\n\nВыберите действие:"
    keyboard = [
        [InlineKeyboardButton("➕ Добавить товар", callback_data='admin_add')],
        [InlineKeyboardButton("📦 Управление товарами", callback_data='admin_products')],
        [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ==================== CALLBACK QUERIES ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'main_menu':
        await start(update, context)
    
    elif data == 'products':
        await show_products(update, context)
    
    elif data.startswith('product_'):
        await show_product_detail(update, context)
    
    elif data.startswith('buy_'):
        await buy_product(update, context)
    
    elif data == 'profile':
        await show_profile(update, context)
    
    elif data == 'my_orders':
        await show_orders(update, context)
    
    elif data == 'reviews':
        await show_reviews(update, context)
    
    elif data == 'back':
        await start(update, context)

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список товаров"""
    query = update.callback_query
    
    products = await db.get_available_products()
    
    if not products:
        text = "🛒 Сейчас нет товаров в наличии."
        keyboard = back_to_main()
    else:
        text = "📋 **Доступные товары:**"
        keyboard = products_keyboard(products)
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def show_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать детали товара"""
    query = update.callback_query
    product_id = int(query.data.split('_')[1])
    
    product = await db.get_product(product_id)
    
    if not product:
        await query.edit_message_text(
            "❌ Товар не найден.",
            reply_markup=back_to_main()
        )
        return
    
    text = (
        f"📦 **{product[1]}**\n\n"
        f"📝 Описание: {product[2]}\n"
        f"💰 Цена: {product[3]} LTC\n\n"
        "Нажмите кнопку ниже чтобы купить:"
    )
    
    await query.edit_message_text(
        text,
        reply_markup=product_detail_keyboard(product_id),
        parse_mode='Markdown'
    )

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Покупка товара"""
    query = update.callback_query
    product_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    
    product = await db.get_product(product_id)
    
    if not product:
        await query.edit_message_text(
            "❌ Товар не найден.",
            reply_markup=back_to_main()
        )
        return
    
    # Генерируем уникальный ID заказа
    payment_id = f"ORDER-{user_id}-{uuid.uuid4().hex[:8]}"
    
    # ТЕСТОВЫЙ LTC АДРЕС (замените на реальный NowPayments API)
    ltc_address = "LQjkT7V5iQnz8hZRwF8s9mNpKqRvS2tUwX"
    amount_ltc = product[3]
    
    # Создаем заказ в БД
    await db.create_order(user_id, product_id, payment_id, ltc_address, amount_ltc)
    
    text = (
        f"🛒 **Заказ создан!**\n\n"
        f"📦 Товар: {product[1]}\n"
        f"💰 Сумма: {amount_ltc} LTC\n\n"
        f"**Для оплаты отправьте {amount_ltc} LTC на адрес:**\n"
        f"`{ltc_address}`\n\n"
        f"После оплаты бот автоматически отправит вам товар.\n"
        f"📝 ID заказа: `{payment_id}`"
    )
    
    await query.edit_message_text(
        text,
        reply_markup=back_to_main(),
        parse_mode='Markdown'
    )

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать профиль"""
    query = update.callback_query
    user_id = query.from_user.id
    
    user = await db.get_user(user_id)
    
    if user:
        balance = user[3] or 0
        promo_used = "✅" if user[4] else "❌"
        
        text = (
            f"👤 **Ваш профиль**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Имя: {user[2] or 'Не указано'}\n"
            f"📛 Юзернейм: @{user[1] or 'Не указан'}\n"
            f"💰 Баланс: {balance:.2f} $\n"
            f"🎁 Промокод использован: {promo_used}"
        )
    else:
        text = "❌ Профиль не найден."
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Пополнить баланс", callback_data='add_balance')],
        [InlineKeyboardButton("🎁 Ввести промокод", callback_data='enter_promo')],
        [InlineKeyboardButton("◀️ Назад", callback_data='main_menu')]
    ])
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать заказы"""
    query = update.callback_query
    
    text = (
        "📦 **История заказов**\n\n"
        "Ваша история заказов будет отображаться здесь.\n"
        "Функция в разработке."
    )
    
    await query.edit_message_text(
        text,
        reply_markup=back_to_main(),
        parse_mode='Markdown'
    )

async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать отзывы"""
    query = update.callback_query
    
    text = (
        "⭐ **Отзывы покупателей**\n\n"
        "Здесь будут отображаться отзывы других покупателей.\n"
        "Функция в разработке."
    )
    
    await query.edit_message_text(
        text,
        reply_markup=back_to_main(),
        parse_mode='Markdown'
    )

# ==================== MAIN ====================

def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    
    # Добавляем обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    logger.info("🚀 Бот запускается...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # Инициализируем базу данных
    import asyncio
    asyncio.run(db.init_db())
    
    # Запускаем бота
    main()
