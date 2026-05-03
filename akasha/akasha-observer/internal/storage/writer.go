package storage

import (
    "encoding/json"
    "os"
    "path/filepath"
)

type Writer struct {
    file *os.File
}

func NewWriter(path string) (*Writer, error) {
    if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
        return nil, err
    }

    f, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0600)
    if err != nil {
        return nil, err
    }

    return &Writer{file: f}, nil
}

func (w *Writer) Write(v any) error {
    enc := json.NewEncoder(w.file)
    return enc.Encode(v)
}

func (w *Writer) Close() error {
    return w.file.Close()
}