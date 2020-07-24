from django.core.mail import EmailMessage, send_mail, BadHeaderError
from django.template.loader import get_template
from django.shortcuts import redirect, render,HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from ..decorators import student_required
from django.contrib.auth import login
from ..forms import PasswordChangeForm, UserCreationForm, UserUpdateForm, StudentSignUpForm, TeacherSignUpForm, ContactForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.views.generic import CreateView
from ..models import User


class SignUpView(TemplateView):
    template_name = 'classroom/user/signup.html'


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'classroom/user/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('login')


class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'classroom/user/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('login')

@login_required
def contactView(request):
    Contact_Form = ContactForm(request.POST or None)
    if request.method == 'GET':
        return render(request, 'classroom/contact.html', {'form': Contact_Form})
    else:
        form = Contact_Form
        if form.is_valid():
            
            contact_name = request.POST.get('contact_name')
            contact_email = request.POST.get('contact_email')
            contact_content = request.POST.get('content')
            content = "- Tên :" + contact_name + "\n\n" + "- Email: " + contact_email + "\n\n" + "- Lời nhắn: " + "\n\t" + contact_content
            
            email = EmailMessage(
                "Hệ thống nhận dạng và điểm danh khuôn mặt - BDU",
                content,
                "Groups Team THTH" + '',
                ['grteam.tht131417@gmail.com'],
            )
        email.send()
        return redirect('success_send')


@login_required
def successView(request):
    messages.info(request, "Gửi thành công! Cảm ơn bạn đã gửi phản hồi đến chúng tôi.")
    return redirect('contact_us')


def selectSignUpView(request):
    return render(request, 'classroom/user/signup.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Mật khẩu của bạn đã được cập nhật thành công!')
            return redirect('home')
        else:
            messages.error(request, 'Vui lòng điền chính xác thông tin.')
    else:
        form = PasswordChangeForm(request.user)
    context = {'form': form}
    return render(request,'classroom/user/change_password.html', context=context)


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance = request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Tài khoản của bạn đã được cập nhật thành công!')
            return redirect('home')
    else:
        u_form = UserUpdateForm(instance = request.user)
    context = {'u_form': u_form}
    return render(request, 'classroom/user/edit_profile.html', context=context)


def aboutTeams(request):
    return render(request, 'classroom/teams.html')


def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teachers:attendance_index')
        else:
            return redirect('students:search_individual')
    return render(request, 'classroom/home.html')
