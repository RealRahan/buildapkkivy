import requests
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.core.text import LabelBase
from kivy.clock import Clock

# Register the emoji font (replace 'NotoColorEmoji.ttf' with your emoji font file)
LabelBase.register(name='EmojiFont', fn_regular='NotoColorEmoji.ttf')  # Replace with your emoji font file

# Country codes (INCOMPLETE - ADD MORE)
country_english_names = {
    "AF": {"name": "Afghanistan", "emoji": "🇦🇫"},
    "AX": {"name": "Åland Islands", "emoji": "🇦🇽"},
    "AL": {"name": "Albania", "emoji": "🇦🇱"},
    "DZ": {"name": "Algeria", "emoji": "🇩🇿"},
    "US": {"name": "United States", "emoji": "🇺🇸"},
    "GB": {"name": "United Kingdom", "emoji": "🇬🇧"},
    "CA": {"name": "Canada", "emoji": "🇨🇦"},
    "DE": {"name": "Germany", "emoji": "🇩🇪"},
    "FR": {"name": "France", "emoji": "🇫🇷"},
    # ... Add the rest of the countries!  A full list is available online.
}

def get_country_info(country_code):
    """Get the English name and emoji of the country from the country code."""
    return country_english_names.get(country_code, {"name": "Unknown", "emoji": "🌍"})


class TikTokUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=60, spacing=60, **kwargs)

        self.main_layout = BoxLayout(orientation='vertical', size_hint=(None, None),
                                     pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.main_layout)

        # Username input
        self.username_input = TextInput(
            hint_text='Enter TikTok username',
            size_hint=(1, None),
            height=150,
            font_size=50,
            multiline=False,
            padding_y=[30, 30],
            halign='left',
            background_color=(0.12, 0.12, 0.12),  # Dark gray in RGB
            foreground_color=(1, 1, 1),  # White in RGB
            hint_text_color=(0.5, 0.5, 0.5),  # Gray in RGB
            font_name='EmojiFont'  # Use emoji font
        )
        self.main_layout.add_widget(self.username_input)

        # Checkbox for saving profile picture
        self.save_pfp_checkbox = CheckBox(size_hint=(1, None), height=100)
        self.main_layout.add_widget(Label(
            text='Do you want to save the profile picture?',
            size_hint=(1, None),
            height=100,
            font_size=50,
            color=(1, 1, 1),  # White in RGB
            font_name='EmojiFont'  # Use emoji font
        ))
        self.main_layout.add_widget(self.save_pfp_checkbox)

        # Button to fetch info
        self.fetch_button = Button(
            text='Get Info',
            size_hint=(0.8, None),
            height=150,
            font_size=50,
            background_color=(0.26, 0.26, 0.26),  # Slightly lighter gray in RGB
            color=(1, 1, 1),  # White
            pos_hint={'center_x': 0.5},
            font_name='EmojiFont'  # Use emoji font
        )
        self.fetch_button.bind(on_press=self.animate_and_fetch)
        self.main_layout.add_widget(self.fetch_button)

        # Output label
        self.output_label = Label(
            size_hint_y=None,
            markup=True,
            font_size=50,
            halign='left',
            valign='top',
            color=(1, 1, 1),  # White
            text_size=(None, None),
            font_name='EmojiFont'  # Use emoji font
        )
        self.output_label.bind(
            width=lambda *x: self.output_label.setter('text_size')(self.output_label, (self.output_label.width, None)),
            texture_size=self.update_label_height
        )
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.scroll_view.add_widget(self.output_label)
        self.main_layout.add_widget(self.scroll_view)

        Window.bind(size=self.on_window_resize)
        Clock.schedule_once(self.set_initial_size, 0)

    def set_initial_size(self, dt):
       self.on_window_resize(Window, Window.size)

    def on_window_resize(self, window, size):
        self.main_layout.size = (size[0] * 0.8, size[1] * 0.8)

    def update_label_height(self, instance, texture_size):
        instance.height = texture_size[1]
        self.scroll_view.scroll_y = 1

    def animate_and_fetch(self, instance):
        original_font_size = instance.font_size

        def restore_font_size(*args):
            instance.font_size = original_font_size

        animation = Animation(font_size=original_font_size * 0.9, duration=0.1)  # Smaller text
        animation += Animation(font_size=original_font_size, duration=0.1)  # Original size

        animation.bind(on_complete=lambda *args: self.fetch_info(instance))
        animation.bind(on_complete=restore_font_size)
        animation.start(instance)

    def fetch_info(self, instance):
        username = self.username_input.text
        save_pfp = self.save_pfp_checkbox.active

        self.output_label.text = "Loading..."
        Clock.schedule_once(lambda dt: self._fetch_and_process(username, save_pfp), 0)

    def _fetch_and_process(self, username, save_pfp, *args):
        try:
            user_data = fetch_tiktok_data(username)  # Defined in Part 3
            if user_data:
                output_text = process_tiktok_data(user_data, save_pfp)  # Defined in Part 3
                self.output_label.text = output_text
                self.scroll_view.scroll_y = 1
            else:
                self.output_label.text = "Could not retrieve data. Check username or network."
        except Exception as e:
            self.output_label.text = f"An error occurred: {e}"


def fetch_tiktok_data(username):
    url = f"https://www.tiktok.com/@{username}"  # Very fragile!
    headers = {  # Mimic a browser
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors

        # Extract JSON data (VERY FRAGILE - TikTok's API changes)
        start_tag = '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
        end_tag = '</script>'
        start_index = response.text.find(start_tag) + len(start_tag)
        end_index = response.text.find(end_tag, start_index)
        json_data = response.text[start_index:end_index]

        data = json.loads(json_data)
        return data
    except (requests.exceptions.RequestException, json.JSONDecodeError, TypeError) as e:
        print(f"Error fetching/parsing: {e}")  # Print for debugging
        return None  # Indicate failure


def process_tiktok_data(data, save_pfp):
    try:
        user_info = data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]
        output_text = ""

        # Core user information (WITHOUT REPETITION)
        output_text += (
            f"Username: {user_info['user']['uniqueId']}\n\n"
            f"Nickname: {user_info['user']['nickname']}\n\n"
            f"ID: {user_info['user']['id']}\n\n"
            f"Followers: {user_info['stats']['followerCount']}\n\n"
            f"Following: {user_info['stats']['followingCount']}\n\n"
            f"Likes: {user_info['stats']['heartCount']}\n\n"
            f"Videos: {user_info['stats']['videoCount']}\n\n"
            f"Bio: {user_info['user']['signature']}\n\n"
        )
        country_code = user_info.get('user', {}).get('region')  # Handle missing data
        country_info = get_country_info(country_code)
        output_text += f"Country: {country_info['name']} {country_info['emoji']}\n"


        if save_pfp:
            pfp_url = user_info['user']['avatarLarger']
            pfp_filename = f"{user_info['user']['uniqueId']}_profile_pic.jpg"
            try:
                with open(pfp_filename, "wb") as f:
                    f.write(requests.get(pfp_url).content)
                output_text += f"Profile picture saved as {pfp_filename}\n"
            except requests.exceptions.RequestException as e:
                output_text += f"Error saving profile picture: {e}\n"

        return output_text

    except (KeyError, TypeError) as e:  # Handle missing data
        return f"Error processing data: {e}.  Likely invalid username or data format."