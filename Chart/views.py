from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth import logout, login, authenticate


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['location'] = 'Index'
        return context


class Login(View):

    def get(self, request):
        if request.user.is_authenticated():
            logout(request)
            return render(request, 'index.html', {'zone': 'Index'})
        else:
            return render(request, 'login.html', {'zone': 'Login'})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'index.html', {'location': 'Index'})
        else:
            return render(request, 'login.html', {'message': 'This user can not be found', 'zone': 'Login'})