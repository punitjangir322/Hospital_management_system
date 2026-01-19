from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User   # ✅ FIXED
from .models import Hospital,Doctor,Patient,Appointment,Prescription,Payment,Meeting,AdmitPatient
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
import logging
import traceback
from django.http import JsonResponse
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
from reportlab.lib import colors
from decimal import Decimal
from io import BytesIO
from django.core.mail import EmailMessage



logger = logging.getLogger(__name__)
def super_admin_login(request):
    return render(request,'super_admin_login.html')




def sa_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == 'admin' and password == 'admin123':
            request.session['super_admin'] = True
            return redirect('super_admin_home')  
        else:
            return render(
                request,
                'super_admin_login.html',
                {'error': 'Invalid username or password'}
            )

    return render(request, 'super_admin_login.html')
 



def sa_logout(request):
    request.session.flush()
    return redirect('super_admin_login')



# Super Admin Home Dashboard
def super_admin_home(request):
    # 🔒 Protect page
    if not request.session.get('super_admin'):
        return redirect('super_admin_login')

    error = None  # to show validation errors

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate fields
        if not all([name, address, phone, email, username, password]):
            error = "All fields are required"
        elif User.objects.filter(username=username).exists():
            error = "Hospital username already exists"
        else:
            # Create hospital admin user
            user = User.objects.create_user(username=username, password=password)

            # Create hospital
            Hospital.objects.create(
                name=name,
                address=address,
                phone=phone,
                email=email,
                admin=user
            )
            return redirect('super_admin_home')

    # List all hospitals
    hospitals = Hospital.objects.all()

    return render(request, 'super_admin_home.html', {
        'hospitals': hospitals,
        'error': error
    })


# Delete Hospital




def delete_hospital(request, id):
    
    if not request.session.get('super_admin'):
        return redirect('super_admin_login')

    
    hospital = get_object_or_404(Hospital, id=id)

    
    if hospital.admin:
        hospital.admin.delete()

    
    hospital.delete()

    
    return redirect('super_admin_home')


def hospital_login_page(request):
    return render(request,'hospital_login.html')

def hospital_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Get user created by super admin
            user = User.objects.get(username=username)

            # Check password
            if check_password(password, user.password):
                # Ensure this user is a hospital admin
                hospital = Hospital.objects.get(admin=user)

                # Store hospital session
                request.session['hospital_id'] = hospital.id
                request.session['hospital_name'] = hospital.name

                return redirect('hospital_dashboard')
            else:
                raise Exception("Invalid password")

        except:
            return render( 
                request,
                'hospital_login.html',
                {'error': 'Invalid hospital username or password'}
            )

    return render(request, 'hospital_login.html')


def hospital_logout(request):
    request.session.flush()
    return redirect('hospital_login_page')





def hospital_dashboard(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login_page')

    hospital = Hospital.objects.get(id=hospital_id)

    patients = Patient.objects.filter(
        hospital=hospital
    ).order_by('-id')

    doctors = Doctor.objects.filter(hospital=hospital)

    return render(request, 'hospital_dashboard.html', {
        'doctors': doctors,
        'patients': patients,
        'hospital':hospital
    })






def add_doctor(request):
    
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login_page')

    hospital = Hospital.objects.get(id=hospital_id)

    # 🟢 Handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        specialization = request.POST.get('specialization')
        mobile = request.POST.get('mobile')
        password=request.POST.get('password')
        email = request.POST.get('email')

        
        if not all([name, specialization, mobile, email, password]):
            error = "All fields are required"
        elif User.objects.filter(username=email).exists():
            error = "Doctor username already exists"
        else:
            
            user = User.objects.create_user(username=email, password=password)


        
        Doctor.objects.create(
            hospital=hospital,
            name=name,
            specialization=specialization,
            mobile=mobile,
            admin=user
        )

        
        return redirect('hospital_dashboard')

    
    return render(request, 'add_doctor.html')

def add_patient(request):
    
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login_page')

    hospital = Hospital.objects.filter(id=hospital_id).first()
    if not hospital:
        return redirect('hospital_login_page')

    
    doctors = Doctor.objects.filter(hospital=hospital)

    if request.method == "POST":
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        
        
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        email=request.POST.get('email')
        doctor_id = request.POST.get('doctor') or None

        # Basic validation
        if not name or not mobile or not password:
            return render(request, 'add_patient.html', {
                'error': 'Name, Mobile and Password are required',
                'doctors': doctors
            })

        try:
            
            user = User.objects.create_user(
                username=mobile,
                password=password
            )

            
            Patient.objects.create(
                name=name,
                age=age,
                gender=gender,
                
                address=address,
                doctor_id=doctor_id,
                admin=user,
                hospital=hospital,
                email=email
            )

            return redirect('hospital_dashboard')

        except IntegrityError:
            return render(request, 'add_patient.html', {
                'error': 'Patient with this mobile already exists',
                'doctors': doctors
            })

    return render(request, 'add_patient.html', {
        'doctors': doctors
    })
    


def edit_doctor(request, doctor_id):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login_page')

    hospital = get_object_or_404(Hospital, id=hospital_id)

    doctor = get_object_or_404(Doctor, id=doctor_id, hospital=hospital)
    user = doctor.admin  # ✅ get linked user

    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        specialization = request.POST.get('specialization')
        password = request.POST.get('password')

        if not name or not mobile or not email or not specialization:
            return render(request, 'edit_doctor.html', {
                'doctor': doctor,
                'hospital': hospital,
                'user': user,
                'error': 'All fields except password are required'
            })

        doctor.name = name
        doctor.mobile = mobile
        doctor.specialization = specialization
        doctor.save()

        user.email = email
        user.username = email
        if password:
            user.set_password(password)
        user.save()

        return redirect('hospital_dashboard')

    return render(request, 'edit_doctor.html', {
        'doctor': doctor,
        'hospital': hospital,
        'user': user
    })





def patient_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            
            user = User.objects.get(username=username)

            
            if not check_password(password, user.password):
                raise Exception("Invalid password")

        
            patient = Patient.objects.get(admin=user)

            
            request.session['patient_id'] = patient.id
            request.session['patient_name'] = patient.name

            return redirect('patient_dashboard')

        except:
            return render(
                request,
                'patient_login.html',
                {'error': 'Invalid patient username or password'}
            )

    return render(request, 'patient_login.html')


def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Check if user exists
            user = User.objects.get(username=username)

            # Verify password
            if not check_password(password, user.password):
                return render(
                    request,
                    'doctor_login.html',
                    {'error': 'Invalid password'}
                )

            try:
                doctor = Doctor.objects.get(admin=user)
            except Doctor.DoesNotExist:
                return render(
                    request,
                    'doctor_login.html',
                    {'error': 'You are not authorized as a doctor'}
                )

            # Store doctor session
            request.session['doctor_id'] = doctor.id
            request.session['doctor_name'] = doctor.name

            return redirect('doctor_dashboard')

        except User.DoesNotExist:
            return render(
                request,
                'doctor_login.html',
                {'error': 'Invalid username'}
            )

    return render(request, 'doctor_login.html')


def doctor_dashboard(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login_page')

    doctor = Doctor.objects.filter(id=doctor_id).first()
    if not doctor:
        return redirect('doctor_login_page')

    # Handle Accept / Reject
    if request.method == "POST":
        appointment_id = request.POST.get('appointment_id')
        action = request.POST.get('action')

        appointment = Appointment.objects.filter(
            id=appointment_id,
            doctor=doctor
        ).first()

        if appointment:
            if action == 'approve':
                appointment.status = 'Approved'
            elif action == 'reject':
                appointment.status = 'Rejected'
            appointment.save()

        return redirect('doctor_dashboard')

    # Fetch appointments by status
    pending = Appointment.objects.filter(
        doctor=doctor,
        status='Pending'
    ).select_related('patient').order_by('-created_at')

    accepted = Appointment.objects.filter(
        doctor=doctor,
        status='Approved'
    ).select_related('patient').order_by('-created_at')

    rejected = Appointment.objects.filter(
        doctor=doctor,
        status='Rejected'
    ).select_related('patient').order_by('-created_at')
    
    appointments = Appointment.objects.filter(
        doctor=doctor,
    
    ).select_related('patient').order_by('-created_at')

    return render(request, 'doctor_dashboard.html', {
        'pending': pending,
        'accepted': accepted,
        'rejected': rejected,
        'appointments':appointments
    })


def patient_dashboard(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login_page')

    patient = Patient.objects.filter(id=patient_id).first()
    if not patient:
        return redirect('patient_login_page')

    doctors = Doctor.objects.filter(hospital=patient.hospital)

    # 🔹 Book appointment
    if request.method == "POST":
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        reason = request.POST.get('reason')

        Appointment.objects.create(
            patient=patient,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            reason=reason,
            status='Pending'
        )
        return redirect('patient_dashboard')

    # 🔹 Fetch appointments with updated status
    appointments = Appointment.objects.filter(
        patient=patient
    ).select_related('doctor').order_by('-appointment_date')

    return render(request, 'patient_dashboard.html', {
        'doctors': doctors,
        'appointments': appointments
    })





def edit_patient(request, patient_id):
    # ---- Check Hospital Login ----
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login_page')

    patient = get_object_or_404(Patient, id=patient_id)
    user = patient.admin
    doctors = Doctor.objects.filter(hospital_id=hospital_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        doctor_id = request.POST.get('doctor')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        
        email=request.POST.get('email')

        # ---- Validation ----
        if not all([name, age, mobile]):
            return render(request, 'edit_patient.html', {
                'patient': patient,
                'user': user,
                'doctors': doctors,
                'error': 'All fields are required'
            })

        # ---- Mobile uniqueness check ----
        if User.objects.filter(username=mobile).exclude(id=user.id).exists():
            return render(request, 'edit_patient.html', {
                'patient': patient,
                'user': user,
                'doctors': doctors,
                'error': 'Mobile number already exists'
            })

        # ---- Update Patient ----
        patient.name = name
        patient.age = age
        patient.doctor_id = doctor_id
        patient.address = address
        
        
        email=email
        patient.save()

        # ---- Update User ----
        user.username = mobile          
        user.set_password(mobile)       
        user.save()

        return redirect('hospital_dashboard')

    return render(request, 'edit_patient.html', {
        'patient': patient,
        'user': user,
        'doctors': doctors
    })




def add_patient_by_doctor(request):
    
    doctor_id = request.session.get('doctor_id')
    

    if not doctor_id:
        return redirect('doctor_login_page')

    doctor = get_object_or_404(Doctor, id=doctor_id)
    hospital = doctor.hospital
    
    if request.method == "POST":
        
        try:
            # Read POST
            name = request.POST['name']
            age = request.POST['age']
            gender = request.POST['gender']
            mobile = request.POST['mobile']
            password = request.POST['password']
            email = request.POST['email']
            address=request.POST['address']
            

            
            user = User.objects.create_user(
                username=mobile,
                
                password=password
            )
            

            
            patient = Patient.objects.create(
                admin=user,
                hospital=hospital,
                doctor=doctor,
                name=name,
                age=age,
                gender=gender,
                mobile=mobile,
                email=email,
                address=address
                
            )
            

            # Send Email
            send_mail(
                "Patient Registered",
                f"""
Dear {name},

You have been registered successfully.

Hospital: {hospital.name}
Doctor: {doctor.name}
Login:
Username: {mobile}
Password: {password}

Login URL:
{request.build_absolute_uri('/patient/login/')}

Thank you
""",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            print("EMAIL SENT")

            return redirect('doctor_dashboard')

        except Exception as e:
            print("ERROR:", e)
            traceback.print_exc()
            return render(request, 'add-patient.html', {
                'error': f"An error occurred: {e}"
            })

    return render(request, 'add-patient.html')




def manage_patient(request):
        
        doctor_id = request.session.get('doctor_id')
        if not doctor_id:
            return redirect('doctor_login_page')

        doctor = get_object_or_404(Doctor, id=doctor_id)

        search = request.GET.get('search', '').strip()

        patients = Patient.objects.filter(
            doctor=doctor
        ).select_related('admin').order_by('-id')

        if search:
            patients = patients.filter(
                Q(name__icontains=search) |
                Q(admin__username__icontains=search)
            )

        patients = patients.order_by('name')

        

        # ✅ Normal page load
        return render(
            request,
            'manage_patient.html',
            {
                'patients': patients,
                'search': search
            }
        )






def generate_prescription(request, meeting_id):

    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login_page')

    doctor = get_object_or_404(Doctor, id=doctor_id)
    meeting = get_object_or_404(Meeting, id=meeting_id)

    hospital = doctor.hospital
    patient = meeting.patient

    if request.method == "POST":
        medicine_names = request.POST.getlist('medicine_name[]')
        quantities = request.POST.getlist('quantity[]')
        descriptions = request.POST.getlist('description[]')

        prescriptions = []

        for name, qty, desc in zip(medicine_names, quantities, descriptions):
            if name.strip():
                prescriptions.append(
                    Prescription.objects.create(
                        hospital=hospital,
                        doctor=doctor,
                        patient=patient,
                        meeting=meeting,   # ✅ LINK TO MEETING
                        medicine_name=name,
                        quantity=int(qty),
                        description=desc
                    )
                )

        # 📄 Generate PDF
        pdf_bytes = generate_prescription_pdf(
            hospital=hospital,
            doctor=doctor,
            patient=patient,
            prescriptions=prescriptions,
            meeting=meeting
        )

        # 📧 Send Email
        email = EmailMessage(
            subject="Your Medical Prescription",
            body=f"""
Hello {patient.name},

Please find your prescription attached.

Doctor: Dr. {doctor.name}
Disease: {meeting.reason}

Regards,
{hospital.name}
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[patient.email],
        )

        email.attach(
            f"Prescription_{patient.name}.pdf",
            pdf_bytes,
            "application/pdf"
        )
        email.send(fail_silently=False)

        # ⬇️ Download PDF
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="Prescription_{patient.name}.pdf"'
        )
        return response

    return render(request, "generate_prescription.html", {
        'patient': patient,
        'doctor': doctor,
        'hospital': hospital,
        'meeting': meeting
    })

def generate_prescription_pdf(hospital, doctor, patient, prescriptions, meeting):

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ================= HEADER =================
    p.setFillColor(colors.HexColor("#1e88e5"))
    p.rect(0, height - 90, width, 90, fill=1)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(40, height - 55, hospital.name)

    p.setFont("Helvetica", 10)
    p.drawString(40, height - 75, hospital.address)
    p.drawRightString(
        width - 40,
        height - 55,
        f"Date: {datetime.now().strftime('%d %b %Y')}"
    )

    # ================= PATIENT INFO =================
    y = height - 130
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Patient Details")
    p.line(40, y - 5, width - 40, y - 5)

    y -= 25
    p.setFont("Helvetica", 11)
    p.drawString(40, y, f"Patient Name: {patient.name}")
    p.drawString(300, y, f"Age: {patient.age}")

    y -= 18
    p.drawString(40, y, f"Gender: {patient.gender}")
    p.drawString(300, y, f"Mobile: {patient.mobile}")

    y -= 18
    p.drawString(40, y, f"Referred Doctor: Dr. {doctor.name}")

    y -= 18
    p.drawString(40, y, f"Disease / Diagnosis: {meeting.reason}")  # ✅ FIXED

    # ================= PRESCRIPTION TABLE =================
    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Prescription")
    p.line(40, y - 5, width - 40, y - 5)

    y -= 25
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, y, "No")
    p.drawString(80, y, "Medicine Name")
    p.drawString(300, y, "Qty")
    p.drawString(360, y, "Description")

    y -= 10
    p.line(40, y, width - 40, y)
    y -= 15

    p.setFont("Helvetica", 10)
    for index, item in enumerate(prescriptions, start=1):
        if y < 120:
            p.showPage()
            y = height - 100

        p.drawString(40, y, str(index))
        p.drawString(80, y, item.medicine_name)
        p.drawString(300, y, str(item.quantity))
        p.drawString(360, y, item.description or "")
        y -= 18

    # ================= SIGNATURE =================
    y -= 40
    p.line(width - 220, y, width - 40, y)
    p.setFont("Helvetica-Bold", 11)
    p.drawRightString(width - 40, y - 15, f"Dr. {doctor.name}")
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 40, y - 30, hospital.name)

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer.read()  # ✅ FIXED SYNTAX





def manage_payment_by_doctor(request, meeting_id):
    # 🔐 Doctor session check
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login_page')

    doctor = get_object_or_404(Doctor, id=doctor_id)
    meeting = get_object_or_404(Meeting, id=meeting_id)

    patient = meeting.patient
    hospital = doctor.hospital

    if request.method == 'POST':
        total = int(request.POST.get('total_amount'))
        paid = int(request.POST.get('paid_amount'))
        date = request.POST.get('payment_date')
        method = request.POST.get('payment_method')

        # ✅ Reason always from meeting
        reason = meeting.reason

        # ✅ Prevent negative remaining
        remaining = max(total - paid, 0)

        Payment.objects.create(
            hospital=hospital,
            doctor=doctor,
            patient=patient,
            meeting=meeting,
            total_payment=total,
            paid_payment=paid,
            remaining_payment=remaining,
            reason=reason,
            payment_method=method,
            payment_date=date
        )

        return redirect('visiting-history', patient.id)

    return render(request, 'create payment.html', {   # ✅ FIXED
        'patient': patient,
        'meeting': meeting
    })


    
def payment_history(request,patient_id):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login_page')

    doctor = get_object_or_404(Doctor, id=doctor_id)
    patient = get_object_or_404(Patient, id=patient_id)
    payment=Payment.objects.filter(patient=patient)
    return render(request,'payment_history.html',{
        'payments':payment,
        'patient':patient
    })
    



def edit_payment(request, payment_id):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login_page')

    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == "POST":
        paid_amount = request.POST.get('paid_payment')
        payment_method = request.POST.get('payment_method')
        payment_date = request.POST.get('payment_date')

        # ✅ Convert to Decimal (IMPORTANT)
        paid_amount = Decimal(paid_amount)
        
        # ❗ Validation
        if paid_amount > payment.remaining_payment:
            return render(
                request,
                'payment_edit.html',
                {
                    'payment': payment,
                    'error': 'Paid amount cannot exceed remaining amount'
                }
            )
        remaining_payment=payment.remaining_payment-paid_amount

        # ✅ Update payment safely
        payment.paid_payment = payment.paid_payment + paid_amount
        payment.payment_method = payment_method
        payment.payment_date = payment_date
        payment.remaining_payment=remaining_payment
        payment.save()  # remaining auto-calculated in model

        return redirect('payment-history', payment.patient.id)

    return render(
        request,
        'payment_edit.html',
        {'payment': payment}
    )

def all_prescription(request,patient_id):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login_page')

    patient=get_object_or_404(Patient,id=patient_id)
    meeting=Meeting.objects.filter(patient=patient)
    prescription=Prescription.objects.filter(patient=patient)
    return render(request,'all prescriptions.html',{
        'prescriptions':prescription,
        'meeting':meeting
        
    })


def download_prescription(request, prescription_id):

    prescription = get_object_or_404(Prescription, id=prescription_id)

    # fetch all prescriptions of same patient + doctor + same date
    prescriptions = Prescription.objects.filter(
        patient=prescription.patient,
        doctor=prescription.doctor,
        created_at__date=prescription.created_at.date()
    )

    # ✅ generate raw pdf bytes
    pdf_bytes = generate_prescription_pdf(
        hospital=prescription.hospital,
        doctor=prescription.doctor,
        patient=prescription.patient,
        prescriptions=prescriptions
    )

    # ✅ return downloadable PDF
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="Prescription_{prescription.patient.name}.pdf"'
    )

    return response

def send_prescription(request, prescription_id):

    prescription = get_object_or_404(Prescription, id=prescription_id)

    # ✅ Safety check
    if not prescription.meeting:
        messages.error(request, "Prescription is not linked to any visit")
        return redirect('all-prescription', prescription.patient.id)

    patient = prescription.patient
    doctor = prescription.doctor
    hospital = prescription.hospital
    meeting = prescription.meeting

    patient_email = patient.email
    if not patient_email:
        messages.error(request, "Patient email not found")
        return redirect('all-prescription', patient.id)

    # ✅ Get all prescriptions of SAME MEETING
    prescriptions = Prescription.objects.filter(
        meeting=meeting
    ).order_by('id')

    # ✅ Generate PDF bytes (PASS MEETING)
    pdf_bytes = generate_prescription_pdf(
        hospital=hospital,
        doctor=doctor,
        patient=patient,
        prescriptions=prescriptions,
        meeting=meeting
    )

    # ✅ Create Email
    email = EmailMessage(
        subject=f"Prescription from {hospital.name}",
        body=(
            f"Dear {patient.name},\n\n"
            f"Please find attached your prescription.\n\n"
            f"Doctor: Dr. {doctor.name}\n"
            f"Disease: {meeting.reason}\n"
            f"Hospital: {hospital.name}\n\n"
            f"Get well soon."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[patient_email],
    )

    # ✅ Attach PDF
    email.attach(
        filename=f"Prescription_{patient.name}.pdf",
        content=pdf_bytes,
        mimetype="application/pdf"
    )

    # ✅ Send Email
    email.send(fail_silently=False)

    messages.success(request, "Prescription sent to patient email successfully")

    return redirect('all-prescription', patient.id)

def create_meeting(request,patient_id):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login_page')
    patient=get_object_or_404(Patient,id=patient_id)
    doctor=get_object_or_404(Doctor,id=doctor_id)
    hospital=doctor.hospital
    if request.method=='POST':
        date=request.POST.get('meeting_date')
        reason=request.POST.get('reason')
        desc=request.POST.get('description')
        
        Meeting.objects.create(
            hospital=hospital,
            doctor=doctor,
            patient=patient,
            meeting_date=date,
            reason=reason,
            description=desc
        )
        return redirect('manage-patient')
    
    return render(request,'create_meeting.html',{
        'patient':patient
    })
    
def visiting_history(request,patient_id):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login_page')
    patient=get_object_or_404(Patient,id=patient_id)
    doctor=get_object_or_404(Doctor,id=doctor_id)
    hospital=doctor.hospital
    meeting=Meeting.objects.filter(patient=patient)
    
        
    return render(request,'visiting_history.html',{
        'meetings':meeting,
        'patient':patient
        
    })
    
def all_appointment(request,doctor_id):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login_page')

    hospital = Hospital.objects.get(id=hospital_id)
    doctor=get_object_or_404(Doctor,id=doctor_id)
    appointment=Appointment.objects.filter(doctor=doctor, status='Approved'
    ).select_related('patient').order_by('-created_at')
    return render(request,'doctor_appointment.html',{
        'appointments':appointment,
        'doctor':doctor
    })



from django.contrib import messages

def admit_patient(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login_page')

    hospital = get_object_or_404(Hospital, id=hospital_id)
    patient = None

    # 🔍 SEARCH PATIENT (ONLY FROM SAME HOSPITAL)
    search = request.GET.get('search')
    if search:
        patient = Patient.objects.filter(
            hospital=hospital
        ).filter(
            Q(name__icontains=search) |
            Q(mobile__icontains=search)
        ).first()

        if not patient:
            messages.error(request, "Patient not found in this hospital")

    # 🏥 ADMIT PATIENT (POST)
    if request.method == "POST":
        patient_id = request.POST.get('patient_id')
        admit_status = request.POST.get('admit_status')
        disease = request.POST.get('disease')

        # ✅ Validate patient belongs to same hospital
        patient = Patient.objects.filter(
            id=patient_id,
            hospital=hospital
        ).first()

        if not patient:
            messages.error(request, "Patient not found in this hospital")
            return redirect('admit_patient')

        AdmitPatient.objects.create(
            patient=patient,
            doctor=patient.doctor,
            hospital=hospital,
            admit_status=admit_status,
            disease=disease,
            mobile=patient.mobile
        )

        messages.success(request, "Patient admitted successfully")
        return redirect('hospital_dashboard')

    return render(request, 'admit patient.html', {
        'patient': patient
    })




def admitted_patient(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login_page')

    hospital = get_object_or_404(Hospital, id=hospital_id)

    search = request.GET.get('search')

    # ✅ Base queryset (ONLY this hospital)
    admits = AdmitPatient.objects.select_related(
        'patient', 'doctor'
    ).filter(hospital=hospital)

    # 🔍 Search inside admitted patients
    if search:
        admits = admits.filter(
            Q(patient__name__icontains=search) |
            Q(patient__mobile__icontains=search) |
            Q(doctor__name__icontains=search) |
            Q(disease__icontains=search)
        )

    return render(request, 'admitted patient.html', {
        'admits': admits
    })


def edit_admitted(request,admit_id):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login_page')

    hospital = get_object_or_404(Hospital, id=hospital_id)
    admit=get_object_or_404(AdmitPatient,id=admit_id)
    if request.method=='POST':
        status=request.POST.get('admit_status')
    
        admit.admit_status=status
        admit.save()
        return redirect('admitted-patient')
    
    
    return render(request,'edit admitted.html',{
        'admit':admit
    })