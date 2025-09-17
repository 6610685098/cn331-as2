#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. ติดตั้ง Library ทั้งหมด
pip install -r requirements.txt

# 2. รวบรวมไฟล์ Static (CSS, JS)
python manage.py collectstatic --no-input

# 3. อัปเดตฐานข้อมูล
python manage.py migrate