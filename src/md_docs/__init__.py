# Load the packages into the name space so we can use a regular name
# space import like `import md_docs` and then use the
# >>> import md_docs
# >>> md_docs.tools.__file__
# '/home/troy/repositories/projects/md_docs/src/md_docs/tools/__init__.py'

from . import md_docs
from . import tools
from . import plugins
