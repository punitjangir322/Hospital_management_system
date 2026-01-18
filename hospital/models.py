from django.db import models
from django.contrib.auth.models import User

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


    disease = models.CharField(max_length=200)
    admitted_on = models.DateTimeField(auto_now_add=True)
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


class Prescription(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE,null=True,blank=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE,null=True,blank=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE,null=True,blank=True)

    medicine_name = models.CharField(max_length=255,null=True,blank=True)
    quantity = models.PositiveIntegerField(null=True,blank=True)
    description = models.TextField(blank=True, null=True)
    reason=models.TextField(max_length=12,blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name} - {self.medicine_name}"


class Payment(models.Model):

    PAYMENT_METHODS = (
        ("Cash", "Cash"),
        ("UPI", "UPI"),
        ("Card", "Card"),
        ("Net Banking", "Net Banking"),
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="payments",null=True,blank=True
    )
    total_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    paid_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    remaining_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    reason = models.CharField(
        max_length=255
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    payment_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment on {self.payment_date} - Remaining {self.remaining_payment}"