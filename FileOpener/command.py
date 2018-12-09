import os
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


	def __execute_output_command(self, command, cwd):
		terminal_args = command.split(" ")

		print(terminal_args)
		stdin = self.get_stdin_file_from_args(terminal_args, cwd)
		if stdin is None:
			stdin = subprocess.PIPE

		output = subprocess.Popen(
			terminal_args,
			cwd=cwd,
			stdin=stdin,
			stdout=subprocess.PIPE
		).communicate()[0]

		if stdin is not subprocess.PIPE:
			stdin.close()

		self.output = output.decode("utf-8")
		print("self.output:", self.output)



	def get_stdin_file_from_args(self, terminal_args, cwd):
		if "<" not in terminal_args:
			return None

		stdin_index = terminal_args.index("<")

		file_path = terminal_args[stdin_index + 1]
		if not os.path.isabs(file_path):
			file_path = os.path.join(cwd, file_path)

		try:
			return open(file_path)
		except FileNotFoundError:
			return None

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