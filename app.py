import streamlit as st
import os
import uuid
import json

# المجلدات الأساسية
PROJECTS_DIR = "all_user_projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)

st.title("🏭 مصنع الأندرويد: المحرك الحقيقي")

with st.form("pro_factory"):
    u_name = st.text_input("اسم المستخدم", "monsef")
    package_id = st.text_input("اسم الحزمة", "com.factory.app")
    proj_name = st.text_input("اسم المشروع", "AndroidPythonApp")
    
    st.write("🛡️ الأذونات (تضاف تلقائياً للـ Manifest):")
    perms = st.multiselect("اختار الأذونات", ["INTERNET", "CAMERA", "STORAGE", "RECORD_AUDIO"])
    
    st.write("📦 المكتبات (Requirements):")
    libs = st.text_input("اكتب المكتبات لي باغي (مثال: requests, flet, pandas)", "flet")
    
    py_code = st.text_area("🐍 كود بايثون الرئيسي (main.py):", height=250)
    
    submit = st.form_submit_button("🏗️ توليد مشروع أندرويد كامل")

if submit:
    build_id = str(uuid.uuid4())[:8]
    root = f"{PROJECTS_DIR}/{u_name}_{build_id}"
    
    # 1. إنشاء هيكل المجلدات (Standard Android Structure)
    pkg_path = package_id.replace(".", "/")
    os.makedirs(f"{root}/app/src/main/java/{pkg_path}", exist_ok=True)
    os.makedirs(f"{root}/app/src/main/python", exist_ok=True)
    os.makedirs(f"{root}/app/src/main/res/drawable", exist_ok=True)

    # 2. توليد MainActivity.kt (الكود اللي كيشغل بايثون)
    # هاد الكود هو "المحرك" اللي كيعيط على محرك Chaquopy
    kotlin_engine = f"""package {package_id}
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState: Bundle?)
        if (!Python.isStarted()) {{
            Python.start(AndroidPlatform(this))
        }}
        val py = Python.getInstance()
        val module = py.getModule("main") // هنا كيعيط على main.py ديال المستخدم
        module.callAttr("main_func") 
    }}
}}"""
    with open(f"{root}/app/src/main/java/{pkg_path}/MainActivity.kt", "w") as f:
        f.write(kotlin_engine)

    # 3. توليد ملف AndroidManifest.xml
    xml_perms = "\n".join([f'<uses-permission android:name="android.permission.{p}" />' for p in perms])
    manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{package_id}">
    {xml_perms}
    <application android:label="{proj_name}" android:icon="@drawable/icon">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>"""
    with open(f"{root}/app/src/main/AndroidManifest.xml", "w") as f:
        f.write(manifest)

    # 4. توليد ملف بناء Gradle (build.gradle) مع تحميل المكتبات تلقائياً
    gradle = f"""
plugins {{
    id 'com.android.application'
    id 'com.chaquo.python' // مكتبة تشغيل بايثون
}}
android {{
    defaultConfig {{
        applicationId "{package_id}"
        python {{
            pip {{
                install "{libs.replace(',', '"\ninstall "')}" // كيحمل المكتبات لي طلبتي
            }}
        }}
    }}
}}"""
    with open(f"{root}/app/build.gradle", "w") as f:
        f.write(gradle)

    # 5. وضع كود بايثون المستخدم في المكان الصحيح
    # كنغلفو الكود في دالة main_func باش كوتلن يعيط عليها
    final_py = f"def main_func():\n" + "\n".join(["    " + line for line in py_code.split("\n")])
    with open(f"{root}/app/src/main/python/main.py", "w") as f:
        f.write(final_py)

    st.success(f"✅ تم إنشاء 'الوحش' بنجاح في مجلد: {root}")
    st.json({"status": "ready", "path": root, "api_endpoint": f"/get_project/{build_id}"})
