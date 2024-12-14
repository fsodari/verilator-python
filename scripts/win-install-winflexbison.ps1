git clone --depth 1 https://github.com/lexxmark/winflexbison $PWD/.ccache/winflexbison
cmake -S $PWD/.ccache/winflexbison -B $PWD/.ccache/winflexbison/build --install-prefix $PWD/.ccache/winflexbison/install
cmake --build $PWD/.ccache/winflexbison/build --config Release
cmake --install $PWD/.ccache/winflexbison/build --prefix $PWD/.ccache/winflexbison/install
