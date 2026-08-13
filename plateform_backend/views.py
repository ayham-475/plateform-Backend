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
from .serializers import UserSerializer,ProfileSerializers,ContentSerializers,BookDetailSerializers,ArticleDetailSerializers,PurchaseSerializers
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
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        
       
        return Response({
                'token': token.key,
                'user': user_data # يحتوي الآن على is_staff و is_superuser
            }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "البريد الإلكتروني أو كلمة المرور غير صحيحة."}, status=status.HTTP_401_UNAUTHORIZED)

class Users(APIView):
    def get(self,request):
        users=User.objects.all()
        serliazerUsers=UserSerializer(users,many=True)
        return Response(serliazerUsers.data) 
    
    def post(self,request):
        serliazerUsers=UserSerializer(data=request.data)

        if serliazerUsers.is_valid():
            serliazerUsers.save()
            return Response(
                serliazerUsers.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serliazerUsers.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    

class Users_PK(APIView):
    
    def get_object(self,pk):
        try:
             return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
            user = self.get_object(pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
         
    def put(self,request,pk):
        users=self.get_object(pk)
        serliazerProfiles=UserSerializer(users,data=request.data)
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
        users=self.get_object(pk)
        users.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT

        )

class Profiles(APIView):
    def get(self,request):
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

class Contents(APIView):

    def get(self,request):
        artices=Content.objects.all()
        serliazerContent=ContentSerializers(artices ,many=True)
        return Response(serliazerContent.data)
    def post(self,request):
        serliazerContent=ContentSerializers(data=request.data)
        if serliazerContent.is_valid():
            serliazerContent.save()
            return Response(serliazerContent.data,
                            status=status.HTTP_200_OK)
        
        return Response(serliazerContent.errors,
                        status=status.HTTP_400_BAD_REQUEST)
class Contents_PK(APIView):


    def get_object(self,pk):
            try:
                 return Content.objects.get(pk=pk)
            except Content.DoesNotExist:
                raise Http404
    def get(self, request, pk, format=None):
        article=self.get_object(pk)
        serilazerContent=ContentSerializers(article)
        return Response(serilazerContent.data,
                        status=status.HTTP_200_OK
                        )
    def put (self,request,pk):
        article=self.get_object(pk)
        serilazerContent=ContentSerializers(article,data=request.data)
        if serilazerContent.is_valid():
            serilazerContent.save()
            return Response(serilazerContent.data,
                                        status=status.HTTP_201_CREATED)
    
        return Response(serilazerContent.errors,
                  status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        article=self.get_object(pk)
        article.delete()
        
        return Response(
                    status=status.HTTP_204_NO_CONTENT
        
                )


    
class BooksDeatils(APIView):
    def get(self,request):
        bookdeails=BookDetail.objects.all()
        serliazerbookdeatils=BookDetailSerializers(bookdeails,many=True)
        return Response(serliazerbookdeatils.data) 
    
    def post(self,request):
        serilazerBookdeatils=BookDetailSerializers(data=request.data)

        if serilazerBookdeatils.is_valid():
            serilazerBookdeatils.save()
            return Response(
                serilazerBookdeatils.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serilazerBookdeatils.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class BooksDeatils_pk(APIView):

    def get_object(self,pk):
            try:
                 return BookDetail.objects.get(pk=pk)
            except BookDetail.DoesNotExist:
                raise Http404
    def get(self, request, pk, format=None):
        bookdeails=self.get_object(pk)
        serilazerBookdeatils=BookDetailSerializers(bookdeails)
        return Response(serilazerBookdeatils.data,
                        status=status.HTTP_200_OK
                        )
    def put (self,request,pk):
        bookdeails=self.get_object(pk)
        serilazerBookdeatils=BookDetailSerializers(bookdeails,data=request.data)
        if serilazerBookdeatils.is_valid():
            serilazerBookdeatils.save()
            return Response(serilazerBookdeatils.data,
                                        status=status.HTTP_201_CREATED)
    
        return Response(serilazerBookdeatils.errors,
                  status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        bookdeails=self.get_object(pk)
        bookdeails.delete()
        
        return Response(
                    status=status.HTTP_204_NO_CONTENT
        
                )
  

    
class ArticlesDeatils(APIView):
    def get(self,request):
        Articledeails=ArticleDetail.objects.all()
        serliazerArticlesdeatils=ArticleDetailSerializers(Articledeails,many=True)
        return Response(serliazerArticlesdeatils.data) 
    
    def post(self,request):
        serliazerArticlesdeatils=ArticleDetailSerializers(data=request.data)

        if serliazerArticlesdeatils.is_valid():
            serliazerArticlesdeatils.save()
            return Response(
                serliazerArticlesdeatils.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serliazerArticlesdeatils.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class ArticlesDeatils_pk(APIView):

    def get_object(self,pk):
            try:
                 return ArticleDetail.objects.get(pk=pk)
            except ArticleDetail.DoesNotExist:
                raise Http404
    def get(self, request, pk, format=None):
        Articledeails=self.get_object(pk)
        serliazerArticlesdeatils=ArticleDetailSerializers(Articledeails)
        return Response(serliazerArticlesdeatils.data,
                        status=status.HTTP_200_OK
                        )
    def put (self,request,pk):
        Articledeails=self.get_object(pk)
        serliazerArticlesdeatils=ArticleDetailSerializers(Articledeails,data=request.data)
        if serliazerArticlesdeatils.is_valid():
            serliazerArticlesdeatils.save()
            return Response(serliazerArticlesdeatils.data,
                                        status=status.HTTP_201_CREATED)
    
        return Response(serliazerArticlesdeatils.errors,
                  status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        Articledeails=self.get_object(pk)
        Articledeails.delete()
        
        return Response(
                    status=status.HTTP_204_NO_CONTENT
        
                )
  
  

    
class Purchases(APIView):
    def get(self,request):
        purchases=Purchase.objects.all()
        serliazerArticlesdeatils=PurchaseSerializers(purchases,many=True)
        return Response(serliazerArticlesdeatils.data) 
    
    def post(self,request):
        purchaseSerializersa=PurchaseSerializers(data=request.data)

        if purchaseSerializersa.is_valid():
            purchaseSerializersa.save()
            return Response(
                purchaseSerializersa.data,
                status=status.HTTP_200_OK
            )
        return Response(
            purchaseSerializersa.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class Purchases_pk(APIView):

    def get_object(self,pk):
            try:
                 return Purchase.objects.get(pk=pk)
            except Purchase.DoesNotExist:
                raise Http404
    def get(self, request, pk, format=None):
        purchases=self.get_object(pk)
        purchaseSerializersa=purchaseSerializersa(purchases)
        return Response(PurchaseSerializers.data,
                        status=status.HTTP_200_OK
                        )
    def put (self,request,pk):
        purchases=self.get_object(pk)
        purchaseSerializersa=PurchaseSerializers(purchases,data=request.data)
        if purchaseSerializersa.is_valid():
            purchaseSerializersa.save()
            return Response(purchaseSerializersa.data,
                                        status=status.HTTP_201_CREATED)
    
        return Response(purchaseSerializersa.errors,
                  status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        Articledeails=self.get_object(pk)
        Articledeails.delete()
        
        return Response(
                    status=status.HTTP_204_NO_CONTENT
        
                )
  