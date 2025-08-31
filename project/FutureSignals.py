from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from core import is_verified, set_verified, verify_key_with_server, fetch_signals_from_site, MIN_CONFIDENCE
from datetime import datetime, timedelta
from threading import Thread
from kivy.clock import Clock

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class SignalApp(App):
    def build(self):
        self.root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.key_verified = is_verified()
        if not self.key_verified:
            self.show_key_popup()
        else:
            self.build_main_interface()
        return self.root_layout

    def show_key_popup(self):
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        self.key_input = TextInput(
            hint_text="Enter your key",
            multiline=False,
            size_hint=(1, None),
            height=400,
            font_size=30,
            background_color=(0.1, 0.1, 0.2, 1),
            foreground_color=(1,1,1,1)
        )
        key_button = Button(
            text="✅ Verify Key",
            size_hint=(1, None),
            height=100,
            background_color=(0,1,0,1),  # Lime Green
            color=(1,1,1,1)
        )
        key_button.bind(on_press=self.check_key)
        content.add_widget(self.key_input)
        content.add_widget(key_button)
        self.popup = Popup(
            title="Enter Licence Key",
            content=content,
            size_hint=(0.8,0.35),
            auto_dismiss=False,
            title_color=(1,1,1,1)
        )
        self.popup.open()

    def check_key(self, instance):
        key = self.key_input.text.strip()
        if not key:
            self.show_error("❌ Please enter a key")
            return
        result = verify_key_with_server(key)
        if result.get("status") == "ok":
            self.show_error("✅ Key verified! You can now use the app.")
            set_verified()
            self.key_verified = True
            self.popup.dismiss()
            self.build_main_interface()
        else:
            self.show_error(f"❌ Key rejected: {result.get('message')}")

    def show_error(self, message):
        if hasattr(self, "output"):
            self.output.text = message
        else:
            popup = Popup(title="Notice", content=Label(text=message), size_hint=(0.6,0.3))
            popup.open()

    def build_main_interface(self):
        button_row = BoxLayout(size_hint=(1, None), height=80, spacing=12)
        self.generate_button = Button(
            text='📈 Generate Signals',
            font_size=20,
            background_normal='',
            background_color=(0.1,0.3,0.6,1),
            color=(1,1,1,1)
        )
        self.generate_button.bind(on_press=self.generate_signals_thread)
        button_row.add_widget(self.generate_button)

        self.copy_button = Button(
            text='📋 Copy',
            font_size=20,
            background_normal='',
            background_color=(0.2,0.5,0.2,1),
            color=(1,1,1,1)
        )
        self.copy_button.bind(on_press=self.copy_to_clipboard)
        button_row.add_widget(self.copy_button)

        self.root_layout.add_widget(button_row)

        self.output = TextInput(
            text='',
            readonly=True,
            font_size=18,
            size_hint_y=1,
            background_normal='',
            background_color=(0.08,0.08,0.08,1),
            foreground_color=(1,1,1,1)
        )
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.output)
        scroll.size_hint_y = 0.9
        self.root_layout.add_widget(scroll)

    def generate_signals_thread(self, instance):
        self.wait_popup = Popup(
            title="Please wait...",
            content=Label(text="Generating Signals..."),
            size_hint=(0.6,0.3),
            auto_dismiss=False
        )
        self.wait_popup.open()
        Thread(target=self.generate_signals).start()

    def generate_signals(self):
        try:
            all_signals = []
            max_iterations = 200
            iteration = 0

            while len(all_signals) < 8 and iteration < max_iterations:
                fetched = fetch_signals_from_site()  # تستخدم MIN_CONFIDENCE من core.py
                new_signals = 0
                for s in fetched:
                    # التأكد أن الثقة >= MIN_CONFIDENCE
                    if float(s.get("confidence",0)) < MIN_CONFIDENCE:
                        continue

                    # تحويل التوقيت من +6 إلى -3
                    time_obj = datetime.strptime(s['time'], "%H:%M")
                    adjusted_time = (time_obj - timedelta(hours=9)).strftime("%H:%M")  # +6 -> -3 = -9 ساعات
                    s['time'] = adjusted_time
                    # منع تكرار نفس التوقيت
                    if not any(sig["time"] == s["time"] for sig in all_signals):
                        all_signals.append(s)
                        new_signals += 1
                iteration += 1
                if new_signals == 0:
                    continue

            # ترتيب الصفقات حسب الوقت
            all_signals.sort(key=lambda x: datetime.strptime(x['time'], "%H:%M"))

            formatted_signals = [f"  M1;{s['pair']};{s['time']};{s['action']}" for s in all_signals]

            header = f"""🌟✧══❂✦ FUTURE SIGNALS BY KHALED DZ TRADER ✦❂══✧🌟

📆 Date {datetime.now().strftime("%d/%m/%Y")}
⏰ UTC -3:00
🚧 1 MTG IF LOSS
⏳ Expiry: 1 Minute

⚠️Avoid:
Doji , Round 00 , Momentum .

Generated Signals:

✧═════════❂═════════✧
"""
            footer = """✧═════════❂═════════✧

🔮Quotex Broker🔮

🌟═ @KhaLedDzTraderSupport ═🌟"""

            full_text = header + "\n".join(formatted_signals) + "\n" + footer

            Clock.schedule_once(lambda dt: self.display_signals(full_text), 0)

        except Exception as e:
            Clock.schedule_once(lambda dt: self.display_signals(f"❌ خطأ أثناء جلب الإشارات:\n{e}"), 0)

    def display_signals(self, text):
        self.output.text = text
        if hasattr(self, "wait_popup") and self.wait_popup:
            self.wait_popup.dismiss()

    def copy_to_clipboard(self, instance):
        Clipboard.copy(self.output.text)
        self.output.text += "\n✅ Copied!"

if __name__ == '__main__':
    SignalApp().run()