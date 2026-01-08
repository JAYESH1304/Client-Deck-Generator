import os


class LocalProposalConnector:
    def __init__(self, base_folder="./Auxo Proposals"):
        self.base_folder = base_folder

        # Ensure base proposals folder exists
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
            print(f"Created base folder: {self.base_folder}")

    def list_clients(self):
        """List all client folders inside proposals"""
        return [
            d for d in os.listdir(self.base_folder)
            if os.path.isdir(os.path.join(self.base_folder, d))
        ]

    def list_files(self, client_name):
        """List all proposal files for a specific client"""
        client_folder = os.path.join(self.base_folder, client_name)
        if not os.path.exists(client_folder):
            raise FileNotFoundError(f"Client folder {client_name} does not exist.")

        return [
            f for f in os.listdir(client_folder)
            if os.path.isfile(os.path.join(client_folder, f))
        ]

    def read_file(self, client_name, file_name):
        """Read contents of a text file proposal"""
        file_path = os.path.join(self.base_folder, client_name, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_name} not found in {client_name}")

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def save_file(self, client_name, file_name, content):
        """Save new proposal under the client folder"""
        client_folder = os.path.join(self.base_folder, client_name)
        if not os.path.exists(client_folder):
            os.makedirs(client_folder)

        file_path = os.path.join(client_folder, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path
