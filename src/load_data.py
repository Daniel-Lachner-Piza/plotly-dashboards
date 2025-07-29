import os
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict

class DataLoader:
    def __init__(self, data_path:Path, extension:str='.csv'):
        self.data_path = data_path
        self.files_ls = []
        self.file_extension = ''
    
    def get_files_in_folder(self):
        self.files_ls = [fn for fn in self.data_path.glob(f"*{self.file_extension}")]
        # Check if any files were found
        assert len(self.files_ls)>0, f"No {self.file_extension} files in folder {self.data_path}"

    def load_data(self) -> pd.DataFrame:
        """
        Load data from a file and return it as a dictionary.
        Parameters:
        file_path (Path): Path to the file to be loaded.
        Returns:
        pd.DataFrame: Loaded data.
        """
        all_pats_data_df = pd.DataFrame()
        for file_path in self.files_ls:
            assert os.path.exists(file_path), f"File {file_path} does not exist."
            df = pd.read_csv(file_path)
            assert df.PatID.nunique() == 1, f"File {file_path} contains multiple unique PatIDs."
            if "PAT" in df.PatID.unique()[0]:
                df['Group'] = "Pediatric"
            else:
                df['Group'] = "Adult"
            all_pats_data_df = pd.concat([all_pats_data_df, df], ignore_index=True)
            pass
        # Check if the DataFrame is empty
        assert not all_pats_data_df.empty, f"DataFrame is empty after loading files from {self.data_path}"
    
        return all_pats_data_df

if __name__ == "__main__":
    data_path = Path("/home/dlp/Development/Data/Stage_Spike_Occurrence_Rate")
    data_loader = DataLoader(data_path=data_path, extension='.csv')
    data_loader.get_files_in_folder()
    data = data_loader.load_data()