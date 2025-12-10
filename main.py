"""
Xe-Bot: Research Paper Animation Generator
Main entry point for the application

Usage:
    python main.py --arxiv 2301.00234
    python main.py --arxiv 2301.00234 --no-render
    python main.py --domain "transformers attention mechanism"
    python main.py --domain "computer vision" --category cs.CV
    python main.py --text "Your text content here"
    python main.py --init-db
"""
import asyncio
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.agents import orchestrator
from src.database import db_manager
from src.extraction import paper_fetcher

console = Console()


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ██╗  ██╗███████╗      ██████╗  ██████╗ ████████╗        ║
    ║   ╚██╗██╔╝██╔════╝      ██╔══██╗██╔═══██╗╚══██╔══╝        ║
    ║    ╚███╔╝ █████╗  █████╗██████╔╝██║   ██║   ██║           ║
    ║    ██╔██╗ ██╔══╝  ╚════╝██╔══██╗██║   ██║   ██║           ║
    ║   ██╔╝ ██╗███████╗      ██████╔╝╚██████╔╝   ██║           ║
    ║   ╚═╝  ╚═╝╚══════╝      ╚═════╝  ╚═════╝    ╚═╝           ║
    ║                                                           ║
    ║        Research Paper Animation Generator                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")


async def process_arxiv_paper(arxiv_id: str, render: bool = True, save_db: bool = True):
    """Process an arXiv paper through the full pipeline"""
    console.print(f"\n[bold]Processing arXiv paper: {arxiv_id}[/bold]\n")
    
    results = await orchestrator.process_paper(
        arxiv_id=arxiv_id,
        render_animations=render,
        save_to_db=save_db
    )
    
    # Print results summary
    if results["status"] == "completed":
        console.print("\n[bold green]✓ Processing Complete![/bold green]")
        
        if results.get("paper"):
            console.print(Panel(
                f"**Title:** {results['paper']['title']}\n\n"
                f"**Authors:** {', '.join(results['paper']['authors'][:3])}",
                title="Paper Info"
            ))
        
        if results.get("segments"):
            segments_text = "\n".join([
                f"• **{s['topic']}** [{s['category']}]"
                for s in results["segments"]
            ])
            console.print(Panel(Markdown(segments_text), title="Segments"))
        
        if results.get("animations"):
            console.print(f"\n[bold]Generated {len(results['animations'])} animations:[/bold]")
            for anim in results["animations"]:
                status = "✓" if anim.get("file_path") else "◯ (code only)"
                path = anim.get("file_path", "Not rendered")
                console.print(f"  {status} {anim.get('topic', anim.get('type', 'Animation'))}: {path}")
    else:
        console.print(f"\n[bold red]✗ Processing Failed[/bold red]")
        for error in results.get("errors", []):
            console.print(f"  Error: {error}")
    
    return results


async def process_text_content(text: str, title: str = "Custom Animation"):
    """Generate animation from custom text content"""
    console.print(f"\n[bold]Generating animation from custom text[/bold]\n")
    
    results = await orchestrator.generate_animation_only(
        text_content=text,
        title=title
    )
    
    if results["success"]:
        console.print("[bold green]✓ Animation generated![/bold green]")
        for anim in results.get("animations", []):
            if anim.get("file_path"):
                console.print(f"  Output: {anim['file_path']}")
    else:
        console.print(f"[bold red]✗ Failed: {results.get('error')}[/bold red]")
    
    return results


async def process_domain_search(
    domain: str, 
    max_results: int = 10, 
    category: str = None,
    render: bool = True,
    save_db: bool = True,
    auto_select: bool = False
):
    """
    Search for papers by domain and process the selected one
    
    Args:
        domain: Domain/topic to search for
        max_results: Maximum number of results to show
        category: Optional arXiv category filter
        render: Whether to render animations
        save_db: Whether to save to database
        auto_select: If True, automatically select the first paper
    """
    console.print(f"\n[bold]Searching for papers in domain: {domain}[/bold]\n")
    
    # Search for papers
    papers = await paper_fetcher.search_by_domain(
        domain=domain,
        max_results=max_results,
        category=category
    )
    
    if not papers:
        console.print(f"[red]No papers found for domain: {domain}[/red]")
        console.print("[yellow]Try a different search term or check your spelling.[/yellow]")
        return None
    
    # Let user select a paper (or auto-select first one)
    if auto_select:
        selected_idx = 0
        console.print(f"\n[cyan]Auto-selecting first paper: {papers[0].title[:60]}...[/cyan]")
    else:
        console.print("\n[bold]Enter the number of the paper you want to process (or 0 to cancel):[/bold]")
        try:
            selected_idx = IntPrompt.ask("Select paper", default=1) - 1
            if selected_idx < 0:
                console.print("[yellow]Cancelled.[/yellow]")
                return None
            if selected_idx >= len(papers):
                console.print(f"[red]Invalid selection. Please choose 1-{len(papers)}[/red]")
                return None
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled.[/yellow]")
            return None
    
    selected_paper = papers[selected_idx]
    
    console.print(f"\n[bold green]📄 Selected: {selected_paper.title}[/bold green]")
    console.print(f"[dim]arXiv ID: {selected_paper.arxiv_id}[/dim]")
    console.print(f"[dim]Authors: {', '.join(selected_paper.authors[:3])}{'...' if len(selected_paper.authors) > 3 else ''}[/dim]")
    
    # Process the selected paper
    results = await process_arxiv_paper(
        arxiv_id=selected_paper.arxiv_id,
        render=render,
        save_db=save_db
    )
    
    return results


async def list_domain_papers(domain: str, max_results: int = 10, category: str = None):
    """Just list papers without processing - useful for exploration"""
    console.print(f"\n[bold]Listing papers in domain: {domain}[/bold]\n")
    
    papers = await paper_fetcher.search_by_domain(
        domain=domain,
        max_results=max_results,
        category=category
    )
    
    if papers:
        console.print("\n[bold cyan]To process any of these papers, run:[/bold cyan]")
        console.print(f"  python main.py --arxiv <arxiv_id>")
        console.print("\n[bold cyan]Or use interactive mode:[/bold cyan]")
        console.print(f'  python main.py --domain "{domain}"')
    
    return papers


def init_database():
    """Initialize database tables"""
    console.print("\n[bold]Initializing database...[/bold]")
    
    try:
        db_manager.create_tables()
        console.print("[green]✓ Database initialized successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Database initialization failed: {e}[/red]")
        console.print("\n[yellow]Make sure your NEON_DATABASE_URL is set correctly in .env[/yellow]")


def check_config():
    """Check if configuration is valid"""
    issues = []
    
    if not config.openrouter.api_key or config.openrouter.api_key == "your_openrouter_api_key_here":
        issues.append("OPENROUTER_API_KEY not set")
    
    if not config.database.database_url or "username:password" in config.database.database_url:
        issues.append("NEON_DATABASE_URL not set (optional, but recommended)")
    
    if issues:
        console.print("\n[yellow]Configuration warnings:[/yellow]")
        for issue in issues:
            console.print(f"  ⚠ {issue}")
        console.print("\n[dim]Copy .env.example to .env and fill in your credentials[/dim]")
        return False
    
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Xe-Bot: Research Paper Animation Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --arxiv 2301.00234           Process an arXiv paper by ID
  python main.py --arxiv 2301.00234 --no-render   Generate code only (no video)
  
  # Domain Search (NEW!)
  python main.py --domain "transformers"      Search & select papers about transformers
  python main.py --domain "computer vision" --category cs.CV   Search in specific category
  python main.py --domain "reinforcement learning" --auto      Auto-select first result
  python main.py --domain "GANs" --list       Just list papers, don't process
  
  python main.py --text "Your content" --title "My Animation"
  python main.py --init-db                    Initialize database tables
  python main.py --demo                       Run demo with sample paper

arXiv Categories:
  cs.AI  - Artificial Intelligence
  cs.LG  - Machine Learning  
  cs.CV  - Computer Vision
  cs.CL  - Computation and Language (NLP)
  cs.NE  - Neural and Evolutionary Computing
  stat.ML - Machine Learning (Statistics)
        """
    )
    
    parser.add_argument("--arxiv", type=str, help="arXiv paper ID to process")
    parser.add_argument("--domain", type=str, help="Search domain/topic (e.g., 'transformers', 'computer vision')")
    parser.add_argument("--category", type=str, help="arXiv category filter (e.g., cs.LG, cs.CV, cs.AI)")
    parser.add_argument("--max-results", type=int, default=10, help="Max papers to show in domain search (default: 10)")
    parser.add_argument("--auto", action="store_true", help="Auto-select first paper in domain search")
    parser.add_argument("--list", action="store_true", help="Just list papers, don't process")
    parser.add_argument("--text", type=str, help="Custom text content to animate")
    parser.add_argument("--title", type=str, default="Research Animation", help="Title for custom animation")
    parser.add_argument("--no-render", action="store_true", help="Skip video rendering (generate code only)")
    parser.add_argument("--no-db", action="store_true", help="Don't save to database")
    parser.add_argument("--init-db", action="store_true", help="Initialize database tables")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample paper")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check configuration
    config_ok = check_config()
    
    if args.init_db:
        init_database()
        return
    
    if args.demo:
        # Demo with a famous AI paper
        args.arxiv = "1706.03762"  # "Attention Is All You Need"
        args.no_render = True  # Skip rendering for demo
        console.print("\n[cyan]Running demo with 'Attention Is All You Need' paper[/cyan]")
    
    # Domain search mode
    if args.domain:
        if not config_ok:
            console.print("\n[red]Please configure your API keys first![/red]")
            return
        
        if args.list:
            # Just list papers
            asyncio.run(list_domain_papers(
                domain=args.domain,
                max_results=args.max_results,
                category=args.category
            ))
        else:
            # Search and process
            asyncio.run(process_domain_search(
                domain=args.domain,
                max_results=args.max_results,
                category=args.category,
                render=not args.no_render,
                save_db=not args.no_db,
                auto_select=args.auto
            ))
    
    elif args.arxiv:
        if not config_ok:
            console.print("\n[red]Please configure your API keys first![/red]")
            return
        
        asyncio.run(process_arxiv_paper(
            arxiv_id=args.arxiv,
            render=not args.no_render,
            save_db=not args.no_db
        ))
    
    elif args.text:
        if not config_ok:
            console.print("\n[red]Please configure your API keys first![/red]")
            return
        
        asyncio.run(process_text_content(
            text=args.text,
            title=args.title
        ))
    
    else:
        parser.print_help()
        console.print("\n[dim]Tip: Start with --demo to see how it works![/dim]")
        console.print("[dim]Or try: python main.py --domain \"transformers\" to search by topic![/dim]")


if __name__ == "__main__":
    main()
