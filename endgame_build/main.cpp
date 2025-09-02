#include <iostream>
#include <map>
#include "endgame_table.h"
#include "utils.h"

using namespace std;

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cerr << "Usage: " << argv[0] << " <pieces_info> <turn>" << endl;
        cerr << "Example: " << argv[0] << " K000P111 0" << endl;
        return 1;
    }

    string query_s = argv[1];
    int turn = atoi(argv[2]);
    
    if (query_s.size() % 4) {
        cout << "Invalid Format." << endl;
        return 1;
    }
    
    vector<Piece> pieces;
    map<pair<char, int>, int> piece_cnt;
    int pc_cnt = query_s.size() / 4;
    
    for (int i = 0; i < pc_cnt; i++) {
        char tp = query_s[i * 4];
        int color = query_s[i * 4 + 1] - '0';
        int x = query_s[i * 4 + 2] - '0';
        int y = query_s[i * 4 + 3] - '0';
        pieces.push_back(Piece(tp, color, {x, y}));
        piece_cnt[{tp, color}]++;
    }

    for (auto [piece, cnt] : piece_cnt) {
        global.push_back(Piece(piece.first, piece.second, cnt));
    }

    string filename = get_filename();
    EndgameTable table;
    bool new_file = false;
    
    if (fileExists(filename)) {
        table.load_file(filename);
    } else {
        new_file = true;
        table.work();
    }
    
    auto state = State(pieces, turn);
    cout << table.query(State(pieces, turn)) << '\n';
    
    auto neighbors = state.get_neighbors();
    cout << neighbors.size() << '\n';
    
    for (auto [move, neighbor_state] : neighbors) {
        cout << move.sx << ' ' << move.sy << ' ' << move.tx << ' ' << move.ty << ' ' << table.query(neighbor_state) << '\n';
    }
    
    if (new_file) saveStateMapBinary(table.table, filename);
    return 0;
}