import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

BOT_TOKEN = "8779652032:AAFgkTsJ797K-1VWLk3yQawctZpvcNiWahc"
ADMIN_CHAT_ID = 8067099747

MENU, CART, NAME, ADDRESS, PAYMENT, CONFIRM = range(6)

MENU_ITEMS = {
    "nigerian": [
        {"id": "n1", "name": "Jollof Rice & Chicken", "price": 2500, "desc": "Smoky party jollof rice with grilled chicken & fried plantain"},
        {"id": "n2", "name": "Egusi Soup & Pounded Yam", "price": 3000, "desc": "Rich egusi soup with assorted meat & smooth pounded yam"},
    ],
    "fastfood": [
        {"id": "f1", "name": "Double Smash Burger", "price": 3200, "desc": "Two smashed beef patties, cheddar cheese & house sauce"},
        {"id": "f2", "name": "Pepperoni Pizza", "price": 4500, "desc": "Hand-stretched dough, tomato sauce & generous pepperoni slices"},
    ],
    "continental": [
        {"id": "c1", "name": "Creamy Pasta Alfredo", "price": 3800, "desc": "Fettuccine pasta in rich parmesan cream sauce with grilled chicken"},
    ],
    "grills": [
        {"id": "g1", "name": "Suya Platter", "price": 2800, "desc": "Tender beef suya skewers with spiced peanut mix & onions"},
        {"id": "g2", "name": "Grilled Chicken Special", "price": 3500, "desc": "Whole grilled chicken with herbs, lemon & roasted vegetables"},
    ],
    "drinks": [
        {"id": "d1", "name": "Zobo Delight", "price": 800, "desc": "Chilled hibiscus drink with ginger, cloves & pineapple"},
    ],
    "desserts": [
        {"id": "de1", "name": "Chocolate Cake", "price": 2200, "desc": "Rich chocolate cake with ganache drizzle & cream swirls"},
    ],
}

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

def get_item_by_id(item_id):
    for category in MENU_ITEMS.values():
        for item in category:
            if item["id"] == item_id:
                return item
    return None

def format_cart(cart):
    if not cart:
        return "Your cart is empty!"
    text = "Your Cart:\n\n"
    total = 0
    for item_id, qty in cart.items():
        item = get_item_by_id(item_id)
        if item:
            subtotal = item["price"] * qty
            total += subtotal
            text += f"- {item['name']} x{qty} = N{subtotal:,}\n"
    text += f"\nTotal: N{total:,}"
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["cart"] = {}
    keyboard = [
        [InlineKeyboardButton("View Menu", callback_data="show_categories")],
        [InlineKeyboardButton("View Cart", callback_data="view_cart")],
        [InlineKeyboardButton("Contact Us", callback_data="contact")],
    ]
    await update.message.reply_text(
        "Welcome to FoodHub!\n\nPremium food delivered to your door in 30 minutes!\n\nWhat would you like to do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MENU

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Nigerian", callback_data="cat_nigerian"),
         InlineKeyboardButton("Fast Food", callback_data="cat_fastfood")],
        [InlineKeyboardButton("Continental", callback_data="cat_continental"),
         InlineKeyboardButton("Grills", callback_data="cat_grills")],
        [InlineKeyboardButton("Drinks", callback_data="cat_drinks"),
         InlineKeyboardButton("Desserts", callback_data="cat_desserts")],
        [InlineKeyboardButton("View Cart", callback_data="view_cart")],
        [InlineKeyboardButton("Main Menu", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        "Our Menu - Choose a category:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MENU

async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("cat_", "")
    items = MENU_ITEMS.get(cat, [])
    cat_names = {
        "nigerian": "Nigerian Cuisine",
        "fastfood": "Fast Food",
        "continental": "Continental",
        "grills": "Grills",
        "drinks": "Drinks",
        "desserts": "Desserts"
    }
    text = f"{cat_names.get(cat, cat)}\n\n"
    keyboard = []
    for item in items:
        text += f"- {item['name']} - N{item['price']:,}\n{item['desc']}\n\n"
        keyboard.append([InlineKeyboardButton(
            f"Add {item['name']} (N{item['price']:,})",
            callback_data=f"add_{item['id']}"
        )])
    keyboard.append([InlineKeyboardButton("Back to Categories", callback_data="show_categories")])
    keyboard.append([InlineKeyboardButton("View Cart", callback_data="view_cart")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return MENU

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item_id = query.data.replace("add_", "")
    item = get_item_by_id(item_id)
    if not item:
        return MENU
    cart = context.user_data.get("cart", {})
    cart[item_id] = cart.get(item_id, 0) + 1
    context.user_data["cart"] = cart
    total_items = sum(cart.values())
    keyboard = [
        [InlineKeyboardButton("View Cart", callback_data="view_cart")],
        [InlineKeyboardButton("Continue Shopping", callback_data="show_categories")],
        [InlineKeyboardButton("Checkout", callback_data="checkout")],
    ]
    await query.edit_message_text(
        f"{item['name']} added to cart!\n\nYou have {total_items} item(s) in your cart.\n\nWhat would you like to do next?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CART

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = context.user_data.get("cart", {})
    cart_text = format_cart(cart)
    keyboard = []
    if cart:
        keyboard.append([InlineKeyboardButton("Checkout Now", callback_data="checkout")])
        keyboard.append([InlineKeyboardButton("Clear Cart", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton("Continue Shopping", callback_data="show_categories")])
    keyboard.append([InlineKeyboardButton("Main Menu", callback_data="main_menu")])
    await query.edit_message_text(cart_text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CART

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cart"] = {}
    keyboard = [
        [InlineKeyboardButton("View Menu", callback_data="show_categories")],
        [InlineKeyboardButton("Main Menu", callback_data="main_menu")],
    ]
    await query.edit_message_text("Cart cleared!\n\nWhat would you like to do?",
                                   reply_markup=InlineKeyboardMarkup(keyboard))
    return MENU

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = context.user_data.get("cart", {})
    if not cart:
        await query.edit_message_text("Your cart is empty! Add items first.")
        return MENU
    await query.edit_message_text("Please enter your full name:")
    return NAME

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        f"Hello {update.message.text}!\n\nPlease enter your delivery address:"
    )
    return ADDRESS

async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Bank Transfer", callback_data="pay_transfer")],
        [InlineKeyboardButton("Pay on Delivery", callback_data="pay_delivery")],
    ]
    await update.message.reply_text(
        "Choose Payment Method:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PAYMENT

async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    payment = "Bank Transfer" if query.data == "pay_transfer" else "Pay on Delivery"
    context.user_data["payment"] = payment
    cart = context.user_data.get("cart", {})
    cart_text = format_cart(cart)
    name = context.user_data.get("name")
    address = context.user_data.get("address")
    keyboard = [
        [InlineKeyboardButton("Confirm Order", callback_data="confirm_order")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_order")],
    ]
    await query.edit_message_text(
        f"Order Summary\n\nName: {name}\nAddress: {address}\nPayment: {payment}\n\n{cart_text}\n\nConfirm your order?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONFIRM

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = context.user_data.get("cart", {})
    name = context.user_data.get("name")
    address = context.user_data.get("address")
    payment = context.user_data.get("payment")
    user = query.from_user
    total = sum(get_item_by_id(item_id)["price"] * qty
                for item_id, qty in cart.items()
                if get_item_by_id(item_id))
    order_text = (
        f"NEW ORDER!\n\n"
        f"Customer: {name}\n"
        f"Telegram: @{user.username or 'N/A'}\n"
        f"Address: {address}\n"
        f"Payment: {payment}\n\n"
        f"Items:\n"
    )
    for item_id, qty in cart.items():
        item = get_item_by_id(item_id)
        if item:
            order_text += f"- {item['name']} x{qty} = N{item['price'] * qty:,}\n"
    order_text += f"\nTotal: N{total:,}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=order_text)
    if payment == "Bank Transfer":
        payment_info = (
            "\n\nBank Transfer Details:\n"
            "Bank: Opay\n"
            "Account Name: Henry Agiya Emmanuel\n"
            "Account Number: 9061868358\n\n"
            "Please send payment and forward your receipt to us."
        )
    else:
        payment_info = "\n\nPlease have the exact amount ready for our delivery rider."
    await query.edit_message_text(
        f"Order Confirmed!\n\n"
        f"Thank you {name}!\n"
        f"Estimated delivery: 30 minutes\n"
        f"Total: N{total:,}"
        f"{payment_info}"
    )
    context.user_data["cart"] = {}
    return MENU

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cart"] = {}
    keyboard = [[InlineKeyboardButton("Main Menu", callback_data="main_menu")]]
    await query.edit_message_text(
        "Order cancelled. Come back when ready!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("View Menu", callback_data="show_categories")],
        [InlineKeyboardButton("View Cart", callback_data="view_cart")],
        [InlineKeyboardButton("Contact Us", callback_data="contact")],
    ]
    await query.edit_message_text(
        "Welcome to FoodHub!\n\nPremium food delivered to your door in 30 minutes!\n\nWhat would you like to do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MENU

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("Back", callback_data="main_menu")]]
    await query.edit_message_text(
        "Contact FoodHub\n\n"
        "Telegram: @FoodHubNaijaBot\n"
        "Website: foodhub-naija.netlify.app\n"
        "Hours: 8AM - 10PM daily",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MENU

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                CallbackQueryHandler(show_categories, pattern="^show_categories$"),
                CallbackQueryHandler(show_category_items, pattern="^cat_"),
                CallbackQueryHandler(view_cart, pattern="^view_cart$"),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
                CallbackQueryHandler(contact, pattern="^contact$"),
                CallbackQueryHandler(add_to_cart, pattern="^add_"),
            ],
            CART: [
                CallbackQueryHandler(view_cart, pattern="^view_cart$"),
                CallbackQueryHandler(clear_cart, pattern="^clear_cart$"),
                CallbackQueryHandler(show_categories, pattern="^show_categories$"),
                CallbackQueryHandler(checkout, pattern="^checkout$"),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
                CallbackQueryHandler(add_to_cart, pattern="^add_"),
            ],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address)],
            PAYMENT: [CallbackQueryHandler(receive_payment, pattern="^pay_")],
            CONFIRM: [
                CallbackQueryHandler(confirm_order, pattern="^confirm_order$"),
                CallbackQueryHandler(cancel_order, pattern="^cancel_order$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )
    app.add_handler(conv_handler)
    print("FoodHub Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
