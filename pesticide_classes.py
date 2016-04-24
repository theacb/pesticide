import os


class FileName:
    def __init__(self, name, directory):
        self.name = name
        self.directory = directory

        self.bad_nodes = []
        self.student_file_status = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return os.path.join(self.directory, self.name)

    def get_name(self):
        return self.name

    def get_directory(self):
        return self.directory

    def get_path(self):
        return os.path.join(self.directory, self.name)

    def get_bad_nodes(self):
        return self.bad_nodes

    def get_student_file_status(self):
        return self.student_file_status

    def append_bad_node(self, node):
        self.bad_nodes.append(node)

    def set_student_file_status(self, b):
        self.student_file_status = b