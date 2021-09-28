from abc import ABC, abstractmethod

try:
    from icecube import dataio  # pyright: reportMissingImports=false
except ImportError:
    print("icecube package not available.")

from .i3extractor import I3Extractor, load_geospatial_data
from .utils import find_i3_files


class DataConverter(ABC):
    """Abstract base class for specialised (SQLite, numpy, etc.) data converter classes."""

    def __init__(self, outdir, mode, pulsemap, gcd_rescue):

        # Member variables
        self._outdir = outdir
        self._mode = mode
        self._pulsemap = pulsemap
        self._gcd_rescue = gcd_rescue

        self._extractor = I3Extractor(mode, pulsemap)  # @TODO: Restructure I3Extractor to be more "class-like."
        
        self._initialise()

    def __call__(self, directories):
        i3_files, gcd_files = find_i3_files(directories, self._gcd_rescue)
        if len(i3_files) == 0:
            print(f"ERROR: No files found in: {directories}.")
            return
        self._process_files(i3_files, gcd_files)

    @abstractmethod
    def _process_files(self, i3_files, gcd_files):
        pass

    def _process_file(self, i3_file, gcd_file, out_file):
        self._extractor.set_files(i3_file, gcd_file)
        frames = dataio.I3File(i3_file, 'r')

        while frames.more():
            try:
                frame = frames.pop_physics()
            except: 
                continue
            array = self._extractor(frame)
            self._save(array, out_file)

    @abstractmethod
    def _save(self, array, out_file):
        pass

    @abstractmethod
    def _initialise(self):
        pass
