# booking/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, RoomForm
from django.contrib import messages
from .models import Room, Booking
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError
from datetime import datetime, time, date

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            username = form.cleaned_data.get('username')
            messages.success(request, f'บัญชีสำหรับ {username} ถูกสร้างขึ้นแล้ว! คุณสามารถเข้าสู่ระบบได้เลย')
            return redirect('login') # ถูกต้องแล้ว เพราะ 'login' ไม่ได้อยู่ในแอป booking
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# แสดงรายการห้องที่เปิดให้จอง
def room_list_view(request):
    rooms = Room.objects.filter(status='open')
    rooms_with_hours = []
    for room in rooms:
        start_hour = room.start_time_available.hour
        end_hour = room.end_time_available.hour
        available_hours = [f"{h:02d}" for h in range(start_hour, end_hour)]
        rooms_with_hours.append({
            'room': room,
            'hours': available_hours
        })
    return render(request, 'booking/room_list.html', {'rooms_data': rooms_with_hours})


# ทำการจองห้อง
@login_required
def book_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":

        # เช็คว่า user คนนี้เคยจองห้องนี้ไปแล้วหรือยัง
        if Booking.objects.filter(user=request.user, room=room).exists():
            messages.error(request, f"คุณได้ทำการจองห้อง '{room.name}' ไปแล้ว (สามารถจองได้เพียงครั้งเดียวต่อห้อง)")
            return redirect("booking:room_list") # <--- แก้ไขแล้ว

        start_time_str = request.POST.get("start_time")
        if not start_time_str:
            return redirect("booking:room_list") # <--- แก้ไขแล้ว

        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = time(start_time.hour + 1, 0)

        # ป้องกันเวลาชนกัน เช็คว่ามี booking ของห้องนี้เวลาเดียวกันยัง
        if Booking.objects.filter(room=room, start_time=start_time).exists():
            messages.error(request, f"ห้อง {room.name} ถูกจองเวลา {start_time_str} แล้วโดยผู้ใช้อื่น")
            return redirect("booking:room_list") # <--- แก้ไขแล้ว

        try:
            Booking.objects.create(
                user=request.user,
                room=room,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, f"จองห้อง {room.name} เวลา {start_time_str}-{end_time.strftime('%H:%M')} สำเร็จ")
        except IntegrityError:
            messages.error(request, f"ไม่สามารถจองได้ เนื่องจากมีการจองเวลา {start_time_str} แล้ว")
            return redirect("booking:room_list")

    return redirect('booking:my_bookings')


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
    messages.success(request, 'ยกเลิกการจองสำเร็จ') # (Optional) เพิ่ม message บอกผู้ใช้
    return redirect('booking:my_bookings')

@staff_member_required
def admin_room_bookings_view(request):
    # เราต้องการแค่ rooms ที่มีการนับจำนวน booking ก็พอ
    rooms = Room.objects.annotate(booking_count=Count('booking')).order_by('name')
    context = {
        'rooms': rooms,
    }
    return render(request, 'booking/admin_room_view.html', context)


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