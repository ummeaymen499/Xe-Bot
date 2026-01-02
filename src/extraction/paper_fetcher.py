"""
Research Paper Fetcher
Handles fetching papers from arXiv and other sources
"""
import arxiv
import httpx
import pdfplumber
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from rich.console import Console

from src.config import config

console = Console()


@dataclass
class PaperData:
    """Structured paper data"""
    arxiv_id: Optional[str]
    title: str
    authors: List[str]
    abstract: str
    pdf_url: str
    source: str
    full_text: Optional[str] = None


class PaperFetcher:
    """
    Fetches research papers from various sources
    Primary support for arXiv
    """
    
    def __init__(self):
        self.cache_dir = config.CACHE_DIR / "papers"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def fetch_from_arxiv(self, arxiv_id: str) -> PaperData:
        """
        Fetch a paper from arXiv by ID
        
        Args:
            arxiv_id: arXiv paper ID (e.g., "2301.00234", "arxiv:2301.00234", or old format "quant-ph/0606228")
        
        Returns:
            PaperData with paper metadata and content
        """
        # Clean up the arxiv ID
        arxiv_id = arxiv_id.replace("arxiv:", "").replace("arXiv:", "").strip()
        
        # Handle old-style arXiv IDs (7 digits without dots, like "0606228")
        # These need category prefix - try common categories
        if arxiv_id.isdigit() and len(arxiv_id) == 7:
            # Old format - try with quant-ph prefix first (common for quantum papers)
            old_id = arxiv_id
            possible_categories = ["quant-ph", "hep-th", "cond-mat", "cs", "math", "physics"]
            
            for category in possible_categories:
                try:
                    test_id = f"{category}/{old_id}"
                    console.print(f"[blue]Trying arXiv ID: {test_id}[/blue]")
                    search = arxiv.Search(id_list=[test_id])
                    client = arxiv.Client()
                    results = list(client.results(search))
                    if results:
                        arxiv_id = test_id
                        break
                except:
                    continue
        
        console.print(f"[blue]Fetching paper from arXiv: {arxiv_id}[/blue]")
        
        # Search for the paper
        search = arxiv.Search(id_list=[arxiv_id])
        client = arxiv.Client()
        
        results = list(client.results(search))
        if not results:
            raise ValueError(f"Paper not found: {arxiv_id}")
        
        paper = results[0]
        
        paper_data = PaperData(
            arxiv_id=arxiv_id,
            title=paper.title,
            authors=[author.name for author in paper.authors],
            abstract=paper.summary,
            pdf_url=paper.pdf_url,
            source="arxiv"
        )
        
        console.print(f"[green]✓ Found paper: {paper_data.title[:60]}...[/green]")
        
        return paper_data
    
    async def search_arxiv(self, query: str, max_results: int = 5) -> List[PaperData]:
        """
        Search arXiv for papers matching a query
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of PaperData objects
        """
        console.print(f"[blue]Searching arXiv for: {query}[/blue]")
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        client = arxiv.Client()
        
        papers = []
        for paper in client.results(search):
            papers.append(PaperData(
                arxiv_id=paper.entry_id.split("/")[-1],
                title=paper.title,
                authors=[author.name for author in paper.authors],
                abstract=paper.summary,
                pdf_url=paper.pdf_url,
                source="arxiv"
            ))
        
        console.print(f"[green]✓ Found {len(papers)} papers[/green]")
        return papers
    
    async def search_by_domain(
        self, 
        domain: str, 
        max_results: int = 10,
        sort_by: str = "relevance",
        category: Optional[str] = None
    ) -> List[PaperData]:
        """
        Search arXiv for papers in a specific domain/topic
        
        Args:
            domain: The domain or topic to search for (e.g., "machine learning", "transformers", "computer vision")
            max_results: Maximum number of results to return
            sort_by: Sort order - "relevance", "submitted", or "updated"
            category: Optional arXiv category filter (e.g., "cs.LG", "cs.CV", "cs.AI")
        
        Returns:
            List of PaperData objects with papers in the domain
        """
        console.print(f"\n[bold blue]🔍 Searching arXiv for domain: {domain}[/bold blue]")
        
        # Build the search query
        # Add category filter if specified
        if category:
            query = f"cat:{category} AND all:{domain}"
        else:
            # Search across common CS/AI categories for the domain
            query = f"all:{domain}"
        
        # Map sort option
        sort_criterion = {
            "relevance": arxiv.SortCriterion.Relevance,
            "submitted": arxiv.SortCriterion.SubmittedDate,
            "updated": arxiv.SortCriterion.LastUpdatedDate
        }.get(sort_by, arxiv.SortCriterion.Relevance)
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion,
            sort_order=arxiv.SortOrder.Descending
        )
        client = arxiv.Client()
        
        papers = []
        for paper in client.results(search):
            # Extract arXiv ID from entry_id
            arxiv_id = paper.entry_id.split("/")[-1]
            # Remove version number for cleaner ID
            if "v" in arxiv_id:
                arxiv_id = arxiv_id.split("v")[0]
            
            papers.append(PaperData(
                arxiv_id=arxiv_id,
                title=paper.title,
                authors=[author.name for author in paper.authors],
                abstract=paper.summary,
                pdf_url=paper.pdf_url,
                source="arxiv"
            ))
        
        console.print(f"[green]✓ Found {len(papers)} papers in domain '{domain}'[/green]")
        
        # Display found papers
        if papers:
            console.print("\n[bold]Available papers:[/bold]")
            for i, p in enumerate(papers, 1):
                console.print(f"  {i}. [{p.arxiv_id}] {p.title[:70]}...")
                console.print(f"     Authors: {', '.join(p.authors[:3])}{'...' if len(p.authors) > 3 else ''}")
        
        return papers
    
    async def get_top_paper_for_domain(self, domain: str, category: Optional[str] = None) -> PaperData:
        """
        Get the most relevant paper for a domain and fetch its full content
        
        Args:
            domain: The domain or topic to search for
            category: Optional arXiv category filter
        
        Returns:
            PaperData with full text for the top matching paper
        """
        papers = await self.search_by_domain(domain, max_results=1, category=category)
        
        if not papers:
            raise ValueError(f"No papers found for domain: {domain}")
        
        # Fetch full content for top paper
        top_paper = papers[0]
        console.print(f"\n[bold green]📄 Selected: {top_paper.title}[/bold green]")
        
        # Download and extract PDF
        pdf_content = await self.download_pdf(top_paper)
        top_paper.full_text = await self.extract_text_from_pdf(pdf_content)
        
        return top_paper
    
    async def download_pdf(self, paper: PaperData) -> bytes:
        """
        Download PDF content from paper URL
        
        Args:
            paper: PaperData with PDF URL
        
        Returns:
            PDF content as bytes
        """
        cache_path = self.cache_dir / f"{paper.arxiv_id or 'paper'}.pdf"
        
        # Check cache first
        if cache_path.exists():
            console.print(f"[cyan]Using cached PDF: {cache_path.name}[/cyan]")
            return cache_path.read_bytes()
        
        console.print(f"[blue]Downloading PDF from {paper.pdf_url}[/blue]")
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            response = await client.get(paper.pdf_url)
            response.raise_for_status()
            pdf_content = response.content
        
        # Cache the PDF
        cache_path.write_bytes(pdf_content)
        console.print(f"[green]✓ Downloaded and cached PDF ({len(pdf_content)} bytes)[/green]")
        
        return pdf_content
    
    async def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract text content from PDF
        
        Args:
            pdf_content: PDF file content as bytes
        
        Returns:
            Extracted text
        """
        console.print("[blue]Extracting text from PDF...[/blue]")
        
        text_parts = []
        
        with pdfplumber.open(BytesIO(pdf_content)) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                
                # Usually introduction is in first few pages
                if i >= 5:
                    break
        
        full_text = "\n\n".join(text_parts)
        console.print(f"[green]✓ Extracted {len(full_text)} characters from PDF[/green]")
        
        return full_text
    
    async def fetch_and_extract(self, arxiv_id: str) -> PaperData:
        """
        Fetch paper metadata and extract full text
        
        Args:
            arxiv_id: arXiv paper ID
        
        Returns:
            PaperData with full text
        """
        # Fetch metadata
        paper = await self.fetch_from_arxiv(arxiv_id)
        
        # Download and extract PDF
        pdf_content = await self.download_pdf(paper)
        paper.full_text = await self.extract_text_from_pdf(pdf_content)
        
        return paper


# Global fetcher instance
paper_fetcher = PaperFetcher()
