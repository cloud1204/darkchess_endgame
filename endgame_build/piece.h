#ifndef PIECE_H
#define PIECE_H

#include <iostream>
#include <fstream>
#include <utility>

struct Piece {
    char type;
    int color;
    int cnt;
    std::pair<int, int> pos;
    
    Piece();
    Piece(char _type, int _color);
    Piece(char _type, int _color, int _cnt);
    Piece(char _type, int _color, std::pair<int, int> _pos);
    
    bool operator<(const Piece &other) const;
    bool operator!=(const Piece &other) const;
    bool operator==(const Piece &other) const;
    
    void serialize(std::ofstream& file) const;
    void deserialize(std::ifstream& file);
};

bool eatable(const Piece& A, const Piece& B);

#endif