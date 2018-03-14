#include "io_wrapper.h"


static Fnf* read_fnf_wrapper(const char* filename) {
    return read_fnf(filename);
}

static Cnf* read_cnf_wrapper(const char* filename) {
    return read_cnf(filename);
}

static Dnf* read_dnf_wrapper(const char* filename) {
    return read_dnf(filename);
}