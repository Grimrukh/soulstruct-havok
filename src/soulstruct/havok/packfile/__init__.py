"""Classes for HKX versions prior to `20150100` (basically up to and including DS3, but not DSR or Sekiro).

Like new HKX, these older `.hkx` files are basically compressed XML trees. The main difference, content-wise, is that
they do *not* contain nearly as much type information as newer `.hkx` files (though it is possible that they *can* hold
this information in the unused 'type' section - and in Sekiro, even the new `.hkx` files offload their type definitions
to a "compendium" `.hkx` file).
"""
