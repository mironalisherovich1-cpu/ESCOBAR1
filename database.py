import aiosqlite
import os

DB_PATH = "bot.db"

class Database:
    def __init__(self):
        self.db_path = DB_PATH
    
    async def init_db(self):
        """Создание базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Пользователи
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    balance REAL DEFAULT 0,
                    promo_used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Товары
            await db.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    price_ltc REAL NOT NULL,
                    image_path TEXT NOT NULL,
                    is_available BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Заказы
            await db.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    payment_id TEXT UNIQUE,
                    ltc_address TEXT,
                    amount_ltc REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            await db.commit()
        print("✅ База данных создана")
    
    async def add_user(self, user_id, username, full_name):
        """Добавить пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                (user_id, username or "", full_name or "")
            )
            await db.commit()
    
    async def get_user(self, user_id):
        """Получить пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone()
    
    async def add_product(self, title, description, price_ltc, image_path):
        """Добавить товар"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO products (title, description, price_ltc, image_path) VALUES (?, ?, ?, ?)",
                (title, description, price_ltc, image_path)
            )
            await db.commit()
            return True
    
    async def get_available_products(self):
        """Получить доступные товары"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, title, price_ltc FROM products WHERE is_available = 1"
            ) as cursor:
                return await cursor.fetchall()
    
    async def get_product(self, product_id):
        """Получить товар"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM products WHERE id = ?", (product_id,)) as cursor:
                return await cursor.fetchone()
    
    async def create_order(self, user_id, product_id, payment_id, ltc_address, amount_ltc):
        """Создать заказ"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO orders (user_id, product_id, payment_id, ltc_address, amount_ltc)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, product_id, payment_id, ltc_address, amount_ltc)
            )
            await db.commit()
            return True

db = Database()
