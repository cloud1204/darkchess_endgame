#include "state.h"
#include <algorithm>
#include <iostream>
using namespace std;

std::vector<Piece> global;

Move::Move(int _sx, int _sy, int _tx, int _ty) {
    sx = _sx, sy = _sy, tx = _tx, ty = _ty;
}

bool State::operator<(const State &other) const {
    if (turn != other.turn) return turn < other.turn;
    if (pieces.size() != other.pieces.size()) return pieces.size() < other.pieces.size();
    for (int i = 0; i < pieces.size(); i++) {
        if (pieces[i] != other.pieces[i]) return pieces[i] < other.pieces[i];
    }
    return false;
}

State::State() {}

State::State(const std::vector<Piece> _pieces, int _turn) : pieces(_pieces), turn(_turn) {
    std::sort(pieces.begin(), pieces.end());

    for (auto g_piece : global) {
        int cnt = 0;
        for (auto piece : pieces) {
            if (piece.type == g_piece.type && piece.color == g_piece.color) cnt++;
        }
        if (cnt < g_piece.cnt) eatens.push_back(Piece(g_piece.type, g_piece.color, g_piece.cnt - cnt));
    }
}

bool State::in_bound(int x, int y) const {
    return 0 <= x && x < 4 && 0 <= y && y < 8;
}

vector<State> State::get_rev_neighbors() const{
    vector<State> neighbors;
    for (const auto& piece : pieces) {
        if (piece.color == turn) continue;
        int x = piece.pos.first;
        int y = piece.pos.second;

        vector<pair<int, int>> dirs = {{x, y + 1}, {x, y - 1}, {x + 1, y}, {x - 1, y}};
        for (const auto& [nx, ny] : dirs) {
            if (!in_bound(nx, ny)) continue;
            bool succ = true;
            vector<Piece> new_pieces;
            for (const auto& other : pieces) {
                if (other.pos == make_pair(nx, ny)) {
                    succ = false;
                    break;
                }
                else if (other == piece){
                    new_pieces.push_back(Piece(piece.type, piece.color, make_pair(nx, ny)));
                }
                else {
                    new_pieces.push_back(other);
                }
            }
            if (!succ) continue;
            neighbors.push_back(State(new_pieces, turn ^ 1));
            for (auto eaten : eatens){
                if (!eatable(piece, eaten)) continue;
                new_pieces.push_back(Piece(eaten.type, eaten.color, piece.pos));
                neighbors.push_back(State(new_pieces, turn ^ 1));
                new_pieces.pop_back();
            }

            
        }
    }
    return neighbors;
}

vector<pair<Move, State>> State::get_neighbors() const {
    vector<pair<Move, State>> neighbors;
    for (const auto& piece : pieces) {
        if (piece.color != turn) continue;
        int x = piece.pos.first;
        int y = piece.pos.second;

        vector<pair<int, int>> dirs = {{x, y + 1}, {x, y - 1}, {x + 1, y}, {x - 1, y}};
        for (const auto& [nx, ny] : dirs) {
            if (!in_bound(nx, ny)) continue;

            vector<Piece> new_pieces;
            bool succ = true;

            for (const auto& other : pieces) {
                if (other.pos == piece.pos) {
                    new_pieces.emplace_back(Piece(piece.type, piece.color, {nx, ny}));
                } else if (other.pos == make_pair(nx, ny)) {
                    if (!eatable(piece, other)) {
                        succ = false;
                        break;
                    }
                    // else: skip adding, it's eaten
                } else {
                    new_pieces.push_back(other);
                }
            }

            if (succ) {
                neighbors.emplace_back(make_pair(Move(x, y, nx, ny), State(new_pieces, turn ^ 1))); 
            }
        }
    }
    return neighbors;
}

void State::serialize(ofstream& file) const {
    file.write(reinterpret_cast<const char*>(&turn), sizeof(turn));
    
    size_t piecesSize = pieces.size();
    file.write(reinterpret_cast<const char*>(&piecesSize), sizeof(piecesSize));
    for (const auto& piece : pieces) {
        piece.serialize(file);
    }
    
    size_t eatensSize = eatens.size();
    file.write(reinterpret_cast<const char*>(&eatensSize), sizeof(eatensSize));
    for (const auto& eaten : eatens) {
        eaten.serialize(file);
    }
}

void State::deserialize(ifstream& file) {
    // Read turn
    file.read(reinterpret_cast<char*>(&turn), sizeof(turn));
    
    size_t piecesSize;
    file.read(reinterpret_cast<char*>(&piecesSize), sizeof(piecesSize));
    pieces.resize(piecesSize);
    for (auto& piece : pieces) {
        piece.deserialize(file);
    }
    
    size_t eatensSize;
    file.read(reinterpret_cast<char*>(&eatensSize), sizeof(eatensSize));
    eatens.resize(eatensSize);
    for (auto& eaten : eatens) {
        eaten.deserialize(file);
    }
}