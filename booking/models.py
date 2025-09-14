# booking/models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import time, date # <-- เพิ่ม import date

# ... คลาส Room ของคุณ (ไม่ต้องแก้ไข) ...
class Room(models.Model):
    STATUS_CHOICES = [
        ('open', 'เปิดให้จอง'),
        ('closed', 'ปิดให้จอง'),
    ]
    room_code = models.CharField(max_length=10, unique=True, verbose_name="รหัสห้อง")
    name = models.CharField(max_length=100, verbose_name="ชื่อห้อง")
    capacity = models.PositiveIntegerField(verbose_name="ความจุ")
    start_time_available = models.TimeField(default=time(8, 0), verbose_name="เวลาเริ่มเปิดให้จอง")
    end_time_available = models.TimeField(default=time(17, 0), verbose_name="เวลาสิ้นสุดการจอง")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open', verbose_name="สถานะ")
    image = models.ImageField(upload_to='room_images/', null=True, blank=True, verbose_name="รูปภาพห้อง")

    def __str__(self):
        return f"{self.name} ({self.room_code})"


# --- แทนที่คลาส Booking เดิมด้วยอันนี้ ---
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ผู้จอง")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="ห้องที่จอง")
    booking_time = models.DateTimeField(auto_now_add=True, verbose_name="เวลาที่ทำรายการ")
    
    # 1. เพิ่มฟิลด์สำหรับเก็บวันที่
    booking_date = models.DateField(default=date.today, verbose_name="วันที่จอง")
    
    start_time = models.TimeField(verbose_name="เวลาเริ่มต้น")
    end_time = models.TimeField(verbose_name="เวลาสิ้นสุด")

    class Meta:
        # 2. แก้ไข unique_together ให้เช็ควันที่ด้วย
        unique_together = [
            ['room', 'booking_date', 'start_time']
        ]

    def __str__(self):
        return f"{self.user.username} จองห้อง {self.room.name} วันที่ {self.booking_date}"