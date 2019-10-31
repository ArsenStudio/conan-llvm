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
        'build_tools': [True, False],
        'enable_pic': [True, False],
        'enable_threads': [True, False]
    }
    default_options = (
        'shared=True',
        'enable_rtti=True',
        'build_tools=True',
        'enable_pic=True',
        'enable_threads=True',
        # 'gtest:shared=False'
    )
    # requires = "gtest/1.8.0@bincrafters/stable"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        if self.version not in self.conan_data["sources"]:
            self.output.error("The version " +self.version + " is not supported.")
            exit(1)

        tools.get(**self.conan_data["sources"][self.version]["llvm"])
        os.rename("llvm-" + self.version + ".src", self._source_subfolder)

        tools.get(**self.conan_data["sources"][self.version]["clang"], destination=os.path.join(self._source_subfolder, "tools"))
        os.rename(os.path.join(self._source_subfolder, "tools", "cfe-" + self.version + ".src"), os.path.join(self._source_subfolder, "tools/clang"))

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder, defs={
            'LIBCXX_INCLUDE_TESTS': False,
            'LIBCXX_INCLUDE_DOCS': False,

            # LLVM
            'LLVM_INCLUDE_TOOLS': self.options.build_tools,
            'LLVM_INCLUDE_TESTS': False,
            'LLVM_INCLUDE_EXAMPLES': False,
            'LLVM_INCLUDE_GO_TESTS': False,
            'LLVM_BUILD_TOOLS': self.options.build_tools,
            'LLVM_ENABLE_PIC': self.options.enable_pic,
            'LLVM_ENABLE_RTTI': self.options.enable_rtti,
            'LLVM_ENABLE_THREADS': self.options.enable_threads,
            'LLVM_BUILD_TESTS': False,

            # Clang
            'CLANG_INCLUDE_DOCS': False,
            'CLANG_INCLUDE_TESTS': False,
        })
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

