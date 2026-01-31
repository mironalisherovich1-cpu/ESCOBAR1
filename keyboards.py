from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("🛍 Витрина", callback_data='products')],
        [InlineKeyboardButton("👤 Профиль", callback_data='profile')],
        [InlineKeyboardButton("📦 Мои заказы", callback_data='my_orders')],
        [InlineKeyboardButton("⭐ Отзывы", callback_data='reviews')]
    ]
    return InlineKeyboardMarkup(keyboard)

def products_keyboard(products):
    """Список товаров"""
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                f"📦 {product[1]} - {product[2]} LTC",
                callback_data=f"product_{product[0]}"
            )
        ])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='back')])
    return InlineKeyboardMarkup(keyboard)

def product_detail_keyboard(product_id):
    """Детали товара"""
    keyboard = [
        [InlineKeyboardButton("✅ Купить", callback_data=f"buy_{product_id}")],
        [InlineKeyboardButton("◀️ Назад", callback_data='products')]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_main():
    """Назад в главное меню"""
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')]])
