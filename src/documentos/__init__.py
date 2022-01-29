# When you try `import documentos` this script is executed. The namespaces
# that are loaded here and the way they are loaded will be tacked on to
# the primary call.

# >>> import documentos
# >>> documentos.tools.__file__
# '/home/troy/repositories/projects/documentos/src/documentos/tools/__init__.py'

from . import documentos
from . import tools

# make sure the default plugins are loaded
from .plugins import (
    toc_plugins,
    nav_plugins,
    json_plugins,
)
