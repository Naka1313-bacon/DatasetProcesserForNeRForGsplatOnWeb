from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class VideoProcessForm(forms.Form):

    video = forms.FileField(label='Video File',help_text=gettext('Upload'), required=False)

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if not video:
            raise forms.ValidationError(gettext("動画ファイルが必要です。"))
        if not video.name.lower().endswith('.mp4'):
            raise forms.ValidationError(gettext("サポートされていないファイル形式が含まれています。"))
        return video  

class BaseProcessImageForm(forms.Form):
    # 共通のフィールドやメソッドを定義
    # 例: 画像ファイルの検証メソッド
    images = MultipleFileField(label='images File',help_text='Upload',required=False)
    def clean_images(self):
        images = self.cleaned_data.get('images', [])
        if len(images) > 200:
            raise forms.ValidationError(gettext("アップロードできる画像は200枚までです。"))
        if not images:
            raise forms.ValidationError(gettext("画像ファイルが必要です。"))
        for image in images:
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise forms.ValidationError(gettext("サポートされていないファイル形式が含まれています。"))
        return images
    
class TrimProcessForm(BaseProcessImageForm):

    trimme_size_t = forms.IntegerField(label='Trimming size top',required=False,initial=0)
    trimme_size_b = forms.IntegerField(label='Trimming size bottom',required=False,initial=0)
    trimme_size_r = forms.IntegerField(label='Trimming size right',required=False,initial=0)
    trimme_size_l = forms.IntegerField(label='Trimming size left',required=False,initial=0)
    def clean_trimme_size(self):
        trimme_size_t = self.cleaned_data.get('trimme_size_t')
        trimme_size_b = self.cleaned_data.get('trimme_size_b')
        trimme_size_r = self.cleaned_data.get('trimme_size_r')
        trimme_size_l = self.cleaned_data.get('trimme_size_l')
        if trimme_size_t is not None and trimme_size_t < 0 or trimme_size_b is not None and trimme_size_b < 0 or trimme_size_r is not None and trimme_size_r < 0 or trimme_size_l is not None and trimme_size_l < 0:
            raise ValidationError(gettext("トリミングのサイズが不正です"))
        return trimme_size_t,trimme_size_b,trimme_size_r,trimme_size_l

    
class RemoveProcessForm(BaseProcessImageForm):

    remove_model = forms.ChoiceField(label='Remove Model', choices=[
        ('u2net', 'U2Net'),
        ('u2netp', 'U2NetP'),
        ('u2net_human_seg', 'U2Net Human Segmentation'),
        ('u2net_cloth_seg', 'U2Net Cloth Segmentation'),
        ('silueta', 'Silueta'),
        ('isnet-general-use', 'ISNet General Use'),
        ('isnet-anime', 'ISNet Anime'),
        ('sam', 'SAM')
    ], initial='isnet-general-use', required=False)
    alpha_matting = forms.BooleanField(label='Alpha Matting', required=False, initial=False)
    only_mask = forms.BooleanField(label='Only Mask', required=False, initial=False)

class ResizeProcessForm(BaseProcessImageForm):

    resize_size_w = forms.IntegerField(label='Resize  w',required=False,initial=0)
    resize_size_h = forms.IntegerField(label='Resize h',required=False,initial=0)
    convert_rgb = forms.BooleanField(label='Convert RGB', required=False, initial=False)
    def clean_resize_size_w(self):
        resize_size_w = self.cleaned_data.get('resize_size_w')
        if resize_size_w is not None and resize_size_w <= 0:
            raise ValidationError(gettext("リサイズの幅は正の整数である必要があります。"))
        return resize_size_w

    def clean_resize_size_h(self):
        resize_size_h = self.cleaned_data.get('resize_size_h')
        if resize_size_h is not None and resize_size_h <= 0:
            raise ValidationError(gettext("リサイズの高さは正の整数である必要があります。"))
        return resize_size_h
    
      
