from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    
    admin = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="hospital"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class Doctor(models.Model):
    
    hospital = models.ForeignKey(
    Hospital,
    on_delete=models.CASCADE,
    related_name="doctors"
    )
    name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    
    admin = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor",null=True,blank=True
    )

    def __str__(self):
        return self.name


class Patient(models.Model):
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()

    gender = models.CharField(
        max_length=10)
    mobile = models.CharField(max_length=15,null=True)

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="patients"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients"
    )
    admin = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patients",null=True,blank=True
    )


    
    address=models.CharField(max_length=30)
    email = models.EmailField(null=True,blank=True)
    ward_no=models.CharField(max_length=10)
    def __str__(self):
        return self.name

class Appointment(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)





from django.db import models



class Meeting(models.Model):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="meetings"
    )
    

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="meetings"
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="meetings"
    )

    meeting_date = models.DateField()

    reason = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    
    def __str__(self):
        return f"{self.patient.name} - {self.meeting_date}"


class Prescription(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE,null=True,blank=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE,null=True,blank=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE,null=True,blank=True)
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="meetings",null=True,blank=True
    )


    medicine_name = models.CharField(max_length=255,null=True,blank=True)
    quantity = models.PositiveIntegerField(null=True,blank=True)
    description = models.TextField(blank=True, null=True)
    reason=models.TextField(max_length=12,blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name} - {self.medicine_name}"
    
class Payment(models.Model):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,null=True,blank=True
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,null=True,blank=True
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,null=True,blank=True
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,null=True,blank=True
    )

    total_payment = models.PositiveIntegerField()
    paid_payment = models.PositiveIntegerField()
    remaining_payment = models.PositiveIntegerField()

    reason = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=50)
    payment_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name} - {self.payment_date}"

    

