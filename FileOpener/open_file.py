import sublime
import sublime_plugin
import os
import json
import subprocess

class Command:

	def __init__(self, command, executable_command = ""):
		self.command = command
		self.executable_command = executable_command
		self.is_executable = (executable_command != "")

	def execute_command(self, abs_path):
		directory = os.path.split(abs_path)[0]
		directory += "/"

		filename = os.path.split(abs_path)[1]

		parse_dict = {
			"<file_name>": filename,
			"<dir>": directory,
			"<abs>": os.path.join(directory, filename)
		}

		command = self.format(self.command, parse_dict)
		os.system(command)
		
		if self.is_executable:
			executable_command = self.format(self.executable_command, parse_dict)
			terminal_args = executable_command.split(" ")
			output = subprocess.Popen(terminal_args, stdout=subprocess.PIPE).communicate()[0]
			print(output)
			os.system(executable_command)

	def format(self, base, parse_dict):
		for key in parse_dict:
			base = base.replace(key, parse_dict[key])
		return base


class ExtensionOpener:

	def __init__(self, command_file):
		self.commands = {}

		packages = sublime.packages_path()
		package = os.path.join(packages, "FileOpener")
		command_file = os.path.join(package, command_file)

		file = open(command_file, "r")
		data = file.read()
		command_list = json.loads(data)

		for command in command_list:
			executable = ""
			if "executable_command" in command:
				executable = command["executable_command"]

			cmd = Command(command["command"], executable)
			self.commands[command["extension"]] = cmd



	def execute_command(self, extension, abs_path):
		if extension not in self.commands:
			print("{} extension not found!".format(extension))
			return
		command = self.commands[extension]
		command.execute_command(abs_path)




class OpenFileCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		self.extensions = ExtensionOpener("commands.txt")
		path = self.view.file_name()
		filename = os.path.split(path)[1];
		extension = filename.split(".")[1];
		self.extensions.execute_command(extension, path)

