from rembg import remove
from rembg.session_factory import new_session
import cv2
import os
import numpy as np
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import logging
from PIL import Image
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)

class ProcessData():

    def frame_divider(self,video,folder_name):

        cap = cv2.VideoCapture(video)
        out_dir = f'{settings.MEDIA_ROOT}/{folder_name}/frame'
        os.makedirs(out_dir,exist_ok=True)
        if not cap.isOpened():
            print("ビデオファイルを開けませんでした。")
            cap.release()
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step_frame = int(total_frames / 100)
        print(f"総フレーム数: {total_frames}")
        digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
        current_frame = 0
        start_frame = 0  
        stop_frame = total_frames  
        step_frame = 100  
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
        
            if current_frame >= start_frame and current_frame <= stop_frame and (current_frame - start_frame) % step_frame == 0 and current_frame != 0:
                print(f"保存するフレーム番号: {current_frame}")
                frames.append(frame)
        
            current_frame += 1
        # random.shuffle(frames)
        for idx, frame in enumerate(frames):
        
            cv2.imwrite(f"{out_dir}/{idx:05}.png", frame)
        
        cap.release()
        return out_dir
    def trimme(self,folder_path, folder_name, size_t, size_b, size_r, size_l): 

        files = os.listdir(folder_path)
        output_dir = os.path.join(settings.MEDIA_ROOT, folder_name, 'trimme')
        os.makedirs(output_dir, exist_ok=True)
        t = int(size_t)
        b = int(size_b)
        r = int(size_r)
        l = int(size_l)
        for idx, file in enumerate(files):
            
                new_filename = f"{idx:05}.png"
                input_path = os.path.join(folder_path, file)
                output_path = os.path.join(output_dir, new_filename)
                input_image = Image.open(input_path)
                width, height = input_image.size
                cropped_image = input_image.crop((l, t, (width-r) , (height-b) ))
                cropped_image.save(output_path, 'PNG')
        
        return output_dir
    

    def remove(self,folder_path,folder_name,model,alpha_matting,only_mask):
        

        
        files = os.listdir(folder_path)
        output_dir = f'{settings.MEDIA_ROOT}/{folder_name}/remove'
        os.makedirs(output_dir,exist_ok=True)
        session = new_session(model)
        print(files)
        for idx,file in enumerate(files):
           
            input = os.path.join(folder_path,file)
            new_filename = f"image_{idx:05}.png"
            output_path = os.path.join(output_dir, new_filename)
            input_image = Image.open(input)
            output_image = remove(input_image,
            session=session,
            only_mask=only_mask,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_structure_size=10,)
            output_image.save(output_path, 'png')
        return output_dir
    
    def resize(self,folder_path,folder_name,size_w,size_h,convert_rgb):

        out_dir = f'{settings.MEDIA_ROOT}/{folder_name}/resize'
        files = os.listdir(folder_path)
        os.makedirs(out_dir,exist_ok=True)
        for idx,file in enumerate(files):
            input = os.path.join(folder_path, file)
            img = Image.open(input)
            new_filename = f"{idx:05}.png"
            output_path = os.path.join(out_dir, new_filename)
            if img.mode == 'RGBA' and convert_rgb:
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3]) 
                img = background        
            img_resize = img.resize((size_w,size_h))
            img_resize.save(output_path)
        return out_dir

    def colmap(self,folder_path, folder_name):
      
        output_path = Path(f'{settings.MEDIA_ROOT}/{folder_name}/colmap')
        output_path.mkdir(parents=True, exist_ok=True)
        database_path = output_path / "database.db"
        folder_path = Path(folder_path)
        subprocess.run([
            'colmap', 'feature_extractor',
            '--database_path', str(database_path),
            '--image_path', str(folder_path),
            '--ImageReader.camera_model', 'PINHOLE',
            '--SiftExtraction.first_octave', '-1'
        ], check=True)
    
        subprocess.run([
            'colmap', 'exhaustive_matcher',
            '--database_path', str(database_path),
        ], check=True)
        subprocess.run([
            'colmap', 'mapper',
            '--database_path', str(database_path),
            '--image_path', str(folder_path),
            '--output_path', str(output_path),
        ], check=True)

        subprocess.run([
            'colmap', 'model_converter',
            '--input_path', f'{output_path}/0',
            '--output_path', f'{output_path}/0/model.ply',
            '--output_type', 'PLY'
        ], check=True)    
        return output_path