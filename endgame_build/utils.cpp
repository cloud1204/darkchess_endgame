#include "utils.h"
#include "state.h"
#include <algorithm>
#include <fstream>

std::string get_filename() {
    std::sort(global.begin(), global.end());
    std::string name = "endgame_build/cached_endgame_boards/";
    for (auto pc : global) {
        for (int i = 0; i < pc.cnt; i++) {
            name += pc.color == 0 ? char(pc.type + 'a' - 'A') : pc.type;
        }
    }
    return name;
}

bool fileExists(const std::string& filename) {
    std::ifstream file(filename);
    return file.good();
}