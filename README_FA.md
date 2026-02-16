#Private Subscription Manager
Private Subscription Manager یک ابزار امن مبتنی بر پایتون است که به شما اجازه می‌دهد چندین فایل سابسکریپشن را مدیریت کنید.

#Private Subscription Manager (PSM)
یک ابزار سبک مدیریت سابسکریپشن HTTPS برای کانفیگ‌های VLESS/Vmess.
معرفی
#Private Subscription Manager
یک ابزار امن مبتنی بر پایتون است که به شما امکان می‌دهد:
- چندین فایل سابسکریپشن ایجاد کنید
- کانفیگ‌ها را اضافه یا حذف کنید
- لینک‌های سابسکریپشن امن HTTPS تولید کنید
- محدودیت تعداد درخواست (Rate Limit) اعمال کنید
- لاگ‌های دسترسی را مشاهده کنید
- به‌صورت سرویس دائمی systemd اجرا شود
- مناسب برای استفاده شخصی یا مدیریت تعداد محدودی سرور.

#نصب سریع (Quick Install)
این دستور را روی اوبونتو اجرا کنید:
```bash
bash <(curl -s https://raw.githubusercontent.com/zahraei/private-subscription-manager/main/install.sh)
```

#ویژگی‌ها
- پشتیبانی از HTTPS
- محدودیت درخواست: ۲۰ درخواست در هر ۱۰ دقیقه برای هر IP
- چرخش خودکار لاگ‌ها (حداکثر ۲ مگابایت)
- امکان حذف کامل (Uninstall کامل)
- دستور سریع در CLI: psm
- پشتیبانی از چندین سابسکریپشن

#گزینه‌های منو
پس از اجرای برنامه، منوی زیر نمایش داده می‌شود:

Install / Run Service
Create a new Subscription
Delete a Subscription
Add Config to subscription
Remove Config from subscription
Reset Config Token
View Logs
Uninstall Everything
Exit

#توضیح منو
1️⃣ Install / Run Service
سرویس systemd را نصب کرده و سرور HTTPS را اجرا می‌کند.
در این مرحله از شما دامنه و پورت پرسیده می‌شود.
2️⃣ Create a new Subscription
یک فایل سابسکریپشن جدید با توکن دسترسی یکتا ایجاد می‌کند.
3️⃣ Delete a Subscription
سابسکریپشن انتخاب‌شده را حذف می‌کند.
4️⃣ Add Config to subscription
یک خط کانفیگ جدید به سابسکریپشن اضافه می‌کند.
5️⃣ Remove Config from subscription
یک کانفیگ مشخص را از سابسکریپشن حذف می‌کند.
6️⃣ Reset Config Token
برای سابسکریپشن انتخابی یک توکن دسترسی جدید تولید می‌کند.
7️⃣ View Logs
لاگ‌های دسترسی را نمایش می‌دهد.
8️⃣ Uninstall Everything
سرویس، فایل‌ها و دستور CLI را به‌طور کامل حذف می‌کند.
