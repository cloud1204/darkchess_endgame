#ifndef STATE_H
#define STATE_H

#include "piece.h"
#include <vector>
#include <fstream>

extern std::vector<Piece> global;

struct Move {
    int sx, sy, tx, ty;
    Move(int _sx, int _sy, int _tx, int _ty);
};

struct State {
    std::vector<Piece> pieces, eatens;
    int turn;

    bool operator<(const State &other) const;
    
    State();
    State(const std::vector<Piece> _pieces, int _turn);

    bool in_bound(int x, int y) const;
    std::vector<State> get_rev_neighbors() const;
    std::vector<std::pair<Move, State>> get_neighbors() const;
    void Print();
    
    void serialize(std::ofstream& file) const;
    void deserialize(std::ifstream& file);
};

#endif