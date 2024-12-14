git clone --depth 1 https://github.com/lexxmark/winflexbison extern/winflexbison
cmake -S extern/winflexbison -B extern/winflexbison/build --install-prefix $PWD/.ccache/winflexbison
cmake --build extern/winflexbison/build --config Release
cmake --install extern/winflexbison/build --prefix $PWD/.ccache/winflexbison
