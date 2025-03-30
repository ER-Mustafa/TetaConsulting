import sqlite3
from datetime import datetime

# Database initialization and connection
def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bom (
            product_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(material_id) REFERENCES materials(id),
            PRIMARY KEY(product_id, material_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_details (
            order_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            quantity_used INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(material_id) REFERENCES materials(id),
            PRIMARY KEY(order_id, material_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Material management functions
def add_material(name, quantity):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO materials (name, quantity) VALUES (?, ?)', (name, quantity))
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Material with this name already exists")
    finally:
        conn.close()

def update_material(material_id, quantity):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE materials SET quantity = quantity + ? WHERE id = ?', (quantity, material_id))
    conn.commit()
    conn.close()

def delete_material(material_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Check if material is used in any BOM
    cursor.execute('SELECT COUNT(*) FROM bom WHERE material_id = ?', (material_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        raise ValueError("Material is used in a product BOM and cannot be deleted")
    
    cursor.execute('DELETE FROM materials WHERE id = ?', (material_id,))
    conn.commit()
    conn.close()

def get_inventory():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, quantity FROM materials ORDER BY id')
    inventory = cursor.fetchall()
    conn.close()
    return inventory

# Product and BOM management functions
def add_product(name, bom):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    try:
        # Add product
        cursor.execute('INSERT INTO products (name) VALUES (?)', (name,))
        product_id = cursor.lastrowid
        
        # Add BOM entries
        for material_id, quantity in bom:
            cursor.execute('''
                INSERT INTO bom (product_id, material_id, quantity)
                VALUES (?, ?, ?)
            ''', (product_id, material_id, quantity))
        
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Product with this name already exists")
    finally:
        conn.close()

def get_products():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM products ORDER BY id')
    products = cursor.fetchall()
    conn.close()
    return products

def get_bom(product_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.id, m.name, b.quantity 
        FROM bom b
        JOIN materials m ON b.material_id = m.id
        WHERE b.product_id = ?
    ''', (product_id,))
    bom = cursor.fetchall()
    conn.close()
    return bom

def delete_product(product_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Delete BOM first
    cursor.execute('DELETE FROM bom WHERE product_id = ?', (product_id,))
    # Delete product
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    
    conn.commit()
    conn.close()

# Order management functions
def place_order(product_id, quantity):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    try:
        # Get BOM and calculate required materials
        bom = get_bom(product_id)
        required = {}
        for material_id, name, qty in bom:
            required[material_id] = qty * quantity
        
        # Check stock availability
        insufficient = []
        for material_id, needed in required.items():
            cursor.execute('SELECT quantity FROM materials WHERE id = ?', (material_id,))
            current = cursor.fetchone()[0]
            if current < needed:
                insufficient.append((name, needed - current))
        
        if insufficient:
            return False, insufficient
        
        # Start transaction
        conn.execute("BEGIN")
        
        # Update material quantities
        for material_id, needed in required.items():
            cursor.execute('''
                UPDATE materials 
                SET quantity = quantity - ? 
                WHERE id = ?
            ''', (needed, material_id))
        
        # Create order record
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO orders (product_id, quantity, timestamp)
            VALUES (?, ?, ?)
        ''', (product_id, quantity, timestamp))
        order_id = cursor.lastrowid
        
        # Create order details
        for material_id, needed in required.items():
            cursor.execute('''
                INSERT INTO order_details (order_id, material_id, quantity_used)
                VALUES (?, ?, ?)
            ''', (order_id, material_id, needed))
        
        conn.commit()
        return True, order_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_order_history():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT o.id, p.name, o.quantity, o.timestamp
        FROM orders o
        JOIN products p ON o.product_id = p.id
        ORDER BY o.timestamp DESC
    ''')
    history = cursor.fetchall()
    print(history)
    conn.close()
    return history

# Initialize database on first import
init_db()