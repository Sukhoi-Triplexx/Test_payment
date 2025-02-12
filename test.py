import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from yookassa import Configuration, Payment

# Настройки логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

# Данные для API ЮKassa
SHOP_ID = '1032619'  # Замените на ваш идентификатор магазина
API_KEY = 'test_oAGk-KejRiNUifJhXcHtoBCXIiZYZB1E9YDHaBkEmUY'  # Замените на ваш секретный ключ

# Инициализация конфигурации ЮKassa
Configuration.configure(SHOP_ID, API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Используйте /pay для создания платежа.')

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        payment = Payment.create({
            "amount": {
                "value": "56000.00",  # Сумма платежа
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://your-return-url.com"  # Замените на ваш URL возврата
            },
            "capture": True,
            "description": "Тестовый платеж"
        })

        keyboard = [
            [InlineKeyboardButton("Проверить оплату", callback_data=f"check_payment_{payment.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f'Платеж создан! ID: {payment.id}. Перейдите по [ссылке]({payment.confirmation.confirmation_url}) для оплаты.',
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f'Ошибка при создании платежа: {str(e)}')

async def check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    payment_id = context.args[0] if context.args else None
    if not payment_id:
        await update.message.reply_text('Пожалуйста, укажите ID платежа.')
        return

    try:
        payment = Payment.find_one(payment_id)
        status = payment.status
        await update.message.reply_text(f'Статус платежа {payment_id}: {status}')
    except Exception as e:
        await update.message.reply_text(f'Ошибка при проверке статуса платежа: {str(e)}')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки

    # Извлекаем ID платежа из callback_data
    payment_id = query.data.split("_")[2]

    # Проверяем статус платежа
    try:
        payment = Payment.find_one(payment_id)
        status = payment.status
        await query.edit_message_text(f'Статус платежа {payment_id}: {status}')
    except Exception as e:
        await query.edit_message_text(f'Ошибка при проверке статуса платежа: {str(e)}')

def main() -> None:
    application = ApplicationBuilder().token("8178914232:AAEHHs8edmiStNxA5FelDC16fTo-NVidNaM").build()  # Замените на токен вашего бота

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pay", pay))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запуск бота с использованием polling
    application.run_polling()

if __name__ == '__main__':
    main()
