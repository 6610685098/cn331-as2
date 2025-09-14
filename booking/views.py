from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, RoomForm
from django.contrib import messages
from .models import Room, Booking
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError
from datetime import datetime, time, date

# สมัครสมาชิก
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            username = form.cleaned_data.get('username')
            messages.success(request, f'บัญชีสำหรับ {username} ถูกสร้างขึ้นแล้ว! คุณสามารถเข้าสู่ระบบได้เลย')
            return redirect('login') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# แสดงรายการห้องที่เปิดให้จอง
def room_list_view(request):
    rooms = Room.objects.filter(status='open').order_by('name')
    today = date.today()
    
    # ดึงข้อมูลการจอง "เฉพาะของวันนี้" ทั้งหมดมาเก็บใน Set เพื่อการค้นหาที่รวดเร็ว
    # เราจะเก็บเป็น tuple (room_id, start_hour)
    todays_booked_slots = set(
        Booking.objects.filter(booking_date=today).values_list('room_id', 'start_time__hour')
    )

    rooms_data = []
    for room in rooms:
        time_slots = []
        start_hour = room.start_time_available.hour
        end_hour = room.end_time_available.hour
        
        for h in range(start_hour, end_hour):
            # ตรวจสอบว่า (room.id, h) อยู่ใน Set ที่เราเตรียมไว้หรือไม่
            is_booked = (room.id, h) in todays_booked_slots
            
            time_slots.append({
                'hour': f"{h:02d}",
                'is_booked': is_booked
            })
        
        rooms_data.append({
            'room': room,
            'hours': time_slots
        })

    return render(request, 'booking/room_list.html', {'rooms_data': rooms_data})


@login_required
def book_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    today = date.today()

    if request.method == "POST":
        
        # --- ส่วนที่เพิ่มเข้ามา: ตรวจสอบว่า User จองห้องนี้ในวันนี้ไปแล้วหรือยัง ---
        # เราจะเช็คว่ามี Booking object ที่ตรงกับ user, room, และ date ของวันนี้อยู่หรือไม่
        if Booking.objects.filter(user=request.user, room=room, booking_date=today).exists():
            messages.error(request, f"คุณได้ทำการจองห้อง '{room.name}' สำหรับวันนี้ไปแล้ว (จำกัด 1 ครั้ง/คน/ห้อง/วัน)")
            return redirect("booking:room_list")
        # --- สิ้นสุดส่วนที่เพิ่มเข้ามา ---

        start_time_str = request.POST.get("start_time")
        if not start_time_str:
            return redirect("booking:room_list")

        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        
        # ตรวจสอบการจองซ้ำ (เวลาชนกับคนอื่น)
        if Booking.objects.filter(room=room, booking_date=today, start_time=start_time).exists():
            messages.error(request, f"ห้อง {room.name} ถูกจองเวลา {start_time_str} ของวันนี้ไปแล้ว")
            return redirect("booking:room_list")

        # สร้าง Booking ใหม่พร้อมบันทึกวันที่
        Booking.objects.create(
            user=request.user,
            room=room,
            booking_date=today,
            start_time=start_time,
            end_time=time(start_time.hour + 1, 0)
        )
        messages.success(request, f"จองห้อง {room.name} เวลา {start_time_str} สำเร็จ")
        return redirect('booking:my_bookings')
    
    return redirect('booking:room_list')


# ดูรายการจองของตนเอง
@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

# ยกเลิกการจอง
@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    messages.success(request, 'ยกเลิกการจองสำเร็จ') 
    return redirect('booking:my_bookings')

# ดูรายการห้องทั้งหมด (สำหรับ admin)
@staff_member_required
def admin_room_bookings_view(request):
    rooms = Room.objects.annotate(booking_count=Count('booking')).order_by('name')
    context = {
        'rooms': rooms,
    }
    return render(request, 'booking/admin_room_view.html', context)

# เพิ่มห้องใหม่ (สำหรับ admin)
@staff_member_required
def add_room_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มห้องใหม่สำเร็จ!')
            return redirect('booking:room_list')
    else:
        form = RoomForm()
    
    return render(request, 'booking/room_form.html', {'form': form})

# แก้ไขข้อมูลห้อง (สำหรับ admin)
@staff_member_required
def edit_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f'แก้ไขข้อมูลห้อง {room.name} สำเร็จ!')
            return redirect('booking:room_list')
    else:
        form = RoomForm(instance=room)
        
    return render(request, 'booking/room_form.html', {'form': form, 'room': room})