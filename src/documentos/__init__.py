# When you try `import md_docs` this script is executed. The namespaces
# that are loaded here and the way they are loaded will be tacked on to
# the primary call.

# >>> import md_docs
# >>> md_docs.tools.__file__
# '/home/troy/repositories/projects/md_docs/src/md_docs/tools/__init__.py'

from . import md_docs
from . import tools

# make sure the default plugins are loaded
from .plugins import (
    toc_plugins,
    nav_plugins,
    json_plugins,
)
