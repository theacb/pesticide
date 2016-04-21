import os


class FileName:
    def __init__(self, name, directory):
        self.name = name
        self.directory = directory

    def get_name(self):
        return self.name

    def get_directory(self):
        return self.directory

    def get_path(self):
        return os.path.join(self.directory, self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return os.path.join(self.directory, self.name)
