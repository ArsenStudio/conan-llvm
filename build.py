from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(reference="llvm/9.0.0@arsen-studio/testing")
    builder.remove_build_if(lambda build: build.settings["compiler"] == "Visual Studio" and build.options['llvm:shared'] == True)

    filtered_builds = []
    for settings, options, env_vars, build_requires, reference in builder.items:
        if settings["compiler"] == "Visual Studio":
            del options['llvm:shared']
        filtered_builds.append([settings, options, env_vars, build_requires, reference])
    builder.builds = filtered_builds

    builder.run()
