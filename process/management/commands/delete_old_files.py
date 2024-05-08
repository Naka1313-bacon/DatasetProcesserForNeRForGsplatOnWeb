# your_app/management/commands/delete_media_contents.py
from django.core.management.base import BaseCommand
from django.conf import settings
import shutil
import os
from datetime import datetime,timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Deletes all files and folders under the MEDIA_ROOT directory'

    def handle(self, *args, **kwargs):
        media_root = settings.MEDIA_ROOT
        print(media_root)
        for item in os.listdir(media_root):
            item_path = os.path.join(media_root, item)
            creation_time = os.path.getmtime(item_path)  # ファイルの最終変更時刻を取得
            if datetime.now() - datetime.fromtimestamp(creation_time) > timedelta(minutes=10):
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    self.stdout.write(self.style.SUCCESS(f'Successfully deleted: {item_path}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error deleting {item_path}: {e}'))

