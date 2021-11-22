import os, glob

#to load all modules (.py files) in general directory
__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]
