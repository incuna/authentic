from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.conf import settings
import os.path
from django.core.paginator import Paginator, InvalidPage, EmptyPage

@staff_member_required
def admin_view(request):
    Context = {}
    if not os.path.exists(settings.LOG_FILENAME):
        Context ['file'] = False
    else:
        filin = open(settings.LOG_FILENAME,'r')
        lines =  filin.readlines()
        filin.close()
        Context ['file'] = True
        paginator =  Paginator(lines, 25)

        try:
            page = int(request.GET.get('page','1'))
        except ValueError:
            page = 1

        try:
            Context ['logs'] = paginator.page(page)
        except (EmptyPage,InvalidPage):
            Context ['logs'] = paginator.page(paginator.num_pages)

    return render_to_response('admin/log_view.html', Context)

# Create your views here.
