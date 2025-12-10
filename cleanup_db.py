"""
Database Cleanup Script for Xe-Bot
Removes papers/videos that don't have proper animations displayed in frontend
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.models import db_manager, ResearchPaper, Animation, IntroSegment, PaperIntroduction, ProcessingStatus
from sqlalchemy import text

def get_stats():
    """Get current database statistics"""
    session = db_manager.get_session()
    try:
        papers = session.query(ResearchPaper).all()
        animations = session.query(Animation).all()
        segments = session.query(IntroSegment).all()
        
        print("\n" + "="*60)
        print("CURRENT DATABASE STATUS")
        print("="*60)
        print(f"Total Papers: {len(papers)}")
        print(f"Total Animations: {len(animations)}")
        print(f"Total Segments: {len(segments)}")
        
        print("\n--- Papers Details ---")
        for paper in papers:
            paper_anims = [a for a in animations if a.paper_id == paper.id]
            paper_segs = [s for s in segments if s.paper_id == paper.id]
            
            # Check if animation files exist
            valid_anims = []
            invalid_anims = []
            for anim in paper_anims:
                if anim.file_path and Path(anim.file_path).exists():
                    valid_anims.append(anim)
                else:
                    invalid_anims.append(anim)
            
            status_icon = "✓" if valid_anims and paper_segs else "✗"
            print(f"\n{status_icon} Paper ID {paper.id}: {paper.title[:60]}...")
            print(f"   arXiv: {paper.arxiv_id}")
            print(f"   Status: {paper.status.value if paper.status else 'unknown'}")
            print(f"   Segments: {len(paper_segs)}")
            print(f"   Animations: {len(paper_anims)} (valid files: {len(valid_anims)}, missing: {len(invalid_anims)})")
            
            if invalid_anims:
                for inv in invalid_anims:
                    print(f"      ⚠ Missing: {inv.file_path}")
        
        return papers, animations, segments
    finally:
        session.close()


def find_invalid_entries():
    """Find papers/animations that are incomplete or broken"""
    session = db_manager.get_session()
    try:
        papers = session.query(ResearchPaper).all()
        animations = session.query(Animation).all()
        segments = session.query(IntroSegment).all()
        
        invalid_papers = []
        invalid_animations = []
        
        for paper in papers:
            paper_anims = [a for a in animations if a.paper_id == paper.id]
            paper_segs = [s for s in segments if s.paper_id == paper.id]
            
            # Check conditions for invalid paper:
            # 1. No segments
            # 2. No animations
            # 3. All animations have missing files
            # 4. Status is FAILED
            
            has_valid_animation = False
            for anim in paper_anims:
                if anim.file_path and Path(anim.file_path).exists():
                    has_valid_animation = True
                    break
            
            reasons = []
            if not paper_segs:
                reasons.append("no segments")
            if not paper_anims:
                reasons.append("no animations")
            elif not has_valid_animation:
                reasons.append("all animation files missing")
            if paper.status == ProcessingStatus.FAILED:
                reasons.append("processing failed")
            
            if reasons:
                invalid_papers.append((paper, reasons))
        
        # Find orphan animations (no valid file)
        for anim in animations:
            if not anim.file_path or not Path(anim.file_path).exists():
                invalid_animations.append(anim)
        
        return invalid_papers, invalid_animations
    finally:
        session.close()


def cleanup_database(dry_run=True):
    """Remove invalid entries from database"""
    invalid_papers, invalid_animations = find_invalid_entries()
    
    print("\n" + "="*60)
    print("CLEANUP ANALYSIS")
    print("="*60)
    
    if not invalid_papers and not invalid_animations:
        print("✓ Database is clean! No invalid entries found.")
        return
    
    print(f"\nFound {len(invalid_papers)} papers to remove:")
    for paper, reasons in invalid_papers:
        print(f"  - Paper {paper.id}: {paper.title[:50]}... ({', '.join(reasons)})")
    
    print(f"\nFound {len(invalid_animations)} invalid animations:")
    for anim in invalid_animations:
        print(f"  - Animation {anim.id}: {anim.animation_type} (file: {anim.file_path})")
    
    if dry_run:
        print("\n⚠ DRY RUN - No changes made. Run with --execute to apply changes.")
        return
    
    # Actually delete
    session = db_manager.get_session()
    try:
        paper_ids_to_delete = [p.id for p, _ in invalid_papers]
        
        if paper_ids_to_delete:
            # Delete in order due to foreign keys
            # 1. Delete animations for these papers
            session.query(Animation).filter(Animation.paper_id.in_(paper_ids_to_delete)).delete(synchronize_session=False)
            print(f"✓ Deleted animations for {len(paper_ids_to_delete)} papers")
            
            # 2. Delete segments for these papers
            session.query(IntroSegment).filter(IntroSegment.paper_id.in_(paper_ids_to_delete)).delete(synchronize_session=False)
            print(f"✓ Deleted segments for {len(paper_ids_to_delete)} papers")
            
            # 3. Delete introductions for these papers
            session.query(PaperIntroduction).filter(PaperIntroduction.paper_id.in_(paper_ids_to_delete)).delete(synchronize_session=False)
            print(f"✓ Deleted introductions for {len(paper_ids_to_delete)} papers")
            
            # 4. Delete the papers themselves
            session.query(ResearchPaper).filter(ResearchPaper.id.in_(paper_ids_to_delete)).delete(synchronize_session=False)
            print(f"✓ Deleted {len(paper_ids_to_delete)} papers")
        
        # Delete orphan animations (those not linked to deleted papers)
        orphan_anim_ids = [a.id for a in invalid_animations if a.paper_id not in paper_ids_to_delete]
        if orphan_anim_ids:
            session.query(Animation).filter(Animation.id.in_(orphan_anim_ids)).delete(synchronize_session=False)
            print(f"✓ Deleted {len(orphan_anim_ids)} orphan animations")
        
        session.commit()
        print("\n✓ Database cleanup completed successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Error during cleanup: {e}")
        raise
    finally:
        session.close()


def delete_all_data():
    """Delete ALL data from database (nuclear option)"""
    session = db_manager.get_session()
    try:
        # Delete in order due to foreign keys
        count_anims = session.query(Animation).delete()
        count_segs = session.query(IntroSegment).delete()
        count_intros = session.query(PaperIntroduction).delete()
        count_papers = session.query(ResearchPaper).delete()
        
        session.commit()
        
        print("\n" + "="*60)
        print("ALL DATA DELETED")
        print("="*60)
        print(f"Deleted {count_anims} animations")
        print(f"Deleted {count_segs} segments")
        print(f"Deleted {count_intros} introductions")
        print(f"Deleted {count_papers} papers")
        print("\n✓ Database is now empty")
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Error: {e}")
        raise
    finally:
        session.close()


def cleanup_local_files(dry_run=True):
    """Remove local video files that don't match valid database entries"""
    import glob
    import shutil
    
    session = db_manager.get_session()
    try:
        # Get all valid file paths from database
        animations = session.query(Animation).all()
        valid_paths = set()
        for anim in animations:
            if anim.file_path:
                # Normalize path
                normalized = Path(anim.file_path).resolve()
                valid_paths.add(str(normalized))
        
        print("\n" + "="*60)
        print("LOCAL FILE CLEANUP ANALYSIS")
        print("="*60)
        print(f"Valid animations in database: {len(valid_paths)}")
        for vp in valid_paths:
            print(f"  ✓ {vp}")
        
        # Define paths to scan
        base_dir = Path(__file__).parent
        scan_dirs = [
            base_dir / "output" / "media" / "videos",  # Served video files
            base_dir / "output" / "animations" / "videos",  # Animation output
        ]
        
        # Find all video files
        files_to_delete = []
        dirs_to_check = []
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
                
            print(f"\nScanning: {scan_dir}")
            
            # Find all mp4 files
            for mp4_file in scan_dir.rglob("*.mp4"):
                file_resolved = str(mp4_file.resolve())
                if file_resolved not in valid_paths:
                    files_to_delete.append(mp4_file)
        
        print(f"\n--- Files to Delete ({len(files_to_delete)}) ---")
        for f in files_to_delete[:20]:  # Show first 20
            print(f"  ✗ {f}")
        if len(files_to_delete) > 20:
            print(f"  ... and {len(files_to_delete) - 20} more files")
        
        # Also check for empty/temp directories in output/animations
        animations_dir = base_dir / "output" / "animations" / "videos"
        partial_dirs = []
        if animations_dir.exists():
            for partial_dir in animations_dir.rglob("partial_movie_files"):
                partial_dirs.append(partial_dir)
        
        print(f"\n--- Partial/Temp Directories ({len(partial_dirs)}) ---")
        for d in partial_dirs[:10]:
            print(f"  ✗ {d}")
        if len(partial_dirs) > 10:
            print(f"  ... and {len(partial_dirs) - 10} more directories")
        
        if dry_run:
            print("\n⚠ DRY RUN - No files deleted. Run with --execute to apply changes.")
            return
        
        # Actually delete files
        deleted_count = 0
        for f in files_to_delete:
            try:
                f.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"  ⚠ Could not delete {f}: {e}")
        
        print(f"\n✓ Deleted {deleted_count} video files")
        
        # Delete partial_movie_files directories
        deleted_dirs = 0
        for d in partial_dirs:
            try:
                shutil.rmtree(d)
                deleted_dirs += 1
            except Exception as e:
                print(f"  ⚠ Could not delete directory {d}: {e}")
        
        print(f"✓ Deleted {deleted_dirs} temp directories")
        
        # Clean up empty directories
        for scan_dir in scan_dirs:
            if scan_dir.exists():
                for dirpath in sorted(scan_dir.rglob("*"), reverse=True):
                    if dirpath.is_dir():
                        try:
                            dirpath.rmdir()  # Only removes if empty
                        except OSError:
                            pass  # Not empty, skip
        
        print("\n✓ Local file cleanup completed!")
        
    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Xe-Bot Database Cleanup")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--cleanup", action="store_true", help="Clean up invalid entries (dry run)")
    parser.add_argument("--clean-files", action="store_true", help="Clean up local video files not in database")
    parser.add_argument("--execute", action="store_true", help="Actually execute the cleanup")
    parser.add_argument("--delete-all", action="store_true", help="Delete ALL data (dangerous!)")
    
    args = parser.parse_args()
    
    # Initialize database
    db_manager.init_sync_engine()
    
    if args.stats:
        get_stats()
    elif args.clean_files:
        cleanup_local_files(dry_run=not args.execute)
    elif args.cleanup:
        get_stats()
        cleanup_database(dry_run=not args.execute)
    elif args.delete_all:
        confirm = input("\n⚠ WARNING: This will delete ALL data! Type 'DELETE ALL' to confirm: ")
        if confirm == "DELETE ALL":
            delete_all_data()
        else:
            print("Cancelled.")
    else:
        # Default: show stats and dry run cleanup
        get_stats()
        cleanup_database(dry_run=True)
