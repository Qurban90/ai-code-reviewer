"""
Dependency Graph — fayllar arasında import əlaqələrini qurub analiz edir.

DSA Konsepti: Directed Graph (DAG ideal)
- Node = Python faylı
- Edge = import əlaqəsi (A → B = A faylı B-ni import edir)

Alqoritmlər:
- BFS/DFS: impact analysis (bu fayl dəyişsə hansı fayllar təsirlənir?)
- Cycle detection: dairəvi import-ları tap
- Topological sort: fayl review sırası

Time complexity: O(V + E)
- V = fayl sayı
- E = import sayı
"""
import os
import ast
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional

import networkx as nx


@dataclass
class GraphAnalysis:
    """Qraf analiz nəticəsi."""
    total_files: int = 0
    total_imports: int = 0
    cycles: List[List[str]] = field(default_factory=list)
    most_imported: List[tuple] = field(default_factory=list)  # (file, in-degree)
    most_dependencies: List[tuple] = field(default_factory=list)  # (file, out-degree)
    isolated_files: List[str] = field(default_factory=list)
    has_cycles: bool = False


class DependencyGraphBuilder:
    """Python layihəsi üçün dependency graph qurur."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self._project_modules: Set[str] = set()
    
    def build_from_directory(self, directory: str) -> nx.DiGraph:
        """
        Verilmiş qovluqda bütün .py fayllarını tap, qraf qur.
        
        Args:
            directory: Layihə qovluğu
        
        Returns:
            networkx.DiGraph
        """
        self.graph = nx.DiGraph()
        self._project_modules = set()
        
        # Mərhələ 1: bütün modul adlarını topla (project-internal nədir təyin etmək üçün)
        py_files = self._find_python_files(directory)
        for file_path in py_files:
            module_name = self._path_to_module(file_path, directory)
            self._project_modules.add(module_name)
            self.graph.add_node(module_name, path=str(file_path))
        
        # Mərhələ 2: hər fayldan import-ları çıxart, edge-lər qur
        for file_path in py_files:
            module_name = self._path_to_module(file_path, directory)
            imports = self._extract_imports(file_path)
            
            for imp in imports:
                # Yalnız layihə-daxili import-lar (xarici kitabxanaları nəzərə almırıq)
                if self._is_project_module(imp):
                    if imp != module_name:  # özünü import etməsin
                        self.graph.add_edge(module_name, imp)
        
        return self.graph
    
    def build_from_files(self, files: Dict[str, str]) -> nx.DiGraph:
        """
        Fayl məzmunundan birbaşa qraf qur (PR analizində istifadə üçün).
        
        Args:
            files: {filename: code_content}
        """
        self.graph = nx.DiGraph()
        self._project_modules = set()
        
        for filename in files:
            module_name = self._filename_to_module(filename)
            self._project_modules.add(module_name)
            self.graph.add_node(module_name, path=filename)
        
        for filename, code in files.items():
            module_name = self._filename_to_module(filename)
            imports = self._extract_imports_from_code(code)
            
            for imp in imports:
                if self._is_project_module(imp) and imp != module_name:
                    self.graph.add_edge(module_name, imp)
        
        return self.graph
    
    def analyze(self) -> GraphAnalysis:
        """Qrafı analiz et və statistika qaytar."""
        result = GraphAnalysis(
            total_files=self.graph.number_of_nodes(),
            total_imports=self.graph.number_of_edges(),
        )
        
        # Cycle detection (DFS əsaslı, networkx daxilində)
        try:
            cycles = list(nx.simple_cycles(self.graph))
            result.cycles = cycles
            result.has_cycles = len(cycles) > 0
        except Exception:
            result.cycles = []
        
        # Ən çox import edilən fayllar (in-degree)
        in_degrees = sorted(
            self.graph.in_degree(),
            key=lambda x: x[1],
            reverse=True,
        )
        result.most_imported = [(n, d) for n, d in in_degrees[:5] if d > 0]
        
        # Ən çox dependency-si olan fayllar (out-degree)
        out_degrees = sorted(
            self.graph.out_degree(),
            key=lambda x: x[1],
            reverse=True,
        )
        result.most_dependencies = [(n, d) for n, d in out_degrees[:5] if d > 0]
        
        # Tək qalmış fayllar (heç bir əlaqəsi yox)
        result.isolated_files = [
            n for n in self.graph.nodes()
            if self.graph.in_degree(n) == 0 and self.graph.out_degree(n) == 0
        ]
        
        return result
    
    def get_impact(self, module: str) -> Set[str]:
        """
        Verilmiş modul dəyişərsə, hansı modullar təsirlənir?
        
        BFS/DFS ilə bütün ancestor-ları tap (bu modulu import edənlər).
        
        Time: O(V + E)
        """
        if module not in self.graph:
            return set()
        # ancestors() = bu node-a doğru gedən bütün yollar
        return nx.ancestors(self.graph, module)
    
    def get_dependencies(self, module: str) -> Set[str]:
        """
        Verilmiş modul hansı modullardan asılıdır?
        
        BFS/DFS ilə bütün descendant-ları tap.
        """
        if module not in self.graph:
            return set()
        return nx.descendants(self.graph, module)
    
    def render_as_image(self, output_path: str = "graphs/dependency_graph") -> str:
        """
        Qrafı PNG şəkil kimi yadda saxla (Graphviz ilə).
        
        Returns:
            Yaradılmış faylın yolu
        """
        from graphviz import Digraph
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        dot = Digraph(comment="Dependency Graph")
        dot.attr(rankdir="LR", size="12,8")
        dot.attr("node", shape="box", style="rounded,filled", fillcolor="lightblue", fontname="Arial")
        dot.attr("edge", color="gray40")
        
        # Cycle-ları qırmızı boya
        cycle_nodes = set()
        for cycle in nx.simple_cycles(self.graph):
            cycle_nodes.update(cycle)
        
        for node in self.graph.nodes():
            color = "lightcoral" if node in cycle_nodes else "lightblue"
            dot.node(node, fillcolor=color)
        
        for source, target in self.graph.edges():
            edge_color = "red" if source in cycle_nodes and target in cycle_nodes else "gray40"
            dot.edge(source, target, color=edge_color)
        
        # PNG kimi render et
        rendered_path = dot.render(output_path, format="png", cleanup=True)
        return rendered_path
    
    # ─── Helper-lər ──────────────────────────────────────────────
    
    def _find_python_files(self, directory: str) -> List[Path]:
        """Qovluqda bütün .py fayllarını tap (venv və __pycache__ istisna)."""
        skip_dirs = {"venv", "env", "__pycache__", ".git", "node_modules", ".pytest_cache"}
        py_files = []
        
        for root, dirs, files in os.walk(directory):
            # skip dirs
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for f in files:
                if f.endswith(".py"):
                    py_files.append(Path(root) / f)
        
        return py_files
    
    def _path_to_module(self, file_path: Path, base_dir: str) -> str:
        """Fayl yolunu Python modul adına çevir."""
        rel = file_path.relative_to(base_dir)
        # __init__.py → qovluq adı
        if rel.name == "__init__.py":
            parts = rel.parent.parts
        else:
            parts = list(rel.parent.parts) + [rel.stem]
        return ".".join(parts) if parts else rel.stem
    
    def _filename_to_module(self, filename: str) -> str:
        """Fayl adından modul adı qaytar."""
        path = Path(filename)
        parts = list(path.parent.parts) + [path.stem]
        # Boş hissələri sil
        parts = [p for p in parts if p and p != "."]
        return ".".join(parts) if parts else path.stem
    
    def _is_project_module(self, module: str) -> bool:
        """Bu modul layihə-daxili-dirmi?"""
        # Tam uyğunluq və ya prefix uyğunluğu
        for project_mod in self._project_modules:
            if module == project_mod or module.startswith(project_mod + "."):
                return True
            # Tərsinə də yoxla (qismən import)
            if project_mod.startswith(module + "."):
                return True
        return False
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Fayldan import-ları çıxar."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            return self._extract_imports_from_code(code)
        except (OSError, UnicodeDecodeError):
            return []
    
    def _extract_imports_from_code(self, code: str) -> List[str]:
        """Kod string-indən import-ları çıxar."""
        imports = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return imports
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports