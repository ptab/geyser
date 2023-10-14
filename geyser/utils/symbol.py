from geyser.utils import color

# all these symbols are followed by https://codepoints.net/U+FE0E to prevent them
# being rendered as emojis
_error_char = '✗︎︎'
_warning_char = '‼︎︎'
_unused_char = '∅︎︎'
_success_char = '✓︎︎'
_cycle_char = '∞︎︎'
_direct_dependency_char = '→︎︎'
_direct_reference_char = '←︎'
_transitive_dependency_char = '⇢︎'
_transitive_reference_char = '⇠︎'

error = color.error(_error_char)
warning = color.warning(_warning_char)
unused = color.warning(_unused_char)
success = color.success(_success_char)
cycle = color.error(_cycle_char)
direct_dependency = color.info(_direct_dependency_char)
direct_reference = color.info(_direct_reference_char)
transitive_dependency = color.info(_transitive_dependency_char)
transitive_reference = color.info(_transitive_reference_char)
