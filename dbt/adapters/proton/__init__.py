"""
Compatibility shim for older references to 'dbt.adapters.proton'.
Re-exports the Timeplus adapter under the old module path.
"""
from dbt.adapters.timeplus import *  # noqa: F401,F403

