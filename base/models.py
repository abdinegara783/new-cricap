from django.db import models
from django.contrib.auth.models import User

# Pilihan untuk response
RESPONSE_CHOICES = [
    ('SS', 'Sangat Setuju'),
    ('S', 'Setuju'),
    ('R', 'Ragu-Ragu'),
    ('TS', 'Tidak Setuju'),
    ('STS', 'Sangat Tidak Setuju')
]

# Model Section untuk menyimpan kategori atau bagian
class Section(models.Model):
    title = models.CharField(max_length=100)  # Nama bagian/kategori

    def __str__(self):
        return self.title

# Model Question untuk menyimpan pertanyaan utama di dalam setiap bagian
class Question(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)  # Relasi ke bagian
    text = models.TextField()  # Teks pertanyaan utama

    def __str__(self):
        return f"{self.section.title} - {self.text}"

# Model SubQuestion untuk menyimpan sub-pertanyaan
class SubQuestion(models.Model):
    main_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="sub_questions")  # Relasi ke pertanyaan utama
    text = models.TextField()  # Teks sub-pertanyaan

    def __str__(self):
        return f"{self.main_question.text} - {self.text}"

# Model Response untuk menyimpan jawaban pengguna
class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relasi ke pengguna
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE)  # Relasi ke sub-pertanyaan
    response = models.CharField(max_length=3, choices=RESPONSE_CHOICES)  # Pilihan jawaban

    def __str__(self):
        return f'{self.user.username} - {self.sub_question.text} - {self.get_response_display()}'
    

class DataDiri(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100, blank=True, null=True)
    usia = models.IntegerField()
    jenis_kelamin = models.CharField(max_length=15, choices=[
        ("Laki-laki", "Laki-laki"),
        ("Perempuan", "Perempuan"),
    ])
    status_perkawinan = models.CharField(max_length=20, choices=[
        ("Belum berkeluarga", "Belum berkeluarga"),
        ("Duda", "Duda"),
        ("Janda", "Janda"),
        ("Berkeluarga", "Berkeluarga"),
    ])
    pendidikan = models.CharField(max_length=20, choices=[
        ("SLTP", "SLTP"),
        ("SLTA", "SLTA"),
        ("Diploma", "Diploma"),
        ("Sarjana", "Sarjana"),
        ("Pascasarjana", "Pascasarjana"),
    ])
    tempat_tinggal = models.CharField(max_length=100)
    kabupaten_kota = models.CharField(max_length=100)
    pekerjaan = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nama or 'Anonim'} - {self.usia} Tahun"

class IRKResult(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Hubungkan ke user
    irk = models.FloatField()  # Nilai IRK
    category = models.CharField(max_length=20)  # Kategori IRK

    def __str__(self):
        return f"{self.user.username} - IRK: {self.irk} - Kategori: {self.category}"
