from django.shortcuts import render,redirect
from django.http import HttpResponseNotFound
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import FileResponse
from .forms import BaseProcessImageForm,VideoProcessForm,TrimProcessForm,RemoveProcessForm,ResizeProcessForm
from .process import ProcessData
import uuid
from django.conf import settings
import os
import zipfile
import time
import shutil
from django.utils import translation
from django.http import HttpResponseRedirect
# Create your views here.
process = ProcessData()
def set_language_from_url(request, language_code):
    translation.activate(language_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = language_code
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def make_zipfile(source_dir, output_filename):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(source_dir, '..')))

def download_zip(request, unique_folder_name):
    zip_file_path = os.path.join(settings.MEDIA_ROOT, f"{unique_folder_name}.zip")
    folder_path = os.path.join(settings.MEDIA_ROOT,unique_folder_name)
    shutil.rmtree(folder_path)
    if os.path.exists(zip_file_path):
        
        return FileResponse(open(zip_file_path, 'rb'), as_attachment=True, filename=f"{unique_folder_name}.zip")
    else:
        # ZIPファイルが存在しない場合の処理
        return HttpResponseNotFound('指定されたファイルが見つかりません。')


def upload(request):
        videoform = VideoProcessForm()
        trimform = TrimProcessForm()
        removeform = RemoveProcessForm()
        resizeform = ResizeProcessForm()
        colmapform = BaseProcessImageForm()
        if request.method == 'POST':
            action = request.POST.get('action')

            if action == 'run_video':
               videoform = VideoProcessForm(request.POST,request.FILES)
               if videoform.is_valid():
                 unique_folder_name = str(uuid.uuid4())
                 folder_path = os.path.join(settings.MEDIA_ROOT, unique_folder_name)
                 os.makedirs(folder_path, exist_ok=True)    
                 fs = FileSystemStorage(location=folder_path)
                 video_file = request.FILES['video']
                 saved_filename = fs.save(video_file.name,video_file)
                 saved_file_path = os.path.join(folder_path, saved_filename)
                 print(f"File saved to: {saved_file_path}")
                                                       
                 out_dir = process.frame_divider(saved_file_path,unique_folder_name)
                 zip_filename = f"{unique_folder_name}.zip"
                 zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
                 make_zipfile(out_dir, zip_file_path)
                 return render(request, 'process/video.html', {
                             'unique_folder_name': unique_folder_name,
                              })
            
            elif action == 'run_trimme':
               trimform = TrimProcessForm(request.POST,request.FILES)
               if trimform.is_valid():
                  unique_folder_name = str(uuid.uuid4())
                  folder_path = f'{settings.MEDIA_ROOT}/{unique_folder_name}'
                  os.makedirs(folder_path, exist_ok=True)    
                  fs = FileSystemStorage(location=folder_path)
                  files = request.FILES.getlist('images')
                  size_t = request.POST.get('trimme_size_t')
                  size_b = request.POST.get('trimme_size_b')
                  size_r = request.POST.get('trimme_size_r')
                  size_l = request.POST.get('trimme_size_l')
                  for file in files:
                      
                     saved_filename = fs.save(file.name, file)
                     saved_file_path = os.path.join(folder_path, saved_filename)
                     print(f"File saved to: {saved_file_path}")
                                      
                  out_dir = process.trimme(folder_path, unique_folder_name, size_t, size_b, size_r, size_l)
                  zip_filename = f"{unique_folder_name}.zip"
                  zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
                  make_zipfile(out_dir, zip_file_path)
                  return render(request, 'process/trimme.html', {
                             'unique_folder_name': unique_folder_name,
                              })
            
            elif action == 'run_remove':
               removeform = RemoveProcessForm(request.POST,request.FILES)
               if removeform.is_valid():
                  unique_folder_name = str(uuid.uuid4())
                  folder_path = os.path.join(settings.MEDIA_ROOT, unique_folder_name)
                  os.makedirs(folder_path, exist_ok=True)    
                  fs = FileSystemStorage(location=folder_path)
                  files = request.FILES.getlist('images')
                  model = request.POST.get('remove_model')
                  matting = request.POST.get('alpha_matting')
                  only_mask = request.POST.get('only_mask')
                  print(files)
                  for file in files:
                      fs.save(file.name, file)
                                     
                  out_dir = process.remove(folder_path,unique_folder_name,model,matting,only_mask)
                  zip_filename = f"{unique_folder_name}.zip"
                  zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
                  make_zipfile(out_dir, zip_file_path)
                  return render(request, 'process/remove.html', {
                             'unique_folder_name': unique_folder_name,
                              })
            
            elif action == 'run_resize':
               resizeform = ResizeProcessForm(request.POST,request.FILES)
               if resizeform.is_valid():
                  unique_folder_name = str(uuid.uuid4())
                  folder_path = os.path.join(settings.MEDIA_ROOT, unique_folder_name)
                  os.makedirs(folder_path, exist_ok=True)    
                  fs = FileSystemStorage(location=folder_path)
                  files = request.FILES.getlist('images')
                  size_w = int(request.POST.get('resize_size_w'))
                  size_h = int(request.POST.get('resize_size_h'))
                  convert_rgb = request.POST.get('convert_rgb')
                  for file in files:
                      fs.save(file.name, file)
                                     
                  out_dir = process.resize(folder_path,unique_folder_name,size_w,size_h,convert_rgb)
                  zip_filename = f"{unique_folder_name}.zip"
                  zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
                  make_zipfile(out_dir, zip_file_path)
                  zip_file_url = settings.MEDIA_URL + zip_filename
                  return render(request, 'process/resize.html', {
                             'unique_folder_name': unique_folder_name,
                              })
            elif action == 'run_colmap':
                colmapform = BaseProcessImageForm(request.POST,request.FILES)
                if colmapform.is_valid():
                   files = request.FILES.getlist('images')
                   
                   # 一意のフォルダを作成
                   unique_folder_name = str(uuid.uuid4())
                   folder_path = os.path.join(settings.MEDIA_ROOT, unique_folder_name)
                   os.makedirs(folder_path, exist_ok=True)
       
                   fs = FileSystemStorage(location=folder_path)
                   for file in files:
                       fs.save(file.name, file)
       
                   # 保存されたファイルのフォルダパスをpycolmapに渡す
                   out_dir = process.colmap(folder_path,unique_folder_name)
                   zip_filename = f"{unique_folder_name}.zip"
                   zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
                   make_zipfile(out_dir, zip_file_path)
                   zip_file_url = settings.MEDIA_URL + zip_filename
     
                   return render(request, 'process/colmap.html', {
                             'unique_folder_name': unique_folder_name,
                             })
            else:
                messages.error(request, '無効なアクションです。')
        

            # GETリクエスト、またはフォームのバリデーションに失敗した場合のフォーム表示
        return render(request, 'process/upload.html', {'videoform'  : videoform,
                                                   'trimform'   : trimform,
                                                   'removeform' : removeform,
                                                   'resizeform' : resizeform,
                                                   'colmapform' : colmapform})