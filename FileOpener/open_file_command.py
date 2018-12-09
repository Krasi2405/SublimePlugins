import sublime
import sublime_plugin
import os
import platform

from .command_manager import *


class OpenFilePromptCommand(sublime_plugin.WindowCommand):

	is_initialized = False

	def __init__(self, window):
		super().__init__(window)

		commands_file_name = ""
		if platform.system() == "Windows":
			commands_file_name = "commands_windows.json"
		elif platform.system() == "Linux":
			commands_file_name = "commands_linux.json"
		elif platform.system() == "Darwin":
			commands_file_name = "commands_linux.json" # Hope that mac works the same way Linux does
		else:
			raise SystemError("OS not recognized!")
		self.extensions = CommandManager(commands_file_name)

	def run(self):
		path = self.window.active_view().file_name()
		path = path.replace("\\", "\\\\") # Do for windows

		filename = os.path.split(path)[1];
		extension = ""
		try:
			extension = filename.split(".")[1];
		except:
			extension = filename


		if self.extensions.requires_args(extension):
		 	self.curr_path = path
		 	self.curr_extension = extension

		 	command_string = self.extensions.get_output_command(extension, path)
		 	self.window.show_input_panel("Arguments:", command_string, self.on_done, None, None)
		else:
			self.extensions.execute_command(extension, path)

		
	def on_done(self, text):
		try:
			if self.window.active_view():

				output = self.extensions.execute_command(
					self.curr_extension, 
					self.curr_path,
					output_command=text
				)
				
				self.window.run_command("show_output", {"output": output} )
		except ValueError:
			pass


class WriteToViewCommand(sublime_plugin.TextCommand):

	def run(self, edit, input):
		self.view.insert(edit, 0, input)



class ShowOutputCommand(sublime_plugin.WindowCommand):
	def run(self, output):
		output_panel = self.window.create_output_panel("panelche")
		self.window.run_command("show_panel", {"panel": "output.panelche"})
		output_panel.run_command("write_to_view", {"input": output})
