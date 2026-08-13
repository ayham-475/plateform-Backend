import uuid
from django.db import models

from django.utils import timezone
from django.contrib.auth.models import User

# User = get_user_model()
class Profile(models.Model):
    # استخدام UUID كمفتاح رئيسي تلقائي التوليد
    profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # علاقة واحد لواحد مع مستخدم ديجانغو مع تسمية سليمة تجنباً لـ user_id_id
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    display_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.TextField(max_length=500, blank=True, null=True)
    payout_method = models.CharField(max_length=100, blank=True, null=True)
    payout_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.display_name} ({self.user.username})"


class Content(models.Model):
    class ContentType(models.TextChoices):
        BOOK = 'BOOK', 'Book'
        ARTICLE = 'ARTICLE', 'Article'

    class ContentStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'

    content_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ربطه مع المستخدم صاحب المحتوى
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='contents',
        default=""
    )
    category_id = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    text_content = models.TextField(blank=True, null=True, default="")
    img_path = models.URLField(
        max_length=500, 
        blank=True, 
        null=True, 
        default="https://via.placeholder.com/600x400"
    )
    language = models.CharField(max_length=50, default='ar')
    status = models.CharField(
        max_length=20, 
        choices=ContentStatus.choices, 
        default=ContentStatus.DRAFT
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[{self.get_content_type_display()}] {self.title}"


class BookDetail(models.Model):
    bookdetail_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # علاقة 1-إلى-1 مباشرة مع المحتوى دون حاجة لـ to_field معقدة
    content = models.OneToOneField(
        Content, 
        on_delete=models.CASCADE, 
        related_name='book_detail'
    )
    file_url = models.URLField(max_length=500)
    pages_count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Book File for: {self.content.title}"


class ArticleDetail(models.Model):
    articledetail_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # علاقة 1-إلى-1 مباشرة مع المحتوى
    content = models.OneToOneField(
        Content, 
        on_delete=models.CASCADE, 
        related_name='article_detail'
    )
    body_html = models.TextField(blank=True, null=True)
    pages_count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Article Detail for: {self.content.title}"

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
class Purchase(models.Model):
    purchase_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content = models.ForeignKey(
        Content, 
        on_delete=models.PROTECT, 
        related_name='purchases'
    )
    
    # -------------------------------------------------------------
    # خيار 1: إذا كنت تريد ربطه برقم ID عادي كمفتاح أجنبي مرتبط بـ User
    # (تأكد أن نموذج User يستخدم رقم عادي وليس UUID)
    payer = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='purchases'
    )

    # خيار 2: إذا كنت تريد احتفاظ بالحقل كـ "رقم مجرد" دون علاقة ForeignKey
    # payer_id = models.BigIntegerField()
    # -------------------------------------------------------------

    author_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50, default='PENDING')
    payment_method = models.CharField(max_length=100)
    transaction_reference = models.CharField(max_length=255, unique=True)
    purchased_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        # استخدام getattr لتجنب أي أخطاء في حال عدم وجود display_name على نموذج User المباشر
        payer_name = getattr(self.payer, 'display_name', str(self.payer))
        return f"Purchase {self.transaction_reference} - {payer_name}"