import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from yookassa import Configuration, Payment

# Данные для API ЮKassa
SHOP_ID = '1032619'
API_KEY = 'test_oAGk-KejRiNUifJhXcHtoBCXIiZYZB1E9YDHaBkEmUY'

#конфигурация ЮKassa
Configuration.configure(SHOP_ID, API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Используйте /pay для создания платежа.')

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Проверяем, есть ли уже созданный платеж для пользователя
        if 'payment_id' in context.user_data and 'payment_url' in context.user_data:
            payment_id = context.user_data['payment_id']
            payment_url = context.user_data['payment_url']
            await update.message.reply_text(
                f'У вас уже есть активный платеж! ID: {payment_id}. Перейдите по [ссылке]({payment_url}) для оплаты.',
                parse_mode='Markdown'
            )
            return

        # Создаем новый платеж
        payment = Payment.create({
            "amount": {
                "value": "56.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/DirTasteBot"
            },
            "capture": True,
            "description": "Тестовый платеж"
        })
        context.user_data['payment_id'] = payment.id
        context.user_data['payment_url'] = payment.confirmation.confirmation_url

        keyboard = [
            [InlineKeyboardButton("Проверить оплату", callback_data=f"check_payment_{payment.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f'Платеж создан! ID: {payment.id}. Перейдите по [ссылке]({payment.confirmation.confirmation_url}) для оплаты.',
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

        # Запускаем асинхронную задачу для проверки статуса платежа
        asyncio.create_task(check_payment_status(update, context, payment.id))

    except Exception as e:
        await update.message.reply_text(f'Ошибка при создании платежа: {str(e)}')

async def check_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: str) -> None:
    await asyncio.sleep(25)  # Ждем 5 минут перед проверкой статуса

    try:
        payment = Payment.find_one(payment_id)
        status = payment.status

        if status == 'succeeded':
            await update.message.reply_text(f'Платеж {payment_id} успешно завершен!')
            # Очищаем данные о платеже после успешной оплаты
            context.user_data.pop('payment_id', None)
            context.user_data.pop('payment_url', None)
        else:
            await update.message.reply_text(
                f'Платеж {payment_id} не прошел. Перейдите по [ссылке]({context.user_data["payment_url"]}) для повторной оплаты.',
                parse_mode='Markdown'
            )

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

def main():
    application = ApplicationBuilder().token("8178914232:AAEHHs8edmiStNxA5FelDC16fTo-NVidNaM").build()  # Замените на токен вашего бота

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pay", pay))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запуск бота с использованием polling
    application.run_polling()

if __name__ == '__main__':
    main()