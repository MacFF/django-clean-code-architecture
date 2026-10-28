# Code Architecture & Structure

อธิบายโครงสร้างโค้ดของโปรเจกต์ ซึ่งเอามาเขียนใหม่เป็น **Django 5.2 + DRF / Python 3.13 (ใช้ uv เป็นตัวที่เหมือนเป็นทั้ง pip + pyenv และทำให้โหลด lib ได้เร็วขึ้นเพราะโหลดเป็น binary ลงมา)**

---

## 1. Clean Architecture Mapping to Django Rest Framework

จากที่ดูโค้ดของ Go ที่เขียน Clean Architecture แบบลุง Bob ที่แยกเป็น domain / usecase / interface /infra ซึ่งใน django ก็มีเขียนแบบ clean ที่เป็น best practice เหมือนกันครับผมจึงเอามาเขียนใหม่ให้อยู่ในสไตล์ของ django ครับ

```
django-clean-code-architecture/
├── apps/
│   ├── shared/
│   │   └── models.py               # Abstract Base Model (created_at, updated_at, audit fields)
│   └── users/
│       ├── models.py               # User Domain Model (พร้อม token_version)
│       ├── services.py             # Business Logic
│       ├── serializers.py          # DTOs Data validation & serialization
│       ├── views.py                # Controllers HTTP Request/Response dispatching
│       ├── authentication.py       # Custom JWT Authentication
│       └── urls.py                 # Router mapping url
├── config/                         # Django settings, SimpleJWT, DRF
│   ├── other_settings/
│   │   ├── rest_framwork.py        # DRF pagination & OpenAPI AutoSchema
│   │   └── simple_jwt.py           # JWT lifetime & serializer bindings
│   ├── settings.py                 # Environment-aware core configuration
│   └── urls.py                     # Root URL routing & Swagger UI integration
├── docker-compose.yml              # PostgreSQL 15 service
├── pyproject.toml                  # Python version
└── uv.lock                         # Pinned dependency lockfile
```

### รายละเอียดแต่ละจุดเทียบกับของ Go Architect:
  django ส่วนใหญ่จะมี folder apps หรือ apis และมีหลาย app ในนั้นโดยปกติจะสร้าง app ใหม่ตาม feature หลัก

- **Domain** ➜ `apps/users/models.py `, `apps/shared/models.py`  
  ใน go จะเก็บ struct ส่วนใน django จะเป็นตัวเก็บ table ของระบบซึ่งจะเป็น class User ก็มีพวก base model ที่เอาไปใช้ในหลายๆที่เพื่อให้ model เอาไป oop หรือ embedding ใน go

- **Use Cases** ➜ `apps/users/services.py`  
  เป็นจุดที่ใส่ Business Logic ส่วนใหญ่จะใส่ logic ที่ยาวซับซ้อนหรือใช้หลายจุด แต่ถ้าเป็น logic สั้นๆใช้แค่จุดเดียวก็จะไว้ใน `apps/users/views.py`, `apps/users/serializers.py` กันเพื่อให้ไล่ code ได้ง่าย maintian ง่าย

- **Interface** ➜ `views.py`, `serializers.py`, `authentication.py`  
  ทำหน้าที่เป็นตัวกลางแปลงข้อมูลระหว่างระบบภายนอกกับ Use Cases ภายใน:
  - **Controllers (`views.py`)**: ชั้น Presentation รับ HTTP Request เรียกใช้งาน Use Cases และส่ง Response กลับและสามารถกำหนด scope ข้อมูลการ filter การ authen ในนี้ได้
  - **DTOs (`serializers.py`)**: ตรวจสอบความถูกต้องของ Input Payload หรือสามารถใส่ logic ในนี้เช่นตอนสร้างตอน update ให้ทำอะไรเพิ่มเติมและแปลงโครงสร้างข้อมูลสำหรับ Response
  - **Auth Guard (`authentication.py`)**: `VersionedJWTAuthentication` validate JWT โดยจะอธิบายในข้อ 2 อีกทีครับ แต่จุดนี้ตัว django จะใช้ lib simpleJWT ในการจัดการเหมือนเป็น middleware validate ทุก request ให้ครับ

- **infrastructure** ➜ `config/`, PostgreSQL 15, `drf-spectacular`  
  แต่การตั้งค่า framework เช่น การตั้งค่าระบบ, การเชื่อมต่อ Database, Swagger UI, jwt oauth และผมได้แยกไฟล์สำหรับการ config แยกในการใช้ lib แต่ละตัว `config/other_settings`

---

## 2. Table / API / Auth Explain (Token Versioning)

- **ใน Go ตัวเดิม**: ผมเข้าใจว่าทุกๆ Request จะเกิดการ Query ตาราง `user_tokens` โดยทำ `JOIN` เข้าตาราง `users` ใน DB เสมอด้วยคำสั่ง (`FindOAuthByUserIdAndAccessToken`) เพื่อดูว่า Token ถูกลบไปตอน Logout หรือยัง และตาราง `user_tokens` ก็จะมีการ Insert/Update ทุกครั้งที่มีการ Login

- **แนวทางที่ผมเลือกทำใน Django**: 
  ตอนแรกผมก็กะจะสร้างตาราง `user_tokens` เหมือนกันครับ แต่อยากลองวิธีอื่นที่ Optimize กว่าเดิม ซึ่งผมเห็นว่าในตัว Django + SimpleJWT มันจะ Query โมเดล User มาใส่ใน `request.user` ให้เราอัตโนมัติอยู่แล้ว (เหมือนการ `c.Locals("user")` ใน Go ครับ) 

  ผมเลยเลือกใช้แนวทาง **Token Versioning**:
  1. เพิ่มฟิลด์ `token_version` ในโมเดล `User`
  2. ตอน Login ดึงค่า `token_version` นี้ไปใส่ใน Payload (Body) ของ JWT แล้ว Gen Access + Refresh Token ส่งให้หน้าบ้าน โดยไม่ต้องเขียนลงตาราง Token
  3. เมื่อมี Request วิ่งเข้ามา ระบบจะ Query User ขึ้นมา แล้วเอา `token_version` ในตัว User มาเทียบกับใน JWT Payload ใน Memory (RAM) เลยว่าตรงกันไหม ถ้าไม่ตรงก็ตัดสิทธิ์ 401 ทันที
  4. ทุกครั้งที่มีการ Logout เราแค่สั่งอัปเดต `user.token_version += 1` ซึ่งจะทำให้ Token เก่าทั้งหมดกลายเป็นเวอร์ชันเก่าและใช้งานไม่ได้ทันที ทำหน้าที่เป็น **Global Logout** เหมือนตัว Go เดิมครับ

- **ข้อดีของวิธีนี้**:
  - ไม่ต้องมีตาราง `user_tokens` ใน DB ช่วยลดภาระ Disk Write ทุกครั้งที่ Login
  - ไม่ต้องส่ง Query ตรวจสอบ Token เพิ่มเติม เพราะเทียบใน Memory จาก User ที่ดึงมาอยู่แล้ว
  - ฐานข้อมูลไม่บวมจากประวัติ Token เก่า และไม่ต้องเขียน Background Job คอยตามลบ Token ขยะครับ

- ส่วนเรื่อง table permission ตัว django มี default ให้อยู่แล้วครับแต่ปกติก็จะมา custom กันเองแล้วแต่ทาง business logic และ ui เลยครับ

