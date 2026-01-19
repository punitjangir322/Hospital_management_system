from django.urls import path
from . import views

urlpatterns = [
    path('', views.sa_login, name='super_admin_login'),
    path('sa-home/', views.super_admin_home, name='super_admin_home'),
    path('hospital/delete/<int:id>/', views.delete_hospital, name='delete_hospital'),
    path('hospital/login/', views.hospital_login, name='hospital_login_page'),
    path('hospital/dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('hospital/dashboard/all-appointment/<int:doctor_id>/', views.all_appointment, name='all-appointment'),
    path('hospital/dashboard/add-doctor/', views.add_doctor, name='add_doctor'),
    path('hospital/dashboard/add-patient/', views.add_patient, name='add_patient'),
    path('hospital/logout/', views.hospital_logout, name='hospital_logout'),
    path('logout/', views.sa_logout, name='sa_logout'),
    path('hospital/dashboard/edit/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    path('doctor/login/', views.doctor_login, name='doctor_login_page'),
    path('patient/login/', views.patient_login, name='patient_login_page'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path(
    'hospital/patient/edit/<int:patient_id>/',
    views.edit_patient,
    name='edit_patient'
),
    path('doctor/dashboard/add-patient', views.add_patient_by_doctor, name='add-patient'),
    path('doctor/dashboard/manage-patient', views.manage_patient, name='manage-patient'),
    path(
    'doctor/dashboard/manage-patient/prescription/<int:meeting_id>/',
    views.generate_prescription,
    name='generate-prescription'
), 
    path(
    'doctor/dashboard/manage-patient/manage-payment/visiting-history/<int:meeting_id>/',
    views.manage_payment_by_doctor,
    name='manage-payment'
),
    path(
    'doctor/dashboard/manage-patient/payment-history/<int:patient_id>/',
    views.payment_history,
    name='payment-history'
),
    path(
        'doctor/dashboard/manage-patient/payment-history/edit-payment/<int:payment_id>/',
        views.edit_payment,
        name='payment-edit'
    ),
    path(
    'doctor/dashboard/manage-patient/all-prescription/<int:patient_id>/',
    views.all_prescription,
    name='all-prescription'),
    path(
    'doctor/dashboard/manage-patient/all-prescription/download-prescription/<int:prescription_id>/',
    views.download_prescription,
    name='download-prescription'),
    
    path(
    'doctor/dashboard/manage-patient/all-prescription/send-prescription/<int:prescription_id>/',
    views.send_prescription,
    name='send-prescription'),
    
    path(
    'doctor/dashboard/manage-patient/create-meeting/<int:patient_id>/',
    views.create_meeting,
    name='create-meeting'
),
    
    path(
    'doctor/dashboard/manage-patient/visiting-history/<int:patient_id>/',
    views.visiting_history,
    name='visiting-history'
),

]
