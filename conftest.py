"""
This file will contain the fixtures that are commonly needed by all other test files
for example: setting up the database, inputqueue, outputqueue, etc..
"""
import pytest
import os,sys,inspect
from multiprocessing import Queue

# add parent dir to path for imports to work
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def do_nothing(*arg):
    """ Used to override the print function because using the self.print causes broken pipes """
    pass

@pytest.fixture
def outputQueue():
    """ This outputqueue will be passed to all module constructors that need it """
    outputQueue = Queue()
    outputQueue.put = do_nothing
    return Queue()

@pytest.fixture
def outputQueue():
    """ This outputqueue will be passed to all module constructors that need it """
    outputQueue = Queue()
    outputQueue.put = do_nothing
    return Queue()

@pytest.fixture
def inputQueue():
    """ This inputQueue will be passed to all module constructors that need it """
    inputQueue = Queue()
    inputQueue.put = do_nothing
    return inputQueue


@pytest.fixture
def database():
    from slips_files.core.database import __database__
    return __database__




