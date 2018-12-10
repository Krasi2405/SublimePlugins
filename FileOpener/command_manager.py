import sublime
import json
import os

from .command import *


class CommandManager:

	def __init__(self, command_file):
		self.__load_commands(command_file)


	def execute_command(self, extension, execute_path, execution_command="", output_command=""):
		if extension not in self.commands:
			print("{} extension not found!".format(extension))
			return

		command = self.commands[extension]
		command.execute(execute_path, execution_command, output_command)

		return command.get_output()


	def requires_args(self, extension):
		if extension not in self.commands:
			print("{} extension not found!".format(extension))
			return
		return self.commands[extension].requires_args


	def get_output_command(self, extension, abs_path):
		cmd = self.commands[extension]
		return cmd.get_output_command(abs_path);


	def __load_commands(self, file_name):
		self.commands = {}

		package_path = os.path.join(sublime.packages_path(), "FileOpener")
		file_path = os.path.join(package_path, file_name)

		file = open(file_path, "r")
		data = file.read()
		command_list = json.loads(data)

		for command in command_list:
			self.__load_command(command)


	def __load_command(self, command_dict):
		execute_command = self.__load_json_property(command_dict, "execute_command", "")
		output_command = self.__load_json_property(command_dict, "output_command", "")
		requires_args = self.__load_json_property(command_dict, "args_support", False)

		command = Command(execute_command, output_command, requires_args)
		self.commands[command_dict["extension"]] = command


	def __load_json_property(self, json_dict, key, default=None):
		value = default
		if key in json_dict:
			value = json_dict[key]
		return value