from rest_framework.decorators import api_view, permission_classes #permission_classes: أداة لتحديد من له الصلاحية لطلب هذا الرابط.
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response # يقوم بتحويل البيانات (كـ Dictionary) إلى صيغة JSON قياسية يفهمها الفرونت-أند.
from rest_framework import status   #مكتبة تحتوي على رموز الحالة القياسية للشبكة (مثل 200 OK, 400 Bad Request, 401 Unauthorized)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate   #: دالة ذكية من ديجانغو تأخذ الإيميل والباسورد، وتقوم بفحصهما وتشفيرهما برمجياً لمطابقتهما مع المخزن في قاعدة البيانات.
from rest_framework.authtoken.models import Token  # استيراد كلاس التوكن الموحد للمشروع لتجنب تضارب مكتبة JWT
from django.views.decorators.csrf import csrf_exempt    
from django.shortcuts import get_object_or_404 
from rest_framework.views import APIView
from django.http import Http404
from .serializers import ProfileSerializers,ContentSerializers,BookDetailSerializers,ArticleDetailSerializers,PurchaseSerializers
from .models import Profile,Content,BookDetail,ArticleDetail,Purchase


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', '')

    if not email or not password:       
        return Response({"error": "البريد الإلكتروني وكلمة المرور مطلوبان."}, status=status.HTTP_400_BAD_REQUEST)

    # التحقق من وجود الحساب مسبقاً
    if User.objects.filter(username=email).exists():
        return Response({"error": "هذا البريد الإلكتروني مسجل مسبقاً."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # نقوم باستخدام الإيميل كـ username أيضاً لضمان فرادته وسهولة تسجيل الدخول
        # create_user دالة آمنة تقوم بتشفير كلمة المرور تلقائياً قبل حفظها
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name # حفظ الاسم هنا
        )
        
        # إنشاء توكن موحد للحساب المسجل حديثاً وحفظه في قاعدة البيانات
        token_object, created = Token.objects.get_or_create(user=user)
        
        user_data = {
            "id": user.id,
            "name": user.first_name,
            "email": user.email,
            "type": "Admin" if user.is_staff else "user"
        }
        
        # تم تصحيح المفتاح النصي للتوكن هنا ليتطابق مع الفرونت-أند تماماً بدلاً من "token  a" الخاطئة
        return Response({
            "user": user_data,
            "token": token_object.key
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return Response({"error": "الرجاء إدخال البريد الإلكتروني وكلمة المرور."}, status=status.HTTP_400_BAD_REQUEST)

    # التحقق من صحة البيانات وتطابقها برمجياً وتشفيرياً
    user = authenticate(username=email, password=password)

    if user is not None:
        # نستطييع ان نستخدم هذا النوع من انشاء التوكن او نستخدم  نظام الـ JWT
        # جلب التوكن الموحد للمستخدم أو إنشاؤه إذا لم يكن موجوداً
        token_object, created = Token.objects.get_or_create(user=user)
        
        user_data = {
            "id": user.id,
            "name": user.first_name if user.first_name else user.username.split('@')[0],
            "email": user.email,
            "type": "Admin" if user.is_superuser or user.is_staff else "user"
        }
        return Response({
            "user": user_data,
            "token": token_object.key
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "البريد الإلكتروني أو كلمة المرور غير صحيحة."}, status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt  # تعطل فحص الـ CSRF لأننا نعتمد على الـ Token للحماية
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_profile_simple(request):
    # 1. استخراج البيانات القادمة من React
    display_name = request.data.get('display_name')
    bio = request.data.get('bio', '')
    avatar_url = request.data.get('avatar_url', '')
    payout_method = request.data.get('payout_method', 'PayPal')
    payout_details = request.data.get('payout_details')

    # 2. التحقق من الحقول المطلوبة
    if not display_name or not payout_details:
        return Response(
            {"error": "اسم العرض وتفاصيل الدفع حقول مطلوبة!"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. إنشاء أو تحديث البروفايل بناءً على المستخدم الحالي (request.user)
    profile, created = Profile.objects.update_or_create(
        user=request.user,  # يربط مع كائن User المصحح في الموديل
        defaults={
            'display_name': display_name,
            'bio': bio,
            'avatar_url': avatar_url,
            'payout_method': payout_method,
            'payout_details': payout_details,
        }
    )

    # 4. تحديد الرسالة المناسبة حسب الحالة
  # تحديد الحالة والرسالة
    if created:
        message = "تم إنشاء الملف الشخصي بنجاح! ✨"
        response_status = status.HTTP_201_CREATED
    else:
        message = "تم تحديث الملف الشخصي بنجاح! ✨"
        response_status = status.HTTP_200_OK

    return Response(
        {
            "message": message,
            "profile_id": str(profile.profile_id),
            "display_name": profile.display_name
        },
        status=response_status
    )
@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def create_or_update_article(request, pk=None):
    # 1. التأكد الجازم من أن المستخدم القادم في الـ Token موجود فعلياً في قاعدة البيانات
    if not User.objects.filter(id=request.user.id).exists():
        return Response(
            {"error": "جلسة التسجيل غير صالحة أو الحساب غير موجود. يرجى إعادة تسجيل الدخول!"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # 2. التحقق من وجود Profile للمستخدم
    user_profile = Profile.objects.filter(user=request.user).first()
    if not user_profile:
        return Response(
            {"error": f"المستخدم ({request.user.username}) لا يملك ملف شخصي (Profile). يرجى إنشاؤه أولاً!"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # استخراج البيانات القادمة من الفرونت
    title = request.data.get('title')
    description = request.data.get('description', '')
    category_id = request.data.get('category_id', 'مقالة تكنلوجيا')
    content_type = request.data.get('content_type', Content.ContentType.ARTICLE)
    price = request.data.get('price', 0.00)
    img_path = request.data.get('img_path', '')
    article_status = request.data.get('status', Content.ContentStatus.DRAFT)
    text_content = request.data.get('text_content', '')

    if not title:
        return Response({"error": "عنوان المقال مطلوب!"}, status=status.HTTP_400_BAD_REQUEST)

    # حالة التعديل (PUT)
    if request.method == 'PUT' or pk:
        article = get_object_or_404(Content, content_id=pk, user=request.user)
        article.title = title
        article.description = description
        article.category_id = category_id
        article.content_type = content_type
        article.price = price
        if img_path:
            article.img_path = img_path
        article.status = article_status
        article.text_content = text_content
        article.save()

        return Response({
            "message": "تم تعديل المقال بنجاح! ✨",
            "id": str(article.content_id),
            "status": article.status
        }, status=status.HTTP_200_OK)

    # حالة الإنشاء (POST)
    try:
        article = Content.objects.create(
            user=request.user,
            title=title,
            description=description,
            category_id=category_id,
            content_type=content_type,
            price=price,
            img_path=img_path if img_path else "https://via.placeholder.com/600x400",
            status=article_status,
            text_content=text_content
        )
        return Response({
            "message": "تم إنشاء المقال بنجاح! ✨",
            "id": str(article.content_id),
            "status": article.status
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": f"خطأ في حفظ البيانات: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ArticleDeatils(request):
    print("success: ", request.data)

    # 1. إزالة الفاصلة الزائدة
    content_id = request.data.get("content_id")
    body_html = request.data.get("body_html")
    pages_count = request.data.get("pages_count")

    # 2. التحقق من وجود البيانات
    if not body_html or not pages_count:
        return Response(
            {"error": "يرجى توفير body_html و pages_count"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 3. استخدام objects.create بشكل صحيح
    article_detail = ArticleDetail.objects.create(
        content_id=content_id,
        body_html=body_html, pages_count=pages_count
    )

    return Response(
        {
            "message": "تم إنشاء تفاصيل المقال بنجاح! ✨",
            "id": article_detail.id,  # إرجاع المعرف للتأكيد
        },
        status=status.HTTP_201_CREATED,
    )


class Profiles(APIView):
    def get(self):
        profiles=Profile.objects.all()
        serliazerProfile=ProfileSerializers(profiles,many=True)
        return Response(serliazerProfile.data) 
    
    def post(self,request):
        serliazerProfiles=ProfileSerializers(data=request.data)
    
        if serliazerProfiles.is_valid():
            serliazerProfiles.save()
            return Response(
                serliazerProfiles.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serliazerProfiles.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class Profiles_PK(APIView):
    
    def get_object(self,pk):
        try:
             return Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
            profile = self.get_object(pk)
            serializer = ProfileSerializers(profile)
            return Response(serializer.data)
         
    def put(self,request,pk):
        profile=self.get_object(pk)
        serliazerProfiles=ProfileSerializers(profile,data=request.data)
        if serliazerProfiles.is_valid():
            serliazerProfiles.save()
            return Response(
                serliazerProfiles.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
                        serliazerProfiles.errors,
                        status=status.HTTP_400_BAD_REQUEST
                    )
    def delete(self,request,pk):
        profile=self.get_object(pk)
        profile.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT

        )
