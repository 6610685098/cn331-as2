# 📚 Room Booking Web Application

### 👥 Team Members
- นายกฤติเดช วิชัยดิษฐ 6610685098
- นางสาวสุภัคจิรา ส่องสว่าง 6610625052

  
### 📝 Project Description

A web application for booking classrooms, developed using Django Framework.

### Main Features:

### 🔑 Authentication System
- Separate roles for Admin and Users
- Users can register, log in, and log out
![register](/readme_picture/register.png)
![login](/readme_picture/login.png)
### 🏫 Classroom Management (Admin)
- Add / edit / delete classrooms
- Set book time period
- Set room capacity and open/close status
![add](/readme_picture/add.png)
![edit](/readme_picture/edit.png)
- View all rooms
  ![admin_view](/readme_picture/admin_view.png)
### 📅 Room Booking (Users)
- book and cancel
 ![mybooking](/readme_picture/mybooking_cancel.png)
- 1-hour per booking slot
- Prevents double booking (reserved slots are red)
  ![room_list](/readme_picture/room_list.png)

### ▶️ Installation & Usage
1. Clone the repository
2. Create a Virtual Environment
```python
py -m venv .venv
source .venv/Scripts/activate   # Windows PowerShell
# or
source .venv/bin/activate       # Mac/Linux
```
3. Install Dependencies
```python
pip install -r requirements.txt
```
4. Run the Development Server
```python
python manage.py runserver
```
[First video](https://youtu.be/kyTAdyPU84g)
[Web](https://cn331-as2-44q8.onrender.com)
[Second video](https://youtu.be/HfNGXYhnprE)

### 📌 Notes / Known Issues
- If runserver fails, check that the virtual environment is activated.
- To reset the database, delete db.sqlite3 and run python manage.py migrate again.
