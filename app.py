import streamlit as st
import sqlite3
import uuid
import os

# --- 1. إعداد قاعدة البيانات ---
# ملاحظة: في السيرفر المجاني، الداتابيز كتكون مؤقتة
def init_db():
    conn = sqlite3.connect("factory.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT, username TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, user_id TEXT, project_name TEXT, path TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS apks (id TEXT PRIMARY KEY, project_id TEXT, user_id TEXT, apk_url TEXT, status TEXT)')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. إدارة الجلسة (Session State) ---
# هادي هي اللي كتعوض "user_session" في Flet
if "view" not in st.session_state:
    st.session_state.view = "login"
if "user" not in st.session_state:
    st.session_state.user = {"name": "", "username": "", "id": ""}

def navigate(view_name):
    st.session_state.view = view_name
    st.rerun()

# --- 3. الدوال المنطقية ---
def login_user(name, username):
    if not name or not username:
        st.error("عافاك دخل الاسم واسم المستخدم")
        return
    
    cursor = db_conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    res = cursor.fetchone()
    
    if res:
        u_id = res[0]
    else:
        u_id = str(uuid.uuid4())[:8]
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (u_id, name, username))
        db_conn.commit()
    
    st.session_state.user = {"name": name, "username": username, "id": u_id}
    navigate("main")

def save_project(p_name, code):
    if not p_name:
        st.error("دخل سمية المشروع")
        return
    
    p_id = str(uuid.uuid4())[:6]
    user_id = st.session_state.user["id"]
    save_path = f"final_projects/{user_id}_{p_name}_{p_id}"
    
    # إنشاء المجلدات
    os.makedirs(save_path, exist_ok=True)
    with open(f"{save_path}/info.txt", "w") as f:
        f.write(f"User: {st.session_state.user['username']}\nCode:\n{code}")
    
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO projects VALUES (?, ?, ?, ?)", (p_id, user_id, p_name, save_path))
    db_conn.commit()
    st.success(f"✅ تم حفظ المشروع: {p_name}")

# --- 4. واجهات العرض (UI Views) ---

# أ- شاشة الدخول
if st.session_state.view == "login":
    st.title("دخول المصنع 🚀")
    name = st.text_input("الاسم", placeholder="مثلا: منصف")
    username = st.text_input("اسم المستخدم", placeholder="username123")
    if st.button("دخول"):
        login_user(name, username)

# ب- الشاشة الرئيسية
elif st.session_state.view == "main":
    st.sidebar.write(f"👤 {st.session_state.user['name']} (ID: {st.session_state.user['id']})")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.view = "login"
        st.rerun()

    st.title("Android Python Factory 🚀")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📁 مشاريعي"): navigate("projects")
    with col2:
        if st.button("📦 APKs"): navigate("apks")

    st.markdown("---")
    proj_name = st.text_input("Project Name")
    py_code = st.text_area("Python Code", height=200, placeholder="import android...")
    
    if st.button("حفظ المشروع 🚀"):
        save_project(proj_name, py_code)

# ج- شاشة المشاريع
elif st.session_state.view == "projects":
    st.title("📁 مشاريعي")
    if st.button("⬅️ رجوع"): navigate("main")
    
    cursor = db_conn.cursor()
    cursor.execute("SELECT project_name, id FROM projects WHERE user_id = ?", (st.session_state.user['id'],))
    rows = cursor.fetchall()
    
    if rows:
        for row in rows:
            st.info(f"📓 {row[0]} (ID: {row[1]})")
    else:
        st.write("مازال ما عندك حتى مشروع.")

# د- شاشة APKs
elif st.session_state.view == "apks":
    st.title("📦 APK Status")
    if st.button("⬅️ رجوع"): navigate("main")
    st.write("قريباً: هنا غاتلقى روابط التحميل...")

