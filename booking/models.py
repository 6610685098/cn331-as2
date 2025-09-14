# booking/models.py

from django.db import models
from django.contrib.auth.models import User
from datetime import time 

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

    # --- ส่วนที่เพิ่มเข้ามา ---
    # upload_to='room_images/' คือให้เก็บไฟล์ไว้ในโฟลเดอร์ media/room_images/
    # null=True, blank=True ทำให้ฟิลด์นี้ไม่บังคับกรอก (สำหรับห้องเก่าที่ยังไม่มีรูป)
    image = models.ImageField(upload_to='room_images/', null=True, blank=True, verbose_name="รูปภาพห้อง")

    def __str__(self):
        return f"{self.name} ({self.room_code})"

# คลาส Booking ไม่ต้องแก้ไข
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ผู้จอง")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="ห้องที่จอง")
    booking_time = models.DateTimeField(auto_now_add=True, verbose_name="เวลาที่ทำรายการ")
    start_time = models.TimeField(verbose_name="เวลาเริ่มต้น")
    end_time = models.TimeField(verbose_name="เวลาสิ้นสุด")

    class Meta:
        unique_together = [
            ['user', 'room'],
            ['room', 'start_time']
        ]

    def __str__(self):
        return f"{self.user.username} จองห้อง {self.room.name}"