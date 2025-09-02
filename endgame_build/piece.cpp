#include "piece.h"
#include <map>

Piece::Piece() {}

Piece::Piece(char _type, int _color) : type(_type), color(_color) {}

Piece::Piece(char _type, int _color, int _cnt) : type(_type), color(_color), cnt(_cnt) {}

Piece::Piece(char _type, int _color, std::pair<int, int> _pos) : type(_type), color(_color), pos(_pos) {}

bool Piece::operator<(const Piece &other) const {
    if (color != other.color) return color < other.color;
    if (type != other.type) return type < other.type;
    return pos < other.pos;
}

bool Piece::operator!=(const Piece &other) const {
    return color != other.color || type != other.type || pos != other.pos;
}

bool Piece::operator==(const Piece &other) const {
    return color == other.color && type == other.type && pos == other.pos;
}

void Piece::serialize(std::ofstream& file) const {
    file.write(reinterpret_cast<const char*>(&type), sizeof(type));
    file.write(reinterpret_cast<const char*>(&color), sizeof(color));
    file.write(reinterpret_cast<const char*>(&cnt), sizeof(cnt));
    file.write(reinterpret_cast<const char*>(&pos.first), sizeof(pos.first));
    file.write(reinterpret_cast<const char*>(&pos.second), sizeof(pos.second));
}

void Piece::deserialize(std::ifstream& file) {
    file.read(reinterpret_cast<char*>(&type), sizeof(type));
    file.read(reinterpret_cast<char*>(&color), sizeof(color));
    file.read(reinterpret_cast<char*>(&cnt), sizeof(cnt));
    file.read(reinterpret_cast<char*>(&pos.first), sizeof(pos.first));
    file.read(reinterpret_cast<char*>(&pos.second), sizeof(pos.second));
}

bool eatable(const Piece& A, const Piece& B) {
    if (A.color == B.color) return false;
    static std::map<char, int> partial_order = {
        {'K', 6}, {'G', 5}, {'M', 4}, {'R', 3}, {'N', 2}, {'C', 1}, {'P', 0}
    };
    if (A.type == 'K' && B.type == 'P') return false;
    if (A.type == 'P' && B.type == 'K') return true;
    return partial_order[A.type] >= partial_order[B.type];
}