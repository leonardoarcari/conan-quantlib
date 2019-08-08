#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default


def _is_dynamic_msvc_build(build):
    if build.options['quantlib:shared'] == True and build.settings['compiler'] == 'Visual Studio':
        return True
    else:
        return False

def _is_not_md(build):
    if build.settings['compiler'] == 'Visual Studio' and build.settings['compiler.runtime'] != 'MD':
        return True
    else:
        return False

def _is_incompatible_gcc(build):
    if build.settings['compiler'] == 'gcc' and build.settings['compiler.version'] == '9' and build.settings['compiler.libcxx'] == 'libstdc++':
        return True
    else:
        return False

if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=False)

    # Filter out (don't build) shared versions the lib, but only for MSVC
    builder.remove_build_if(_is_dynamic_msvc_build)
    # Filter out non dynamic, release runtime for Visual Studio
    builder.remove_build_if(_is_not_md)
    # Filter out incompatible GCC
    builder.remove_build_if(_is_incompatible_gcc)

    builder.run()
