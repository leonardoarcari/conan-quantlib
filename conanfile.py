from conans import ConanFile, CMake, tools
import os


class LibnameConan(ConanFile):
    name = "quantlib"
    version = "1.15"
    description = "The QuantLib C++ library"
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("cpp", "quantitative-finance", "finance")
    url = "https://github.com/leonardoarcari/conan-quantlib"
    homepage = "https://github.com/lballabio/QuantLib"
    author = "Leonardo Arcari <leonardo1.arcari@gmail.com>"
    license = "BSD-3-Clause"  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md"]      # Packages the license for the conanfile.py
    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "boost/1.67.0@conan/stable"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        sha256='c8d457e7605c443b3b60a010d8e3662676c2f77872e47a08cbc91c77064a7add'
        source_url = "https://github.com/lballabio/QuantLib"
        tools.get("{0}/archive/QuantLib-v{1}.tar.gz".format(source_url, self.version), sha256=sha256)
        extracted_dir = self.name + "-" + self.version

        print(extracted_dir)
        prefix = 'QuantLib-QuantLib-v1.15/'

        tools.replace_in_file(prefix + "CMakeLists.txt", "project(QuantLib)",
                              '''project(QuantLib)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')
        # Do not build Examples nor unit tests
        tools.replace_in_file(prefix + "CMakeLists.txt",
                              "add_subdirectory(Examples)", "")
        tools.replace_in_file(prefix + "CMakeLists.txt",
                              "add_subdirectory(test-suite)", "")
        # Fix multiple macro definition warning in config.msvc.hpp
        tools.replace_in_file(prefix + 'ql/config.msvc.hpp', '#define BOOST_ALL_NO_LIB',
                              '''#ifndef BOOST_ALL_NO_LIB
                                 #define BOOST_ALL_NO_LIB
                                 #endif
                              ''')
        # Turn on debugging symbols also in all build types
        tools.replace_in_file(prefix + 'ql/CMakeLists.txt', 'set(QL_LINK_LIBRARY ${QL_OUTPUT_NAME} PARENT_SCOPE)',
        '''set(QL_LINK_LIBRARY ${QL_OUTPUT_NAME} PARENT_SCOPE)
# Always turn debugging symbols on
target_compile_options(${QL_OUTPUT_NAME} PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/Zi>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-g>
)

# MSVC requires debugging symbols to be explicitely set in linker
if( "${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC" )
    set(new_linker_flags "/DEBUG")
    get_target_property(existing_linker_flags ${QL_OUTPUT_NAME} LINK_FLAGS)
    if(existing_linker_flags)
        set(new_linker_flags "${existing_linker_flags} ${new_linker_flags}")
    endif()
    set_target_properties(${QL_OUTPUT_NAME} PROPERTIES LINK_FLAGS ${new_linker_flags})
endif()''')

        # Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        target = self._get_target_name()
        cmake.build(target=target)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self._source_subfolder, "ql")
        self.copy(pattern="*", dst="include/ql", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        target = self._get_target_name()
        if self.settings.compiler == 'Visual Studio':
            libname = target + '-gd' if self.settings.build_type == 'Debug' else target
        else:
            libname = target
        self.cpp_info.libs = [libname]
    
    def _get_target_name(self):
        if self.settings.compiler == 'Visual Studio':
            # Compiler Version
            if self.settings.compiler.version == "15":
                ql_lib_toolset = '-vc141'
            elif self.settings.compiler.version == "14":
                ql_lib_toolset = '-vc140'
            elif self.settings.compiler.version == "13":
                ql_lib_toolset = '-vc120'
            elif self.settings.compiler.version == "11":
                ql_lib_toolset = '-vc110'
            elif self.settings.compiler.version == "10":
                ql_lib_toolset = '-vc100'
            else:
                raise RuntimeError("Compiler below VC++2010 is not supported")
            # Platform
            if self.settings.arch == "x86_64":
                ql_lib_platform = '-x64'
            else:
                ql_lib_platform = ''
            # Set target name
            return 'QuantLib{}{}-mt'.format(ql_lib_toolset, ql_lib_platform)
        else:
            return 'QuantLib' 
