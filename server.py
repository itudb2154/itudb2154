#Project Flask MVC

__author__ = "indhifarhandika"
__version__ = "1"
__email__ = "indhifarhandika@gmail.com"

#from project folder, import app object (constructed in project/__init__.py)
from project import app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True, threaded=True)
