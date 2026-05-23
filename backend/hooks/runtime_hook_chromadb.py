"""
Runtime hook for PyInstaller to fix ChromaDB's dynamic module discovery.

ChromaDB uses pkgutil.iter_modules() with a filesystem path to discover
embedding functions at runtime. In PyInstaller frozen apps, the Python modules
are inside the PYZ archive and not on disk, so filesystem-based discovery fails.

This hook patches pkgutil.iter_modules to return the known embedding function
modules when the chromadb embedding_functions path is queried.
"""
import sys
import pkgutil

# Known chromadb embedding function modules that need to be discoverable
_CHROMADB_EF_MODULES = [
    ('onnx_mini_lm_l6_v2', False),
    ('openai_embedding_function', False),
    ('google_embedding_function', False),
    ('ollama_embedding_function', False),
    ('huggingface_embedding_function', False),
    ('sentence_transformer_embedding_function', False),
    ('cohere_embedding_function', False),
    ('chroma_langchain_embedding_function', False),
    ('amazon_bedrock_embedding_function', False),
    ('instructor_embedding_function', False),
    ('jina_embedding_function', False),
    ('open_clip_embedding_function', False),
    ('roboflow_embedding_function', False),
    ('text2vec_embedding_function', False),
]

if getattr(sys, 'frozen', False):
    _original_iter_modules = pkgutil.iter_modules

    def _patched_iter_modules(path=None, prefix=''):
        """Patched iter_modules that handles chromadb embedding_functions discovery."""
        if path is not None:
            # Check if this is looking for chromadb embedding_functions
            for p in path:
                if 'chromadb' in str(p) and 'embedding_functions' in str(p):
                    # Yield our known modules
                    for name, ispkg in _CHROMADB_EF_MODULES:
                        yield None, prefix + name, ispkg
                    return

        # Fall through to original for everything else
        yield from _original_iter_modules(path, prefix)

    pkgutil.iter_modules = _patched_iter_modules
