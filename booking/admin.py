from django.contrib import admin
from .models import Room, Booking
from django.utils.html import format_html 

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    
    list_display = ('room_code', 'name', 'capacity', 'status', 'image_preview')
    list_filter = ('status',)
    search_fields = ('name', 'room_code')

    
    # ฟังก์ชันนี้จะถูกเรียกเพื่อสร้างข้อมูลสำหรับคอลัมน์ 'image_preview'
    def image_preview(self, obj):
        # ตรวจสอบว่าห้องมีไฟล์รูปภาพหรือไม่
        if obj.image:
            # ถ้ามี ให้สร้าง HTML tag <img> โดยใช้ URL ของรูปภาพ
            return format_html(f'<img src="{obj.image.url}" width="100" height="auto" />')
        # ถ้าไม่มีรูป ให้แสดงข้อความ "ไม่มีรูป"
        return "ไม่มีรูป"
    
    image_preview.short_description = 'รูปตัวอย่าง'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'booking_time', 'start_time', 'end_time')
    list_filter = ('room',)
    search_fields = ('user__username', 'room__name')