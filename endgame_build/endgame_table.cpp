#include "endgame_table.h"
#include <stdexcept>
using namespace std;

EndgameTable::EndgameTable(){}

void EndgameTable::init_degree(State state){
    auto it = degree.find(state);
    if (visited[state] || it != degree.end())
        return;
    degree[state] = state.get_neighbors().size();
}

vector<pair<int, int>> EndgameTable::generate_all_pos(){
    vector<pair<int, int>> pos;
    for (int i = 0; i < 4; i++) for (int j = 0; j < 8; j++) pos.push_back({i, j});
    return pos;
}

void EndgameTable::generate_terminals(vector<Piece> pieces, int cur){
    map<pair<int, int>, bool> used;
    int n = pieces.size();
    if (cur >= n) {
        for (int msk = 1; msk < (1 << n); msk++){
            vector<Piece> tmp;
            for (int i = 0; i < n; i++){
                if (msk >> i & 1) tmp.push_back(pieces[i]);
            }
            State terminal = State(tmp, pieces.back().color ^ 1);
            if (!in_terminals[terminal]){
                terminals.push_back(terminal);
                in_terminals[terminal] = true;
            }
        }
        return;
    }
    for (int i = 0; i < cur; i++){
        used[pieces[i].pos] = 1;
    }
    for (auto pos : generate_all_pos()){
        if (used[pos]) continue;
        pieces[cur].pos = pos;
        generate_terminals(pieces, cur + 1);
    }
}

void saveStateMapBinary(const map<State, int>& stateMap, const string& filename) {
    ofstream file(filename, ios::binary);
    if (!file.is_open()) {
        throw runtime_error("Cannot open file for writing");
    }
    
    // Write map size
    size_t mapSize = stateMap.size();
    file.write(reinterpret_cast<const char*>(&mapSize), sizeof(mapSize));
    
    // Write each key-value pair
    for (const auto& pair : stateMap) {
        pair.first.serialize(file);  // Serialize State key
        file.write(reinterpret_cast<const char*>(&pair.second), sizeof(pair.second)); // Write int value
    }
    file.close();
}

map<State, int> loadStateMapBinary(const string& filename) {
    map<State, int> stateMap;
    ifstream file(filename, ios::binary);
    if (!file.is_open()) {
        throw runtime_error("Cannot open file for reading");
    }
    
    // Read map size
    size_t mapSize;
    file.read(reinterpret_cast<char*>(&mapSize), sizeof(mapSize));
    
    // Read each key-value pair
    for (size_t i = 0; i < mapSize; ++i) {
        State key;
        int value;
        key.deserialize(file);
        file.read(reinterpret_cast<char*>(&value), sizeof(value));
        stateMap[key] = value;
    }
    file.close();
    return stateMap;
}

void EndgameTable::load_file(const string &filename){
    table = loadStateMapBinary(filename);
}

void EndgameTable::bfs(){
    while (!q.empty()){
        cnt++;
        auto state = q.front();
        int result = table[state];
        q.pop();
        for (auto nei : state.get_rev_neighbors()){
            if (visited[nei]) continue;
            init_degree(nei);
            if (result == -1){
                table[nei] = 1;
                q.push(nei);
                visited[nei] = 1;
            } 
            else if (result == 1){
                degree[nei]--;
                if (!degree[nei]){
                    table[nei] = table[nei] == 1 ? 1 : -1;
                    q.push(nei);
                    visited[nei] = 1;
                }
            }
        }
    }
}

void EndgameTable::work(){
    vector<Piece> group[2];
    for (auto piece : global){
        for (int i = 0; i < piece.cnt; i++) group[piece.color].push_back(piece);
    }
    generate_terminals(group[0], 0);
    generate_terminals(group[1], 0);
    for (auto state : terminals){
        visited[state] = 1;
        table[state] = -1;
        q.push(state);
    }
    bfs();
}

int EndgameTable::query(State state){
    return table[state];
}