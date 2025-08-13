from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import File, Category, FileExtension
from Social_Platform.models import CustomUser
from datetime import datetime, timedelta
from django.utils import timezone


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for Bootstrap styling
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'name@example.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'password'
        })


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['title', 'categories', 'file_description', 'file_urls', 'file_thumbnail', 'file_status', 'file_price']
        # Extension sẽ được tự động set, không cần user chọn
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tiêu đề tài liệu...'
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'extension': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'updatePriceVisibility()'
            }),
            'file_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mô tả chi tiết về tài liệu...'
            }),
            'file_urls': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.jpg,.jpeg,.png,.gif,.webp,.mp4,.avi,.mov,.wmv,.flv,.webm,.mkv'
            }),
            'file_thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'file_status': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'updatePriceVisibility()'
            }),
            'file_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'step': '1000'
            })
        }
        labels = {
            'title': 'Tiêu đề tài liệu',
            'categories': 'Danh mục',
            'file_description': 'Mô tả',
            'file_urls': 'Tệp tài liệu',
            'file_thumbnail': 'Ảnh thumbnail (tùy chọn)',
            'file_status': 'Trạng thái',
            'file_price': 'Giá (VNĐ)'
        }
        help_texts = {
            'title': 'Tên tài liệu phải là duy nhất',
            'categories': 'Chọn một hoặc nhiều danh mục con (không chọn danh mục cha)',
            'file_urls': 'Chọn file PDF, Word, PowerPoint, Excel, Text, ảnh (JPG, PNG, GIF, WEBP) hoặc video (MP4, AVI, MOV, WMV, FLV, WEBM, MKV) (tối đa 500MB)',
            'file_thumbnail': 'Tải ảnh đại diện cho tài liệu (tối đa 5MB)',
            'file_price': 'Nhập giá bằng VNĐ (0 = miễn phí)'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Lưu user instance để sử dụng trong validation
        self.user = user
        
        # Cập nhật choices cho file_status theo thời gian tạo tài khoản của user
        if user:
            # Kiểm tra xem tài khoản đã được tạo ít nhất 1 ngày chưa
            one_day_ago = timezone.now() - timedelta(days=1)
            if user.date_joined <= one_day_ago:
                self.fields['file_status'].choices = [(0, 'Free'), (1, 'For sales')]
            else:
                self.fields['file_status'].choices = [(0, 'Free')]
      

        self.fields['file_status'].initial = 0
        
        # Chỉ hiển thị categories con (không hiển thị categories cha)
        self.fields['categories'].queryset = Category.objects.filter(parent__isnull=False)
        
        # Log file info for debugging
        print(f"📁 FileUploadForm initialized with fields: {list(self.fields.keys())}")
        print(f"📁 file_status choices: {self.fields['file_status'].choices}")

    def clean_file_urls(self):
        file = self.cleaned_data.get('file_urls')
        
        if file and hasattr(file, 'size'):
            # Kiểm tra kích thước file (500MB)
            if file.size > 500 * 1024 * 1024:
                raise forms.ValidationError('Kích thước file không được vượt quá 500MB.')
            
            # Kiểm tra định dạng file
            allowed_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError('Định dạng file không được hỗ trợ. Vui lòng chọn file PDF, Word, PowerPoint, Excel, Text, ảnh (JPG, PNG, GIF, WEBP) hoặc video (MP4, AVI, MOV, WMV, FLV, WEBM, MKV).')
        elif not file:
            raise forms.ValidationError('Vui lòng chọn tệp để tải lên.')
            
        return file

    def clean_file_thumbnail(self):
        thumbnail = self.cleaned_data.get('file_thumbnail')
        
        if thumbnail and hasattr(thumbnail, 'size'):
            # Kiểm tra kích thước ảnh (5MB)
            if thumbnail.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Kích thước ảnh không được vượt quá 5MB.')
            
            # Kiểm tra định dạng ảnh
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_extension = thumbnail.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError('Định dạng ảnh không được hỗ trợ. Vui lòng chọn file JPG, PNG, GIF hoặc WEBP.')
                
        return thumbnail

    def clean_file_price(self):
        price = self.cleaned_data.get('file_price')
        status = self.cleaned_data.get('file_status')
        
        # Kiểm tra giá khi status = For sales
        if status == 1 and (price is None or price <= 0):
            raise forms.ValidationError('Vui lòng nhập giá cho tài liệu có phí.')
        
        if price is not None and price < 0:
            raise forms.ValidationError('Giá không được âm.')
            
        return price or 0

    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        # Kiểm tra trùng lặp title (trừ chính nó nếu đang edit)
        if File.objects.filter(title=title).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError('Tiêu đề này đã tồn tại. Vui lòng chọn tiêu đề khác.')
            
        return title

    def clean_file_status(self):
        file_status = self.cleaned_data.get('file_status')
        
        # Kiểm tra quyền đăng tài liệu tính phí - tài khoản phải được tạo ít nhất 1 ngày
        if file_status == 1:
            if not hasattr(self, 'user') or not self.user:
                raise forms.ValidationError('Vui lòng đăng nhập để đăng tài liệu có phí.')
            
            # Kiểm tra xem tài khoản đã được tạo ít nhất 1 ngày chưa
            one_day_ago = timezone.now() - timedelta(days=1)
            if self.user.date_joined > one_day_ago:
                raise forms.ValidationError('Bạn cần có tài khoản ít nhất 1 ngày để đăng tài liệu có phí.')
            
        return file_status

    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        
        # Kiểm tra xem có ít nhất một category được chọn
        if not categories:
            raise forms.ValidationError('Vui lòng chọn ít nhất một danh mục.')
        
        # Kiểm tra xem có category cha nào được chọn không
        parent_categories = categories.filter(parent__isnull=True)
        if parent_categories.exists():
            raise forms.ValidationError('Không thể chọn danh mục cha. Vui lòng chỉ chọn các danh mục con.')
            
        return categories
    
    def save(self, commit=True):
        """Override save để tự động set extension"""
        instance = super().save(commit=False)
        
        # Tự động set extension dựa trên file được upload
        if instance.file_urls:
            try:
                file_extension = instance.file_urls.name.split('.')[-1].lower()
                extension_obj = FileExtension.get_or_create_extension(file_extension)
                instance.extension = extension_obj
            except Exception as e:
                # Nếu có lỗi với FileExtension, bỏ qua và tiếp tục
                print(f"Warning: Could not set extension: {e}")
                pass
        
        if commit:
            instance.save()
            # Lưu many-to-many relationships
            self.save_m2m()
        
        return instance 