from conans import ConanFile, CMake, tools


class LlvmConan(ConanFile):
    name = "llvm"
    version = "6.0.0"
    license = "<Put the package license here>"
    url = "https://gitlab.com/HeiGameStudio/ArsenEngine/dependencies/conan-llvm"
    description = "The LLVM Project is a collection of modular and reusable compiler and toolchain technologies"
    license = "University of Illinois/NCSA Open Source License"
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
        'gtest:shared=False'
    )
    requires = "gtest/1.8.0@bincrafters/stable"
    generators = "cmake"
    branch = "release_60"

    def source(self):
        self.run("git clone https://git.llvm.org/git/llvm -b {} --depth 1".format(self.branch))
        self.run("cd llvm/tools && git clone https://git.llvm.org/git/clang -b {} --depth 1".format(self.branch))


    def build(self):
        cmake = CMake(self)
        cmake.configure(build_folder="build", source_folder="llvm", defs={
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

            'CMAKE_INSTALL_PREFIX': 'install',
            'BUILD_SHARED_LIBS': self.options.shared
        })
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="*.h", dst="include", src="install/include", keep_path=True)
        self.copy(pattern="*.lib", dst="lib", src="install/lib", keep_path=True)
        self.copy(pattern="*.dll", dst="bin", src="install/bin", keep_path=True)
        self.copy(pattern="*.a", dst="lib", src="install/lib", keep_path=True)
        self.copy(pattern="*.dylib", dst="lib", src="install/lib", keep_path=True)
        self.copy(pattern="*.so", dst="lib", src="install/lib", keep_path=True)
        self.copy(pattern="*.cmake", dst="lib", src="install/lib", keep_path=True)


        self.copy(pattern="*", dst="share", src="install/share", keep_path=True)
        self.copy(pattern="*", dst="libexec", src="install/libexec", keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["libclang"]

