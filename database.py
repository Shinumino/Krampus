# database.py
import sqlite3
from typing import List, Tuple, Optional

DB_PATH = "bot_data.db"

def init_db():
    """Inicializa o banco de dados criando as tabelas necessárias."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabela para mensagens de formulário persistentes (embed com botão)
    c.execute('''
        CREATE TABLE IF NOT EXISTS persistent_formularios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            custom_id TEXT NOT NULL,
            embed_title TEXT,
            embed_description TEXT,
            embed_color INTEGER
        )
    ''')
    # Tabela para tickets ativos
    c.execute('''
        CREATE TABLE IF NOT EXISTS active_tickets (
            channel_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            welcome_message_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# --- Funções para formulário persistente ---
def add_persistent_formulario(channel_id: int, message_id: int, custom_id: str,
                              embed_title: str = None, embed_description: str = None,
                              embed_color: int = None) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO persistent_formularios (channel_id, message_id, custom_id, embed_title, embed_description, embed_color)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (channel_id, message_id, custom_id, embed_title, embed_description, embed_color))
    conn.commit()
    conn.close()

def remove_persistent_formulario(message_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM persistent_formularios WHERE message_id = ?", (message_id,))
    conn.commit()
    conn.close()

def get_all_persistent_formularios() -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT channel_id, message_id, custom_id, embed_title, embed_description, embed_color FROM persistent_formularios")
    rows = c.fetchall()
    conn.close()
    return rows

# --- Funções para tickets ativos ---
def add_active_ticket(channel_id: int, user_id: int, welcome_message_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO active_tickets (channel_id, user_id, welcome_message_id)
        VALUES (?, ?, ?)
    ''', (channel_id, user_id, welcome_message_id))
    conn.commit()
    conn.close()

def remove_active_ticket(channel_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM active_tickets WHERE channel_id = ?", (channel_id,))
    conn.commit()
    conn.close()

def get_all_active_tickets() -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT channel_id, user_id, welcome_message_id FROM active_tickets")
    rows = c.fetchall()
    conn.close()
    return rows