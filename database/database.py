import sqlite3
import datetime
import os

# تحديد مسار قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "progress.db")

def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """إنشاء جدول التقدم إذا لم يكن موجوداً"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            device TEXT NOT NULL,
            topic TEXT NOT NULL,
            summary TEXT NOT NULL,
            questions TEXT,
            rating INTEGER DEFAULT 3,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_entry(date, device, topic, summary, questions="", rating=3):
    """إضافة إدخال جديد إلى قاعدة البيانات"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO progress (date, device, topic, summary, questions, rating)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, device, topic, summary, questions, rating))
    conn.commit()
    conn.close()

def get_all_entries():
    """الحصول على جميع الإدخالات مرتبة حسب التاريخ (الأحدث أولاً)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM progress ORDER BY date DESC, created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_entries_by_device(device):
    """الحصول على إدخالات جهاز معين"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM progress WHERE device = ? ORDER BY date DESC, created_at DESC', (device,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_entry_by_id(entry_id):
    """الحصول على إدخال بواسطة معرفه"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM progress WHERE id = ?', (entry_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_entry(entry_id, date, device, topic, summary, questions, rating):
    """تحديث إدخال موجود"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE progress
        SET date = ?, device = ?, topic = ?, summary = ?, questions = ?, rating = ?
        WHERE id = ?
    ''', (date, device, topic, summary, questions, rating, entry_id))
    conn.commit()
    conn.close()

def delete_entry(entry_id):
    """حذف إدخال بواسطة معرفه"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM progress WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()

def get_device_statistics():
    """إحصائيات لكل جهاز"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT device, COUNT(*) as count, AVG(rating) as avg_rating
        FROM progress
        GROUP BY device
        ORDER BY count DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_total_entries():
    """عدد الإدخالات الكلي"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM progress')
    count = c.fetchone()[0]
    conn.close()
    return count

# ============================================================
# دوال للمساعدة في التطوير (للتجربة السريعة)
# ============================================================

def add_sample_entries():
    """إضافة عينة من الإدخالات للتجربة"""
    sample_entries = [
        ("2026-06-20", "القلبي", "مقدمة في القلب", "تعلمت أن القلب مضخة مزدوجة...", "ما هي وظيفة البطين الأيسر؟", 4),
        ("2026-06-21", "التنفسي", "آلية التنفس", "الشهيق والزفير عملية معقدة...", "كيف يعمل الحجاب الحاجز؟", 3),
        ("2026-06-22", "الهضمي", "وظائف الكبد", "الكبد معمل كيميائي رئيسي...", "ما هي وظيفة الصفراء؟", 5),
        ("2026-06-23", "العصبي", "أجزاء الدماغ", "المخ والمخيخ وجذع الدماغ...", "أي جزء يتحكم في التوازن؟", 4),
        ("2026-06-24", "الهيكلي", "العظام الطويلة", "عظم الفخذ هو أطول عظم...", "كم عظمة في الجسم؟", 5),
    ]
    
    for entry in sample_entries:
        date, device, topic, summary, questions, rating = entry
        add_entry(date, device, topic, summary, questions, rating)

if __name__ == "__main__":
    # تجربة الدوال
    init_db()
    print("✅ قاعدة البيانات جاهزة")
    
    # إضافة عينة (اختياري)
    add_sample_entries()
    print("✅ تم إضافة عينة من الإدخالات")
    
    # عرض الإحصائيات
    stats = get_device_statistics()
    print("\n📊 إحصائيات الأجهزة:")
    for device, count, avg_rating in stats:
        print(f"  - {device}: {count} إدخال، متوسط التقييم: {avg_rating:.1f}")