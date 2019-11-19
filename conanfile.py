from conans import ConanFile, CMake, tools, errors
import os

class LlvmConan(ConanFile):
    name = "llvm"
    description = "The LLVM Project is a collection of modular and reusable compiler and toolchain technologies"
    topics = ("conan", "llvm", "clang")
    url = "https://gitlab.com/ArsenStudio/tools/conan/conan-llvm"
    homepage = "https://llvm.org/"
    license = "NCSA"

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    short_paths = True

    settings = "os", "compiler", "build_type", "arch"
    options = {
        'shared': [True, False],
        'enable_rtti': [True, False],
        'enable_pic': [True, False],
        'enable_threads': [True, False],
        'arch_targets': "ANY",
    }
    default_options = {
        'shared': True,
        'enable_rtti': True,
        'enable_pic': True,
        'enable_threads': True,
        'arch_targets': None,
        # 'gtest:shared=False'
    }
    # requires = "gtest/1.8.0@bincrafters/stable"

    _source_subfolder = "llvm-project"
    _build_subfolder = "llvm-project/build"

    def source(self):
        if self.version not in self.conan_data["sources"]:
            self.output.error("The version " + self.version + " is not supported.")
            exit(1)

        tools.get(**self.conan_data["sources"][self.version])
        os.rename("llvm-project-llvmorg-" + self.version, self._source_subfolder)

        tools.replace_in_file("llvm-project/llvm/CMakeLists.txt", '''project(LLVM
  VERSION ${LLVM_VERSION_MAJOR}.${LLVM_VERSION_MINOR}.${LLVM_VERSION_PATCH}
  LANGUAGES C CXX ASM)''',
                              '''project(LLVM
  VERSION ${LLVM_VERSION_MAJOR}.${LLVM_VERSION_MINOR}.${LLVM_VERSION_PATCH}
  LANGUAGES C CXX ASM)

include(../../conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)''')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.shared

    def _configure_cmake(self):
        cmake = CMake(self)
        args = None

        if self.settings.compiler == "Visual Studio" and self.settings.arch == "x86_64":
            args = ["-Thost=x64"]

        defs = {
            # LLVM
            'LLVM_ENABLE_PROJECTS': 'clang',
            'LLVM_BUILD_EXAMPLES': False,
            #'LLVM_INCLUDE_EXAMPLES': False,
            'LLVM_BUILD_TESTS': False,
            #'LLVM_INCLUDE_TESTS': False,
            'LLVM_INSTALL_CCTOOLS_SYMLINKS': False,
            'LLVM_INSTALL_BINUTILS_SYMLINKS': False,

            'LLVM_BUILD_TOOLS': False,

            'LLVM_ENABLE_PIC': self.options.enable_pic,
            'LLVM_ENABLE_RTTI': self.options.enable_rtti,
            'LLVM_ENABLE_THREADS': self.options.enable_threads,

            # Clang
            'CLANG_INCLUDE_DOCS': False,
            'CLANG_INCLUDE_TESTS': False,
            'CLANG_BUILD_TOOLS': False,
        }

        if self.options.arch_targets:
            defs['LLVM_TARGETS_TO_BUILD'] = self.options.arch_targets

        if self.settings.os != "Windows":
            defs['LLVM_BUILD_LLVM_DYLIB'] = self.options.shared

        cmake.configure(source_folder="llvm-project/llvm", build_folder=self._build_subfolder, args=args, defs=defs)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(target="clang")

    def removeSymlinks(self, path):
        for r, _, files in os.walk(path):
            for file in files:
                f = os.path.join(r, file)
                if os.path.islink(f):
                    os.unlink(f)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        if self.settings.os == "Linux":
            self.removeSymlinks(os.path.join(self.package_folder, 'bin'))

    def isPlugin(self, libname):
        return libname.endswith("Plugin")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux":
            self.cpp_info.libs = [libname for libname in self.cpp_info.libs if not self.isPlugin(libname)]

        if self.settings.os == "Windows":
            self.cpp_info.libs.append("Version")
