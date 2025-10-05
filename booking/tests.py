# booking/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Room, Booking
from datetime import date, time

class UserAuthTests(TestCase):
    """
    Test Case สำหรับการสมัครสมาชิกและ Authentication
    """
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('booking:register')

    def test_register_page_loads(self):
        """
        ทดสอบว่าหน้าสมัครสมาชิก (GET request) สามารถโหลดได้สำเร็จ
        """
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_user_registration_success(self):
        """
        ทดสอบการสมัครสมาชิกสำเร็จ (POST request)
        - ต้องสร้าง User ใหม่ในระบบ
        - ต้อง Redirect ไปยังหน้า login
        """
        user_data = {
            'username': 'testuser1',
            'email': 'testuser1@example.com',
            'password1': 'StrongPassword123',
            'password2': 'StrongPassword123',
        }
        response = self.client.post(self.register_url, user_data)
        
        # ตรวจสอบว่ามี user ใหม่ถูกสร้างขึ้นจริง
        self.assertTrue(User.objects.filter(username='testuser1').exists())
        # ตรวจสอบว่า redirect ไปที่หน้า login
        self.assertRedirects(response, reverse('login'))


class BookingProcessTests(TestCase):
    """
    Test Case สำหรับกระบวนการจองห้อง, ดูรายการ, และยกเลิก
    """
    def setUp(self):
        # สร้าง Client และ User สำหรับการทดสอบ
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        
        # Log in user หลัก
        self.client.login(username='testuser', password='password123')

        # สร้างห้องตัวอย่าง
        self.room = Room.objects.create(
            room_code='R101',
            name='Test Room 1',
            capacity=10,
            start_time_available=time(9, 0),
            end_time_available=time(17, 0)
        )
        
        # URL ที่ใช้บ่อย
        self.room_list_url = reverse('booking:room_list')
        self.my_bookings_url = reverse('booking:my_bookings')
        self.book_room_url = reverse('booking:book_room', args=[self.room.id])

    def test_room_list_view_loads(self):
        """
        ทดสอบว่าหน้ารายการห้องสามารถเข้าถึงได้
        """
        response = self.client.get(self.room_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/room_list.html')
        
    def test_successful_booking(self):
        """
        [Good Path] ทดสอบการจองห้องสำเร็จ
        """
        booking_data = {'start_time': '10:00'}
        response = self.client.post(self.book_room_url, booking_data)
        
        # ตรวจสอบว่าการจองถูกสร้างขึ้นใน database
        self.assertTrue(Booking.objects.filter(user=self.user, room=self.room).exists())
        # ตรวจสอบว่า redirect ไปยังหน้ารายการจองของฉัน
        self.assertRedirects(response, self.my_bookings_url)

    def test_booking_a_taken_slot(self):
        """
        [Bad Path] ทดสอบการจองห้องในเวลาที่ถูกคนอื่นจองไปแล้ว
        """
        # ให้ other_user จองห้องเวลา 11:00 น. ไปก่อน
        Booking.objects.create(
            user=self.other_user,
            room=self.room,
            booking_date=date.today(),
            start_time=time(11, 0),
            end_time=time(12, 0)
        )
        
        # user หลักพยายามจองเวลา 11:00 น. ซ้ำ
        booking_data = {'start_time': '11:00'}
        response = self.client.post(self.book_room_url, booking_data)
        
        # ตรวจสอบว่าไม่มีการจองใหม่ถูกสร้างขึ้นสำหรับ user ของเรา
        self.assertFalse(Booking.objects.filter(user=self.user, room=self.room, start_time=time(11, 0)).exists())
        # ตรวจสอบว่า redirect กลับไปหน้ารายการห้อง
        self.assertRedirects(response, self.room_list_url)

    def test_user_cannot_book_same_room_twice_a_day(self):
        """
        [Bad Path] ทดสอบว่า user คนเดิมไม่สามารถจองห้องเดิมซ้ำในวันเดียวกันได้
        """
        # จองครั้งแรก (สำเร็จ)
        self.client.post(self.book_room_url, {'start_time': '14:00'})
        self.assertEqual(Booking.objects.filter(user=self.user, room=self.room).count(), 1)
        
        # พยายามจองครั้งที่สองในเวลาอื่น
        response = self.client.post(self.book_room_url, {'start_time': '15:00'})
        
        # การจองต้องมีแค่ 1 รายการเท่าเดิม
        self.assertEqual(Booking.objects.filter(user=self.user, room=self.room).count(), 1)
        self.assertRedirects(response, self.room_list_url)
        
    def test_cancel_booking(self):
        """
        ทดสอบการยกเลิกการจองของตนเอง
        """
        # สร้างการจองก่อน
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            booking_date=date.today(),
            start_time=time(13, 0),
            end_time=time(14, 0)
        )
        self.assertEqual(Booking.objects.count(), 1)
        
        cancel_url = reverse('booking:cancel_booking', args=[booking.id])
        response = self.client.post(cancel_url)
        
        # ตรวจสอบว่าการจองถูกลบไปแล้ว
        self.assertEqual(Booking.objects.count(), 0)
        # ตรวจสอบว่า redirect ไปหน้า my_bookings
        self.assertRedirects(response, self.my_bookings_url)

    def test_user_cannot_cancel_others_booking(self):
        """
        ทดสอบว่า User ไม่สามารถยกเลิกการจองของคนอื่นได้
        """
        # สร้างการจองของ other_user
        other_booking = Booking.objects.create(
            user=self.other_user,
            room=self.room,
            booking_date=date.today(),
            start_time=time(13, 0),
            end_time=time(14, 0)
        )
        
        # user หลักพยายามยกเลิก
        cancel_url = reverse('booking:cancel_booking', args=[other_booking.id])
        response = self.client.post(cancel_url)
        
        # ต้องได้รับ 404 Not Found เพราะหา booking id ที่ตรงกับ user ไม่เจอ
        self.assertEqual(response.status_code, 404)
        # ตรวจสอบว่าการจองยังคงอยู่
        self.assertTrue(Booking.objects.filter(id=other_booking.id).exists())


class AdminViewsTests(TestCase):
    """
    Test Case สำหรับ View ที่ต้องใช้สิทธิ์ Staff/Admin
    """
    def setUp(self):
        self.client = Client()
        # สร้าง User ธรรมดา
        self.user = User.objects.create_user(username='normaluser', password='password123')
        # สร้าง Staff User
        self.staff_user = User.objects.create_user(username='staffuser', password='password123', is_staff=True)
        
        self.add_room_url = reverse('booking:add_room')

    def test_non_staff_cannot_access_add_room_page(self):
        """
        ทดสอบว่า User ธรรมดาไม่สามารถเข้าหน้า "เพิ่มห้อง" ได้ และจะถูก redirect
        """
        self.client.login(username='normaluser', password='password123')
        response = self.client.get(self.add_room_url)
        
        # User ธรรมดาจะถูก redirect ไปหน้า admin login
        self.assertRedirects(response, f'/admin/login/?next={self.add_room_url}')

    def test_staff_can_access_add_room_page(self):
        """
        ทดสอบว่า Staff สามารถเข้าหน้า "เพิ่มห้อง" ได้สำเร็จ
        """
        self.client.login(username='staffuser', password='password123')
        response = self.client.get(self.add_room_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/room_form.html')

    def test_staff_can_add_a_new_room(self):
        """
        ทดสอบว่า Staff สามารถสร้างห้องใหม่ผ่านฟอร์มได้สำเร็จ
        """
        self.client.login(username='staffuser', password='password123')
        
        room_data = {
            'room_code': 'R202',
            'name': 'New Test Room',
            'capacity': 20,
            'start_time_available': '08:00',
            'end_time_available': '18:00',
            'status': 'open'
        }
        
        response = self.client.post(self.add_room_url, room_data)
        
        # ตรวจสอบว่าห้องใหม่ถูกสร้างขึ้นจริง
        self.assertTrue(Room.objects.filter(room_code='R202').exists())
        # ตรวจสอบว่า redirect ไปยังหน้ารายการห้อง
        self.assertRedirects(response, reverse('booking:room_list'))

    def test_staff_can_edit_room_successfully(self):
        """
        [Good Path] ทดสอบว่า Staff สามารถแก้ไขข้อมูลห้องได้สำเร็จ
        """
        # 1. ล็อกอินในฐานะ Staff
        self.client.login(username='staffuser', password='password123')
        
        # 2. สร้างห้องตัวอย่างขึ้นมาก่อน
        room = Room.objects.create(room_code='R101', name='Old Name', capacity=10)
        edit_url = reverse('booking:edit_room', args=[room.id])
        
        # 3. เตรียมข้อมูลใหม่ที่จะส่งไปแก้ไข (***** แก้ไขตรงนี้ *****)
        updated_data = {
            'room_code': 'R101',
            'name': 'New Updated Name', # <-- เปลี่ยนชื่อห้อง
            'capacity': 20,
            # --- เพิ่มฟิลด์ที่เหลือให้ครบ โดยใช้ค่าเดิม ---
            'start_time_available': room.start_time_available.strftime('%H:%M'),
            'end_time_available': room.end_time_available.strftime('%H:%M'),
            'status': room.status,
        }
        
        # 4. ส่ง POST request เพื่อแก้ไข
        response = self.client.post(edit_url, updated_data)
        
        # 5. ตรวจสอบว่า redirect ไปยังหน้ารายการห้อง
        self.assertRedirects(response, reverse('booking:room_list')) 
        
        # 6. ตรวจสอบว่าข้อมูลใน database ถูกอัปเดตจริง
        room.refresh_from_db()
        self.assertEqual(room.name, 'New Updated Name')
        self.assertEqual(room.capacity, 20)

    def test_staff_edit_room_with_invalid_data(self):
        """
        [Bad Path] ทดสอบการแก้ไขห้องด้วยข้อมูลที่ไม่ถูกต้อง
        """
        # 1. ล็อกอินในฐานะ Staff
        self.client.login(username='staffuser', password='password123')
        
        # 2. สร้างห้องตัวอย่าง
        room = Room.objects.create(room_code='R102', name='Original Name', capacity=15)
        edit_url = reverse('booking:edit_room', args=[room.id])
        
        # 3. ส่งข้อมูลที่ไม่ถูกต้อง (ทำให้ 'name' เป็นค่าว่าง)
        invalid_data = {
            'room_code': 'R102',
            'name': '', # <-- ข้อมูลไม่ถูกต้อง
            'capacity': 25,
        }
        
        response = self.client.post(edit_url, invalid_data)
        
        # 4. ตรวจสอบว่ายังอยู่ที่หน้าเดิม (status code 200) และไม่ได้ redirect
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/room_form.html')
        
        # 5. ตรวจสอบว่าข้อมูลใน database "ไม่" ถูกเปลี่ยนแปลง
        room.refresh_from_db()
        self.assertEqual(room.name, 'Original Name')