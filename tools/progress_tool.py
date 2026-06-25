"""
أداة سجل التقدم الشخصي - لجميع أجهزة الجسم
هذه الأداة تسمح للمستخدم بتسجيل وتتبع تقدمه التعليمي في أي جهاز من أجهزة الجسم.
"""

import streamlit as st
import datetime
import sys
import os
import pandas as pd

# إعداد المسار للوصول إلى مجلد database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================
# استيراد دوال قاعدة البيانات من database/database.py
# ============================================================
try:
    from database.database import (
        init_db, add_entry, get_all_entries, get_entries_by_device,
        get_entry_by_id, update_entry, delete_entry, get_device_statistics
    )
    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    st.error(f"⚠️ فشل استيراد قاعدة البيانات: {e}")
    
    # دوال وهمية باستخدام session_state
    def init_db():
        if "progress_entries" not in st.session_state:
            st.session_state.progress_entries = []
    
    def add_entry(date, device, topic, summary, questions="", rating=3):
        new_entry = {
            "id": len(st.session_state.progress_entries) + 1,
            "date": date,
            "device": device,
            "topic": topic,
            "summary": summary,
            "questions": questions,
            "rating": rating,
            "created_at": str(datetime.datetime.now())
        }
        st.session_state.progress_entries.append(new_entry)
    
    def get_all_entries():
        return st.session_state.progress_entries
    
    def get_entries_by_device(device):
        return [e for e in st.session_state.progress_entries if e.get("device") == device]
    
    def get_entry_by_id(entry_id):
        for entry in st.session_state.progress_entries:
            if entry["id"] == entry_id:
                return entry
        return None
    
    def update_entry(entry_id, date, device, topic, summary, questions, rating):
        entry = get_entry_by_id(entry_id)
        if entry:
            entry.update({
                "date": date,
                "device": device,
                "topic": topic,
                "summary": summary,
                "questions": questions,
                "rating": rating
            })
    
    def delete_entry(entry_id):
        st.session_state.progress_entries = [
            e for e in st.session_state.progress_entries 
            if e["id"] != entry_id
        ]
    
    def get_device_statistics():
        stats = {}
        for entry in st.session_state.progress_entries:
            device = entry.get("device", "غير محدد")
            if device not in stats:
                stats[device] = {"count": 0, "ratings": []}
            stats[device]["count"] += 1
            stats[device]["ratings"].append(entry.get("rating", 0))
        return [(device, data["count"], sum(data["ratings"])/len(data["ratings"]) if data["ratings"] else 0) 
                for device, data in stats.items()]

# قائمة الأجهزة المتاحة
DEVICES = [
    "الهيكلي", "العضلي", "العصبي", "القلبي", "التنفسي",
    "الهضمي", "البولي", "الغدي الصماء", "المناعي", "التكاملي (الجلد)", "التناسلي"
]

# ============================================================
# الدالة الرئيسية
# ============================================================
def show():
    """عرض أداة سجل التقدم الشخصي لجميع الأجهزة"""
    
    # تهيئة قاعدة البيانات
    init_db()
    
    st.title("📖 سجل التقدم الشخصي")
    st.markdown("دوّن ما تعلمته اليوم عن أي جهاز من أجهزة الجسم، وراقب تقدمك!")
    
    # ====== القائمة الجانبية ======
    st.sidebar.header("📊 إحصائيات سريعة")
    all_entries = get_all_entries()
    st.sidebar.metric("📝 عدد الإدخالات", len(all_entries))
    
    # إحصائيات لكل جهاز
    stats = get_device_statistics()
    if stats:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📈 توزيع الإدخالات")
        for device, count, avg_rating in stats:
            st.sidebar.text(f"{device}: {count} إدخال ({avg_rating:.1f}⭐)")
    
    # ====== تذكير يومي ======
    st.sidebar.markdown("---")
    st.sidebar.subheader("⏰ تذكير يومي")
    import random
    quotes = [
        "التعلم المستمر هو مفتاح النجاح 🧠",
        "دوّن ما تعلمته اليوم، وسترى تقدمك غداً 📈",
        "كل معلومة جديدة تقربك من فهم جسدك 💪",
        "التكرار والممارسة يصنعان الخبرة 🏆",
        "المعرفة هي الاستثمار الذي لا يفشل 📚",
        "كل يوم تتعلم شيئاً جديداً، أنت أقرب لهدفك 🌟"
    ]
    st.sidebar.info(random.choice(quotes))
    
    # ====== إضافة إدخال جديد ======
    with st.expander("➕ إضافة إدخال جديد", expanded=False):
        with st.form("add_entry_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("📅 التاريخ", datetime.date.today())
                device = st.selectbox("🩺 الجهاز", DEVICES)
                topic = st.text_input("📚 الموضوع", placeholder="مثال: آلية الشهيق والزفير")
            with col2:
                rating = st.slider("⭐ تقييم الفهم (1 = صعب، 5 = سهل)", 1, 5, 3)
            
            summary = st.text_area("📝 الملخص", placeholder="اكتب ملخصاً لما تعلمته اليوم...", height=150)
            questions = st.text_area("❓ أسئلة للمراجعة (اختياري)", placeholder="اكتب أي أسئلة تريد مراجعتها لاحقاً...", height=80)
            
            submitted = st.form_submit_button("💾 حفظ الإدخال")
            
            if submitted:
                if not topic or not summary:
                    st.error("⚠️ الرجاء ملء حقل الموضوع والملخص")
                else:
                    add_entry(str(date), device, topic, summary, questions, rating)
                    st.success(f"✅ تم حفظ الإدخال للجهاز {device} بنجاح!")
                    st.rerun()
    
    # ====== عرض الإدخالات ======
    st.subheader("📚 إدخالاتك السابقة")
    
    # تصفية حسب الجهاز
    filter_device = st.selectbox("🔍 تصفية حسب الجهاز:", ["الكل"] + DEVICES)
    
    if filter_device == "الكل":
        entries = get_all_entries()
    else:
        entries = get_entries_by_device(filter_device)
    
    if not entries:
        st.info("لا توجد إدخالات بعد. ابدأ بتسجيل تقدمك التعليمي!")
    else:
        for entry in entries:
            # التعامل مع تنسيقات مختلفة
            if isinstance(entry, dict):
                entry_id = entry.get("id")
                date = entry.get("date", "")
                device = entry.get("device", "")
                topic = entry.get("topic", "")
                summary = entry.get("summary", "")
                questions = entry.get("questions", "")
                rating = entry.get("rating", 3)
            else:
                entry_id = entry[0] if len(entry) > 0 else None
                date = entry[1] if len(entry) > 1 else ""
                device = entry[2] if len(entry) > 2 else ""
                topic = entry[3] if len(entry) > 3 else ""
                summary = entry[4] if len(entry) > 4 else ""
                questions = entry[5] if len(entry) > 5 else ""
                rating = entry[6] if len(entry) > 6 else 3
            
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"### 📌 {topic}")
                    st.markdown(f"**📅 التاريخ:** {date} | **🩺 الجهاز:** {device}")
                    st.markdown(f"**📝 الملخص:** {summary}")
                    if questions:
                        st.markdown(f"**❓ أسئلة للمراجعة:** {questions}")
                    st.markdown(f"**⭐ تقييم الفهم:** {'⭐' * rating}")
                
                with col2:
                    if st.button("✏️ تعديل", key=f"edit_{entry_id}"):
                        st.session_state.edit_mode = entry_id
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ حذف", key=f"delete_{entry_id}"):
                        delete_entry(entry_id)
                        st.success("✅ تم الحذف بنجاح!")
                        st.rerun()
    
    # ====== وضع التعديل ======
    if "edit_mode" in st.session_state and st.session_state.edit_mode:
        entry_id = st.session_state.edit_mode
        entry = get_entry_by_id(entry_id)
        
        if entry:
            st.subheader("✏️ تعديل الإدخال")
            with st.form("edit_entry_form"):
                if isinstance(entry, dict):
                    current_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
                    current_device = entry.get("device", "")
                    current_topic = entry["topic"]
                    current_summary = entry["summary"]
                    current_questions = entry.get("questions", "")
                    current_rating = entry.get("rating", 3)
                else:
                    current_date = datetime.datetime.strptime(entry[1], "%Y-%m-%d").date()
                    current_device = entry[2] if len(entry) > 2 else ""
                    current_topic = entry[3] if len(entry) > 3 else ""
                    current_summary = entry[4] if len(entry) > 4 else ""
                    current_questions = entry[5] if len(entry) > 5 else ""
                    current_rating = entry[6] if len(entry) > 6 else 3
                
                col1, col2 = st.columns(2)
                with col1:
                    date = st.date_input("📅 التاريخ", current_date)
                    device = st.selectbox("🩺 الجهاز", DEVICES, index=DEVICES.index(current_device) if current_device in DEVICES else 0)
                    topic = st.text_input("📚 الموضوع", current_topic)
                with col2:
                    rating = st.slider("⭐ تقييم الفهم", 1, 5, current_rating)
                
                summary = st.text_area("📝 الملخص", current_summary, height=150)
                questions = st.text_area("❓ أسئلة للمراجعة", current_questions, height=80)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 حفظ التغييرات"):
                        update_entry(entry_id, str(date), device, topic, summary, questions, rating)
                        st.success("✅ تم التحديث بنجاح!")
                        del st.session_state.edit_mode
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ إلغاء"):
                        del st.session_state.edit_mode
                        st.rerun()
    
    # ====== تحليل التقدم ======
    if all_entries:
        st.markdown("---")
        st.subheader("📊 تحليل التقدم")
        
        # استخراج التقييمات
        ratings = []
        devices_list = []
        for entry in all_entries:
            if isinstance(entry, dict):
                ratings.append(entry.get("rating", 0))
                devices_list.append(entry.get("device", "غير محدد"))
            else:
                ratings.append(entry[6] if len(entry) > 6 else 0)
                devices_list.append(entry[2] if len(entry) > 2 else "غير محدد")
        
        if ratings:
            # توزيع التقييمات
            rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for r in ratings:
                if r in rating_counts:
                    rating_counts[r] += 1
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("⭐ 1 (صعب)", rating_counts[1])
            with col2:
                st.metric("⭐ 2", rating_counts[2])
            with col3:
                st.metric("⭐ 3 (متوسط)", rating_counts[3])
            with col4:
                st.metric("⭐ 4", rating_counts[4])
            with col5:
                st.metric("⭐ 5 (سهل)", rating_counts[5])
            
            # متوسط التقييم العام
            avg_rating = sum(ratings) / len(ratings)
            st.progress(avg_rating / 5, text=f"متوسط التقييم العام: {avg_rating:.1f} / 5")
            
            # عدد الأيام الفريدة
            dates = set()
            for entry in all_entries:
                if isinstance(entry, dict):
                    date_str = entry.get("date", "")
                else:
                    date_str = entry[1] if len(entry) > 1 else ""
                if date_str:
                    dates.add(date_str)
            st.metric("📅 أيام التعلم الفريدة", len(dates))
    
    # ====== زر تصدير التقرير ======
    st.markdown("---")
    if st.button("📄 تصدير التقرير (نسخة نصية)"):
        if all_entries:
            report = f"تقرير التقدم الشخصي\n"
            report += f"تاريخ التقرير: {datetime.date.today()}\n"
            report += f"عدد الإدخالات: {len(all_entries)}\n"
            report += "-" * 50 + "\n\n"
            
            # تجميع الإدخالات حسب الجهاز
            entries_by_device = {}
            for entry in all_entries:
                if isinstance(entry, dict):
                    device = entry.get("device", "غير محدد")
                    topic = entry.get("topic", "")
                    date = entry.get("date", "")
                    summary = entry.get("summary", "")
                    rating = entry.get("rating", 0)
                else:
                    device = entry[2] if len(entry) > 2 else "غير محدد"
                    topic = entry[3] if len(entry) > 3 else ""
                    date = entry[1] if len(entry) > 1 else ""
                    summary = entry[4] if len(entry) > 4 else ""
                    rating = entry[6] if len(entry) > 6 else 0
                
                if device not in entries_by_device:
                    entries_by_device[device] = []
                entries_by_device[device].append((date, topic, summary, rating))
            
            for device, entries_list in entries_by_device.items():
                report += f"\n🩺 جهاز {device}\n"
                report += "-" * 30 + "\n"
                for date, topic, summary, rating in entries_list:
                    report += f"  📌 {topic} ({date}) - التقييم: {rating}/5\n"
                    report += f"     {summary[:80]}...\n"
            
            st.download_button(
                "⬇️ تحميل التقرير", 
                report, 
                file_name=f"تقرير_التقدم_{datetime.date.today()}.txt"
            )
        else:
            st.warning("لا توجد إدخالات لتصديرها")
    
    # ====== تذييل الصفحة ======
    st.markdown("---")
    st.caption("سجل تقدمك التعليمي يومياً لتعزيز التعلم المستدام 💪")

if __name__ == "__main__":
    show()