import sqlite3
import threading
from datetime import datetime

class InventoryDB:
    def __init__(self, db_path='inventory.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_db()
    
    def init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create inventory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT UNIQUE NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create transactions table for tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    user_phone TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def add_item(self, item_name, quantity, user_phone):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Check if item exists
                cursor.execute('SELECT quantity FROM inventory WHERE item_name = ?', (item_name,))
                result = cursor.fetchone()
                
                if result:
                    # Update existing item
                    new_quantity = result[0] + quantity
                    cursor.execute('''
                        UPDATE inventory 
                        SET quantity = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE item_name = ?
                    ''', (new_quantity, item_name))
                else:
                    # Insert new item
                    cursor.execute('''
                        INSERT INTO inventory (item_name, quantity) 
                        VALUES (?, ?)
                    ''', (item_name, quantity))
                
                # Record transaction
                cursor.execute('''
                    INSERT INTO transactions (item_name, transaction_type, quantity, user_phone)
                    VALUES (?, ?, ?, ?)
                ''', (item_name, 'ADD', quantity, user_phone))
                
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                print(f"Error adding item: {e}")
                return False
            finally:
                conn.close()
    
    def remove_item(self, item_name, quantity, user_phone):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Check if item exists and has enough quantity
                cursor.execute('SELECT quantity FROM inventory WHERE item_name = ?', (item_name,))
                result = cursor.fetchone()
                
                if not result:
                    return False, "Item not found in inventory"
                
                current_quantity = result[0]
                if current_quantity < quantity:
                    return False, f"Not enough stock. Available: {current_quantity}"
                
                # Update quantity
                new_quantity = current_quantity - quantity
                cursor.execute('''
                    UPDATE inventory 
                    SET quantity = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE item_name = ?
                ''', (new_quantity, item_name))
                
                # Record transaction
                cursor.execute('''
                    INSERT INTO transactions (item_name, transaction_type, quantity, user_phone)
                    VALUES (?, ?, ?, ?)
                ''', (item_name, 'REMOVE', quantity, user_phone))
                
                conn.commit()
                return True, "Success"
            except Exception as e:
                conn.rollback()
                print(f"Error removing item: {e}")
                return False, str(e)
            finally:
                conn.close()
    
    def check_item(self, item_name):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT quantity FROM inventory WHERE item_name = ?', (item_name,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
    
    def list_all_items(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT item_name, quantity FROM inventory ORDER BY item_name')
            results = cursor.fetchall()
            conn.close()
            
            return results