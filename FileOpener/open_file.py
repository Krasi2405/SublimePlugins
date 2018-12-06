import sublime
import sublime_plugin
import os
import json
import subprocess

class Command:

	def __init__(self, execution_command="", output_command="", requires_args=False):
		# Used either for one off actions or for compiling
		self.execution_command_template = execution_command 

		# Used for terminal output
		self.output_command_template = output_command

		# Whether player is allowed to put in args.
		self.requires_args = requires_args

			

	def execute(self, file_path):
		work_dir = os.path.split(file_path)[0]

		self.__execute_command(file_path, work_dir)
		self.__execute_output_command(file_path, work_dir)


	def get_output_command(self, abs_path):
		return self.__format_command(self.output_command_template, abs_path)


	def get_execute_command(self, abs_path):

		return self.__format_command(self.execution_command_template, abs_path)


	def __execute_output_command(self, command, cwd=None):
		pass
		# command = self.get_command(command)
		# output_command = self.format(self.output_command)
		# terminal_args = output_command.split(" ")
		# if args:
		# 	args = self.format(args, abs_path)
		# 	args = args.split(" ")
		# 	terminal_args += args

		# print(terminal_args)
		# output = subprocess.Popen(
		# 	terminal_args, 
		# 	cwd=os.path.split(abs_path)[0], 
		# 	stdout=subprocess.PIPE
		# ).communicate()[0]

		# print(output)




	def __execute_command(self, command, cwd=None):
		# Format the command using template if not formatted already
		command = self.get_execute_command(command)

		print(command)
		sublime_dir = os.getcwd()
		if cwd is not None:
			os.chdir(cwd)

		os.system(command)

		if cwd is not None:
			os.chdir(sublime_dir)


	def __format(self, template, abs_path):
		directory = os.path.split(abs_path)[0]
		directory += "/"
		filename = os.path.split(abs_path)[1]


		print(filename)

		parse_dict = {
			"<filename>": filename,
			"<dir>": directory,
			"<abs>": os.path.join(directory, filename)
		}


		for key in parse_dict:
			template = template.replace(key, parse_dict[key])

		return template


	def __format_command(self, command_template, abs_path):
		if command_template:
			return self.__format(command_template, abs_path)
		else:
			return None


	
		


class ExtensionManager:

	def __init__(self, command_file):
		self.__load_commands(command_file)


	def execute_command(self, extension, execute_path):
		if extension not in self.commands:
			print("{} extension not found!".format(extension))
			return
		command = self.commands[extension]
		command.execute(execute_path)


	def requires_args(self, extension):
		if extension not in self.commands:
			print("{} extension not found!".format(extension))
			return
		return self.commands[extension].requires_args


	def get_command(self, extension, abs_path):
		cmd = self.commands[extension]
		return cmd.get_command_string(abs_path);
			

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
		requires_args = self.__load_json_property(command_dict, "requires_args", False)

		command = Command(execute_command, output_command, requires_args)
		self.commands[command_dict["extension"]] = command


	def __load_json_property(self, json_dict, key, default=None):
		value = default
		if key in json_dict:
			value = json_dict[key]
		return value




	




# Deprecated
class OpenFileCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		self.extensions = ExtensionManager("commands.txt")
		path = self.view.file_name()
		filename = os.path.split(path)[1];
		extension = filename.split(".")[1];
		self.extensions.execute_command(extension, path)




class OpenFilePromptCommand(sublime_plugin.WindowCommand):
	extensions = ExtensionManager("commands.json")

	def run(self):

		path = self.window.active_view().file_name()
		filename = os.path.split(path)[1];
		extension = filename.split(".")[1];

		
		# if self.extensions.requires_args(extension):
		# 	self.curr_path = path
		# 	self.curr_extension = extension

		# 	command_string = self.extensions.get_command(extension, path)
		# 	self.window.show_input_panel("Arguments:", command_string, self.on_done, None, None)

		self.extensions.execute_command(extension, path)
		
		#terminal = subprocess.Popen(["ls"], shell=True, cwd=os.path.split(path)[0], stdout=subprocess.PIPE);

	def on_done(self, text):
		try:
			if self.window.active_view():
				print("Give txt", text)
				self.extensions.execute_command(self.curr_extension, self.curr_path, text)
		except ValueError:
			pass
