from django.shortcuts import render, render_to_response, redirect
from django.contrib import auth
from .forms import LoginForm, RegistrationForm


def login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        # login_user - модель пользователя возвращается, елси такой пользователь есть в системе
        login_user = auth.authenticate(username=username, password=password)
        if login_user:
            # если есть такой пользователь, то логиним его
            auth.login(request, login_user)
            return redirect('/')
    context = {
        'form': form
    }
    return render(request, 'registration/login_page.html', context)


def logout(request):
    auth.logout(request)
    return redirect('/')

def register(request):
    # args = {}
    # args.update(csrf(request))
    # args['form'] = UserCreationForm()
    # if request.POST:
    #     newuser_form = UserCreationForm(request.POST)
    #     if newuser_form.is_valid():
    #         newuser_form.save()
    #         newuser = auth.authenticate(username=newuser_form.cleaned_data['username'],
    #                                     password=newuser_form.cleaned_data['password2']
    #                                     )
    #         auth.login(request, newuser)
    #         return redirect('/')
    #     else:
    #         args['form'] = newuser_form
    # return render_to_response('register.html', args)
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        new_user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        new_user.username = username
        new_user.set_password(password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.email = email
        new_user.save()
        # login_user - модель пользователя возвращается, елси такой пользователь есть в системе
        login_user = auth.authenticate(username=username, password=password)
        if login_user:
            # если есть такой пользователь, то логиним его
            auth.login(request, login_user)
            return redirect('/')
    context = {
        'form': form
    }
    return render(request, 'registration/registration_page.html', context)