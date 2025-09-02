#ifndef ENDGAME_TABLE_H
#define ENDGAME_TABLE_H

#include "state.h"
#include <map>
#include <queue>
#include <string>

void saveStateMapBinary(const std::map<State, int>& stateMap, const std::string& filename);
std::map<State, int> loadStateMapBinary(const std::string& filename);

struct EndgameTable {
    int cnt = 0;
    std::map<State, int> table, degree;
    std::map<State, bool> visited, in_terminals;
    std::queue<State> q;
    std::vector<State> terminals;
    
    EndgameTable();
    void init_degree(State state);
    std::vector<std::pair<int, int>> generate_all_pos();
    void generate_terminals(std::vector<Piece> pieces, int cur);
    void load_file(const std::string &filename);
    void work();
    void bfs();
    int query(State state);
};

#endif