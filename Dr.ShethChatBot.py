import tkinter as tk
from tkinter import scrolledtext
import random
import re

available_items = {
    "body lotion": 307,
    "body wash": 298,
    "cleanser": 287,
    "face wash": 314,
    "serum": 325,
    "sunscreen": 285,
    "moisturizer": 299,
    "roll-ons": 235,
    "face mask": 310
}

current_state = None
order_dict = {}
orders_db = {}

def generate_order_id():
    return str(random.randint(1000, 9999))

def extract_quantity(text):
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else 1

def get_order_summary(order):
    summary = "\n✨ Here's your luxurious order summary:"
    for item, qty in order.items():
        summary += f"\n{qty} x {item.title()} (₹{available_items[item]} each) = ₹{available_items[item] * qty}"
    return summary

root = tk.Tk()
root.title("Dr.ShethBot")
root.geometry("600x600")
root.configure(bg="#fef8f4")

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Segoe UI", 12), bg="#fff9f6", fg="#5a4e4d")
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_area.config(state=tk.DISABLED)

input_frame = tk.Frame(root, bg="#fef8f4")
input_frame.pack(fill=tk.X, padx=10, pady=10)

user_input = tk.Entry(input_frame, font=("Segoe UI", 12), bg="#fbeeee")
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

send_btn = tk.Button(input_frame, text="Send", font=("Segoe UI", 10), command=lambda: send_message(), bg="#e6b5ab")
send_btn.pack(side=tk.LEFT, padx=(5, 0))

exit_btn = tk.Button(input_frame, text="Exit", font=("Segoe UI", 10), command=root.destroy, bg="#e6b5ab")
exit_btn.pack(side=tk.RIGHT)

def add_message(message, sender):
    chat_area.config(state=tk.NORMAL)
    if sender == "user":
        chat_area.insert(tk.END, f"\n🧑‍🏬 You: {message}")
    else:
        chat_area.insert(tk.END, f"\n🤖 Dr.ShethBot: {message}")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)

def send_message():
    global current_state

    user_msg = user_input.get().strip()
    if not user_msg:
        return

    add_message(user_msg, "user")
    user_msg_lower = user_msg.lower()

    if user_msg_lower in ["exit", "quit", "bye"]:
        add_message("Thank you for choosing Dr.ShethBot 🌸. Stay radiant!", "bot")
        root.after(2000, root.destroy)
        return


    if "view cart" in user_msg_lower:
        if order_dict:
            summary = get_order_summary(order_dict)
            add_message(f"🛒 Your cart:\n{summary}", "bot")
        else:
            add_message("Your cart is empty 🛒. Start adding your skincare treats!", "bot")

    elif "clear cart" in user_msg_lower:
        order_dict.clear()
        add_message("Your cart has been cleared 🧼. Ready to start fresh!", "bot")

    elif "remove" in user_msg_lower:
        removed = False
        for item in available_items:
            if item in user_msg_lower:
                qty_to_remove = extract_quantity(user_msg_lower)
                if item in order_dict:
                    if qty_to_remove >= order_dict[item]:
                        del order_dict[item]
                        add_message(f"Removed all of {item.title()} from your cart.", "bot")
                    else:
                        order_dict[item] -= qty_to_remove
                        add_message(f"Removed {qty_to_remove} x {item.title()} from your cart.", "bot")
                else:
                    add_message(f"{item.title()} is not in your cart to remove.", "bot")
                removed = True
                break
        if removed:
            add_message("Would you like to proceed for billing (type *bill*) or add more items (type *add*)?", "bot")
        else:
            add_message("Couldn't find that product in your cart. Please check the name!", "bot")


    elif "bill" in user_msg_lower:
        if order_dict:
            summary = get_order_summary(order_dict)
            total = sum(available_items[item] * qty for item, qty in order_dict.items())
            order_id = generate_order_id()
            orders_db[order_id] = order_dict.copy()
            add_message(f"{summary}\n\nYour total is: ₹{total}.\nYour Order ID is #{order_id} 🧾\nWe’ll pamper your skin soon! 💖", "bot")
            order_dict.clear()
            current_state = None
        else:
            add_message("Your cart is empty 🛒. Please add some items first.", "bot")

    elif user_msg_lower.strip() in available_items:
        item = user_msg_lower.strip()
        price = available_items[item]
        add_message(f"{item.title()} is one of our bestsellers 🌟! Priced at ₹{price}.", "bot")

    elif current_state is None:
        if "new order" in user_msg_lower:
            current_state = "awaiting_order"
            add_message(
                "Got it! Starting a new order 💼.\n"
                "Please tell me what you'd like. For example:\n"
                "'1 face wash and 2 roll-ons'.\n\n"
                "✨ Available items:\n" +
                "\n".join([f"- {item.title()} - ₹{price}" for item ,price in available_items.items()]) +
                "\n\n💡 You can also try:\n- 'view cart'\n- 'clear cart'\n- 'remove <item>'\n- 'bill' to proceed for checkout.",
                "bot")
        elif "track order" in user_msg_lower:
            current_state = "awaiting_order_id"
            add_message("Sure 🕵️‍♀️, could you please share your order ID?", "bot")
        else:
            add_message("Hi there! 👋 How can I assist you today?\nType 'New Order' or 'Track Order' to get started.", "bot")

    elif current_state == "awaiting_order":
        if user_msg_lower == "add":
            add_message("Go ahead and tell me what to add 🛍️", "bot")
        elif user_msg_lower == "no":
            if order_dict:
                summary = get_order_summary(order_dict)
                total = sum(available_items[item] * qty for item, qty in order_dict.items())
                order_id = generate_order_id()
                orders_db[order_id] = order_dict.copy()
                add_message(f"{summary}\n\nYour total is: ₹{total}.\nYour Order ID is #{order_id} 🧾\nWe’ll pamper your skin soon! 💖", "bot")
                order_dict.clear()
                current_state = None
            else:
                add_message("Your order is empty! Please add some products first.", "bot")
        elif user_msg_lower == "yes":
            add_message("Perfect! Go ahead and add more products like '1 serum'.", "bot")
        else:
            added = False
            for item in available_items:
                if item in user_msg_lower:
                    qty = extract_quantity(user_msg_lower)
                    if qty > 0:
                        order_dict[item] = order_dict.get(item, 0) + qty
                        add_message(f"Added {qty} x {item.title()} to your order.", "bot")
                        added = True
            if added:
                add_message("Need anything more? (yes/no)", "bot")
            else:
                add_message("I couldn't identify any products. Please try again with correct names and quantities.", "bot")

    elif current_state == "awaiting_order_id":
        order_id = user_msg.replace("#", "")
        if order_id in orders_db:
            add_message(f"Thanks! Order #{order_id} is out for delivery 🚚.\nIt should reach you soon!", "bot")
        else:
            add_message("Hmm 🤔... I couldn't find that order. Please double-check the ID!", "bot")
        current_state = None

    user_input.delete(0, tk.END)

user_input.bind("<Return>", lambda event: send_message())

add_message("Hi there! 👋 How can I assist you today?\nType 'New Order' or 'Track Order' to get started.", "bot")

root.mainloop()
