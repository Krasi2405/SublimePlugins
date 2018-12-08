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

			

	def execute(self, file_path, execution_command="", output_command=""):
		work_dir = os.path.split(file_path)[0]

		print("Work dir: ", work_dir)

		if self.execution_command_template:
			command = ""
			if execution_command:
				command = execution_command
			else:
				command = self.get_execute_command(file_path)


			print("Execute: ", command)
			self.__execute_command(command, work_dir)

		if self.output_command_template:
			command = ""
			if output_command:
				command = output_command
			else:
				command = self.get_output_command(file_path)
			print("Output: ", command)
			self.__execute_output_command(command, work_dir)


	def get_output_command(self, abs_path):
		return self.__format_command(self.output_command_template, abs_path)


	def get_execute_command(self, abs_path):
		return self.__format_command(self.execution_command_template, abs_path)


	def __execute_output_command(self, command, cwd=None):
		terminal_args = command.split(" ")

		print(terminal_args)
		print("cwd: ", cwd)
		output = subprocess.Popen(
			terminal_args, 
			cwd=cwd, 
			stdout=subprocess.PIPE
		).communicate()[0]

		self.output = output.decode("utf-8")


	def get_output(self):
		return self.output



	def __execute_command(self, command, cwd=None):
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


class OpenFilePromptCommand(sublime_plugin.WindowCommand):
	extensions = ExtensionManager("commands.json")

	def run(self):

		path = self.window.active_view().file_name()
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
