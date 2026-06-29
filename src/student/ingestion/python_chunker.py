import ast
import hashlib
from pathlib import Path

from student.models import Chunk


class PythonChunker:
    def __init__(self, max_chunk_size: int = 2000) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk_file(self, path: Path) -> list[Chunk]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return self._split_large_chunk(path, text, 0)

        # Precompute line break character boundaries
        line_starts = [0]
        for line in text.splitlines(keepends=True):
            line_starts.append(line_starts[-1] + len(line))

        chunks: list[Chunk] = []

        # 1. Capture Global Module Context (Imports, Globals)
        global_end_line = min(35, len(line_starts) - 1)
        global_end_char = min(line_starts[global_end_line], self.max_chunk_size)
        global_text = f"# file: {path.name}\n# context: global_scope_and_imports\n" + text[:global_end_char]
        chunks.extend(self._split_large_chunk(path, global_text, 0))

        # Helper to extract raw text boundaries safely
        def get_node_text(node):
            s_line = node.lineno
            e_line = getattr(node, "end_lineno", None)
            if e_line is None:
                return "", 0, 0
            s_char = line_starts[s_line - 1]
            e_char = line_starts[min(e_line, len(line_starts) - 1)]
            return text[s_char:e_char], s_char, e_char

        # 2. Smart Structural Traversal
        for node in ast.iter_child_nodes(tree):
            # Handle Standalone Top-Level Functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                node_text, s_char, _ = get_node_text(node)
                if not node_text: continue
                meta = f"# file: {path.name}\n# context: function {node.name}\n"
                chunks.extend(self._split_large_chunk(path, meta + node_text, s_char))

            # Handle Classes and their internal methods
            elif isinstance(node, ast.ClassDef):
                class_text, class_s_char, _ = get_node_text(node)
                if not class_text: continue
                
                # Chunk the Class definition as its own structural unit
                class_meta = f"# file: {path.name}\n# context: class {node.name}\n"
                chunks.extend(self._split_large_chunk(path, class_meta + class_text, class_s_char))

                # Process inner methods with explicit parent context injection
                for sub_node in node.body:
                    if isinstance(sub_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_text, method_s_char, _ = get_node_text(sub_node)
                        if not method_text: continue
                        
                        # Inject parent class name so embedding models can map it accurately
                        method_meta = f"# file: {path.name}\n# context: class {node.name} -> method {sub_node.name}\n"
                        chunks.extend(self._split_large_chunk(path, method_meta + method_text, method_s_char))

        if not chunks:
            return self._split_large_chunk(path, text, 0)
            
        return chunks

    def _split_large_chunk(self, path: Path, text: str, start_offset: int) -> list[Chunk]:
        """Splits text at line boundaries using a true sliding window overlap."""
        lines = text.splitlines(keepends=True)
        chunks: list[Chunk] = []
        
        line_lengths = [len(l) for l in lines]
        num_lines = len(lines)
        start_line_idx = 0
        
        while start_line_idx < num_lines:
            current_chunk_lines = []
            current_size = 0
            end_line_idx = start_line_idx
            
            while end_line_idx < num_lines:
                next_line_len = line_lengths[end_line_idx]
                if current_size + next_line_len > self.max_chunk_size and current_chunk_lines:
                    break
                current_chunk_lines.append(lines[end_line_idx])
                current_size += next_line_len
                end_line_idx += 1
                
            chunk_text_str = "".join(current_chunk_lines)
            relative_start = sum(line_lengths[:start_line_idx])
            absolute_start = start_offset + relative_start
            absolute_end = absolute_start + len(chunk_text_str)
            
            chunk_id = hashlib.md5(f"{path}{absolute_start}".encode()).hexdigest()
            
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    file_path=str(path),
                    file_type="python",
                    text=chunk_text_str,
                    first_character_index=absolute_start,
                    last_character_index=absolute_end,
                )
            )
            
            if end_line_idx == num_lines:
                break
                
            overlap_target = 200
            overlap_size = 0
            next_start_idx = end_line_idx
            
            while next_start_idx > start_line_idx:
                prev_line_len = line_lengths[next_start_idx - 1]
                if overlap_size + prev_line_len > overlap_target:
                    break
                overlap_size += prev_line_len
                next_start_idx -= 1
                
            if next_start_idx >= end_line_idx:
                start_line_idx = end_line_idx
            else:
                start_line_idx = next_start_idx

        return chunks

