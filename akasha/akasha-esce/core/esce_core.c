/*
 * esce_core.c — Low-level C primitive for ESCE XOR transform
 *
 * Ported from Termux/Android to Debian 13 Linux.
 * Requires: python3-dev, gcc (build-essential)
 * Build via: pip install . (from repo root)
 *
 * Akasha lineage: akasha-esce / layer: transformation
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* xor_bytes(PyObject* self, PyObject* args) {
    Py_buffer input;
    int key;

    if (!PyArg_ParseTuple(args, "y*i", &input, &key)) {
        return NULL;
    }

    PyObject* result = PyBytes_FromStringAndSize(NULL, input.len);
    if (!result) {
        PyBuffer_Release(&input);
        return PyErr_NoMemory();
    }

    char* out_buf = PyBytes_AsString(result);
    const char* in_buf = (const char*)input.buf;

    for (Py_ssize_t i = 0; i < input.len; i++) {
        out_buf[i] = in_buf[i] ^ (char)(key & 0xFF);
    }

    PyBuffer_Release(&input);
    return result;
}

static PyMethodDef EsceMethods[] = {
    {"xor_bytes", xor_bytes, METH_VARARGS, "XOR each byte of input with key (int)."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef escemodule = {
    PyModuleDef_HEAD_INIT,
    "_core",
    "ESCE low-level C primitives.",
    -1,
    EsceMethods
};

PyMODINIT_FUNC PyInit__core(void) {
    return PyModule_Create(&escemodule);
}
