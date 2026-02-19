import streamlit as st
import os
import json
import uuid
import shutil

# إعدادات المخزن
PROJECTS_BASE = "factory_output"
os.makedirs(PROJECTS_BASE, exist_ok=True)

# ---------------------------------------------------------
# المرحلة 2: الكود المولد للمشروع (The Generator Engine)
# ---------------------------------------------------------
def generate_android_files(root_path, config):
    package_path = config['package'].replace(".", "/")
    # إنشاء المسارات
    os.makedirs(f"{root_path}/app/src/main/java/{package_path}", exist_ok=True)
    os.makedirs(f"{root_path}/app/src/main/python", exist_ok=True)
    
    # 1. ملف MainActivity.kt (محرك التشغيل)
    kt_code = f"""package {config['package']}
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState: Bundle?)
        if (!Python.isStarted()) {{ Python.start(AndroidPlatform(this)) }}
        val py = Python.getInstance()
        py.getModule("main").callAttr("start")
    }}
}}"""
    with open(f"{root_path}/app/src/main/java/{package_path}/MainActivity.kt", "w") as f:
        f.write(kt_code)

    # 2. ملف AndroidManifest.xml (الأذونات والهوية)
    perms_xml = "\n".join([f'<uses-permission android:name="android.permission.{p}" />' for p in config['permissions']])
    manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{config['package']}">
    {perms_xml}
    <application android:label="{config['app_name']}">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>"""
    with open(f"{root_path}/app/src/main/AndroidManifest.xml", "w") as f:
        f.write(manifest)

    # 3. ملف Python Code (main.py)
    # كنغلفو الكود فدالة start باش كوتلن يعيط عليها
    final_py = f"def start():\n" + "\n".join(["    " + line for line in config['py_code'].split("\n")])
    with open(f"{root_path}/app/src/main/python/main.py", "w") as f:
        f.write(final_py)

# ---------------------------------------------------------
# المرحلة 3: المغلف (The Packager & Meta Handler)
# ---------------------------------------------------------
def package_user_project(u_name, u_id, config):
    build_id = str(uuid.uuid4())[:8]
    folder_name = f"{u_name}_{u_id}_{build_id}"
    full_path = os.path.join(PROJECTS_BASE, folder_name)
    os.makedirs(full_path, exist_ok=True)
    
    # حفظ معلومات المستخدم (User Meta)
    meta_data = {"user_name": u_name, "user_id": u_id, "build_id": build_id, "config": config}
    with open(f"{full_path}/user_meta.json", "w") as f:
        json.dump(meta_data, f, indent=4)
    
    # توليد ملفات الأندرويد داخل المجلد
    generate_android_files(full_path, config)
    
    return folder_name

# ---------------------------------------------------------
# المرحلة 1: واجهة المستخدم (The UI / Input Stage)
# ---------------------------------------------------------
st.title("🏭 مصنع الأندرويد الذكي")

with st.sidebar:
    st.header("👤 معلومات المستخدم")
    u_name = st.text_input("إسم المستخدم", "Monsef")
    u_id = st.text_input("معرف المستخدم (ID)", "7788")

st.header("🛠️ إعدادات التطبيق")
col1, col2 = st.columns(2)
with col1:
    app_name = st.text_input("اسم التطبيق", "MyApp")
    package_id = st.text_input("اسم الحزمة", "com.factory.app")
with col2:
    perms = st.multiselect("الأذونات", ["INTERNET", "CAMERA", "STORAGE", "LOCATION"])

py_code = st.text_area("🐍 كود بايثون الرئيسي", "print('App Started!')", height=200)

if st.button("🚀 تشغيل المصنع وبناء المشروع"):
    config = {
        "app_name": app_name,
        "package": package_id,
        "permissions": perms,
        "py_code": py_code
    }
    
    # نداء المرحلة 3 (اللي هي بدورها كتعيط للمرحلة 2)
    final_folder = package_user_project(u_name, u_id, config)
    
    st.success(f"✅ تم البناء بنجاح!")
    st.info(f"المجلد النهائي: {final_folder}")
    
    # عرض محتوى المجلد (API Simulation)
    st.write("📂 محتويات المجلد الجاهز للجلب:")
    st.json(os.listdir(os.path.join(PROJECTS_BASE, final_folder)))
