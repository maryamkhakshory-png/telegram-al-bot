#!/bin/bash
echo "📦 نصب پیش‌نیازها..."
pkg update -y
pkg install python python-pip git -y
pip install -r requirements.txt
echo "✅ نصب تموم شد!"
echo "حالا با دستور python bot.py ربات رو اجرا کن"
