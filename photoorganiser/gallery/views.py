from django.shortcuts import render,redirect
from .forms import ImageUploadForm
from .utils import analyze_image_with_openai
from django.conf import settings
from .models import Image
import os
from django.db.models import Q

# Create your views here.
def image_upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST,request.FILES)
        if form.is_valid():
            image_instance = form.save()
            image_full_path= os.path.join(settings.MEDIA_ROOT,image_instance.image.name)
            image_instance.tags = analyze_image_with_openai(image_full_path)
            image_instance.save()
            return redirect('image_upload')
    else:
        form = ImageUploadForm()
    return render(request, 'gallery/image_upload.html', {'form':form})

def image_search(request):
    query = request.GET.get('query','').strip()
    matching_images = Image.objects.none()
    if query:
        query_tags = query.split(' ')
        q_objects = Q()
        for tag in query_tags:
            q_objects|= Q(tags__icontains=tag)
        matching_images = Image.objects.filter(q_objects).distinct()
    return render(request,'gallery/search_results.html',{'images':matching_images, 'query':query})