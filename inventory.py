from database import InventoryDB

class InventoryManager:
    def __init__(self):
        self.db = InventoryDB()
    
    def process_command(self, message, user_phone):
        """Process WhatsApp message and return appropriate response"""
        message = message.strip().upper()
        
        if message == 'HELP':
            return self.get_help_message()
        elif message == 'LIST':
            return self.list_items()
        elif message.startswith('ADD '):
            return self.add_item_command(message, user_phone)
        elif message.startswith('REMOVE '):
            return self.remove_item_command(message, user_phone)
        elif message.startswith('CHECK '):
            return self.check_item_command(message)
        else:
            return "❌ Invalid command. Type 'HELP' for available commands."
    
    def add_item_command(self, message, user_phone):
        try:
            parts = message.split()
            if len(parts) != 3:
                return "❌ Usage: ADD item_name quantity\nExample: ADD apple 50"
            
            item_name = parts[1].lower()
            quantity = int(parts[2])
            
            if quantity <= 0:
                return "❌ Quantity must be positive"
            
            success = self.db.add_item(item_name, quantity, user_phone)
            if success:
                current_stock = self.db.check_item(item_name)
                return f"✅ Added {quantity} {item_name}(s)\n📦 Current stock: {current_stock}"
            else:
                return "❌ Error adding item to inventory"
        except ValueError:
            return "❌ Invalid quantity. Please enter a number."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def remove_item_command(self, message, user_phone):
        try:
            parts = message.split()
            if len(parts) != 3:
                return "❌ Usage: REMOVE item_name quantity\nExample: REMOVE apple 10"
            
            item_name = parts[1].lower()
            quantity = int(parts[2])
            
            if quantity <= 0:
                return "❌ Quantity must be positive"
            
            success, msg = self.db.remove_item(item_name, quantity, user_phone)
            if success:
                current_stock = self.db.check_item(item_name)
                return f"✅ Removed {quantity} {item_name}(s)\n📦 Current stock: {current_stock}"
            else:
                return f"❌ {msg}"
        except ValueError:
            return "❌ Invalid quantity. Please enter a number."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def check_item_command(self, message):
        try:
            parts = message.split()
            if len(parts) != 2:
                return "❌ Usage: CHECK item_name\nExample: CHECK apple"
            
            item_name = parts[1].lower()
            quantity = self.db.check_item(item_name)
            
            if quantity is not None:
                return f"📦 {item_name}: {quantity} units"
            else:
                return f"❌ {item_name} not found in inventory"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def list_items(self):
        try:
            items = self.db.list_all_items()
            if not items:
                return "📦 Inventory is empty"
            
            response = "📦 **INVENTORY LIST**\n\n"
            for item_name, quantity in items:
                response += f"• {item_name}: {quantity} units\n"
            
            return response
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def get_help_message(self):
        return """🤖 **INVENTORY COMMANDS**

📝 **Available Commands:**
- ADD item_name quantity
- REMOVE item_name quantity  
- CHECK item_name
- LIST
- HELP

💡 **Examples:**
- ADD apple 50
- REMOVE apple 10
- CHECK apple
- LIST

Need help? Just type any command!"""