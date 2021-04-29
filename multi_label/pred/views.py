from django.shortcuts import render, redirect
from PIL import Image
from pred import use_model, models, my_form
from functools import wraps
from django.contrib import messages


# Create your views here.


def check_login(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        next_url = request.get_full_path()
        if request.session.get("user_name"):
            return func(request, *args, **kwargs)
        else:
            return redirect("/pred/login/?next={}".format(next_url))

    return wrapper


@check_login
def index(request):
    return render(request, "index.html", {"user_name": request.session.get("user_name")})


def user_register(request):
    if request.method == "POST":
        form = my_form.UserRegisterForm(request.POST)
        if form.is_valid():
            models.User.objects.create(user_name=request.POST.get('user_name'),
                                       password=my_form.getMd5Passwd(request.POST.get('password')))
            messages.info(request, "注册成功")
            return redirect("/pred/login")
        else:
            messages.error(request, form.errors['__all__'][0])
    form = my_form.UserRegisterForm()
    return render(request, "user_register.html", {'form': form})


def user_login(request):
    if request.method == "POST":
        form = my_form.UserLoginForm(request.POST)
        if form.is_valid():
            request.session['user_name'] = request.POST.get('user_name')
            messages.info(request, "登录成功")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("/pred/index")
        else:
            messages.error(request, form.errors['__all__'][0])
    form = my_form.UserLoginForm()
    return render(request, "user_login.html", {'form': form})


def user_logout(request):
    request.session.delete()
    messages.info(request, "注销成功")
    return redirect("/pred/login")


@check_login
def user_change_passwd(request):
    if request.method == "POST":
        form = my_form.UserChangePasswdForm(request.POST)
        if form.is_valid():
            old_passwd = request.POST.get("old_passwd")
            if my_form.getMd5Passwd(old_passwd) != models.User.objects.get(
                    user_name=request.session.get("user_name")).password:
                messages.error(request, "旧密码错误")
                return render(request, "user_change_passwd.html", {'form': form})
            new_passwd = request.POST.get("new_passwd")
            models.User.objects.filter(user_name=request.session.get("user_name")).update(
                password=my_form.getMd5Passwd(new_passwd))
            messages.info(request, "修改成功")
            return redirect("/pred/logout")
        else:
            messages.error(request, form.errors['__all__'][0])
    form = my_form.UserChangePasswdForm()
    return render(request, "user_change_passwd.html", {'form': form})


@check_login
def history_list(request):
    history_obj_list = models.History.objects.filter(
        user=models.User.objects.get(user_name=request.session.get("user_name"))).order_by("-pred_time")
    if request.method == "POST":
        patient_id = request.POST.get('patient_id')
        patient_name = request.POST.get('patient_name')
        if len(patient_id) > 0:
            history_obj_list = models.History.objects.filter(
                user=models.User.objects.get(user_name=request.session.get("user_name")),
                patient_id=patient_id).order_by("-pred_time")
        if len(patient_name) > 0:
            history_obj_list = models.History.objects.filter(
                user=models.User.objects.get(user_name=request.session.get("user_name")),
                patient_name=patient_name).order_by("-pred_time")
        if len(patient_id) > 0 and len(patient_name) > 0:
            history_obj_list = models.History.objects.filter(
                user=models.User.objects.get(user_name=request.session.get("user_name")), patient_id=patient_id,
                patient_name=patient_name).order_by("-pred_time")
        messages.info(request, "检索成功")
        return render(request, "history_list.html", {"history_obj_list": history_obj_list, "patient_id": patient_id,
                                                     "patient_name": patient_name})
    return render(request, "history_list.html", {"history_obj_list": history_obj_list})


@check_login
def compute(request):
    if request.method == "POST":
        form = my_form.UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            user = models.User.objects.get(user_name=request.session.get("user_name"))
            history = models.History(photo=request.FILES['photo'],
                                     patient_id=request.POST.get("patient_id"),
                                     patient_name=request.POST.get("patient_name"),
                                     img_type=request.POST.get("img_type"),
                                     note=request.POST.get("note"),
                                     user=user,
                                     pred_result="无"
                                     )
            history.save()
            photo = Image.open(history.photo.path)
            labels = use_model.multi_label_classify(photo, history.img_type)
            history.pred_result = labels
            history.save()
            return render(request, "compute.html", {'form': form, 'photo': history.photo, 'labels': labels})
    form = my_form.UploadImageForm()
    return render(request, "compute.html", {'form': form})
