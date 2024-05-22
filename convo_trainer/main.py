import json
from kivymd.app import MDApp
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField


# Load the conversation data from the JSON file
with open("conversations.json") as f:
    conversation_data = json.load(f)


class ConversationApp(MDApp):
    current_conversation = ObjectProperty(None)
    current_speaker = ObjectProperty(None)
    current_line = StringProperty("")
    speaker_options = ObjectProperty(None)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"  # "Purple", "Red"
        # Set window size
        # self.window.size = (800, 600)

        # Create the main layout
        main_layout = MDBoxLayout(orientation="vertical")

        # Conversation selection section
        conversation_dropdown_items = []
        for conversation in conversation_data["conversations"]:
            conversation_dropdown_items.append(
                {
                    "viewclass": "MDMenuItem",
                    "text": conversation["context"],
                    "on_release": lambda x, y: self.select_conversation(y.text),
                }
            )
        self.conversation_dropdown = MDDropdownMenu(
            items=conversation_dropdown_items, width_mult=4
        )

        conversation_selection_box = MDBoxLayout(orientation="horizontal", padding=20)

        self.conversation_selection_button = MDRaisedButton(
            text="Select Conversation:",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        conversation_selection_box.add_widget(self.conversation_selection_button)

        self.conversation_dropdown.caller = self.conversation_selection_button
        self.conversation_selection_button.bind(
            on_release=self.conversation_dropdown.open
        )

        conversation_selection_label = MDLabel(
            text="Select Conversation:", size_hint=(0.3, 1)
        )
        conversation_selection_box.add_widget(conversation_selection_label)

        main_layout.add_widget(conversation_selection_box)

        # Conversation information section
        conversation_info_box = MDBoxLayout(orientation="horizontal")

        current_speaker_label = MDLabel(text="Current Speaker:", size_hint=(0.3, 1))
        conversation_info_box.add_widget(current_speaker_label)

        self.current_line_label = MDLabel(text="", size_hint=(0.7, 1))
        conversation_info_box.add_widget(self.current_line_label)

        main_layout.add_widget(conversation_info_box)

        # Conversation control section
        conversation_control_box = MDBoxLayout(orientation="horizontal")

        self.previous_button = MDFlatButton(
            text="Previous", disabled=True, on_press=self.previous_line
        )
        conversation_control_box.add_widget(self.previous_button)

        self.next_button = MDRaisedButton(text="Next", on_press=self.next_line)
        conversation_control_box.add_widget(self.next_button)

        main_layout.add_widget(conversation_control_box)

        # Speaker selection section
        speaker_selection_box = MDBoxLayout(orientation="horizontal", padding=20)

        speaker_selection_label = MDLabel(text="Select Speaker:", size_hint=(0.3, 1))
        speaker_selection_box.add_widget(speaker_selection_label)

        self.speaker_dropdown = MDDropdownMenu()
        speaker_selection_box.add_widget(self.speaker_dropdown)

        main_layout.add_widget(speaker_selection_box)

        # User input section
        user_input_box = MDBoxLayout(orientation="horizontal", padding=20)

        user_input_label = MDLabel(text="Your Line:", size_hint=(0.3, 1))
        user_input_box.add_widget(user_input_label)

        self.user_input_field = MDTextField(multiline=True)
        user_input_box.add_widget(self.user_input_field)

        main_layout.add_widget(user_input_box)

        return main_layout

    def select_conversation(self, instance):  # Called when a conversation is selected
        self.current_conversation = instance.text
        self.update_conversation()

    def update_conversation(
        self, instance=None
    ):  # Update UI elements based on selected conversation
        self.current_speaker = None  # Reset current speaker
        self.current_line = ""  # Reset current line
        self.previous_line_button.disabled = True  # Disable previous button initially
        self.next_line_button.disabled = False  # Enable next button

        # Clear speaker dropdown options
        self.speaker_dropdown.clear()

        if self.current_conversation:
            # Find the selected conversation data
            for conversation in conversation_data["conversations"]:
                if conversation["context"] == self.current_conversation:
                    self.speaker_options = conversation["dialogue"]
                    break

            # Populate speaker dropdown options
            for speaker_data in self.speaker_options:
                self.speaker_dropdown.add_widget(
                    Button(text=speaker_data["speaker"], on_press=self.select_speaker)
                )

    def select_speaker(self, instance):  # Called when a speaker is selected
        self.current_speaker = instance.text
        self.current_line = ""  # Reset current line
        self.previous_line_button.disabled = True  # Disable previous button initially
        self.next_line_button.disabled = False  # Enable next button

    def previous_line(self, instance):  # Go to the previous line in the conversation
        if self.current_conversation and self.speaker_options:
            current_line_index = 0
            for i, speaker_data in enumerate(self.speaker_options):
                if speaker_data["speaker"] == self.current_speaker:
                    current_line_index = i
                    break

            if current_line_index > 0:
                self.current_speaker = self.speaker_options[current_line_index - 1][
                    "speaker"
                ]
                self.current_line = self.speaker_options[current_line_index - 1]["line"]
                self.next_line_button.disabled = False
                if current_line_index == 1:
                    self.previous_line_button.disabled = True

    def next_line(self, instance):  # Go to the next line in the conversation
        if self.current_conversation and self.speaker_options:
            current_line_index = 0
            for i, speaker_data in enumerate(self.speaker_options):
                if speaker_data["speaker"] == self.current_speaker:
                    current_line_index = i
                    break

            if current_line_index < len(self.speaker_options) - 1:
                self.current_speaker = self.speaker_options[current_line_index + 1][
                    "speaker"
                ]
                self.current_line = self.speaker_options[current_line_index + 1]["line"]
                self.previous_line_button.disabled = False
                if current_line_index == len(self.speaker_options) - 2:
                    self.next_line_button.disabled = True


if __name__ == "__main__":
    ConversationApp().run()
