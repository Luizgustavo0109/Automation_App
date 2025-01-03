import unittest
from unittest.mock import MagicMock, patch, mock_open
from main import AutomationApp, BUTTONS_FILE
import os
import json
import tempfile

class TestAutomationApp(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing loading and saving
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file.close()  # Close the file so it can be used by the test
        BUTTONS_FILE = self.test_file.name

        # Mock the tkinter window
        self.mock_root = MagicMock()
        self.app = AutomationApp(self.mock_root)

    def tearDown(self):
        # Clean up the temporary file after tests
        if os.path.exists(self.test_file.name):
            os.remove(self.test_file.name)

    @patch("builtins.open", new_callable=mock_open, read_data='{"TestApp": "test_path"}')
    @patch("os.path.exists", return_value=True)
    def test_load_buttons(self, mock_exists, mock_open_file):
        # Test loading saved buttons
        self.app.load_buttons()
        self.assertIn("TestApp", self.app.buttons)
        self.assertEqual(self.app.buttons["TestApp"], "test_path")

        mock_open_file.assert_called_once_with(self.test_file.name, "r")
        mock_open_file().read.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    def test_save_buttons(self, mock_open_file):
        # Test saving buttons to JSON file
        self.app.buttons = {"TestApp": "test_path"}
        self.app.save_buttons()
        mock_open_file.assert_called_once_with(self.test_file.name, "w")
        mock_open_file().write.assert_called_once_with('{"TestApp": "test_path"}')

    def test_create_custom_button(self):
        # Test creating a custom button
        self.app.create_custom_button("TestApp", "test_path")
        buttons = self.app.custom_buttons_frame.winfo_children()
        self.assertEqual(len(buttons), 1)
        button = buttons[0].winfo_children()[0]

        
        button.cget = MagicMock(return_value="TestApp")
        self.assertEqual(button.cget("text"), "TestApp")
        self.assertTrue(button.winfo_exists())  

    @patch("subprocess.Popen")
    def test_open_application(self, mock_popen):
        
        self.app.open_application("test_path")
        mock_popen.assert_called_once_with("test_path")

    @patch("subprocess.Popen")
    def test_open_application_error(self, mock_popen):
        
        mock_popen.side_effect = OSError("Error opening application")
        with self.assertRaises(OSError):
            self.app.open_application("test_path")

    @patch("tkinter.messagebox.showinfo")
    def test_remove_selected_button(self, mock_messagebox):
        
        self.app.buttons = {"TestApp": "test_path"}
        mock_button = MagicMock()
        mock_button.cget.return_value = "TestApp"
        self.app.selected_button = mock_button

        self.app.remove_selected_button()
        self.assertNotIn("TestApp", self.app.buttons)
        mock_messagebox.assert_called_once_with("Success", "The button 'TestApp' has been removed.")

    @patch("tkinter.messagebox.showinfo")
    def test_remove_all_buttons(self, mock_messagebox):
        # Test removing all buttons
        self.app.buttons = {"App1": "path1", "App2": "path2"}
        self.app.remove_all_buttons()
        self.assertEqual(len(self.app.buttons), 0)
        mock_messagebox.assert_not_called()

    @patch("tkinter.filedialog.askopenfilename", return_value="test_path")
    @patch("tkinter.simpledialog.askstring", return_value="TestApp")
    @patch("automation_app.AutomationApp.save_buttons")
    def test_add_application(self, mock_save_buttons, mock_askstring, mock_filedialog):
        # Test adding an application
        self.app.add_application()
        self.assertIn("TestApp", self.app.buttons)
        self.assertEqual(self.app.buttons["TestApp"], "test_path")
        mock_save_buttons.assert_called_once()

    @patch("tkinter.filedialog.askopenfilename", return_value="")
    def test_add_application_cancelled(self, mock_filedialog):
        # Test behavior when file dialog is cancelled
        self.app.add_application()
        self.assertNotIn("TestApp", self.app.buttons)  # The button should not be added

    @patch("webbrowser.open")
    def test_open_youtube(self, mock_webbrowser):
        # Test opening YouTube
        self.app.open_youtube()
        mock_webbrowser.assert_called_once_with("https://www.youtube.com")

    @patch("webbrowser.open")
    def test_open_chatgpt(self, mock_webbrowser):
        # Test opening ChatGPT
        self.app.open_chatgpt()
        mock_webbrowser.assert_called_once_with("https://chat.openai.com")

    @patch("os.path.exists", return_value=False)
    def test_load_buttons_not_found(self, mock_exists):
        # Test loading buttons when file is not found
        self.app.load_buttons()
        self.assertEqual(self.app.buttons, {})  

    @patch("builtins.open", side_effect=IOError("File cannot be read"))
    @patch("os.path.exists", return_value=True)
    def test_load_buttons_file_error(self, mock_exists, mock_open_file):
        
        self.app.load_buttons()
        self.assertEqual(self.app.buttons, {})

        mock_open_file.assert_called_once_with(self.test_file.name, "r")
        mock_open_file().read.assert_called_once()

        mock_exists.assert_called_once_with(self.test_file.name)

    @patch("builtins.open", new_callable=mock_open, read_data='{"TestApp": "test_path"}')
    def test_save_buttons_structure(self, mock_open_file):
       
        self.app.buttons = {"TestApp": "test_path"}
        self.app.save_buttons()

        
        mock_open_file.assert_called_once_with(self.test_file.name, "w")
        saved_data = json.loads(mock_open_file().read())
        self.assertTrue(isinstance(saved_data, dict))
        self.assertIn("TestApp", saved_data)

    def test_no_buttons(self):
        
        self.app.buttons = {}
        self.app.load_buttons()
        self.assertEqual(self.app.buttons, {})  

    @patch("tkinter.messagebox.askyesno", return_value=True)
    def test_remove_selected_button_confirmation(self, mock_askyesno):
        # Test removing selected button with confirmation
        self.app.buttons = {"TestApp": "test_path"}
        self.app.selected_button = MagicMock(cget="TestApp")

        self.app.remove_selected_button()
        self.assertNotIn("TestApp", self.app.buttons)
        mock_askyesno.assert_called_once_with("Confirmation", "Do you want to remove the button 'TestApp'?")

    def test_save_buttons_structure(self):
        # Test the structure of saved data
        self.app.buttons = {"TestApp": "test_path"}
        self.app.save_buttons()
        saved_data = json.loads(open(self.test_file.name).read())
        self.assertTrue(isinstance(saved_data, dict))
        self.assertIn("TestApp", saved_data)


if __name__ == "__main__":
    unittest.main()