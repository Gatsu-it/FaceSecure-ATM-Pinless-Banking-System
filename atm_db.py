import sqlite3
import hashlib

DB_NAME = "atm.db"

# ------------------- Database Initialization ------------------- #
def init_db():
    """Initialize the ATM database with users and transactions tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            balance REAL DEFAULT 1000
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


# ------------------- Password Handling ------------------- #
def hash_password(password: str) -> str:
    """Return SHA-256 hash of a password."""
    return hashlib.sha256(password.encode()).hexdigest()


# ------------------- User Management ------------------- #
def create_user(username: str, password: str) -> bool:
    """Create a new user. Returns True if successful, False if username exists."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate_user(username: str, password: str):
    """Authenticate user. Returns user row if valid, else None."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password_hash))
    user = c.fetchone()
    conn.close()
    return user


# ------------------- Account Management ------------------- #
def get_balance(user_id: int) -> float:
    """Return current balance of user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0.0


def update_balance(user_id: int, new_balance: float):
    """Update the balance of the user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
    conn.commit()
    conn.close()


# ------------------- Transaction Management ------------------- #
def add_transaction(user_id: int, txn_type: str, amount: float):
    """Add a transaction record with current timestamp."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (user_id, type, amount, date)
        VALUES (?, ?, ?, datetime("now", "localtime"))
    ''', (user_id, txn_type, amount))
    conn.commit()
    conn.close()


def get_transactions(user_id: int, limit: int = 10):
    """Return last 'limit' transactions of a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT type, amount, date
        FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
    ''', (user_id, limit))
    transactions = c.fetchall()
    conn.close()
    return transactions


# ------------------- Utilities ------------------- #
def deposit(user_id: int, amount: float):
    """Deposit money into account."""
    balance = get_balance(user_id)
    new_balance = balance + amount
    update_balance(user_id, new_balance)
    add_transaction(user_id, "Deposit", amount)
    return new_balance


def withdraw(user_id: int, amount: float) -> bool:
    """Withdraw money if sufficient balance. Returns True if successful."""
    balance = get_balance(user_id)
    if balance >= amount:
        new_balance = balance - amount
        update_balance(user_id, new_balance)
        add_transaction(user_id, "Withdraw", amount)
        return True
    return False


# ------------------- Example Usage ------------------- #
if __name__ == "__main__":
    init_db()
    # Example: create a new user
    if create_user("alice", "password123"):
        print("User created successfully.")
    else:
        print("Username already exists.")
    
    user = authenticate_user("alice", "password123")
    if user:
        print("Authenticated:", user)
        print("Balance:", get_balance(user[0]))
        deposit(user[0], 500)
        withdraw(user[0], 200)
        print("Last transactions:", get_transactions(user[0]))
